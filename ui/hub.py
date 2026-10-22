"""
ui/hub.py — Panel de corridas de PSYCHE SIMULACRA.

Desde acá se configuran y lanzan una o más simulaciones. Cada corrida es un
proceso propio con su carpeta (ver core/runtime/corridas.py y
ui/corrida_worker.py). El panel:

  - arma tandas: escenarios × réplicas (semillas consecutivas);
  - respeta un máximo de corridas simultáneas (el resto queda en cola);
  - muestra el progreso de todas y permite abrir el monitor en vivo de la que
    se elija, detenerla, reanudarla o borrarla;
  - compara la población y las tribus de las corridas seleccionadas.

Doctrina C: el panel observa y lanza; nunca toca el mundo de una corrida en curso.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

from core.runtime import corridas as C
from ui.theme import apply_theme

ROOT = Path(__file__).resolve().parent.parent
HUB_PORT = int(os.environ.get("PSYCHE_HUB_PORT", "8080"))

# ── Textos para quien no conoce el código ─────────────────────────────────────

MECANISMOS: list[tuple[str, str, str]] = [
    ("filtro_interpretativo", "Filtro interpretativo",
     "Cada persona interpreta lo que vive según su psicología: el mismo hecho "
     "no significa lo mismo para todos."),
    ("reinterpretacion_receptor", "Reinterpretación del receptor",
     "Lo que alguien comunica llega deformado por la lectura de quien lo recibe "
     "(héroes y monstruos se reconocen por tribu, no en general)."),
    ("boveda_mental", "Bóveda mental",
     "Memoria interna persistente de cada persona, que tiñe sus decisiones "
     "(requiere el filtro interpretativo; sin él se apaga sola)."),
    ("recalibracion_arquetipica", "Recalibración arquetípica",
     "Las vivencias sostenidas pueden reorganizar la personalidad de fondo "
     "(requiere el filtro interpretativo). EXPERIMENTAL: todavía no está calibrada; "
     "en las pruebas casi toda la población termina dominada por la sombra."),
]

AYUDA_NATALIDAD = (
    "Con los valores por defecto casi no hay nacimientos y toda sociedad termina "
    "extinguiéndose por desgaste. Subir la probabilidad diaria o bajar el vínculo "
    "mínimo permite que la población se renueve."
)

_FASE_COLOR = {
    "en_cola": "grey", "iniciando": "blue", "corriendo": "green", "pausada": "orange",
    "deteniendo": "orange", "terminada": "purple", "extinta": "red-9",
    "detenida": "brown", "error": "red", "interrumpida": "red-4",
}
_FASE_TEXTO = {
    "en_cola": "en cola", "iniciando": "iniciando", "corriendo": "corriendo",
    "pausada": "pausada", "deteniendo": "deteniendo", "terminada": "terminada",
    "extinta": "extinta", "detenida": "detenida", "error": "error",
    "interrumpida": "interrumpida",
}


# ── Procesos ──────────────────────────────────────────────────────────────────

def _entorno_hijo() -> dict[str, str]:
    """Entorno para los procesos de corridas: sin las variables internas de NiceGUI."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("NICEGUI_", "PYTEST_"))}
    env["PSYCHE_HUB_URL"] = f"http://127.0.0.1:{HUB_PORT}"
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _pid_vivo(pid: int | None) -> bool:
    if not pid:
        return False
    if sys.platform == "win32":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
            return code.value == STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    # Un hijo terminado sin recoger sigue "existiendo" como zombie
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
            return f.read().split(") ", 1)[1][:1] != "Z"
    except (OSError, IndexError):
        return True


