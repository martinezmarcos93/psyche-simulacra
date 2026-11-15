"""
scripts/calibrar_natalidad.py — Mide la natalidad con distintos valores de los
parámetros de reproducción, para elegir los recomendados.

Cada combinación (parámetros × semilla) corre en un proceso propio, porque el
motor lee los parámetros de variables de entorno al importarse. Además de
nacimientos y muertes, registra cada día cuántas parejas pasan cada filtro de
`_check_reproduccion` (edad, necesidades, vínculo), para saber qué filtro es el
que frena los nacimientos. El observador no toca el estado ni el RNG.

Uso:
    python scripts/calibrar_natalidad.py --salida /tmp/calib --anios 10 \
        --semillas 42 7 --config base --config "prob=0.02" \
        --config "prob=0.02,vinculo=0.40"

Claves de --config: prob, vinculo, necesidades, cooldown, fatiga (lo que falte usa el
valor por defecto del motor). Resultado: <salida>/<nombre>_s<semilla>.json y,
al final, una tabla resumen por pantalla.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_CLAVES = {
    "prob": "PROB_REPRO_DIARIA",
    "vinculo": "BOND_REPRO_MIN",
    "necesidades": "REPRO_NEEDS_MAX",
    "cooldown": "REPRO_COOLDOWN_DIAS",
    "fatiga": "REPRO_FATIGA_MAX",
}
_UMBRALES_VINCULO = (0.10, 0.20, 0.30, 0.40, 0.55)


def _parsear_config(texto: str) -> dict[str, str]:
    if texto.strip() in ("", "base"):
        return {}
    env: dict[str, str] = {}
    for parte in texto.split(","):
        clave, _, valor = parte.partition("=")
        clave = clave.strip()
        if clave not in _CLAVES:
            raise SystemExit(f"Clave desconocida en --config: {clave!r} (válidas: {', '.join(_CLAVES)})")
        float(valor)  # valida que sea un número
        env[_CLAVES[clave]] = valor.strip()
    return env


def _nombre(texto: str) -> str:
    return "base" if texto.strip() in ("", "base") else texto.replace("=", "").replace(",", "_").replace(".", "p")


# ── Proceso hijo: una corrida ────────────────────────────────────────────────

def _correr_una(salida: Path, nombre: str, semilla: int, anios: int, poblacion: str) -> None:
    """Corre una simulación y escribe su JSON. El entorno ya trae los parámetros."""
    sys.path.insert(0, str(ROOT))
    trabajo = salida / f"_trabajo_{nombre}_s{semilla}"
    trabajo.mkdir(parents=True, exist_ok=True)
    os.chdir(trabajo)

    from core.agents import agent_core as AC
    from core.simulation import SimulationRunner

    runner = SimulationRunner.new_session(
        seed_file=str(ROOT / "data" / "seeds" / poblacion), seed=semilla,
        db_path="data/db/simulation.db", checkpoint_dir="data/checkpoints", vault_path="vault",
    )
    core = runner.agents
    por_anio: list[dict] = []
    acum = {"dias": 0, "en_edad": 0, "aptos": 0, "elegibles": 0,
            "con_hambre": 0, "con_sed": 0, "con_fatiga": 0, "en_descanso": 0,
            **{f"pares_vinculo_{u:.2f}": 0 for u in _UMBRALES_VINCULO}}
    previos = {"nac": 0, "mue": 0}
    inicio = time.monotonic()

    def _cerrar_anio(dia: int) -> None:
        n = max(1, acum["dias"])
        nac, mue = len(core.birth_log), len(core.death_log)
        causas: dict[str, int] = {}
        for m in core.death_log[previos["mue"]:]:
            causas[m["causa"]] = causas.get(m["causa"], 0) + 1
        por_anio.append({
            "anio": len(por_anio) + 1, "dia": dia, "vivos": core.alive_count(),
            "nacimientos": nac - previos["nac"], "muertes": mue - previos["mue"],
            "causas": causas,
            **{k: round(v / n, 2) for k, v in acum.items() if k != "dias"},
        })
        previos["nac"], previos["mue"] = nac, mue
        for k in acum:
            acum[k] = 0
        _guardar(False)

    def _guardar(terminada: bool) -> None:
        datos = {
            "nombre": nombre, "semilla": semilla, "poblacion": poblacion,
            "parametros": {"prob": AC._PROB_REPRO_DIARIA, "vinculo": AC._BOND_REPRODUCCION,
                           "necesidades": AC._REPRO_NEEDS_MAX, "cooldown": AC._COOLDOWN_REPRO,
                           "fatiga": AC._REPRO_FATIGA_MAX},
            "terminada": terminada, "dias": runner.current_dia,
            "vivos_final": core.alive_count(), "nacimientos": len(core.birth_log),
            "muertes": len(core.death_log), "minutos": round((time.monotonic() - inicio) / 60, 1),
            "por_anio": por_anio,
        }
        destino = salida / f"{nombre}_s{semilla}.json"
        tmp = destino.with_suffix(".tmp")
        tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(destino)

    def _observar(tp) -> None:
        vivos = [a for a in core.agents.values() if a.is_alive]
        en_edad = [a for a in vivos if AC._EDAD_MIN_REPRO <= a.edad <= AC._EDAD_MAX_REPRO]
        aptos = {a.id for a in en_edad
                 if a._cooldown_reproduccion <= 0 and a.needs.hambre < AC._REPRO_NEEDS_MAX
                 and a.needs.sed < AC._REPRO_NEEDS_MAX and a.needs.fatiga < AC._REPRO_FATIGA_MAX}
        acum["dias"] += 1
        acum["con_hambre"] += sum(a.needs.hambre >= AC._REPRO_NEEDS_MAX for a in en_edad)
        acum["con_sed"] += sum(a.needs.sed >= AC._REPRO_NEEDS_MAX for a in en_edad)
        acum["con_fatiga"] += sum(a.needs.fatiga >= AC._REPRO_FATIGA_MAX for a in en_edad)
        acum["en_descanso"] += sum(a._cooldown_reproduccion > 0 for a in en_edad)
        acum["en_edad"] += len(en_edad)
        acum["aptos"] += len(aptos)
        for i, a in enumerate(en_edad):
            for b in en_edad[i + 1:]:
                vinculo = core.social_network.get_bond(a.id, b.id)
                for u in _UMBRALES_VINCULO:
                    if vinculo >= u:
                        acum[f"pares_vinculo_{u:.2f}"] += 1
                if vinculo >= AC._BOND_REPRODUCCION and a.id in aptos and b.id in aptos:
                    acum["elegibles"] += 1
        if tp.dia_simulado % 365 == 0:
            _cerrar_anio(tp.dia_simulado)
        if not vivos:
            runner.shutdown()

    runner.clock.on_day(_observar, priority=97)
    runner.run(n_days=anios * 365)
    if acum["dias"]:
        _cerrar_anio(runner.current_dia)
    _guardar(True)


# ── Proceso padre: lanza y resume ────────────────────────────────────────────

def _lanzar(args, texto: str, semilla: int) -> tuple[str, int, int]:
    nombre = _nombre(texto)
    env = {**os.environ, **_parsear_config(texto), "PYTHONHASHSEED": "0",
           "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8", "NARRATIVE_ENABLED": "false"}
    log = args.salida / f"{nombre}_s{semilla}.log"
    with open(log, "w", encoding="utf-8") as f:
        r = subprocess.run(
            [sys.executable, "-u", str(Path(__file__).resolve()), "--hijo", nombre,
             "--salida", str(args.salida), "--anios", str(args.anios),
             "--semillas", str(semilla), "--poblacion", args.poblacion],
            env=env, stdout=f, stderr=subprocess.STDOUT)
    return nombre, semilla, r.returncode


def _resumen(salida: Path) -> None:
    print(f"\n{'config':<34}{'sem':>4}{'años':>6}{'vivos':>6}{'nac':>5}{'mue':>5}"
          f"{'aptos/día':>10}{'pares≥vínc':>11}{'elegibles':>10}")
    for p in sorted(salida.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        a = d["por_anio"]
        n = max(1, len(a))
        umbral = f"pares_vinculo_{min(_UMBRALES_VINCULO, key=lambda u: abs(u - d['parametros']['vinculo'])):.2f}"
        print(f"{d['nombre']:<34}{d['semilla']:>4}{d['dias'] / 365:>6.1f}{d['vivos_final']:>6}"
              f"{d['nacimientos']:>5}{d['muertes']:>5}"
              f"{sum(x['aptos'] for x in a) / n:>10.1f}{sum(x.get(umbral, 0) for x in a) / n:>11.1f}"
              f"{sum(x['elegibles'] for x in a) / n:>10.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--salida", type=Path, required=True)
    ap.add_argument("--anios", type=int, default=10)
    ap.add_argument("--semillas", type=int, nargs="+", default=[42])
    ap.add_argument("--config", action="append", default=[])
    ap.add_argument("--poblacion", default="initial_personas.yaml")
    ap.add_argument("--procesos", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--hijo", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    args.salida = args.salida.resolve()
    args.salida.mkdir(parents=True, exist_ok=True)

    if args.hijo is not None:
        _correr_una(args.salida, args.hijo, args.semillas[0], args.anios, args.poblacion)
        return

    tareas = [(c, s) for c in (args.config or ["base"]) for s in args.semillas]
    with ThreadPoolExecutor(max_workers=args.procesos) as pool:
        for nombre, semilla, codigo in pool.map(lambda t: _lanzar(args, *t), tareas):
            print(f"[calibrar] {nombre} s{semilla}: {'ok' if codigo == 0 else f'ERROR {codigo}'}", flush=True)
    _resumen(args.salida)


if __name__ == "__main__":
    main()
