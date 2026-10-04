"""
ArchetypeRecalibrator — recalibración arquetípica por vivencia.

Las vivencias de un agente (los PerceivedEvent que produce su Ecuación Personal)
recalibran su ArchetypeVector mediante un único mecanismo, en vez de deltas
sueltos al vector. Cinco piezas, todas Capa A (estructura, sin vocabulario):

  1. Acumulador de experiencia, SEPARADO de los pesos base. Se alimenta de la
     resonancia que el ResonanceOperator ya calcula (`archetype_activation`): no
     asigna significado a ningún evento, solo registra qué se encendió en ESTA
     psique. El mismo estímulo deja huellas distintas en agentes distintos.
  2. Decaimiento diario: lo que no se vuelve a vivir se apaga.
  3. Consolidación por umbral: solo la experiencia que se sostiene una ventana de
     días se vuelca a los pesos base. Se redistribuye desde el resto del vector
     (la energía psíquica no se crea: principio de equivalencia), así este canal
     no satura los pesos.
  4. Dominante estable con histéresis: el arquetipo dominante solo cambia cuando
     otro lo supera por un margen durante una ventana de días. Ese cambio es un
     evento discreto ("reorganización") que se cuenta y se registra.
  5. Conservación: la suma del vector se mantiene en el presupuesto que el agente
     tenía el primer día. Los ~15 sistemas que suman deltas directos al vector
     (sueños, sustancias, apego, rituales, cultura) dejan de inflarlo: lo que se
     vive sube y el resto cede. Sin esto el vector satura — a 300 días, 2 de 12
     arquetipos por agente llegan a 1.0 y el dominante lo decide el orden del dict.

Compensación: si la valencia vivida cae de forma sostenida por debajo de la línea
de base DEL PROPIO agente, la presión de experiencia va a los arquetipos menos
desarrollados y se retira del dominante — lo indiferenciado se activa cuando la
actitud dominante deja de servir. El malestar es relativo y no absoluto porque la
valencia típica es muy positiva (mediana ~+0.65): un umbral fijo no dispara nunca.

Patrón tomado de JPAF (arXiv 2601.10025) y reimplementado en numérico, sin LLM —
ver docs/proposals/2026-10-04-jpaf-ideas-aplicables.md (P1 y P2).
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .archetypes import ARCHETYPE_NAMES

if TYPE_CHECKING:
    from .archetypes import ArchetypeVector

# Ganancia global de la experiencia sobre la resonancia cruda. Calibrable para A/B.
_GAIN = float(os.getenv("RECALIBRATION_GAIN", "1.0"))

# Acumulador
_RETENCION_DIARIA = 0.90   # fracción de experiencia que sobrevive cada día
_EXPERIENCIA_MAX  = 0.30   # cota por arquetipo (en ambos signos)

# Consolidación
_UMBRAL_CONSOLIDACION  = 0.05  # |experiencia| mínima para contar como sostenida
_VENTANA_CONSOLIDACION = 5     # días seguidos sobre el umbral
_TASA_CONSOLIDACION    = 0.25  # fracción de la experiencia que pasa al peso base

# Dominante estable
_MARGEN_REORGANIZACION  = 0.03  # ventaja mínima del candidato sobre el dominante
_VENTANA_REORGANIZACION = 7     # días seguidos con esa ventaja

# Compensación
_ALPHA_MALESTAR    = 0.20  # memoria de ~5 días sobre la valencia media diaria
_ALPHA_LINEA_BASE  = 0.02  # memoria de ~50 días: la valencia habitual del agente
_UMBRAL_MALESTAR   = 0.10  # caída de la valencia reciente bajo la línea de base que dispara
_GAIN_COMPENSACION = 0.05
_N_COMPENSADOS     = 2     # cuántos arquetipos menos desarrollados reciben presión


class ArchetypeRecalibrator:
    """Estado de recalibración de un agente. Uno por agente."""

    def __init__(self) -> None:
        self.experiencia: dict[str, float] = {a: 0.0 for a in ARCHETYPE_NAMES}
        self._dias_sostenido: dict[str, int] = {a: 0 for a in ARCHETYPE_NAMES}
        # Valencia vivida durante el día en curso (se resetea en on_day)
        self._valencia_sum: float = 0.0
        self._valencia_n:   int   = 0
        self.valencia_ema:  float = 0.0
        self.valencia_base: float | None = None   # línea de base; None hasta la primera vivencia
        # Presupuesto de energía arquetípica (suma del vector el primer día)
        self.presupuesto: float | None = None
        # Dominante estable
        self.dominante: str | None = None
        self._candidato: str | None = None
        self._dias_candidato: int = 0
        self.reorganizaciones: int = 0

    # ── Vivencia ──────────────────────────────────────────────────────────────

    def registrar(self, activation: dict[str, float], valence: float) -> None:
        """Acumula la huella de un PerceivedEvent. Llamado por cada percepción."""
        self._valencia_sum += valence
        self._valencia_n   += 1
        for arch, delta in activation.items():
            if arch in self.experiencia:
                self.experiencia[arch] = _clamp_exp(self.experiencia[arch] + delta * _GAIN)

    # ── Ciclo diario ──────────────────────────────────────────────────────────

    def on_day(self, archetypes: "ArchetypeVector") -> tuple[str, str] | None:
        """
        Decae, compensa, consolida y actualiza el dominante estable.
        Devuelve (dominante_anterior, dominante_nuevo) si hubo reorganización.
        """
        self._actualizar_malestar()
        self._compensar(archetypes)
        self._consolidar(archetypes)
        for arch in self.experiencia:
            self.experiencia[arch] *= _RETENCION_DIARIA
        self._conservar(archetypes)
        return self._actualizar_dominante(archetypes)

    def _actualizar_malestar(self) -> None:
        if self._valencia_n > 0:
            media = self._valencia_sum / self._valencia_n
            if self.valencia_base is None:
                self.valencia_base = media
                self.valencia_ema  = media
            else:
                self.valencia_ema  += _ALPHA_MALESTAR   * (media - self.valencia_ema)
                self.valencia_base += _ALPHA_LINEA_BASE * (media - self.valencia_base)
        self._valencia_sum = 0.0
        self._valencia_n   = 0

    def malestar(self) -> float:
        """Cuánto cayó la valencia reciente bajo la línea de base, pasado el umbral (>= 0)."""
        if self.valencia_base is None:
            return 0.0
        return max(0.0, self.valencia_base - self.valencia_ema - _UMBRAL_MALESTAR)

    def _conservar(self, archetypes: "ArchetypeVector") -> None:
        pesos = archetypes.to_dict()
        total = sum(pesos.values())
        if self.presupuesto is None:
            self.presupuesto = total
            return
        if total <= 0.0 or abs(total - self.presupuesto) < 1e-12:
            return
        factor = self.presupuesto / total
        for arch, peso in pesos.items():
            setattr(archetypes, _attr(arch), max(0.0, min(1.0, peso * factor)))

    def _compensar(self, archetypes: "ArchetypeVector") -> None:
        malestar = self.malestar()
        if malestar <= 0.0:
            return
        pesos = archetypes.to_dict()
        presion = _GAIN_COMPENSACION * malestar * _GAIN
        # Desempate por nombre: el orden no depende del orden de inserción del dict.
        menos_desarrollados = sorted(pesos, key=lambda a: (pesos[a], a))[:_N_COMPENSADOS]
        for arch in menos_desarrollados:
            self.experiencia[arch] = _clamp_exp(self.experiencia[arch] + presion)
        dom = self.dominante or archetypes.dominant()
        self.experiencia[dom] = _clamp_exp(self.experiencia[dom] - presion)

    def _consolidar(self, archetypes: "ArchetypeVector") -> None:
        for arch in ARCHETYPE_NAMES:
            if abs(self.experiencia[arch]) >= _UMBRAL_CONSOLIDACION:
                self._dias_sostenido[arch] += 1
            else:
                self._dias_sostenido[arch] = 0
            if self._dias_sostenido[arch] < _VENTANA_CONSOLIDACION:
                continue
            self._dias_sostenido[arch] = 0
            delta = self.experiencia[arch] * _TASA_CONSOLIDACION
            self.experiencia[arch] -= delta
            _transferir(archetypes, arch, delta)

    def _actualizar_dominante(self, archetypes: "ArchetypeVector") -> tuple[str, str] | None:
        pesos = archetypes.to_dict()
        candidato = max(pesos, key=pesos.get)
        reorganizacion = None

        if self.dominante is None:
            self.dominante = candidato
        elif (candidato != self.dominante
              and pesos[candidato] >= pesos[self.dominante] + _MARGEN_REORGANIZACION):
            if candidato == self._candidato:
                self._dias_candidato += 1
            else:
                self._candidato = candidato
                self._dias_candidato = 1
            if self._dias_candidato >= _VENTANA_REORGANIZACION:
                reorganizacion = (self.dominante, candidato)
                self.dominante = candidato
                self.reorganizaciones += 1
                self._candidato = None
                self._dias_candidato = 0
        else:
            self._candidato = None
            self._dias_candidato = 0

        archetypes._dominante_estable = self.dominante
        return reorganizacion

    # ── Persistencia ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "experiencia":      dict(self.experiencia),
            "dias_sostenido":   dict(self._dias_sostenido),
            "valencia_sum":     self._valencia_sum,
            "valencia_n":       self._valencia_n,
            "valencia_ema":     self.valencia_ema,
            "valencia_base":    self.valencia_base,
            "presupuesto":      self.presupuesto,
            "dominante":        self.dominante,
            "candidato":        self._candidato,
            "dias_candidato":   self._dias_candidato,
            "reorganizaciones": self.reorganizaciones,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchetypeRecalibrator":
        r = cls()
        for arch in ARCHETYPE_NAMES:
            r.experiencia[arch]     = float(data.get("experiencia", {}).get(arch, 0.0))
            r._dias_sostenido[arch] = int(data.get("dias_sostenido", {}).get(arch, 0))
        r._valencia_sum    = float(data.get("valencia_sum", 0.0))
        r._valencia_n      = int(data.get("valencia_n", 0))
        r.valencia_ema     = float(data.get("valencia_ema", 0.0))
        r.valencia_base    = data.get("valencia_base")
        r.presupuesto      = data.get("presupuesto")
        r.dominante        = data.get("dominante")
        r._candidato       = data.get("candidato")
        r._dias_candidato  = int(data.get("dias_candidato", 0))
        r.reorganizaciones = int(data.get("reorganizaciones", 0))
        return r


def _clamp_exp(x: float) -> float:
    return max(-_EXPERIENCIA_MAX, min(_EXPERIENCIA_MAX, x))


def _attr(arch: str) -> str:
    return "self_" if arch == "self" else arch


def _transferir(archetypes: "ArchetypeVector", arch: str, delta: float) -> None:
    """
    Suma `delta` al peso de `arch` y lo compensa en el resto del vector, en
    proporción al peso de cada uno. La suma total se conserva salvo recortes
    en los bordes [0, 1].
    """
    actual = getattr(archetypes, _attr(arch))
    nuevo  = max(0.0, min(1.0, actual + delta))
    aplicado = nuevo - actual
    if aplicado == 0.0:
        return
    setattr(archetypes, _attr(arch), nuevo)

    otros = [a for a in ARCHETYPE_NAMES if a != arch]
    total_otros = sum(getattr(archetypes, _attr(a)) for a in otros)
    if total_otros <= 0.0:
        return
    for a in otros:
        peso = getattr(archetypes, _attr(a))
        setattr(archetypes, _attr(a),
                max(0.0, min(1.0, peso - aplicado * peso / total_otros)))