class Gestor:
    """Lanza y sigue los procesos de las corridas. Un único gestor por panel."""

    def __init__(self) -> None:
        self._procs: dict[str, subprocess.Popen] = {}
        self._lock = threading.Lock()
        self.max_paralelo = max(1, (os.cpu_count() or 2) - 1)
        self._liminal_proc: subprocess.Popen | None = None

    # Estado efectivo: corrige "corriendo" de procesos que ya no existen
    def estado(self, d: Path) -> dict:
        est = C.leer_estado(d)
        fase = est.get("fase")
        if fase in C.FASES_ACTIVAS and not self._vivo(d, est):
            est = C.escribir_estado(d, fase="interrumpida")
        return est

    def _vivo(self, d: Path, est: dict) -> bool:
        p = self._procs.get(str(d))
        if p is not None:
            return p.poll() is None
        return _pid_vivo(est.get("pid"))

    def activas(self) -> int:
        return sum(1 for d in C.listar_corridas()
                   if self.estado(d).get("fase") in C.FASES_ACTIVAS)

    def lanzar(self, d: Path) -> None:
        cfg = C.leer_config(d)
        if cfg.liminal and cfg.liminal_host in ("localhost", "127.0.0.1"):
            self._asegurar_liminal(cfg.liminal_port)
        env = _entorno_hijo()
        log = open(d / C.ARCHIVO_LOG, "a", encoding="utf-8")
        kwargs: dict = {"stdout": log, "stderr": subprocess.STDOUT, "env": env, "cwd": str(d)}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        else:
            kwargs["start_new_session"] = True
        C.escribir_estado(d, fase="iniciando", error=None)
        p = subprocess.Popen(C.comando_corrida(d), **kwargs)
        log.close()
        with self._lock:
            self._procs[str(d)] = p
        C.escribir_estado(d, pid=p.pid)

    def procesar_cola(self) -> None:
        """Lanza corridas en cola, de la más vieja a la más nueva, si hay lugar."""
        libres = self.max_paralelo - self.activas()
        if libres <= 0:
            return
        en_cola = [d for d in reversed(C.listar_corridas())
                   if C.leer_estado(d).get("fase") == "en_cola"]
        for d in en_cola[:libres]:
            try:
                self.lanzar(d)
            except Exception as e:
                print(f"[hub] no se pudo lanzar {d.name}: {e}", file=sys.stderr)
                C.escribir_estado(d, fase="error", error=f"No se pudo lanzar: {e}")

    def visor_url(self, d: Path) -> str | None:
        """URL del visor de estado final si está levantado y vivo."""
        v = C.leer_estado(d).get("visor") or {}
        if v.get("puerto") and _pid_vivo(v.get("pid")):
            return f"http://127.0.0.1:{v['puerto']}"
        return None

    def ver_estado_final(self, d: Path) -> None:
        """Levanta el visor de estado final de una corrida (si no está ya)."""
        if self.visor_url(d):
            return
        C.escribir_estado(d, visor={"lanzando": True})
        env = _entorno_hijo()
        log = open(d / C.ARCHIVO_LOG, "a", encoding="utf-8")
        kwargs: dict = {"stdout": log, "stderr": subprocess.STDOUT, "env": env}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        else:
            kwargs["start_new_session"] = True
        subprocess.Popen(C.comando_corrida(d, ver=True), **kwargs)
        log.close()

    def reanudar(self, d: Path) -> None:
        (d / C.ARCHIVO_DETENER).unlink(missing_ok=True)
        C.escribir_estado(d, fase="en_cola", error=None)

    def detener(self, d: Path) -> None:
        est = C.leer_estado(d)
        if est.get("fase") == "en_cola":
            C.escribir_estado(d, fase="detenida")
        else:
            C.pedir_detencion(d)

    def _asegurar_liminal(self, port: int) -> None:
        if self._liminal_proc is not None and self._liminal_proc.poll() is None:
            return
        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--liminal-server"]
        else:
            cmd = [sys.executable, str(ROOT / "main.py"), "--liminal-server"]
        cmd += ["--host", "0.0.0.0", "--port", str(port), "--seed", "0"]
        kwargs: dict = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        else:
            kwargs["start_new_session"] = True
        self._liminal_proc = subprocess.Popen(cmd, **kwargs)


GESTOR = Gestor()


# ── Utilidades ────────────────────────────────────────────────────────────────

def _poblaciones() -> dict[str, str]:
    out = {}
    for nombre, path in C.listar_poblaciones().items():
        n = C.contar_personas(path)
        out[nombre] = f"{path.stem} ({n} personas)" if n else path.stem
    return out


def _ollama_estado() -> str:
    if shutil.which("ollama") is None:
        return "no_instalado"
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=0.5):
            return "activo"
    except Exception:
        return "instalado"


def _abrir_carpeta(d: Path) -> None:
    try:
        if sys.platform == "win32":
            os.startfile(d)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(d)])
        else:
            subprocess.Popen(["xdg-open", str(d)])
    except Exception as e:
        print(f"[hub] no se pudo abrir la carpeta {d}: {e}", file=sys.stderr)


def _orden_texto(est: dict, cfg: C.CorridaConfig) -> str:
    if cfg.escenario == "off":
        return "—"
    if cfg.escenario == "orden":
        return "vigente"
    ev = est.get("eden_event")
    if ev:
        return f"roto el día {ev.get('dia')} ({ev.get('agent_nombre', '?')})"
    return "vigente" if est.get("nomos_activo", True) else "roto"


# ── Página ────────────────────────────────────────────────────────────────────

