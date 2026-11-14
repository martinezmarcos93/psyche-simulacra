"""Contadores de flujo por tribu (core/metrics/flujos.py) y su exportación."""
import csv
from dataclasses import asdict

from core.metrics.emergence import DayMetrics
from core.metrics.exporter import MetricsExporter
from core.metrics.flujos import ContadorFlujos, FlujoTribu, categoria_muerte, emparejar_tribus


def _muerte(aid, causa):
    return {"dia": 1, "tick": 0, "agent_id": aid, "nombre": aid, "causa": causa}


def _nacimiento(cid, padre):
    return {"dia": 1, "id": cid, "nombre": cid, "padre_a": padre, "padre_b": "x"}


def _filas(flujo):
    return {f.tribe_id: f for f in flujo.por_tribu}


# ── Clasificación de causas ───────────────────────────────────────────────────

def test_categorias_de_muerte():
    assert categoria_muerte("vejez") == "vejez"
    assert categoria_muerte("inanicion") == "carencia"
    assert categoria_muerte("orfandad") == "carencia"
    assert categoria_muerte("depredador_lobo") == "violenta"
    assert categoria_muerte("plaga") == "catastrofe"
    assert categoria_muerte("invierno_brutal") == "catastrofe"
    assert categoria_muerte("causa_liminal_inexplicable") == "liminal"
    assert categoria_muerte("muerte_inexplicable_zona_maldita") == "liminal"
    assert categoria_muerte("algo_nuevo") == "otra"


# ── Identidad de tribus ───────────────────────────────────────────────────────

def test_emparejar_tribus_por_mayor_solapamiento():
    previas = {"t_a": {"a", "b", "c"}, "t_d": {"d", "e"}}
    nuevas = {"t_b": {"b", "c"}, "t_d": {"d", "e", "a"}}
    assert emparejar_tribus(previas, nuevas) == {"t_d": "t_d", "t_b": "t_a"}


def test_renombre_de_tribu_no_cuenta_como_migracion():
    c = ContadorFlujos()
    c.sincronizar({"a": "t_a", "b": "t_a", "c": "t_a"}, [], [])
    # muere "a" (el que daba nombre) y al reclusterizar la tribu pasa a llamarse t_b
    flujo = c.registrar_dia(1, {"b": "t_b", "c": "t_b"}, [], [_muerte("a", "vejez")])
    assert flujo.cambios_de_tribu == 0
    assert flujo.tribus_nuevas == 0 and flujo.tribus_extintas == 0
    assert flujo.muertes_vejez == 1
    assert _filas(flujo)["t_a"].muertes == 1  # la muerte queda en la tribu que tenía


# ── Flujos del día ────────────────────────────────────────────────────────────

def test_migracion_nacimientos_y_muertes_por_tribu():
    c = ContadorFlujos()
    c.sincronizar({"a": "t_a", "b": "t_a", "c": "t_c", "d": "t_c"}, [], [])
    births = [_nacimiento("n1", "a")]
    deaths = [_muerte("d", "depredador_oso")]
    # "b" se pasa a la tribu de "c"; "d" muere; nace "n1" (todavía sin tribu asignada)
    flujo = c.registrar_dia(1, {"a": "t_a", "b": "t_c", "c": "t_c"}, births, deaths)

    assert flujo.nacimientos == 1
    assert flujo.muertes_violentas == 1
    assert flujo.cambios_de_tribu == 1
    f = _filas(flujo)
    assert (f["t_a"].poblacion, f["t_a"].nacimientos, f["t_a"].salidas) == (1, 1, 1)
    assert (f["t_c"].poblacion, f["t_c"].llegadas) == (2, 1)
    assert (f["t_c"].muertes, f["t_c"].muertes_violentas) == (1, 1)


def test_no_recuenta_eventos_de_dias_anteriores():
    c = ContadorFlujos()
    births, deaths = [_nacimiento("n1", "a")], [_muerte("b", "inanicion")]
    c.sincronizar({"a": "t_a", "b": "t_a"}, [], [])
    c.registrar_dia(1, {"a": "t_a"}, births, deaths)
    flujo = c.registrar_dia(2, {"a": "t_a"}, births, deaths)
    assert flujo.nacimientos == 0 and flujo.muertes_carencia == 0


