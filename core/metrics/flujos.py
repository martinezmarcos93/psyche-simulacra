"""
Contadores de flujo por tribu (idea tomada de los contadores por reino de WorldBox 0.50–0.51,
ver docs/proposals/2026-11-10-worldbox-ideas-aplicables.md §2).

Cuenta, por día y por tribu: nacimientos, muertes (por categoría de causa), llegadas y
salidas de integrantes. Responde al pendiente "qué comparar entre corridas además de
población y tribus".

Es un observador puro: solo lee el mapeo agente→tribu y los logs de nacimientos y muertes,
no toca el estado de la simulación.

Identidad de las tribus: el TribeManager las nombra por su primer integrante ordenado, así
que al reclusterizar una tribu puede cambiar de ID sin que nadie se mueva. Para no contar eso
como una migración masiva, cada tribu nueva se empareja con la tribu anterior con la que
comparte más integrantes (cada una se usa una sola vez). Un agente migra solo si su tribu
nueva no es la heredera de la que tenía.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from core.world.catastrophe import _DURATIONS as _CATASTROFES

CATEGORIAS_MUERTE = ("vejez", "carencia", "violenta", "catastrofe", "liminal", "otra")

_CARENCIA = frozenset({"deshidratacion", "inanicion", "orfandad"})


def categoria_muerte(causa: str) -> str:
    """Agrupa la causa registrada por AgentCore._register_death."""
    if causa == "vejez":
        return "vejez"
    if causa in _CARENCIA:
        return "carencia"
    if causa.startswith("depredador_"):
        return "violenta"
    if causa in _CATASTROFES:
        return "catastrofe"
    if "liminal" in causa or "inexplicable" in causa:
        return "liminal"
    return "otra"


@dataclass
class FlujoTribu:
    """Fila del día para una tribu (tribe_flows.csv)."""
    dia: int
    tribe_id: str
    poblacion: int = 0
    nacimientos: int = 0
    muertes: int = 0
    muertes_violentas: int = 0
    llegadas: int = 0
    salidas: int = 0


@dataclass
class FlujoDia:
    """Totales del día (columnas nuevas de emergence_series.csv) + detalle por tribu."""
    nacimientos: int = 0
    muertes_vejez: int = 0
    muertes_carencia: int = 0
    muertes_violentas: int = 0
    muertes_catastrofe: int = 0
    muertes_otras: int = 0          # liminales + no clasificadas
    cambios_de_tribu: int = 0
    tribus_nuevas: int = 0
    tribus_extintas: int = 0
    por_tribu: list[FlujoTribu] = field(default_factory=list)

    def columnas(self) -> dict[str, int]:
        return {k: v for k, v in self.__dict__.items() if k != "por_tribu"}


def emparejar_tribus(previas: dict[str, set[str]], nuevas: dict[str, set[str]]) -> dict[str, str]:
    """nueva → previa heredera, por mayor solapamiento de integrantes (greedy, 1 a 1)."""
    pares = sorted(
        ((len(mn & mp), tn, tp) for tn, mn in nuevas.items() for tp, mp in previas.items() if mn & mp),
        key=lambda x: (-x[0], x[1], x[2]),
    )
    herencia: dict[str, str] = {}
    usadas: set[str] = set()
    for _, tn, tp in pares:
        if tn in herencia or tp in usadas:
            continue
        herencia[tn] = tp
        usadas.add(tp)
    return herencia


def _por_tribu(mapeo: dict[str, str]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for aid, tid in mapeo.items():
        out.setdefault(tid, set()).add(aid)
    return out


class ContadorFlujos:
    """
    Llevar uno por simulación y llamar `registrar_dia` una vez por día oficial.
    `sincronizar` fija la línea de base (fin de la prehistoria, reanudación desde checkpoint)
    para que lo ocurrido antes no se cuente como flujo del primer día.
    """

    def __init__(self) -> None:
        self._mapeo_previo: dict[str, str] | None = None
        self._cursor_nac = 0
        self._cursor_mue = 0

    def sincronizar(self, mapeo_vivos: dict[str, str], birth_log: list[dict], death_log: list[dict]) -> None:
        self._mapeo_previo = dict(mapeo_vivos)
        self._cursor_nac = len(birth_log)
        self._cursor_mue = len(death_log)

    def registrar_dia(self, dia: int, mapeo_vivos: dict[str, str],
                      birth_log: list[dict], death_log: list[dict]) -> FlujoDia:
        """`mapeo_vivos`: agente vivo → tribu, tal como quedó al cerrar el día."""
        # Primer día sin línea de base: las membresías arrancan como están (nadie migró),
        # pero los nacimientos y muertes del día sí se cuentan.
        previo = self._mapeo_previo if self._mapeo_previo is not None else dict(mapeo_vivos)
        nacidos = birth_log[self._cursor_nac:]
        muertos = death_log[self._cursor_mue:]

        herencia = emparejar_tribus(_por_tribu(previo), _por_tribu(mapeo_vivos))
        tribus_hoy = set(mapeo_vivos.values())
        tribus_ayer = set(previo.values())

        filas: dict[str, FlujoTribu] = {t: FlujoTribu(dia, t) for t in sorted(tribus_hoy)}
        for tid in mapeo_vivos.values():
            filas[tid].poblacion += 1

        def fila(tid: str) -> FlujoTribu:
            if tid not in filas:  # tribu de ayer que hoy ya no existe
                filas[tid] = FlujoTribu(dia, tid)
            return filas[tid]

        flujo = FlujoDia(
            nacimientos=len(nacidos),
            tribus_nuevas=sum(1 for t in tribus_hoy if t not in herencia),
            tribus_extintas=len(tribus_ayer - set(herencia.values())),
        )

        for n in nacidos:
            tid = (mapeo_vivos.get(n.get("id", "")) or mapeo_vivos.get(n.get("padre_a", ""))
                   or previo.get(n.get("padre_a", "")))
            if tid:
                fila(tid).nacimientos += 1

        for m in muertos:
            cat = categoria_muerte(m.get("causa", ""))
            if cat == "vejez":
                flujo.muertes_vejez += 1
            elif cat == "carencia":
                flujo.muertes_carencia += 1
            elif cat == "violenta":
                flujo.muertes_violentas += 1
            elif cat == "catastrofe":
                flujo.muertes_catastrofe += 1
            else:
                flujo.muertes_otras += 1
            tid = previo.get(m.get("agent_id", ""))
            if tid:
                f = fila(tid)
                f.muertes += 1
                if cat == "violenta":
                    f.muertes_violentas += 1

        # Migraciones: vivos ayer y hoy cuya tribu nueva no hereda la de ayer.
        for aid, tid_hoy in mapeo_vivos.items():
            tid_ayer = previo.get(aid)
            if tid_ayer is None or herencia.get(tid_hoy) == tid_ayer:
                continue
            flujo.cambios_de_tribu += 1
            fila(tid_ayer).salidas += 1
            filas[tid_hoy].llegadas += 1

        flujo.por_tribu = [filas[t] for t in sorted(filas)]
        self.sincronizar(mapeo_vivos, birth_log, death_log)
        return flujo


def mapeo_vivos(agents: dict, tribe_manager) -> dict[str, str]:
    """agente vivo → tribu (el TribeManager conserva a los muertos hasta reclusterizar)."""
    return {aid: tid for aid, tid in tribe_manager.agent_to_tribe.items()
            if aid in agents and agents[aid].is_alive}