def construir_panel() -> None:
    from nicegui import ui

    apply_theme(ui)
    with ui.header().classes("text-white items-center ps-main-header"):
        ui.image("/assets/psyche-seal.svg").classes("ps-brand-seal")
        ui.label("PSYCHE SIMULACRA").classes("text-xl font-bold tracking-widest ps-brand-mark")
        ui.label("Laboratorio de sociedades simuladas").classes("text-sm ps-brand-subtitle")
        ui.space()
        ui.label("El inconsciente colectivo emerge — no se construye.").classes("ps-header-motto")
        ui.link("Guía de uso", "/guia", new_tab=True).classes("text-sm ps-guide-link")

    with ui.row().classes("w-full ps-app-layout no-wrap"):
        with ui.column().classes("ps-sidebar"):
            ui.link("▷  Corridas", "#ps-runs").classes("ps-nav-link ps-nav-active")
            ui.link("◉  Observatorio", "#ps-observatory").classes("ps-nav-link")
            ui.link("▥  Comparar", "#ps-compare").classes("ps-nav-link")
            ui.link("▤  Archivo", "#ps-runs").classes("ps-nav-link")
            ui.image("/assets/observatory-mandala.svg").classes("ps-sidebar-mandala")
            ui.label("“Modelar para observar lo que siempre ha estado ahí.”").classes("ps-sidebar-quote")
        with ui.column().classes("w-full ps-page-shell"):
            with ui.row().classes("w-full ps-dashboard-top no-wrap"):
                with ui.column().classes("ps-dashboard-main"):
                    _seccion_nueva(ui)
                _seccion_estado_laboratorio(ui)
            with ui.row().classes("w-full ps-dashboard-bottom no-wrap"):
                tabla = _seccion_corridas(ui)
                _seccion_comparar(ui, tabla)


def _seccion_estado_laboratorio(ui) -> None:
    """Resumen lateral del estado efectivo del panel; no inicia ni modifica corridas."""
    from nicegui import ui

    dirs = C.listar_corridas()
    activas = GESTOR.activas()
    ollama = _ollama_estado()
    ollama_texto = {"activo": "Funcionando", "instalado": "Instalado", "no_instalado": "No instalado"}[ollama]
    with ui.card().classes("ps-lab-status-card"):
        ui.label("⚙  Estado del laboratorio").classes("ps-lab-status-title")
        with ui.column().classes("ps-status-list"):
            for icono, nombre, estado, ok in [
                ("⚙", "Motor de simulación", "Listo", True),
                ("▤", "Registro de corridas", f"{len(dirs)} registradas", True),
                ("✣", "Narrativa (Ollama)", ollama_texto, ollama == "activo"),
            ]:
                with ui.row().classes("ps-status-row items-center no-wrap"):
                    ui.label(icono).classes("ps-status-icon")
                    ui.label(nombre).classes("ps-status-name")
                    ui.space()
                    ui.label("●").classes("ps-status-dot " + ("is-ready" if ok else "is-idle"))
                    ui.label(estado).classes("ps-status-value")
        ui.separator()
        with ui.row().classes("w-full items-center justify-between ps-active-runs"):
            ui.label("Corridas activas").classes("ps-panel-title")
            ui.label(f"{activas} / {GESTOR.max_paralelo}").classes("ps-active-count")
        ui.label("Procesos de simulación en ejecución o inicialización.").classes("ps-status-caption")
        ui.separator()
        ui.label("Símbolo del observatorio").classes("ps-panel-title")
        ui.image("/assets/observatory-mandala.svg").classes("ps-status-art")
        ui.label("Mundo, mito y psicología: observación de sistemas emergentes.").classes("ps-status-caption")


def _ajustes_finos(ui, seccion: str, destino: dict) -> None:
    """Campos numéricos de los ajustes finos de una sección (ver corridas.PARAMETROS_FINOS)."""
    for var, sec, etiqueta, ayuda, default, minimo, maximo, paso, entero in C.PARAMETROS_FINOS:
        if sec != seccion:
            continue
        with ui.row().classes("items-center gap-3 w-full no-wrap"):
            destino[var] = ui.number(etiqueta, value=default, min=minimo, max=maximo, step=paso,
                                     format="%d" if entero else "%.2f").classes("w-72 shrink-0")
            ui.label(ayuda).classes("text-xs text-gray-400")


