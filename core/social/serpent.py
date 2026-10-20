from __future__ import annotations

import random
from dataclasses import dataclass, field

from core.agents.psyche.archetypes import ArchetypeVector

# Elegibilidad del "librepensador" — dos caminos arquetípicos distintos a la
# autonomía (Capa A, documentado como axioma del experimento, no como
# hallazgo — ver docs/experiments/): el rebelde/trickster que rompe por
# desafío, el self-integrado que rompe por coherencia propia. Constantes
# elegidas a mano, mismo criterio que los umbrales de MythologyEngine.
_REBELDE_MIN       = 0.6
_TRICKSTER_MIN     = 0.6
_PERSONA_MAX       = 0.4
_INDIVIDUACION_MIN = 0.7

# Dinámica de la tentación — acumula por contacto, decae sin él. Umbral
# elegido a mano (mismo criterio que `_COHERENCE_TO_CRYSTALLIZE` en
# MythologyEngine): ni instantáneo ni inalcanzable con contacto sostenido.
_TENTACION_INCREMENTO = 0.15
_TENTACION_DECAY      = 0.05
_TENTACION_UMBRAL     = 0.60

# Sesgo de la tentación una vez cruzado el umbral — empuja lejos de la
# cooperación. Mismo estatus arquitectónico que `VOCACIONES` en nomos.py:
# un catálogo fijo de deltas, no una decisión de acción.
_TENTACION_BIAS: dict[str, float] = {
    "competencia":  0.20,
    "aislamiento":  0.15,
    "manipulacion": 0.15,
    "cooperacion":  -0.25,
}

_ACCIONES = ("cooperacion", "competencia", "aislamiento", "manipulacion")

# Fracción esperada de agentes elegibles vivos que la Serpiente contacta en
# un día dado — no visita a todos a la vez. Constante Capa A, elegida a mano.
_PROB_CONTACTO_DIARIO = 0.5


def es_elegible(arch: ArchetypeVector) -> bool:
    """
    Dos caminos a la elegibilidad, no uno — el rebelde caótico y el self
    integrado llegan a la autonomía por rutas opuestas (ver docstring del
    módulo). Ninguno es "mejor"; son los dos tipos de agente que una
    sociedad impuesta no puede retener indefinidamente.
    """
    camino_rebelde = (
        arch.rebelde >= _REBELDE_MIN
        and arch.trickster >= _TRICKSTER_MIN
        and arch.persona <= _PERSONA_MAX
    )
    camino_individuado = arch.individuacion_index() >= _INDIVIDUACION_MIN
    return camino_rebelde or camino_individuado


@dataclass
class Serpiente:
    """
    Entidad única, fuera del ciclo biológico normal (no come, no muere, no
    se reproduce, no está sujeta al mapa físico). Busca agentes elegibles
    (`es_elegible`) y acumula tentación en ellos por contacto (`tentar`),
    que decae sin él (`decaer`).

    Una vez cruzado el umbral, `influence()` expone el sesgo de la
    tentación como un canal más del colapso cuántico nativo — igual
    estatus que `Nomos.vocacion_bias`. La Serpiente nunca decide la acción
    del agente, solo la vuelve una posibilidad real que compite contra la
    vocación impuesta y el resto de la psique del agente en el mismo
    colapso. El acto de desafío en sí (si el colapso resuelve no-cooperación
    mientras la tentación está activa) es lo que el orquestador usa para
    disparar el switch global de `Nomos` — ver integración en `AgentCore`.
    """
    seed: int | None = None
    _tentacion: dict[str, float] = field(default_factory=dict)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def tentar(self, agent_id: str, arch: ArchetypeVector) -> None:
        """Un contacto de la Serpiente con el agente. No-op si no es elegible."""
        if not es_elegible(arch):
            return
        actual = self._tentacion.get(agent_id, 0.0)
        self._tentacion[agent_id] = min(1.0, actual + _TENTACION_INCREMENTO)

    def decaer(self, agent_id: str) -> None:
        """Decaimiento por falta de contacto — llamar una vez por agente vivo
        y período (día) en que la Serpiente no lo visitó."""
        actual = self._tentacion.get(agent_id, 0.0)
        if actual > 0.0:
            self._tentacion[agent_id] = max(0.0, actual - _TENTACION_DECAY)

    def nivel(self, agent_id: str) -> float:
        return self._tentacion.get(agent_id, 0.0)

    def tentado(self, agent_id: str) -> bool:
        """True si la tentación acumulada cruzó el umbral de actuar."""
        return self.nivel(agent_id) >= _TENTACION_UMBRAL

    def influence(self, agent_id: str) -> dict[str, float]:
        """{acción: delta} — vacío si el agente todavía no cruzó el umbral."""
        return dict(_TENTACION_BIAS) if self.tentado(agent_id) else {}

    def visitar(self, archetypes: dict[str, ArchetypeVector]) -> None:
        """
        Un día de actividad de la Serpiente sobre la población viva: a cada
        agente elegible lo contacta con probabilidad `_PROB_CONTACTO_DIARIO`
        (RNG propio, reproducible vía `seed`); si no lo contacta (o no es
        elegible), su tentación decae. Pensado para llamarse una vez por día
        desde el orquestador (ver `AgentCore.on_day`).
        """
        for agent_id, arch in archetypes.items():
            if es_elegible(arch) and self._rng.random() < _PROB_CONTACTO_DIARIO:
                self.tentar(agent_id, arch)
            else:
                self.decaer(agent_id)
