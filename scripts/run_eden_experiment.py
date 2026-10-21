"""
Experimento EDEN — corrida A/B pareada por semilla.

Para cada semilla corre dos condiciones con la MISMA población y mundo
iniciales (mismo seed_file + seed):

  - control:    Nomos activo todo el run, sin Serpiente — el orden
                providencial nunca se rompe. Baseline: ¿qué métricas tiene
                una sociedad bajo orden impuesto sostenido?
  - tratamiento: Nomos + Serpiente activos — el switch se dispara cuando
                emerja (un agente elegible, tentado, cuyo propio colapso
                resuelva no-cooperación). Variable: el día del switch no es
                fijo, depende de la historia real de esa corrida.

Headless (sin BD/narrativa/Obsidian/UI) — mismo patrón que ab_interpretive.py
y run_robustness.py (ver docs/ARCHITECTURE.md §6: modo correcto para
experimentos A/B reproducibles).

Uso:
    python scripts/run_eden_experiment.py --seed-file data/seeds/eden_pilot_10.yaml --seeds 1,2,3 --days 200
    python scripts/run_eden_experiment.py --seed-file data/seeds/100_personas.yaml --seeds 1,2,3,4,5 --days 400

Salida: una línea "EDEN_RESULT " + JSON por cada (semilla, condición), y al
final el agregado en data/experiments/eden/<label>_summary.json. La serie
día-a-día de cada corrida se guarda en data/experiments/eden/<label>_<seed>_<condicion>.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from core.time import SimulationClock, ClockPriority
from core.world import WorldCore
from core.agents import AgentCore
from core.metrics import EmergenceMetrics
from core.social.nomos import Nomos
from core.social.serpent import Serpiente

# Ventana de agregación alrededor del evento (o del final del run en el
# control, que no tiene evento) — días, no ticks. Elegida a mano, mismo
# criterio que el resto de las constantes del experimento.
_VENTANA_DIAS = 60


def _mean(xs: list[float]) -> float:
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def _window_stats(series: list, metric: str) -> float:
    return round(_mean([getattr(m, metric) for m in series]), 6)


_METRICAS_REPORTADAS = (
    "kl_mean", "mig", "imi", "vfe_global",
    "behavioral_kl_mean", "behavioral_intra_tribe_dispersion",
    "field_kl_mean", "n_tribes", "n_alive",
)


def _run_condition(
    seed_file: str, seed: int, days: int, condicion: str,
) -> tuple[list, dict | None]:
    """Corre una condición (control|tratamiento) y devuelve (serie, eden_event)."""
    world = WorldCore(seed=seed)
    agents = AgentCore.from_yaml(seed_file, world, seed=seed)
    clock = SimulationClock(start_dia=0, start_hora=6)
    metrics = EmergenceMetrics()

    agents.nomos = Nomos(seed=seed + 100)
    agents.serpiente = Serpiente(seed=seed + 101) if condicion == "tratamiento" else None

    clock.on_tick(world.on_tick, priority=ClockPriority.WORLD)
    clock.on_day(world.on_day, priority=ClockPriority.WORLD)
    clock.on_tick(agents.on_tick, priority=ClockPriority.AGENT)
    clock.on_day(agents.on_day, priority=ClockPriority.AGENT)
    clock.on_season_change(world.on_season_change, priority=ClockPriority.WORLD)
    clock.on_season_change(agents.on_season_change, priority=ClockPriority.AGENT)

    series: list = []

    def _collect(tp) -> None:
        series.append(metrics.compute_day(
            dia=tp.dia_simulado,
            agents=agents.agents,
            tribe_manager=agents.tribe_manager,
            collective_field=agents.collective_field,
            culture_engine=agents.culture_engine,
            nomos=agents.nomos,
        ))

    def _stopper(tp) -> None:
        if tp.dia_simulado >= days:
            clock.shutdown()

    def _extinction(tp) -> None:
        if agents.alive_count() == 0:
            clock.shutdown()

    clock.on_day(_collect, priority=ClockPriority.PERSISTENCE)
    clock.on_day(_stopper, priority=ClockPriority.STOPPER)
    clock.on_day(_extinction, priority=ClockPriority.EXTINCTION)

    clock.start()
    return series, agents.eden_event


def _summarize(series: list, eden_event: dict | None) -> dict:
    if eden_event is None:
        pre = series
        post = []
    else:
        switch_day = eden_event["dia"]
        pre = [m for m in series if switch_day - _VENTANA_DIAS <= m.dia < switch_day]
        post = [m for m in series if switch_day <= m.dia < switch_day + _VENTANA_DIAS]

    result = {
        "days_run": len(series),
        "final_alive": series[-1].n_alive if series else 0,
        "switched": eden_event is not None,
        "switch_day": eden_event["dia"] if eden_event else None,
        "switch_agent": eden_event["agent_id"] if eden_event else None,
        "switch_accion": eden_event["accion_desafio"] if eden_event else None,
        "switch_en_armonia": eden_event["en_armonia"] if eden_event else None,
    }
    for metric in _METRICAS_REPORTADAS:
        result[f"{metric}_pre"] = _window_stats(pre, metric) if pre else None
        result[f"{metric}_post"] = _window_stats(post, metric) if post else None
    return result


def _write_series_csv(series: list, path: Path) -> None:
    if not series:
        return
    rows = [asdict(m) for m in series]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Experimento EDEN — corrida A/B pareada por semilla")
    parser.add_argument("--seed-file", default="data/seeds/eden_pilot_10.yaml")
    parser.add_argument("--seeds", default="1,2,3", help="Lista de semillas separadas por coma")
    parser.add_argument("--days", type=int, default=200)
    parser.add_argument("--output-dir", default="data/experiments/eden")
    parser.add_argument("--label", default=None, help="Prefijo de archivos de salida (default: nombre del seed-file)")
    args = parser.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    label = args.label or Path(args.seed_file).stem
    out_dir = Path(args.output_dir)

    resultados: list[dict] = []
    t0 = time.time()

    for seed in seeds:
        for condicion in ("control", "tratamiento"):
            series, eden_event = _run_condition(args.seed_file, seed, args.days, condicion)
            resumen = _summarize(series, eden_event)
            resumen.update({"seed": seed, "condicion": condicion, "seed_file": args.seed_file})
            resultados.append(resumen)
            _write_series_csv(series, out_dir / f"{label}_{seed}_{condicion}.csv")
            print("EDEN_RESULT " + json.dumps(resumen))

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / f"{label}_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "seed_file": args.seed_file,
            "seeds": seeds,
            "days": args.days,
            "elapsed_s": round(time.time() - t0, 1),
            "runs": resultados,
        }, f, indent=2, ensure_ascii=False)

    print(f"Resumen escrito en {summary_path}")


if __name__ == "__main__":
    main()
