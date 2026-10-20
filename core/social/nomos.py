from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Solo se usa como type hint — importarlo en tiempo de ejecución dispara
    # la inicialización de core.agents (que importa de vuelta este módulo
    # desde agent_core.py), un import circular si algo importa core.social.nomos
    # antes de que core.agents se haya tocado. Ver core/social/serpent.py,
    # mismo patrón.
    from core.agents.psyche.archetypes import ArchetypeVector

# Vocaciones impuestas por el orden providencial — catálogo fijo (Capa A),
# mismo estatus arquitectónico que los 12 arquetipos o los 5 tipos de mito
# campbellianos (ver docs/EMERGENCE.md). Cada vocación es un sesgo de acción
# análogo a `_ACTION_AFFINITY` de ArchetypeVector — compite dentro del mismo
# canal de colapso que ya mezcla arquetipo/complejo/rasgo/campo/interpretación
# (ver core/agents/quantum/collapse.py). Nomos nunca decide una acción
# directamente: solo aporta un sesgo más al mismo colapso cuántico nativo.
VOCACIONES: dict[str, dict[str, float]] = {
    "guardian": {"cooperacion": 0.30, "aislamiento": -0.15, "competencia": -0.10, "manipulacion": -0.10},
    "cuidador": {"cooperacion": 0.35, "competencia": -0.15, "manipulacion": -0.10, "aislamiento": -0.10},
    "artesano": {"cooperacion": 0.20, "aislamiento": -0.20, "competencia": -0.05, "manipulacion": -0.05},
    "mediador": {"cooperacion": 0.25, "manipulacion": -0.20, "competencia": -0.15, "aislamiento": -0.05},
}

_ACCIONES = ("cooperacion", "competencia", "aislamiento", "manipulacion")

# Multiplicadores de la providencia — constantes Capa A, elegidas a mano,
# igual criterio que los umbrales de MythologyEngine. Vuelven a neutro (1.0)
# en cuanto Nomos se desactiva; no hay degradado ni rampa, el retiro es
# abrupto y total (ver docs/experiments/ para la justificación del diseño).
_PROVIDENCE_RESOURCE_MULTIPLIER     = 1.60
_PROVIDENCE_CULTURE_MULTIPLIER      = 0.50
_PROVIDENCE_MORTALITY_MULTIPLIER    = 0.40
_PROVIDENCE_REPRODUCTION_MULTIPLIER = 0.60

# Fracción esperada de agentes "en armonía" con su vocación (contentos con su
# lugar en el mundo) vs. "en tensión" (su vocación contradice su naturaleza).
# No todos los agentes deberían estar en conflicto con el orden impuesto —
# algunos coinciden con él genuinamente. Constante Capa A, 50/50 deliberado
# (sin privilegiar a priori el resultado "todos rebeldes" ni "todos dóciles");
# recalibrable como las demás constantes del proyecto (ver docs/experiments/).
_PROB_EN_ARMONIA = 0.5


