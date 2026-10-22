"""
ui/corrida_worker.py — Proceso de UNA corrida: simula y sirve su monitor en vivo.

Lo lanza el panel de corridas (ui/hub.py) con `main.py --corrida <carpeta>`.
Pasos:
  1. Lee config.json y aplica sus variables de entorno ANTES de importar el motor
     (los mecanismos se leen al importar los módulos).
  2. Hace chdir a la carpeta de la corrida: BD, checkpoints, métricas y vault
     quedan ahí adentro.
  3. Corre la simulación en un hilo; cada día actualiza estado.json y revisa si
     el panel pidió detenerla (detener.flag).
  4. Sirve el monitor en vivo (NiceGUI) en un puerto libre propio.
  5. Al terminar, el proceso se cierra solo cuando nadie está mirando el monitor.
"""
from __future__ import annotations

import os
import socket
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Minutos que el monitor de una corrida terminada sigue disponible sin nadie mirando
_ESPERA_SIN_CLIENTES_S = 60
# Mínimo de segundos entre escrituras de estado.json
_ESTADO_CADA_S = 1.0


def _puerto_libre() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def ejecutar(carpeta: str, ver: bool = False) -> None:
    d = Path(carpeta).resolve()
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    # Solo stdlib + corridas (no importa nada del motor) antes de fijar el entorno
    from core.runtime import corridas as C

    cfg = C.leer_config(d)
    os.environ.update(cfg.entorno())

    puerto = _puerto_libre()
    hub_url = os.environ.get("PSYCHE_HUB_URL", "")

    if ver:
        _ver_estado_final(d, cfg, C, puerto, hub_url)
        return

    os.chdir(d)
    C.escribir_estado(d, fase="iniciando", pid=os.getpid(), puerto=puerto,
                      inicio=time.strftime("%Y-%m-%dT%H:%M:%S"))

    try:
        _correr(d, cfg, C, puerto, hub_url)
    except Exception as e:
        traceback.print_exc()
        C.escribir_estado(d, fase="error", error=f"{type(e).__name__}: {e}")
        raise


def _correr(d: Path, cfg, C, puerto: int, hub_url: str) -> None:
    from ui.app_state import AppState
    from ui import db_reader

    db_reader.configurar(d / "data")
    app_state = AppState()

    def _preparar() -> None:
        """Arma el runner fuera del hilo de la UI (puede tardar con 100 agentes)."""
        try:
            if cfg.narrativa:
                from core.narrative.daemon import OllamaDaemon
                OllamaDaemon().setup()

            from core.simulation import SimulationRunner
            from core.runtime.psyche_runtime import PsycheRuntime

            cp_dir = Path("data/checkpoints")
            reanudar = cp_dir.is_dir() and any(cp_dir.glob("checkpoint_*.json"))
            if reanudar:
                runner = SimulationRunner.resume(
                    db_path="data/db/simulation.db", checkpoint_dir=str(cp_dir),
                    vault_path="vault")
            else:
                runner = SimulationRunner.new_session(
                    seed_file=str(C.ruta_poblacion(cfg.poblacion)),
                    seed=cfg.semilla,
                    db_path="data/db/simulation.db",
                    checkpoint_dir=str(cp_dir),
                    vault_path="vault")

            if cfg.liminal:
                from ui.psyche_ui import conectar_liminal
                conectar_liminal(runner, app_state, cfg.liminal_host, cfg.liminal_port, cfg.semilla)

            runtime = PsycheRuntime()
            runtime.attach_runner(runner)
            runtime.state.simulation = "running"
            app_state.set_runner(runner, runtime)

            total = len(runner.agents.agents)
            ultimo = [0.0]

            def _pausa_y_estado(tp) -> None:
                # Pausa desde el monitor
                if app_state._pause_event.is_set():
                    C.escribir_estado(d, fase="pausada")
                    while app_state._pause_event.is_set() and not C.detencion_pedida(d):
                        time.sleep(0.05)
                # Detención pedida por el panel o el monitor
                if C.detencion_pedida(d):
                    C.escribir_estado(d, fase="deteniendo")
                    runner.shutdown()
                    return
                ahora = time.monotonic()
                if ahora - ultimo[0] >= _ESTADO_CADA_S:
                    ultimo[0] = ahora
                    _escribir_progreso(d, C, runner, total, fase="corriendo")

            runner.clock.on_day(_pausa_y_estado, priority=98)  # antes del stopper (99)

            dias = cfg.dias_efectivos()
            if reanudar:
                # Si se reanuda, correr lo que falte hasta el objetivo original
                dias = max(1, dias - runner.current_dia)
            _escribir_progreso(d, C, runner, total, fase="corriendo")
            runner.run(n_days=dias)

            _cerrar(d, C, runner, total)
        except Exception as e:
            traceback.print_exc()
            C.escribir_estado(d, fase="error", error=f"{type(e).__name__}: {e}")
        finally:
            app_state._pause_event.clear()
            rt = app_state.get_runtime()
            if rt is not None:
                rt.state.simulation = "stopped"
            threading.Thread(target=_salir_sin_clientes, daemon=True,
                             name="salida_corrida").start()

    t = threading.Thread(target=_preparar, daemon=True, name="sim_worker")
    t.start()
    app_state.sim_thread = t

    _servir_monitor(app_state, cfg, puerto, hub_url, d, C)


