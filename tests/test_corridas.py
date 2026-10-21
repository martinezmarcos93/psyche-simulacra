"""
Tests del sistema de corridas (panel multicorrida):
  - configuración, validación y traducción a variables de entorno;
  - carpetas, estado y lectura de la serie;
  - modos de EDEN (off / orden / eden) en AgentCore;
  - corrida real de punta a punta en un proceso aparte, y visor de estado final
    que no modifica la carpeta de la corrida.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from core.runtime import corridas as C

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def datos(tmp_path, monkeypatch):
    monkeypatch.setenv("PSYCHE_DATOS_DIR", str(tmp_path))
    monkeypatch.delenv("PSYCHE_CORRIDAS_DIR", raising=False)
    return tmp_path


# ── Configuración ─────────────────────────────────────────────────────────────

def test_config_por_defecto_es_valida():
    assert C.CorridaConfig().validar() == []


@pytest.mark.parametrize("cambios, fragmento", [
    ({"escenario": "caos"}, "Escenario"),
    ({"poblacion": "no_existe.yaml"}, "población"),
    ({"semilla": -1}, "semilla"),
    ({"dias": -5}, "días"),
    ({"recalibracion_arquetipica": True}, "filtro interpretativo"),
    ({"prob_repro_diaria": 1.5}, "prob_repro_diaria"),
    ({"dias_hasta_clustering": 0}, "intervalos"),
])
def test_config_invalida(cambios, fragmento):
    errores = C.CorridaConfig(**cambios).validar()
    assert any(fragmento in e for e in errores), errores


def test_recalibracion_con_filtro_es_valida():
    cfg = C.CorridaConfig(recalibracion_arquetipica=True, filtro_interpretativo=True)
    assert cfg.validar() == []


def test_entorno_traduce_todo():
    cfg = C.CorridaConfig(escenario="orden", narrativa=True, modelo_ollama="mistral",
                          filtro_interpretativo=True, boveda_mental=True,
                          prob_repro_diaria=0.02, vinculo_min_repro=0.3,
                          necesidades_max_repro=0.6, dias_hasta_clustering=15,
                          dias_entre_checkpoints=5)
    env = cfg.entorno()
    assert env["EDEN_MODE"] == "orden"
    assert env["NARRATIVE_ENABLED"] == "true"
    assert env["OLLAMA_MODEL"] == "mistral"
    assert env["INTERPRETIVE_FILTER_ENABLED"] == "1"
    assert env["COMM_REINTERPRETATION_ENABLED"] == "0"
    assert env["MENTAL_VAULT_ENABLED"] == "1"
    assert env["ARCHETYPE_RECALIBRATION_ENABLED"] == "0"
    assert float(env["PROB_REPRO_DIARIA"]) == 0.02
    assert float(env["BOND_REPRO_MIN"]) == 0.3
    assert float(env["REPRO_NEEDS_MAX"]) == 0.6
    assert env["DAYS_UNTIL_CLUSTERING"] == "15"
    assert env["CHECKPOINT_INTERVAL"] == "5"
    assert env["PYTHONHASHSEED"] == "0"


def test_ajustes_finos_por_defecto_y_personalizados():
    env = C.CorridaConfig().entorno()
    for var, _sec, _et, _ay, default, *_resto, entero in C.PARAMETROS_FINOS:
        assert var in env
        assert (int(env[var]) if entero else float(env[var])) == default
    env = C.CorridaConfig(ajustes={"NOMOS_WEIGHT": 0.5, "REPRO_COOLDOWN_DIAS": 30.0}).entorno()
    assert float(env["NOMOS_WEIGHT"]) == 0.5
    assert env["REPRO_COOLDOWN_DIAS"] == "30"


@pytest.mark.parametrize("ajustes, fragmento", [
    ({"NO_EXISTE": 1.0}, "desconocido"),
    ({"LETHALITY_FACTOR": 9.0}, "Letalidad"),
    ({"MYTH_CONTEXT_THRESHOLD": -0.1}, "proto-mito"),
])
def test_ajustes_finos_invalidos(ajustes, fragmento):
    errores = C.CorridaConfig(ajustes=ajustes).validar()
    assert any(fragmento in e for e in errores), errores


def test_dias_efectivos_hasta_extincion_usa_tope():
    assert C.CorridaConfig(dias=0).dias_efectivos() == C.TOPE_EXTINCION_DIAS
    assert C.CorridaConfig(dias=90).dias_efectivos() == 90


def test_desde_dict_ignora_campos_desconocidos():
    cfg = C.CorridaConfig.desde_dict({"escenario": "eden", "creada": "x", "otra": 1})
    assert cfg.escenario == "eden"


# ── Carpetas y estado ─────────────────────────────────────────────────────────

def test_crear_listar_y_estado(datos):
    a = C.crear_corrida(C.CorridaConfig(escenario="off", semilla=1))
    b = C.crear_corrida(C.CorridaConfig(escenario="eden", semilla=1))
    assert a != b and a.parent == datos / "corridas"
    assert C.leer_estado(a)["fase"] == "en_cola"
    assert C.leer_config(b).escenario == "eden"
    assert C.leer_config(b).nombre  # se genera si falta
    assert set(C.listar_corridas()) == {a, b}
    C.escribir_estado(a, fase="corriendo", dia=3)
    est = C.leer_estado(a)
    assert est["fase"] == "corriendo" and est["dia"] == 3 and "actualizado" in est


def test_crear_corrida_invalida_no_deja_carpeta(datos):
    with pytest.raises(ValueError):
        C.crear_corrida(C.CorridaConfig(escenario="nada"))
    assert C.listar_corridas() == []


def test_no_se_borra_una_corrida_activa(datos):
    d = C.crear_corrida(C.CorridaConfig())
    C.escribir_estado(d, fase="corriendo")
    with pytest.raises(RuntimeError):
        C.eliminar_corrida(d)
    C.escribir_estado(d, fase="terminada")
    C.eliminar_corrida(d)
    assert not d.exists()


def test_pedir_detencion(datos):
    d = C.crear_corrida(C.CorridaConfig())
    assert not C.detencion_pedida(d)
    C.pedir_detencion(d)
    assert C.detencion_pedida(d)


def test_leer_serie_tolera_ausente_y_filas_rotas(datos):
    d = C.crear_corrida(C.CorridaConfig())
    assert C.leer_serie(d) == {"dia": [], "n_alive": [], "n_tribes": []}
    p = C.serie_csv(d)
    p.parent.mkdir(parents=True)
    p.write_text("dia,n_alive,n_tribes\n1,10,5\n2,9,\n3,8,4\n", encoding="utf-8")
    assert C.leer_serie(d) == {"dia": [1.0, 3.0], "n_alive": [10.0, 8.0], "n_tribes": [5.0, 4.0]}


def test_generar_poblacion(datos):
    p = C.generar_poblacion(6, 3)
    assert p.parent == datos / "poblaciones"
    assert C.contar_personas(p) == 6
    assert p.name in C.listar_poblaciones()
    assert C.CorridaConfig(poblacion=p.name).validar() == []


def test_importar_corridas_no_carga_el_motor():
    """El proceso de la corrida fija el entorno DESPUÉS de importar corridas:
    si eso arrastrara módulos del motor, los flags se leerían antes de tiempo."""
    codigo = ("import sys; import core.runtime.corridas; "
              "print([m for m in sys.modules if m.startswith(('core.agents', 'core.social', "
              "'core.narrative', 'core.world'))])")
    out = subprocess.run([sys.executable, "-c", codigo], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip()
    assert out == "[]"


# ── Modos de EDEN ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("env, esperado", [
    ({}, "off"),
    ({"EDEN_ENABLED": "1"}, "eden"),
    ({"EDEN_MODE": "orden"}, "orden"),
    ({"EDEN_MODE": "EDEN"}, "eden"),
    ({"EDEN_MODE": "off", "EDEN_ENABLED": "1"}, "off"),
])
def test_eden_mode_from_env(monkeypatch, env, esperado):
    from core.agents import agent_core
    monkeypatch.delenv("EDEN_MODE", raising=False)
    monkeypatch.delenv("EDEN_ENABLED", raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    assert agent_core.eden_mode_from_env() == esperado


def test_eden_mode_invalido(monkeypatch):
    from core.agents import agent_core
    monkeypatch.setenv("EDEN_MODE", "anarquia")
    with pytest.raises(ValueError):
        agent_core.eden_mode_from_env()


@pytest.mark.parametrize("modo, hay_nomos, hay_serpiente", [
    ("off", False, False), ("orden", True, False), ("eden", True, True),
])
def test_agent_core_segun_modo(monkeypatch, modo, hay_nomos, hay_serpiente):
    from core.agents import agent_core
    from core.world.world_core import WorldCore
    monkeypatch.setattr(agent_core, "_EDEN_MODE", modo)
    core = agent_core.AgentCore(WorldCore(seed=1))
    assert (core.nomos is not None) == hay_nomos
    assert (core.serpiente is not None) == hay_serpiente


# ── Punta a punta (proceso real) ──────────────────────────────────────────────

def _esperar(cond, timeout: float):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        r = cond()
        if r:
            return r
        time.sleep(0.5)
    return None


def _env(datos: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("NICEGUI_", "PYTEST_"))}
    env["PSYCHE_DATOS_DIR"] = str(datos)
    return env


def _matar(pid: int | None) -> None:
    if pid:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


@pytest.mark.slow
def test_corrida_de_punta_a_punta_y_visor(datos):
    d = C.crear_corrida(C.CorridaConfig(escenario="eden", poblacion="eden_pilot_10.yaml",
                                        semilla=2, dias=8))
    p = subprocess.Popen(C.comando_corrida(d), cwd=d, env=_env(datos),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        est = _esperar(lambda: (e := C.leer_estado(d)).get("fase") in C.FASES_FINALES and e,
                       timeout=180)
        assert est, C.leer_estado(d)
        assert est["fase"] == "terminada"
        assert est["dia"] == 8 and est["vivos"] == 10 and est["total"] == 10
        assert est["nomos_activo"] is True
        assert C.serie_csv(d).is_file()
        assert (d / "data" / "metrics" / "emergence_summary.json").is_file()
        assert list((d / "data" / "checkpoints").glob("checkpoint_*.json"))
        assert not (d / C.ARCHIVO_DETENER).exists()
        serie = C.leer_serie(d)
        assert len(serie["dia"]) == 8
        # el monitor sigue en pie un rato después de terminar
        html = _esperar(lambda: _get(f"http://127.0.0.1:{est['puerto']}/"), timeout=60)
        assert html and b"PSYCHE" in html
    finally:
        p.kill()
        p.wait(timeout=10)

    # Visor de estado final: no debe tocar nada de la carpeta de la corrida
    def _foto():
        return {str(f.relative_to(d)): (f.stat().st_size, f.stat().st_mtime_ns)
                for f in d.rglob("*") if f.is_file() and f.name not in (C.ARCHIVO_ESTADO, C.ARCHIVO_LOG)}
    antes = _foto()
    v = subprocess.Popen(C.comando_corrida(d, ver=True), env=_env(datos),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        visor = _esperar(lambda: (C.leer_estado(d).get("visor") or {}).get("puerto")
                         and C.leer_estado(d)["visor"], timeout=60)
        assert visor and "error" not in visor
        html = _esperar(lambda: _get(f"http://127.0.0.1:{visor['puerto']}/"), timeout=60)
        assert html and b"estado final" in html
        time.sleep(3)
        assert C.leer_estado(d)["fase"] == "terminada"
        assert "error" not in (C.leer_estado(d).get("visor") or {})
    finally:
        v.kill()
        v.wait(timeout=10)
    assert _foto() == antes


def _get(url: str) -> bytes | None:
    try:
        return urllib.request.urlopen(url, timeout=5).read()
    except Exception:
        return None


@pytest.mark.slow
def test_detener_una_corrida(datos):
    d = C.crear_corrida(C.CorridaConfig(poblacion="eden_pilot_10.yaml", dias=0))
    p = subprocess.Popen(C.comando_corrida(d), cwd=d, env=_env(datos),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        assert _esperar(lambda: (C.leer_estado(d).get("dia") or 0) >= 3, timeout=120)
        C.pedir_detencion(d)
        est = _esperar(lambda: (e := C.leer_estado(d)).get("fase") in C.FASES_FINALES and e,
                       timeout=120)
        assert est and est["fase"] == "detenida", C.leer_estado(d)
        assert list((d / "data" / "checkpoints").glob("checkpoint_*.json"))
    finally:
        p.kill()
        p.wait(timeout=10)