@dataclass
class Nomos:
    """
    Orden providencial global — instancia única, igual estatus que
    `MythologyEngine`. Mientras `enabled` es True:

    - Asigna a cada agente una vocación fija. Para una fracción de agentes
      (`_PROB_EN_ARMONIA`) la vocación REFUERZA su propio sesgo arquetípico
      — están en armonía, genuinamente contentos con su lugar. Para el
      resto, la vocación lo CONTRADICE deliberadamente — están en tensión
      entre ley impuesta y naturaleza real. `vocacion_bias()` expone esa
      vocación como un canal más de `collapse_state`, con el mismo peso que
      cualquier otro sesgo.
    - Favorece recursos, cultura/tecnología, mortalidad y reproducción vía
      multiplicadores que los sistemas correspondientes consultan
      (`resource_multiplier`, `culture_cooldown_multiplier`,
      `mortality_multiplier`, `reproduction_cooldown_multiplier`).

    Nomos nunca escribe `agente.accion = X` ni fuerza un resultado — todo lo
    que hace es sesgar canales y multiplicadores que el resto del sistema ya
    mezcla o consulta nativamente. `disable()` es el interruptor: abrupto y
    global, sin rampa.
    """
    enabled: bool = True
    seed: int | None = None
    _vocaciones: dict[str, str] = field(default_factory=dict)
    _en_armonia: dict[str, bool] = field(default_factory=dict)
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    @staticmethod
    def _afinidad(vocacion: str, native_bias: dict[str, float]) -> float:
        """Cuánto REFUERZA (positivo) o contradice (negativo) una vocación
        el sesgo arquetípico nativo del agente."""
        bias = VOCACIONES[vocacion]
        return sum(bias.get(accion, 0.0) * native_bias[accion] for accion in _ACCIONES)

    def _vocacion_en_armonia(self, arch: ArchetypeVector) -> str:
        """La vocación cuyo sesgo más refuerza la naturaleza del agente."""
        native_bias = {accion: arch.action_bias(accion) for accion in _ACCIONES}
        return max(VOCACIONES, key=lambda v: self._afinidad(v, native_bias))

    def _vocacion_en_tension(self, arch: ArchetypeVector) -> str:
        """La vocación cuyo sesgo más contradice la naturaleza del agente."""
        native_bias = {accion: arch.action_bias(accion) for accion in _ACCIONES}
        return min(VOCACIONES, key=lambda v: self._afinidad(v, native_bias))

    def assign_vocaciones(self, archetypes: dict[str, ArchetypeVector]) -> None:
        """
        Asigna a cada agente SIN vocación todavía una — en armonía o en
        tensión con su propio arquetipo, decidido por agente (RNG propio de
        Nomos, reproducible vía `seed`). No es una contradicción universal:
        refleja que en una sociedad impuesta hay quienes coinciden
        genuinamente con su lugar y quienes no.

        Idempotente por agente: llamarlo de nuevo (p. ej. una vez por día,
        para cubrir nacimientos) no reasigna a quien ya tiene vocación.
        """
        for agent_id, arch in archetypes.items():
            if agent_id in self._vocaciones:
                continue
            en_armonia = self._rng.random() < _PROB_EN_ARMONIA
            vocacion = (
                self._vocacion_en_armonia(arch) if en_armonia
                else self._vocacion_en_tension(arch)
            )
            self._vocaciones[agent_id] = vocacion
            self._en_armonia[agent_id] = en_armonia

    def vocacion_de(self, agent_id: str) -> str | None:
        return self._vocaciones.get(agent_id)

    def en_armonia(self, agent_id: str) -> bool | None:
        """True si la vocación del agente refuerza su naturaleza, False si la
        contradice, None si no tiene vocación asignada."""
        return self._en_armonia.get(agent_id)

    def vocacion_bias(self, agent_id: str) -> dict[str, float]:
        """{acción: delta} de la vocación impuesta — vacío si Nomos está
        apagado o el agente no tiene una asignada."""
        if not self.enabled:
            return {}
        vocacion = self._vocaciones.get(agent_id)
        if vocacion is None:
            return {}
        return VOCACIONES[vocacion]

    @property
    def resource_multiplier(self) -> float:
        return _PROVIDENCE_RESOURCE_MULTIPLIER if self.enabled else 1.0

    @property
    def culture_cooldown_multiplier(self) -> float:
        return _PROVIDENCE_CULTURE_MULTIPLIER if self.enabled else 1.0

    @property
    def mortality_multiplier(self) -> float:
        return _PROVIDENCE_MORTALITY_MULTIPLIER if self.enabled else 1.0

    @property
    def reproduction_cooldown_multiplier(self) -> float:
        return _PROVIDENCE_REPRODUCTION_MULTIPLIER if self.enabled else 1.0

    def disable(self) -> None:
        """El interruptor. Abrupto y global — no hay rampa ni degradado.
        Las vocaciones asignadas quedan como dato histórico (no se borran),
        simplemente dejan de aplicarse."""
        self.enabled = False
