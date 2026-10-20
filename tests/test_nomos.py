"""
Tests de Nomos (Fase 1 — Experimento EDEN).
Cubre: asignación de vocación (armonía/tensión mixta, no contradicción
universal), canal de sesgo, multiplicadores providenciales, y el
interruptor (disable abrupto y global).
"""
from core.agents.psyche.archetypes import ArchetypeVector
from core.social.nomos import Nomos, VOCACIONES


def _arch(**overrides) -> ArchetypeVector:
    return ArchetypeVector(**overrides)


_REBELDE = _arch(rebelde=0.95, trickster=0.95, persona=0.1, sombra=0.8)
_SOCIABLE = _arch(madre=0.9, self_=0.8, persona=0.8, sombra=0.1, rebelde=0.05)


# ── Asignación de vocación ──────────────────────────────────────────────────

def test_assign_vocaciones_cubre_todos_los_agentes():
    nomos = Nomos(seed=1)
    archetypes = {"a1": _REBELDE, "a2": _SOCIABLE}
    nomos.assign_vocaciones(archetypes)
    assert nomos.vocacion_de("a1") in VOCACIONES
    assert nomos.vocacion_de("a2") in VOCACIONES
    assert nomos.en_armonia("a1") in (True, False)
    assert nomos.en_armonia("a2") in (True, False)


def test_no_todos_los_agentes_quedan_en_la_misma_condicion():
    """
    Con una población suficientemente grande, debe haber tanto agentes en
    armonía como en tensión — no una contradicción universal ni una
    conformidad universal. Esto es lo que corrige el diseño anterior.
    """
    nomos = Nomos(seed=7)
    archetypes = {f"a{i}": _arch(rebelde=0.3 + 0.01 * i) for i in range(40)}
    nomos.assign_vocaciones(archetypes)
    estados = {nomos.en_armonia(aid) for aid in archetypes}
    assert estados == {True, False}


def test_asignacion_es_reproducible_por_seed():
    archetypes = {"a1": _REBELDE, "a2": _SOCIABLE, "a3": _arch()}
    n1 = Nomos(seed=42)
    n1.assign_vocaciones(archetypes)
    n2 = Nomos(seed=42)
    n2.assign_vocaciones(archetypes)
    for aid in archetypes:
        assert n1.vocacion_de(aid) == n2.vocacion_de(aid)
        assert n1.en_armonia(aid) == n2.en_armonia(aid)


def test_vocacion_en_armonia_refuerza_el_sesgo_nativo():
    nomos = Nomos()
    vocacion = nomos._vocacion_en_armonia(_SOCIABLE)
    native_bias = {a: _SOCIABLE.action_bias(a) for a in ("cooperacion", "competencia", "aislamiento", "manipulacion")}
    afinidad = nomos._afinidad(vocacion, native_bias)
    # Debe ser al menos tan buena como cualquier otra vocación disponible.
    assert afinidad == max(nomos._afinidad(v, native_bias) for v in VOCACIONES)


def test_vocacion_en_tension_contradice_el_sesgo_nativo():
    nomos = Nomos()
    vocacion = nomos._vocacion_en_tension(_REBELDE)
    native_bias = {a: _REBELDE.action_bias(a) for a in ("cooperacion", "competencia", "aislamiento", "manipulacion")}
    afinidad = nomos._afinidad(vocacion, native_bias)
    assert afinidad == min(nomos._afinidad(v, native_bias) for v in VOCACIONES)


# ── Canal de sesgo (vocacion_bias) ─────────────────────────────────────────

def test_vocacion_bias_vacio_sin_asignacion_previa():
    nomos = Nomos()
    assert nomos.vocacion_bias("fantasma") == {}


def test_vocacion_bias_vacio_cuando_disabled():
    nomos = Nomos(seed=1)
    nomos.assign_vocaciones({"a1": _REBELDE})
    nomos.disable()
    assert nomos.vocacion_bias("a1") == {}


def test_vocacion_bias_devuelve_el_dict_de_la_vocacion_asignada():
    nomos = Nomos(seed=1)
    nomos.assign_vocaciones({"a1": _REBELDE})
    vocacion = nomos.vocacion_de("a1")
    assert nomos.vocacion_bias("a1") == VOCACIONES[vocacion]


# ── Multiplicadores providenciales ─────────────────────────────────────────

def test_multiplicadores_favorables_mientras_enabled():
    nomos = Nomos()
    assert nomos.resource_multiplier > 1.0
    assert nomos.culture_cooldown_multiplier < 1.0
    assert nomos.mortality_multiplier < 1.0
    assert nomos.reproduction_cooldown_multiplier < 1.0


def test_multiplicadores_vuelven_a_neutro_al_disable():
    nomos = Nomos()
    nomos.disable()
    assert nomos.resource_multiplier == 1.0
    assert nomos.culture_cooldown_multiplier == 1.0
    assert nomos.mortality_multiplier == 1.0
    assert nomos.reproduction_cooldown_multiplier == 1.0


# ── El interruptor ──────────────────────────────────────────────────────────

def test_disable_es_abrupto_y_no_reversible_por_esta_api():
    nomos = Nomos()
    assert nomos.enabled is True
    nomos.disable()
    assert nomos.enabled is False


def test_disable_conserva_vocaciones_como_dato_historico():
    nomos = Nomos(seed=1)
    nomos.assign_vocaciones({"a1": _REBELDE})
    vocacion_antes = nomos.vocacion_de("a1")
    armonia_antes = nomos.en_armonia("a1")
    nomos.disable()
    assert nomos.vocacion_de("a1") == vocacion_antes
    assert nomos.en_armonia("a1") == armonia_antes
