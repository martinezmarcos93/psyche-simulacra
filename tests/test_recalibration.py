"""
Tests de la recalibración arquetípica por vivencia (ArchetypeRecalibrator).

Verifican el contrato del mecanismo:
  - La vivencia se acumula APARTE del vector: una percepción suelta no lo mueve.
  - Lo que no se vuelve a vivir se apaga (decaimiento).
  - Solo la experiencia sostenida se consolida, y lo hace redistribuyendo.
  - El dominante es estable: no alterna sin un margen sostenido (histéresis).
  - El malestar sostenido presiona hacia los arquetipos menos desarrollados.
  - Con el flag OFF no existe y nada cambia.
"""
import pytest

from core.agents import Agent
from core.agents.psyche.archetypes import ArchetypeVector, ARCHETYPE_NAMES
from core.agents.psyche.recalibration import (
    ArchetypeRecalibrator,
    _EXPERIENCIA_MAX, _RETENCION_DIARIA, _UMBRAL_CONSOLIDACION,
    _VENTANA_CONSOLIDACION, _VENTANA_REORGANIZACION, _MARGEN_REORGANIZACION,
)
from core.metrics.emergence import EmergenceMetrics
from unittest.mock import MagicMock


def _vivir(r: ArchetypeRecalibrator, v: ArchetypeVector, arch: str, dias: int,
           intensidad: float = 0.05, valence: float = 0.0) -> list:
    """Vive `dias` días con una resonancia diaria en `arch`. Devuelve las reorganizaciones."""
    reorgs = []
    for _ in range(dias):
        r.registrar({arch: intensidad}, valence)
        reorg = r.on_day(v)
        if reorg:
            reorgs.append(reorg)
    return reorgs