def _escribir_progreso(d: Path, C, runner, total: int, fase: str) -> None:
    try:
        agents = runner.agents
        tribus = len(getattr(agents.tribe_manager, "tribes", {}) or {})
        nomos = getattr(agents, "nomos", None)
        C.escribir_estado(
            d, fase=fase,
            dia=runner.current_dia,
            vivos=runner.alive_count,
            total=max(total, len(agents.agents)),
            tribus=tribus,
            nomos_activo=(nomos.enabled if nomos is not None else None),
            eden_event=getattr(agents, "eden_event", None),
        )
    except Exception as e:
        print(f"[corrida] no se pudo escribir el progreso: {e}", file=sys.stderr)


def _cerrar(d: Path, C, runner, total: int) -> None:
    """Fase final + resumen de métricas."""
    if runner.alive_count == 0:
        fase = "extinta"
    elif C.detencion_pedida(d):
        fase = "detenida"
    else:
        fase = "terminada"
    try:
        runner.metrics_exporter.export_summary()
    except Exception as e:
        print(f"[corrida] no se pudo exportar el resumen de métricas: {e}", file=sys.stderr)
    _escribir_progreso(d, C, runner, total, fase=fase)
    C.escribir_estado(d, fin=time.strftime("%Y-%m-%dT%H:%M:%S"))
    try:
        (d / C.ARCHIVO_DETENER).unlink(missing_ok=True)
    except OSError as e:
        print(f"[corrida] no se pudo borrar detener.flag: {e}", file=sys.stderr)


def _salir_sin_clientes() -> None:
    """Cierra el proceso cuando nadie mira el monitor durante un rato."""
    from nicegui import Client
    quieto_desde = time.monotonic()
    while True:
        time.sleep(2)
        conectados = sum(1 for c in list(Client.instances.values())
                         if getattr(c, "has_socket_connection", False))
        if conectados:
            quieto_desde = time.monotonic()
        elif time.monotonic() - quieto_desde > _ESPERA_SIN_CLIENTES_S:
            os._exit(0)


def _ver_estado_final(d: Path, cfg, C, puerto: int, hub_url: str) -> None:
    """Visor de una corrida que ya no corre: carga su último checkpoint y sirve el
    monitor SIN avanzar el reloj ni escribir nada en la carpeta de la corrida.

    Se reanuda desde una copia temporal del checkpoint, con BD y vault
    descartables; las métricas históricas se leen de la BD real en solo lectura.
    """
    import shutil
    import tempfile
    from ui.app_state import AppState
    from ui import db_reader

    os.environ["NARRATIVE_ENABLED"] = "false"   # el visor no narra
    checkpoints = sorted((d / "data" / "checkpoints").glob("checkpoint_*.json"))
    if not checkpoints:
        C.escribir_estado(d, visor={"error": "La corrida no tiene ningún guardado"})
        return

    tmp = Path(tempfile.mkdtemp(prefix="psyche_visor_"))
    (tmp / "checkpoints").mkdir()
    shutil.copy2(checkpoints[-1], tmp / "checkpoints" / checkpoints[-1].name)
    os.chdir(tmp)
    db_reader.configurar(d / "data")
    app_state = AppState()
    C.escribir_estado(d, visor={"pid": os.getpid(), "puerto": puerto})

    def _cargar() -> None:
        try:
            from core.simulation import SimulationRunner
            from core.runtime.psyche_runtime import PsycheRuntime
            runner = SimulationRunner.resume(
                checkpoint_dir=str(tmp / "checkpoints"),
                db_path=str(tmp / "visor.db"), vault_path=str(tmp / "vault"))
            runner.world.refresh_snapshot(runner.clock.now)
            runtime = PsycheRuntime()
            runtime.attach_runner(runner)
            runtime.state.simulation = "stopped"
            app_state.set_runner(runner, runtime)
        except Exception as e:
            traceback.print_exc()
            C.escribir_estado(d, visor={"error": f"{type(e).__name__}: {e}"})
        threading.Thread(target=_salir_sin_clientes, daemon=True, name="salida_visor").start()

    threading.Thread(target=_cargar, daemon=True, name="visor").start()
    titulo = f"{cfg.nombre or cfg.resumen()} — estado final"
    try:
        _servir_monitor(app_state, cfg, puerto, hub_url, d, C, titulo=titulo, detener=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _servir_monitor(app_state, cfg, puerto: int, hub_url: str, d: Path, C,
                    titulo: str | None = None, detener: bool = True) -> None:
    from nicegui import app, ui
    from ui.psyche_ui import build_monitor_page

    # Fuentes e ilustraciones del tema
    app.add_static_files("/assets", str(ROOT / "assets"))

    @ui.page("/")
    def monitor():
        build_monitor_page(app_state, hub_url=hub_url or None,
                           titulo=titulo or cfg.nombre or cfg.resumen(),
                           on_detener=(lambda: C.pedir_detencion(d)) if detener else None)

    ui.run(
        title=f"{titulo or cfg.nombre or 'Corrida'} · PSYCHE SIMULACRA",
        host="127.0.0.1",
        port=puerto,
        dark=True,
        show=False,
        favicon="🧠",
        reload=False,
        reconnect_timeout=10,
        show_welcome_message=False,
    )