def _seccion_nueva(ui) -> None:
    pobl = _poblaciones()
    finos: dict[str, object] = {}
    with ui.card().classes("w-full bg-gray-900 text-gray-100 p-6 ps-hero-card").props("id=ps-observatory"):
        with ui.row().classes("w-full items-start justify-between ps-hero-heading-row"):
            with ui.column().classes("gap-1"):
                ui.label("DISEÑO DEL EXPERIMENTO").classes("ps-section-kicker")
                ui.label("Nueva tanda de corridas").classes("text-lg font-semibold text-purple-200 ps-section-heading")
            ui.button("Configurar rápido", icon="settings", on_click=lambda: ui.notify("Los parámetros avanzados están disponibles en cada sección.")).props("outline dense").classes("ps-quick-config")
        ui.label("Elegí uno o más escenarios. Cada escenario se corre una vez por réplica; "
                 "las réplicas usan semillas consecutivas, y el mismo número de semilla "
                 "significa el mismo mundo y la misma población inicial en todos los escenarios."
                 ).classes("text-sm text-gray-400 mb-2 ps-section-description")

        esc_checks: dict[str, object] = {}
        with ui.row().classes("w-full gap-4 items-stretch ps-scenario-grid"):
            for clave, nombre in C.ESCENARIOS.items():
                scenario_asset = {"off": "ps-scenario-off", "orden": "ps-scenario-orden", "eden": "ps-scenario-eden"}.get(clave, "ps-scenario-generic")
                with ui.card().classes(f"flex-1 min-w-[220px] bg-gray-800 p-4 ps-scenario-card {scenario_asset}"):
                    esc_checks[clave] = ui.checkbox(nombre, value=(clave == "off")).classes(
                        "font-semibold")
                    ui.label(C.ESCENARIOS_DESC[clave]).classes("text-xs text-gray-400 ps-scenario-description")

        with ui.row().classes("w-full gap-4 mt-2 items-end ps-primary-fields"):
            poblacion = ui.select(pobl, value=next(iter(pobl), None),
                                  label="Población inicial").classes("min-w-[240px]")
            semilla = ui.number("Semilla inicial", value=1, min=0, format="%d").classes("w-36")
            replicas = ui.number("Réplicas", value=1, min=1, max=100, format="%d").classes("w-28")
            nombre = ui.input("Nombre de la tanda (opcional)").classes("flex-1 min-w-[200px] ps-run-name-field")

        with ui.expansion("Generar una población nueva", icon="group_add").classes("w-full ps-config-section"):
            ui.label("Crea un grupo de personas con perfiles psicológicos variados, distinto "
                     "según la semilla. Queda disponible en «Población inicial».").classes(
                "text-xs text-gray-400")
            with ui.row().classes("gap-4 items-end"):
                gen_n = ui.number("Cantidad de personas", value=50, min=2, max=1000,
                                  format="%d").classes("w-48")
                gen_s = ui.number("Semilla de la población", value=1, min=0,
                                  format="%d").classes("w-48")

                def _generar() -> None:
                    try:
                        out = C.generar_poblacion(int(gen_n.value or 2), int(gen_s.value or 0))
                    except Exception as e:
                        ui.notify(f"No se pudo generar: {e}", type="negative")
                        return
                    poblacion.set_options(_poblaciones(), value=out.name)
                    ui.notify(f"Población {out.stem} creada.", type="positive")

                ui.button("Generar", icon="add", on_click=_generar).props("outline")

        with ui.row().classes("w-full gap-4 items-end ps-duration-row"):
            duracion = ui.radio({"ext": "Hasta la extinción", "dias": "Cantidad de días"},
                                value="dias").props("inline dark")
            dias = ui.number("Días", value=365, min=1, format="%d").classes("w-32") \
                .bind_visibility_from(duracion, "value", value="dias")
            ui.label(f"(tope de seguridad: {C.TOPE_EXTINCION_DIAS // 365} años)").classes(
                "text-xs text-gray-500").bind_visibility_from(duracion, "value", value="ext")

        mec: dict[str, object] = {}
        with ui.expansion("Mecanismos psicológicos", icon="psychology").classes("w-full ps-config-section"):
            ui.label("Vienen apagados: el modelo base funciona sin ellos.").classes(
                "text-xs text-gray-500")
            for clave, titulo, ayuda in MECANISMOS:
                with ui.row().classes("items-start gap-2 w-full no-wrap"):
                    mec[clave] = ui.switch(titulo)
                    ui.label(ayuda).classes("text-xs text-gray-400 pt-2")
            _ajustes_finos(ui, "Mecanismos psicológicos", finos)

        defaults = C.CorridaConfig()
        with ui.expansion("Natalidad", icon="child_care").classes("w-full ps-config-section"):
            ui.label(AYUDA_NATALIDAD).classes("text-xs text-gray-400")
            with ui.row().classes("gap-4"):
                prob = ui.number("Probabilidad diaria de concebir", value=defaults.prob_repro_diaria,
                                 min=0, max=1, step=0.001, format="%.3f").classes("w-64")
                vinc = ui.number("Vínculo mínimo de la pareja (0–1)", value=defaults.vinculo_min_repro,
                                 min=0, max=1, step=0.05, format="%.2f").classes("w-64")
                nec = ui.number("Hambre/sed máxima para concebir (0–1)",
                                value=defaults.necesidades_max_repro,
                                min=0, max=1, step=0.05, format="%.2f").classes("w-64")
            _ajustes_finos(ui, "Natalidad", finos)

        with ui.expansion("Orden y Serpiente", icon="balance").classes("w-full ps-config-section"):
            _ajustes_finos(ui, "Orden y Serpiente", finos)

        with ui.expansion("Mundo, cultura y mito", icon="public").classes("w-full ps-config-section"):
            _ajustes_finos(ui, "Mundo", finos)
            _ajustes_finos(ui, "Cultura y mito", finos)

        estado_ollama = _ollama_estado()
        with ui.expansion("Narrativa con IA", icon="auto_stories").classes("w-full ps-config-section"):
            ui.label("Genera crónicas, elegías y leyendas en texto con un modelo de lenguaje "
                     "local (Ollama). Hace la corrida mucho más lenta y no cambia la simulación."
                     ).classes("text-xs text-gray-400")
            aviso = {
                "no_instalado": "Ollama no está instalado en esta computadora: la narrativa no "
                                "va a funcionar. Se puede instalar desde ollama.com.",
                "instalado": "Ollama está instalado; se va a iniciar al lanzar una corrida con "
                             "narrativa (la primera vez descarga el modelo, varios GB).",
                "activo": "Ollama está funcionando.",
            }[estado_ollama]
            ui.label(aviso).classes("text-xs " + ("text-red-400" if estado_ollama == "no_instalado"
                                                 else "text-green-400"))
            with ui.row().classes("gap-4 items-end"):
                narr = ui.switch("Activar narrativa", value=False)
                modelo = ui.input("Modelo", value=defaults.modelo_ollama).classes("w-48")
            if estado_ollama == "no_instalado":
                narr.disable()

        with ui.expansion("Avanzado", icon="tune").classes("w-full ps-config-section"):
            with ui.row().classes("gap-4 items-end"):
                clus = ui.number("Días hasta formar tribus", value=defaults.dias_hasta_clustering,
                                 min=1, format="%d").classes("w-56")
                cp = ui.number("Días entre guardados", value=defaults.dias_entre_checkpoints,
                               min=1, format="%d").classes("w-48")
                paralelo = ui.number("Corridas simultáneas", value=GESTOR.max_paralelo, min=1,
                                     max=max(1, os.cpu_count() or 1), format="%d").classes("w-48")
            with ui.row().classes("gap-4 items-end"):
                lim = ui.switch("Zona Liminal (intercambio de personas entre corridas)")
                lim_host = ui.input("Servidor", value="localhost").classes("w-48") \
                    .bind_visibility_from(lim, "value")
                lim_port = ui.number("Puerto", value=8765, min=1024, max=65534,
                                     format="%d").classes("w-28").bind_visibility_from(lim, "value")

        resumen = ui.label("").classes("text-sm text-purple-200 mt-2 ps-run-summary")

        def _escenarios() -> list[str]:
            return [k for k, cb in esc_checks.items() if cb.value]

        def _actualizar_resumen() -> None:
            n = len(_escenarios()) * int(replicas.value or 1)
            resumen.set_text(f"Se van a crear {n} corrida{'s' if n != 1 else ''}."
                             if n else "Elegí al menos un escenario.")

        for w in (*esc_checks.values(), replicas):
            w.on_value_change(lambda _: _actualizar_resumen())
        _actualizar_resumen()

        def _lanzar() -> None:
            escs = _escenarios()
            if not escs:
                ui.notify("Elegí al menos un escenario.", type="warning")
                return
            GESTOR.max_paralelo = int(paralelo.value or 1)
            base = int(semilla.value or 0)
            creadas = 0
            for r in range(int(replicas.value or 1)):
                for esc in escs:
                    s = base + r
                    etiqueta = (nombre.value or "").strip()
                    cfg = C.CorridaConfig(
                        escenario=esc,
                        poblacion=poblacion.value,
                        semilla=s,
                        dias=0 if duracion.value == "ext" else int(dias.value or 1),
                        nombre=(f"{etiqueta} · " if etiqueta else "")
                               + f"{C.ESCENARIOS[esc]} · semilla {s}",
                        narrativa=bool(narr.value),
                        modelo_ollama=(modelo.value or "llama3.2").strip(),
                        filtro_interpretativo=bool(mec["filtro_interpretativo"].value),
                        reinterpretacion_receptor=bool(mec["reinterpretacion_receptor"].value),
                        boveda_mental=bool(mec["boveda_mental"].value),
                        recalibracion_arquetipica=bool(mec["recalibracion_arquetipica"].value),
                        prob_repro_diaria=float(prob.value or 0),
                        vinculo_min_repro=float(vinc.value or 0),
                        necesidades_max_repro=float(nec.value or 0),
                        dias_hasta_clustering=int(clus.value or 30),
                        dias_entre_checkpoints=int(cp.value or 10),
                        liminal=bool(lim.value),
                        liminal_host=(lim_host.value or "localhost").strip(),
                        liminal_port=int(lim_port.value or 8765),
                        ajustes={var: float(w.value) for var, w in finos.items()
                                 if w.value is not None},
                    )
                    errores = cfg.validar()
                    if errores:
                        ui.notify(" · ".join(errores), type="negative", multi_line=True)
                        return
                    C.crear_corrida(cfg)
                    creadas += 1
            GESTOR.procesar_cola()
            ui.notify(f"{creadas} corrida{'s' if creadas != 1 else ''} en marcha o en cola.",
                      type="positive")

        ui.button("Lanzar", icon="play_arrow", on_click=_lanzar).props(
            "color=purple-7").classes("mt-2 ps-launch-btn")