def test_sincronizar_descarta_lo_previo_y_sin_base_cuenta_el_primer_dia():
    previos = [_muerte("x", "vejez")]
    c = ContadorFlujos()
    c.sincronizar({"a": "t_a"}, [], previos)  # p. ej. muertes de la prehistoria
    assert c.registrar_dia(1, {"a": "t_a"}, [], previos).muertes_vejez == 0

    sin_base = ContadorFlujos()
    flujo = sin_base.registrar_dia(1, {"a": "t_a"}, [], previos)
    assert flujo.muertes_vejez == 1 and flujo.cambios_de_tribu == 0


def test_tribu_extinta_y_tribu_nueva():
    c = ContadorFlujos()
    c.sincronizar({"a": "t_a", "b": "t_b"}, [], [])
    flujo = c.registrar_dia(1, {"a": "t_a", "n": "t_n"}, [], [_muerte("b", "plaga")])
    assert flujo.tribus_extintas == 1 and flujo.tribus_nuevas == 1
    assert flujo.muertes_catastrofe == 1
    assert _filas(flujo)["t_b"].poblacion == 0


# ── Exportación ───────────────────────────────────────────────────────────────

def _day(dia, **kw):
    base = dict(dia=dia, kl_mean=0, kl_max=0, vfe_global=0, vfe_tribe_mean=0, imi=0, mig=0,
                n_alive=3, n_tribes=1, n_structures=0)
    return DayMetrics(**{**base, **kw})


def test_exporter_escribe_flujos_por_tribu(tmp_path):
    ex = MetricsExporter(str(tmp_path))
    ex.record(_day(1, nacimientos=2))
    ex.record_tribus([FlujoTribu(1, "t_a", poblacion=3, nacimientos=2)])
    ex.flush()
    with open(tmp_path / "emergence_series.csv", encoding="utf-8") as f:
        assert next(csv.DictReader(f))["nacimientos"] == "2"
    with open(tmp_path / "tribe_flows.csv", encoding="utf-8") as f:
        assert list(csv.DictReader(f)) == [{k: str(v) for k, v in asdict(FlujoTribu(1, "t_a", 3, 2)).items()}]


def test_exporter_respeta_encabezado_de_csv_viejo(tmp_path):
    """Corrida reanudada desde una versión anterior: la serie no se desalinea."""
    viejo = tmp_path / "emergence_series.csv"
    viejo.write_text("dia,n_alive,n_tribes\n1,10,2\n", encoding="utf-8")
    ex = MetricsExporter(str(tmp_path))
    ex.record(_day(2, n_alive=9, nacimientos=1))
    ex.flush()
    with open(viejo, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert filas[-1] == {"dia": "2", "n_alive": "9", "n_tribes": "1"}


# ── Integración con la simulación ─────────────────────────────────────────────

def test_simulacion_corta_escribe_flujos(tmp_path):
    from core.simulation import SimulationRunner
    from tests.test_simulation import SEEDS_FILE

    runner = SimulationRunner.new_session(
        seed_file=SEEDS_FILE,
        db_path=str(tmp_path / "sim.db"),
        checkpoint_dir=str(tmp_path / "cp"),
    )
    runner.metrics_exporter = MetricsExporter(str(tmp_path / "metrics"))
    runner.run(n_days=3)
    runner.metrics_exporter.flush()

    with open(tmp_path / "metrics" / "emergence_series.csv", encoding="utf-8") as f:
        serie = list(csv.DictReader(f))
    assert serie and "cambios_de_tribu" in serie[0]
    with open(tmp_path / "metrics" / "tribe_flows.csv", encoding="utf-8") as f:
        tribus = list(csv.DictReader(f))
    # la población por tribu suma los vivos de cada día
    for fila in serie:
        dia = fila["dia"]
        assert sum(int(t["poblacion"]) for t in tribus if t["dia"] == dia) <= int(fila["n_alive"])
