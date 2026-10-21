"""
Tests de Serpiente (Fase 2 — Experimento EDEN).
Cubre: elegibilidad (dos caminos arquetípicos), acumulación/decaimiento de
tentación, y el canal de sesgo una vez cruzado el umbral.
"""
from core.agents.psyche.archetypes import ArchetypeVector
from core.social.serpent import Serpiente, es_elegible


def _arch(**overrides) -> ArchetypeVector:
    return ArchetypeVector(**overrides)


# ── Elegibilidad ─────────────────────────────────────────────────────────

def test_elegible_por_camino_rebelde():
    arch = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    assert es_elegible(arch)


def test_elegible_por_camino_individuado():
    # self alto + sombra igualmente alta (sin polarización) → tensión baja, individuación alta
    arch_integrado = _arch(self_=0.95, sombra=0.95, anima_animus=0.4, heroe=0.4, sabio=0.4,
                            trickster=0.25, madre=0.4, padre=0.4, nino_divino=0.3, gobernante=0.4, rebelde=0.3)
    assert arch_integrado.individuacion_index() >= _umbral_individuacion()
    assert es_elegible(arch_integrado)


def _umbral_individuacion() -> float:
    from core.social.serpent import _INDIVIDUACION_MIN
    return _INDIVIDUACION_MIN


def test_no_elegible_perfil_conforme_y_no_individuado():
    arch = _arch(rebelde=0.2, trickster=0.2, persona=0.8, self_=0.3, sombra=0.3)
    assert not es_elegible(arch)


# ── Acumulación y decaimiento ────────────────────────────────────────────

def test_tentar_incrementa_solo_si_elegible():
    serpiente = Serpiente()
    elegible = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    no_elegible = _arch(rebelde=0.2, trickster=0.2, persona=0.8)

    serpiente.tentar("a1", elegible)
    serpiente.tentar("a2", no_elegible)

    assert serpiente.nivel("a1") > 0.0
    assert serpiente.nivel("a2") == 0.0


def test_tentar_acumula_con_contactos_repetidos():
    serpiente = Serpiente()
    elegible = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    for _ in range(3):
        serpiente.tentar("a1", elegible)
    assert serpiente.nivel("a1") == min(1.0, 3 * 0.15)


def test_tentar_cruza_el_umbral_con_contacto_sostenido():
    serpiente = Serpiente()
    elegible = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    assert not serpiente.tentado("a1")
    for _ in range(5):
        serpiente.tentar("a1", elegible)
    assert serpiente.tentado("a1")


def test_decaer_reduce_sin_contacto():
    serpiente = Serpiente()
    elegible = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    for _ in range(5):
        serpiente.tentar("a1", elegible)
    nivel_con_tentacion = serpiente.nivel("a1")
    serpiente.decaer("a1")
    assert serpiente.nivel("a1") < nivel_con_tentacion


def test_decaer_no_baja_de_cero():
    serpiente = Serpiente()
    serpiente.decaer("fantasma")
    assert serpiente.nivel("fantasma") == 0.0


# ── Canal de sesgo ───────────────────────────────────────────────────────

def test_influence_vacio_antes_del_umbral():
    serpiente = Serpiente()
    elegible = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    serpiente.tentar("a1", elegible)  # un solo contacto, por debajo del umbral
    assert serpiente.influence("a1") == {}


def test_influence_aleja_de_la_cooperacion_tras_el_umbral():
    serpiente = Serpiente()
    elegible = _arch(rebelde=0.9, trickster=0.9, persona=0.1)
    for _ in range(5):
        serpiente.tentar("a1", elegible)
    bias = serpiente.influence("a1")
    assert bias["cooperacion"] < 0
    assert bias["competencia"] > 0


# ── visitar (un día de actividad sobre la población) ───────────────────────

def test_visitar_no_elegibles_nunca_acumula():
    serpiente = Serpiente(seed=1)
    no_elegibles = {f"a{i}": _arch(rebelde=0.2, trickster=0.2, persona=0.8) for i in range(10)}
    for _ in range(10):
        serpiente.visitar(no_elegibles)
    assert all(serpiente.nivel(aid) == 0.0 for aid in no_elegibles)


def test_visitar_eventualmente_tienta_a_elegibles_con_contacto_sostenido():
    serpiente = Serpiente(seed=2)
    elegibles = {f"a{i}": _arch(rebelde=0.9, trickster=0.9, persona=0.1) for i in range(20)}
    for _ in range(30):
        serpiente.visitar(elegibles)
    assert any(serpiente.tentado(aid) for aid in elegibles)


def test_visitar_es_reproducible_por_seed():
    elegibles = {f"a{i}": _arch(rebelde=0.9, trickster=0.9, persona=0.1) for i in range(10)}
    s1 = Serpiente(seed=99)
    s2 = Serpiente(seed=99)
    for _ in range(10):
        s1.visitar(elegibles)
        s2.visitar(elegibles)
    for aid in elegibles:
        assert s1.nivel(aid) == s2.nivel(aid)