def _seccion_corridas(ui):
    columnas = [
        {"name": "nombre", "label": "Corrida", "field": "nombre", "align": "left"},
        {"name": "fase", "label": "Estado", "field": "fase", "align": "left"},
        {"name": "dia", "label": "Día", "field": "dia"},
        {"name": "anios", "label": "Años", "field": "anios"},
        {"name": "vivos", "label": "Vivos", "field": "vivos"},
        {"name": "tribus", "label": "Tribus", "field": "tribus"},
        {"name": "orden", "label": "Orden (Nomos)", "field": "orden", "align": "left"},
        {"name": "acciones", "label": "", "field": "acciones"},
    ]
    with ui.card().classes("w-full bg-gray-900 text-gray-100 p-4 ps-runs-card").props("id=ps-runs"):
        ui.label("REGISTRO DE EJECUCIONES").classes("ps-section-kicker")
        with ui.row().classes("w-full items-center"):
            ui.label("Corridas").classes("text-lg font-semibold text-purple-200 ps-section-heading")
            ui.space()
            ui.button("Detener todas", icon="stop", on_click=lambda: _detener_todas(ui)).props(
                "flat color=red-4")
        ui.label("«Ver en vivo» abre el monitor completo (mapa, personas, mitos, red social) "
                 "de esa corrida en otra pestaña. Las demás siguen corriendo por detrás y "
                 "guardan todos sus datos en su carpeta.").classes("text-xs text-gray-400")
        tabla = ui.table(columns=columnas, rows=[], row_key="id", selection="multiple"
                         ).classes("w-full ps-runs-table").props(
                             'dark flat dense no-data-label="Todavía no hay corridas registradas."'
                         )
        tabla.add_slot("body-cell-fase", r'''
            <q-td :props="props">
              <q-badge :color="props.row.color" :label="props.value" />
              <div v-if="props.row.error" class="text-red-4 text-caption">{{ props.row.error }}</div>
            </q-td>''')
        tabla.add_slot("body-cell-nombre", r'''
            <q-td :props="props">
              <div>{{ props.value }}</div>
              <div class="text-grey-6 text-caption">{{ props.row.detalle }}</div>
            </q-td>''')
        tabla.add_slot("body-cell-acciones", r'''
            <q-td :props="props" class="q-gutter-xs">
              <q-btn v-if="props.row.url" dense size="sm" color="purple-7" icon="visibility"
                     label="Ver en vivo" :href="props.row.url" target="_blank" />
              <q-btn v-if="!props.row.url && props.row.puede_ver_final" dense size="sm" outline
                     color="purple-3" icon="visibility" label="Estado final"
                     :href="'/visor/' + props.row.id" target="_blank" />
              <q-btn v-if="props.row.puede_detener" dense flat size="sm" color="red-4" icon="stop"
                     @click="$parent.$emit('detener', props.row.id)"><q-tooltip>Detener</q-tooltip></q-btn>
              <q-btn v-if="props.row.puede_reanudar" dense flat size="sm" color="green-4"
                     icon="replay" @click="$parent.$emit('reanudar', props.row.id)">
                     <q-tooltip>Reanudar</q-tooltip></q-btn>
              <q-btn dense flat size="sm" color="grey-5" icon="folder_open"
                     @click="$parent.$emit('carpeta', props.row.id)"><q-tooltip>Abrir carpeta con los datos</q-tooltip></q-btn>
              <q-btn v-if="!props.row.puede_detener" dense flat size="sm" color="grey-6" icon="delete"
                     @click="$parent.$emit('borrar', props.row.id)"><q-tooltip>Borrar</q-tooltip></q-btn>
            </q-td>''')

        def _por_id(rid: str) -> Path | None:
            d = C.directorio_corridas() / rid
            return d if d.is_dir() else None

        def _on(evento: str, fn) -> None:
            def h(e) -> None:
                d = _por_id(e.args)
                if d is not None:
                    fn(d)
                    _refrescar()
            tabla.on(evento, h)

        _on("detener", GESTOR.detener)
        _on("reanudar", GESTOR.reanudar)
        _on("carpeta", _abrir_carpeta)

        with ui.dialog() as dlg, ui.card().classes("bg-gray-800 text-gray-100"):
            dlg_txt = ui.label("")
            objetivo: dict[str, Path | None] = {"d": None}
            with ui.row():
                ui.button("Cancelar", on_click=dlg.close).props("flat")

                def _confirmar() -> None:
                    d = objetivo["d"]
                    dlg.close()
                    if d is None:
                        return
                    try:
                        C.eliminar_corrida(d)
                        ui.notify("Corrida borrada.")
                    except Exception as e:
                        ui.notify(str(e), type="negative")
                    _refrescar()
                ui.button("Borrar", color="red", on_click=_confirmar)

        def _pedir_borrado(d: Path) -> None:
            objetivo["d"] = d
            dlg_txt.set_text(f"¿Borrar «{C.leer_config(d).nombre}» y todos sus datos? "
                             "No se puede deshacer.")
            dlg.open()

        tabla.on("borrar", lambda e: (_por_id(e.args) and _pedir_borrado(_por_id(e.args))))

        def _refrescar() -> None:
            filas = []
            for d in C.listar_corridas():
                cfg = C.leer_config(d)
                est = GESTOR.estado(d)
                fase = est.get("fase", "desconocida")
                dia = est.get("dia")
                vivo = fase in ("corriendo", "pausada", "deteniendo") or (
                    fase in C.FASES_FINALES and GESTOR._vivo(d, est))
                filas.append({
                    "id": d.name,
                    "nombre": cfg.nombre or d.name,
                    "detalle": cfg.resumen(),
                    "fase": _FASE_TEXTO.get(fase, fase),
                    "color": _FASE_COLOR.get(fase, "grey"),
                    "error": est.get("error"),
                    "dia": dia if dia is not None else "—",
                    "anios": f"{dia / 365:.1f}" if dia else "—",
                    "vivos": (f"{est.get('vivos')}/{est.get('total')}"
                              if est.get("vivos") is not None else "—"),
                    "tribus": est.get("tribus", "—"),
                    "orden": _orden_texto(est, cfg),
                    "url": (f"http://127.0.0.1:{est['puerto']}"
                            if vivo and est.get("puerto") else None),
                    "puede_detener": fase in ("en_cola", *C.FASES_ACTIVAS),
                    "puede_reanudar": fase in ("detenida", "interrumpida", "error"),
                    "puede_ver_final": fase in C.FASES_FINALES or fase == "interrumpida",
                })
            tabla.rows = filas
            tabla.update()

        _refrescar()
        ui.timer(2.0, _refrescar)
    return tabla