class TestAcumulador:

    def test_una_percepcion_no_mueve_el_vector(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        antes = v.to_dict()
        r.registrar({"sombra": 0.02}, valence=0.0)
        assert v.to_dict() == antes
        assert r.experiencia["sombra"] == pytest.approx(0.02)

    def test_experiencia_esta_acotada(self):
        r = ArchetypeRecalibrator()
        for _ in range(1000):
            r.registrar({"heroe": 0.05}, valence=0.0)
        assert r.experiencia["heroe"] == pytest.approx(_EXPERIENCIA_MAX)

    def test_arquetipo_desconocido_se_ignora(self):
        r = ArchetypeRecalibrator()
        r.registrar({"amante": 0.1}, valence=0.0)
        assert "amante" not in r.experiencia

    def test_lo_que_no_se_revive_se_apaga(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        r.registrar({"sabio": 0.04}, valence=0.0)   # bajo el umbral: nunca consolida
        antes = v.to_dict()
        for _ in range(60):
            r.on_day(v)
        assert r.experiencia["sabio"] < 0.001
        assert v.to_dict() == antes


class TestConsolidacion:

    def test_experiencia_sostenida_sube_el_peso(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        inicial = v.trickster
        _vivir(r, v, "trickster", dias=30)
        assert v.trickster > inicial

    def test_experiencia_breve_no_consolida(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        antes = v.to_dict()
        _vivir(r, v, "trickster", dias=_VENTANA_CONSOLIDACION - 2, intensidad=0.03)
        assert v.to_dict() == antes

    def test_la_consolidacion_conserva_la_suma(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        suma = sum(v.to_dict().values())
        _vivir(r, v, "trickster", dias=60)
        assert sum(v.to_dict().values()) == pytest.approx(suma, abs=1e-9)

    def test_los_pesos_quedan_en_rango(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        _vivir(r, v, "heroe", dias=2000, intensidad=0.3)
        assert all(0.0 <= x <= 1.0 for x in v.to_dict().values())


class TestDominanteEstable:

    def test_primer_dia_fija_el_maximo_sin_reorganizar(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.9)
        assert r.on_day(v) is None
        assert r.dominante == "heroe"
        assert v.dominant() == "heroe"
        assert r.reorganizaciones == 0

    def test_sin_recalibrador_el_dominante_es_el_maximo(self):
        v = ArchetypeVector(sabio=0.95)
        assert v.dominant() == "sabio"

    def test_ventaja_bajo_el_margen_no_reorganiza(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.80)
        r.on_day(v)
        v.sabio = 0.80 + _MARGEN_REORGANIZACION / 2
        for _ in range(_VENTANA_REORGANIZACION * 3):
            assert r.on_day(v) is None
        assert v.dominant() == "heroe"

    def test_ventaja_breve_no_reorganiza(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.80)
        r.on_day(v)
        v.sabio = 0.95
        for _ in range(_VENTANA_REORGANIZACION - 1):
            assert r.on_day(v) is None
        v.sabio = 0.40                       # la ventaja se pierde antes de la ventana
        assert r.on_day(v) is None
        assert v.dominant() == "heroe"

    def test_ventaja_sostenida_reorganiza_una_vez(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.80)
        r.on_day(v)
        v.sabio = 0.95
        reorgs = [x for x in (r.on_day(v) for _ in range(_VENTANA_REORGANIZACION * 3)) if x]
        assert reorgs == [("heroe", "sabio")]
        assert v.dominant() == "sabio"
        assert r.reorganizaciones == 1

    def test_la_vivencia_sostenida_termina_reorganizando(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        r.on_day(v)
        inicial = v.dominant()
        reorgs = _vivir(r, v, "trickster", dias=400, intensidad=0.3)
        assert reorgs and reorgs[-1][1] == "trickster"
        assert inicial != "trickster"


class TestCompensacion:

    def _dias(self, r, v, n, valence):
        for _ in range(n):
            r.registrar({}, valence=valence)
            r.on_day(v)

    def test_caida_bajo_la_linea_de_base_presiona_a_los_menos_desarrollados(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.9)
        self._dias(r, v, 60, valence=0.6)            # vida habitual: buena
        assert all(x == 0.0 for x in r.experiencia.values())
        self._dias(r, v, 10, valence=-0.2)           # racha mala
        assert r.malestar() > 0.0
        assert r.experiencia["trickster"] > 0.0      # el de menor peso por defecto
        assert r.experiencia["heroe"] < 0.0          # el dominante cede

    def test_valencia_estable_no_compensa_aunque_sea_negativa(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.9)
        self._dias(r, v, 60, valence=-0.5)           # su normalidad es mala, pero estable
        assert r.malestar() == 0.0
        assert all(x == 0.0 for x in r.experiencia.values())

    def test_el_malestar_se_habitua(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.9)
        self._dias(r, v, 60, valence=0.6)
        self._dias(r, v, 400, valence=-0.2)          # lo malo se vuelve la nueva normalidad
        assert r.malestar() == 0.0


class TestConservacion:

    def test_la_deriva_externa_no_infla_el_vector(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector()
        r.on_day(v)
        presupuesto = sum(v.to_dict().values())
        for _ in range(200):                         # un sistema externo empuja sabio cada día
            v.sabio = min(1.0, v.sabio + 0.03)
            r.on_day(v)
        assert sum(v.to_dict().values()) == pytest.approx(presupuesto, abs=1e-6)
        assert v.sabio > 0.9                         # lo vivido sube...
        assert v.heroe < 0.5                         # ...y el resto cede


class TestPersistencia:

    def test_roundtrip(self):
        r, v = ArchetypeRecalibrator(), ArchetypeVector(heroe=0.8)
        _vivir(r, v, "sombra", dias=12, valence=-0.4)
        r.registrar({"sabio": 0.01}, valence=0.2)    # día en curso sin cerrar
        r2 = ArchetypeRecalibrator.from_dict(r.to_dict())
        assert r2.to_dict() == r.to_dict()


class TestIntegracionAgente:

    def test_flag_off_no_hay_recalibrador(self):
        a = Agent(agent_id="a1", nombre="Test", posicion=(40, 30), seed=42)
        assert a.recalibrator is None
        assert a.to_dict()["recalibrator"] is None
        a.recalibrate_archetypes(dia=1)              # no-op, no rompe
        assert a.archetypes._dominante_estable is None

    def test_agente_con_recalibrador_registra_y_persiste(self):
        a = Agent(agent_id="a1", nombre="Test", posicion=(40, 30), seed=42)
        a.recalibrator = ArchetypeRecalibrator()
        a.archetypes.heroe = 0.9
        a.recalibrate_archetypes(dia=1)
        assert a.arquetipo_dominante == "heroe"
        a.archetypes.sabio = 0.99
        for dia in range(2, 2 + _VENTANA_REORGANIZACION):
            a.recalibrate_archetypes(dia=dia)
        assert a.arquetipo_dominante == "sabio"
        assert any("reorganizó" in linea for linea in a.episodic_log)
        assert a.to_dict()["recalibrator"]["reorganizaciones"] == 1


class TestMetricasDeTribus:

    def _agente(self, aid: str, accion: str, reorganizaciones: int = 0):
        a = MagicMock()
        a.id = aid
        a.is_alive = True
        a.behavioral_state.ultimo_colapso = accion
        a.recalibrator.reorganizaciones = reorganizaciones
        return a

    def test_cuenta_aislados_y_tribus_reales(self):
        alive = {x: self._agente(x, "cooperacion") for x in "abcdef"}
        tribes = {"t1": ["a", "b", "c"], "t2": ["d", "e"], "t3": ["f"], "t4": ["muerto"]}
        assert EmergenceMetrics()._tribe_size_counts(alive, tribes) == (1, 2)

    def test_kl_multi_ignora_tribus_chicas(self):
        em = EmergenceMetrics()
        alive = {x: self._agente(x, "cooperacion") for x in "abc"}
        alive["z"] = self._agente("z", "competencia")
        tribes = {"t1": ["a", "b", "c"], "aislado": ["z"]}
        assert em._behavioral_divergence(alive, tribes) > 1.0
        assert em._behavioral_divergence(alive, tribes, min_members=3) == 0.0

    def test_reorganizaciones_se_suman(self):
        alive = {"a": self._agente("a", "cooperacion", 2), "b": self._agente("b", "cooperacion", 1)}
        assert EmergenceMetrics()._reorganizations_total(alive) == 3


def test_nombres_del_recalibrador_coinciden_con_el_vector():
    assert set(ArchetypeRecalibrator().experiencia) == set(ArchetypeVector().to_dict())
    assert set(ARCHETYPE_NAMES) == set(ArchetypeVector().to_dict())
