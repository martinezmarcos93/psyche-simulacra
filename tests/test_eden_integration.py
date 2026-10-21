"""
Test de integración del Experimento EDEN (Fase 3): Nomos + Serpiente
conectados a AgentCore de punta a punta — vocación asignada, tentación
acumulada por contacto real, y el switch disparado por el acto de desafío
de un agente concreto resuelto por su propio colapso cuántico nativo (no
por un `if` que decida la rebelión).
"""
import time

from core.agents.agent import Agent
from core.agents.agent_core import AgentCore
from core.agents.psyche.archetypes import ArchetypeVector
from core.social.nomos import Nomos
from core.social.serpent import Serpiente
from core.time import TimePoint
from core.world.world_core import WorldCore

_DESAFIO = ("competencia", "aislamiento", "manipulacion")


def _make_tp(tick: int, hora: int) -> TimePoint:
    dia = tick // 24
    return TimePoint(
        tick=tick, dia_simulado=dia, hora_del_dia=hora,
        dia_del_año=dia % 360, año_simulado=dia // 360,
        estacion="verano",
        es_amanecer=(hora == 6), es_mediodia=(hora == 12),
        es_anochecer=(hora == 20), es_medianoche=(hora == 23),
        es_inicio_dia=(hora == 0), es_fin_dia=(hora == 23),
        timestamp_real=time.monotonic(),
    )


def _build_core(n_agents: int = 5, nomos_seed: int = 1, serpiente_seed: int = 1):
    world = WorldCore(seed=42)
    core = AgentCore(world)
    cx, cy = world.terrain.center
    for i in range(n_agents):
        core.add_agent(Agent(agent_id=f"a{i}", nombre=f"A{i}", posicion=(cx, cy), seed=i))
    core.nomos = Nomos(seed=nomos_seed)
    core.serpiente = Serpiente(seed=serpiente_seed)
    return world, core


def _run_days(world: WorldCore, core: AgentCore, dias: int, start_tick: int = 0) -> int:
    """Corre `dias` días completos (24 ticks c/u) y devuelve el próximo tick libre."""
    tick = start_tick
    for _ in range(dias):
        for hora in range(24):
            tp = _make_tp(tick, hora)
            world.on_tick(tp)
            core.on_tick(tp)
            tick += 1
        tp0 = _make_tp(tick - 24, 0)
        world.on_day(tp0)
        core.on_day(tp0)
    return tick


class TestEdenIntegration:

    def test_nomos_asigna_vocacion_al_primer_dia(self):
        world, core = _build_core(3)
        _run_days(world, core, dias=1)
        for agent_id in core.agents:
            assert core.nomos.vocacion_de(agent_id) is not None

    def test_switch_no_dispara_sin_agente_elegible(self):
        """Con psiques por defecto (no elegibles para la Serpiente), el orden
        providencial debe sobrevivir intacto — nadie puede tentarse."""
        world, core = _build_core(3)
        _run_days(world, core, dias=20)
        assert core.nomos.enabled is True
        assert core.eden_event is None

    def test_switch_dispara_por_agente_rebelde_tentado(self):
        world, core = _build_core(5)
        core.agents["a0"].archetypes = ArchetypeVector(
            rebelde=0.95, trickster=0.95, persona=0.05, sombra=0.8
        )

        _run_days(world, core, dias=30)

        assert core.nomos.enabled is False
        assert core.eden_event is not None
        assert core.eden_event["agent_id"] == "a0"
        assert core.eden_event["accion_desafio"] in _DESAFIO

    def test_switch_es_abrupto_y_no_se_revierte_solo(self):
        world, core = _build_core(5)
        core.agents["a0"].archetypes = ArchetypeVector(
            rebelde=0.95, trickster=0.95, persona=0.05, sombra=0.8
        )
        tick = _run_days(world, core, dias=30)
        assert core.nomos.enabled is False
        evento_original = dict(core.eden_event)

        # Correr más días tras el switch no debe reactivar a Nomos ni
        # pisar el evento ya registrado.
        _run_days(world, core, dias=10, start_tick=tick)
        assert core.nomos.enabled is False
        assert core.eden_event == evento_original

    def test_sin_eden_habilitado_el_comportamiento_es_el_de_siempre(self):
        """Sin Nomos/Serpiente asignados (core.nomos/core.serpiente == None,
        el default fuera de EDEN_ENABLED=1), on_tick/on_day corren igual que
        antes — ninguna de las piezas nuevas se activa por accidente."""
        world = WorldCore(seed=42)
        core = AgentCore(world)
        cx, cy = world.terrain.center
        for i in range(3):
            core.add_agent(Agent(agent_id=f"a{i}", nombre=f"A{i}", posicion=(cx, cy), seed=i))

        assert core.nomos is None
        assert core.serpiente is None
        _run_days(world, core, dias=5)  # no debe lanzar excepciones
        assert core.eden_event is None