def _detener_todas(ui) -> None:
    n = 0
    for d in C.listar_corridas():
        if C.leer_estado(d).get("fase") in ("en_cola", *C.FASES_ACTIVAS):
            GESTOR.detener(d)
            n += 1
    ui.notify(f"Deteniendo {n} corrida{'s' if n != 1 else ''}.")


def _seccion_comparar(ui, tabla) -> None:
    with ui.card().classes("w-full bg-gray-900 text-gray-100 p-4 ps-compare-card").props("id=ps-compare"):
        ui.label("ANÁLISIS COMPARATIVO").classes("ps-section-kicker")
        ui.label("Comparar").classes("text-lg font-semibold text-purple-200 ps-section-heading")
        ui.label("Marcá corridas en la tabla de arriba para ver su población y sus tribus "
                 "a lo largo del tiempo.").classes("text-xs text-gray-400")
        graf = ui.plotly(_figura([])).classes("w-full ps-chart-frame").style("height:520px")

        def _actualizar() -> None:
            ids = [r["id"] for r in (tabla.selected or [])]
            graf.update_figure(_figura(ids))

        tabla.on("selection", lambda _: _actualizar())
        ui.timer(10.0, _actualizar)


def _figura(ids: list[str]) -> dict:
    trazas = []
    colores = ["#b68ae8", "#d6b16d", "#53c7b0", "#78a9e8", "#e98b9a", "#b7c77b"]
    for i, rid in enumerate(ids):
        color = colores[i % len(colores)]
        d = C.directorio_corridas() / rid
        if not d.is_dir():
            continue
        cfg = C.leer_config(d)
        serie = C.leer_serie(d)
        x = [v / 365 for v in serie["dia"]]
        etiqueta = cfg.nombre or rid
        trazas.append({"type": "scatter", "mode": "lines", "x": x, "y": serie["n_alive"],
                       "name": etiqueta, "legendgroup": rid,
                       "line": {"color": color, "width": 2.5},
                       "xaxis": "x", "yaxis": "y"})
        trazas.append({"type": "scatter", "mode": "lines", "x": x, "y": serie["n_tribes"],
                       "name": etiqueta, "legendgroup": rid, "showlegend": False,
                       "line": {"color": color, "dash": "dot", "width": 1.8},
                       "xaxis": "x2", "yaxis": "y2"})
    eje = {
        "gridcolor": "rgba(111, 133, 163, 0.18)",
        "zerolinecolor": "rgba(214, 177, 109, 0.28)",
        "linecolor": "rgba(111, 133, 163, 0.28)",
        "tickfont": {"color": "#91a2bb", "size": 11},
        "title_font": {"color": "#c6a2f2", "size": 12},
    }
    return {
        "data": trazas,
        "layout": {
            "paper_bgcolor": "#0b1523", "plot_bgcolor": "#0b1523",
            "font": {"color": "#e5eaf4", "family": "Inter, Segoe UI, sans-serif", "size": 12},
            "colorway": ["#b68ae8", "#d6b16d", "#53c7b0", "#78a9e8", "#e98b9a", "#b7c77b"],
            "hoverlabel": {"bgcolor": "#19293f", "bordercolor": "#536a87", "font": {"color": "#e5eaf4"}},
            "margin": {"l": 58, "r": 24, "t": 32, "b": 48},
            "grid": {"rows": 2, "columns": 1, "pattern": "independent"},
            "xaxis": {**eje, "title": {"text": "", "font": {"color": "#c6a2f2"}}},
            "yaxis": {**eje, "title": {"text": "Personas vivas", "font": {"color": "#c6a2f2"}}},
            "xaxis2": {**eje, "title": {"text": "Años simulados", "font": {"color": "#c6a2f2"}}},
            "yaxis2": {**eje, "title": {"text": "Tribus", "font": {"color": "#c6a2f2"}}},
            "legend": {"orientation": "h", "y": -0.15, "font": {"color": "#b8c5d8", "size": 11}},
            "annotations": [] if trazas else [{
                "text": "Seleccioná corridas en el registro para comparar personas vivas y tribus.",
                "showarrow": False, "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                "font": {"color": "#b8c5d8", "size": 13},
                "bgcolor": "rgba(16,28,44,.78)", "bordercolor": "rgba(59,80,106,.7)",
                "borderpad": 10}],
        },
    }


def construir_visor(rid: str) -> None:
    """Pestaña puente: levanta el visor de estado final y redirige cuando responde."""
    from nicegui import ui

    d = C.directorio_corridas() / rid
    with ui.column().classes("w-full items-center p-16 gap-4"):
        if not d.is_dir():
            ui.label("Esa corrida no existe.").classes("text-red-400")
            return
        ui.label(C.leer_config(d).nombre or rid).classes("text-xl text-purple-200")
        msg = ui.label("Cargando el estado final de la corrida…").classes("text-gray-400")
        ui.spinner(size="xl", color="purple")
    GESTOR.ver_estado_final(d)
    intentos = {"n": 0}

    def _esperar() -> None:
        intentos["n"] += 1
        v = C.leer_estado(d).get("visor") or {}
        if v.get("error"):
            msg.set_text(f"No se pudo abrir: {v['error']}")
            timer.cancel()
            return
        url = GESTOR.visor_url(d)
        if url:
            try:
                urllib.request.urlopen(url, timeout=1)
            except Exception:
                return
            timer.cancel()
            ui.navigate.to(url)
        elif intentos["n"] > 120:
            msg.set_text("El visor tardó demasiado en arrancar. Revisá corrida.log en la carpeta.")
            timer.cancel()

    timer = ui.timer(0.5, _esperar)


def lanzar_panel() -> None:
    from nicegui import app, ui

    app.add_static_files("/assets", str(ROOT / "assets"))

    @ui.page("/")
    def panel():
        construir_panel()

    @ui.page("/guia")
    def guia():
        apply_theme(ui)
        texto = (ROOT / "docs" / "GUIA_DE_USO.md").read_text(encoding="utf-8")
        with ui.column().classes("w-full max-w-4xl mx-auto p-6 text-gray-200"):
            ui.markdown(texto, extras=["tables"]).classes("w-full")

    @ui.page("/visor/{rid}")
    def visor(rid: str):
        construir_visor(rid)

    # La cola avanza aunque nadie tenga el panel abierto
    app.timer(3.0, GESTOR.procesar_cola)

    ui.run(
        title="PSYCHE SIMULACRA",
        host="127.0.0.1",
        port=HUB_PORT,
        dark=True,
        show=os.environ.get("PSYCHE_ABRIR_NAVEGADOR", "1") != "0",
        favicon="🧠",
        reload=False,
        reconnect_timeout=10,
    )

