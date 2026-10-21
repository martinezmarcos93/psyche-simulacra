"""
core/runtime/corridas.py — Corridas de simulación aisladas (una carpeta y un proceso por corrida).

Cada corrida vive en su propia carpeta:

    <corridas>/2026-10-21_1530_eden_s1/
        config.json      ← qué se pidió (escenario, población, semilla, mecanismos…)
        estado.json      ← lo que escribe el proceso de la corrida (día, vivos, fase…)
        detener.flag     ← si existe, la corrida se detiene limpia al terminar el día
        corrida.log      ← salida completa del proceso
        data/ vault/     ← BD, checkpoints, métricas y notas de ESA corrida

El motor resuelve todas sus rutas relativas al directorio de trabajo, así que el
proceso de la corrida hace chdir a su carpeta y nada se pisa entre corridas.

Los mecanismos del motor se configuran por variables de entorno que se leen al
importar los módulos; por eso cada corrida es un proceso separado (dos corridas
en el mismo proceso no podrían tener configuraciones distintas).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

ESCENARIOS: dict[str, str] = {
    "off":   "Mundo libre",
    "orden": "Orden permanente",
    "eden":  "Edén",
}

ESCENARIOS_DESC: dict[str, str] = {
    "off": "Sin fuerza ordenadora. La sociedad se organiza sola desde el día 1.",
    "orden": "Una fuerza providencial (Nomos) asigna vocaciones, provee y pacifica "
             "durante toda la historia. Nadie puede romperla.",
    "eden": "El mismo orden providencial, pero una figura tentadora (la Serpiente) "
            "puede inducir a alguien a desobedecer. Si ocurre, el orden se retira "
            "para siempre y para todos.",
}

# Ajustes finos: perillas del motor que se leen de variables de entorno.
# (variable, sección, etiqueta, explicación, default, mínimo, máximo, paso, entero)
PARAMETROS_FINOS: list[tuple[str, str, str, str, float, float, float, float, bool]] = [
    ("REPRO_COOLDOWN_DIAS", "Natalidad", "Días de descanso tras un nacimiento",
     "Cuánto espera cada progenitor antes de poder volver a tener un hijo.",
     180, 0, 3650, 10, True),
    ("LETHALITY_FACTOR", "Mundo", "Letalidad de las catástrofes",
     "1 = normal. Menos de 1: mueren menos personas, pero el trauma simbólico "
     "de los sobrevivientes es mayor.", 1.0, 0.0, 3.0, 0.1, False),
    ("MYTH_CONTEXT_THRESHOLD", "Cultura y mito", "Umbral para que nazca un proto-mito",
     "Más bajo = la sociedad produce relatos míticos con más facilidad.",
     0.25, 0.0, 1.0, 0.05, False),
    ("MYTH_TRANSMISSION_CHOQUE_VIOLENTO", "Cultura y mito", "Transmisión de mitos en choques violentos",
     "Cuánto se contagia el mito cuando dos personas se enfrentan con violencia.",
     1.0, 0.0, 3.0, 0.05, False),
    ("MYTH_TRANSMISSION_CONFLICTO_EXPLOTACION", "Cultura y mito",
     "Transmisión de mitos en conflictos de explotación",
     "Cuánto se contagia el mito cuando una persona se aprovecha de otra.",
     0.5, 0.0, 3.0, 0.05, False),
    ("MYTH_TRANSMISSION_COOPERACION_PURA", "Cultura y mito", "Transmisión de mitos al cooperar",
     "Cuánto se contagia el mito en encuentros cooperativos.", 0.25, 0.0, 3.0, 0.05, False),
    ("NOMOS_WEIGHT", "Orden y Serpiente", "Fuerza del orden (Nomos)",
     "Peso de la vocación impuesta en cada decisión. Solo afecta a «Orden permanente» y «Edén».",
     0.20, 0.0, 1.0, 0.05, False),
    ("SERPENT_WEIGHT", "Orden y Serpiente", "Fuerza de la tentación (Serpiente)",
     "Peso de la tentación en las decisiones de quien fue tentado. Solo afecta a «Edén».",
     0.20, 0.0, 1.0, 0.05, False),
    ("INTERPRETIVE_WEIGHT", "Mecanismos psicológicos", "Peso del filtro interpretativo",
     "Cuánto influye la interpretación personal en lo que cada uno decide "
     "(si el filtro está activado).", 0.15, 0.0, 1.0, 0.05, False),
    ("RECALIBRATION_GAIN", "Mecanismos psicológicos", "Intensidad de la recalibración",
     "Cuánto pesan las vivencias al reorganizar la personalidad (si la recalibración "
     "está activada).", 1.0, 0.0, 5.0, 0.1, False),
]
_FINOS = {p[0]: p for p in PARAMETROS_FINOS}

# Tope de seguridad para "hasta la extinción" (100 años simulados).
TOPE_EXTINCION_DIAS = 36_500

ARCHIVO_CONFIG = "config.json"
ARCHIVO_ESTADO = "estado.json"
ARCHIVO_DETENER = "detener.flag"
ARCHIVO_LOG = "corrida.log"

# Fases que escribe el proceso de la corrida en estado.json
FASES_ACTIVAS = ("iniciando", "corriendo", "pausada", "deteniendo")
FASES_FINALES = ("terminada", "extinta", "detenida", "error")


@dataclass
class CorridaConfig:
    """Todo lo configurable de una corrida. Se guarda tal cual en config.json."""

    escenario: str = "off"                 # off | orden | eden
    poblacion: str = "initial_personas.yaml"  # nombre de archivo en data/seeds/
    semilla: int = 42
    dias: int = 0                          # 0 = hasta la extinción (con tope)
    nombre: str = ""                       # etiqueta libre; si falta se genera

    # Narrativa con IA local (Ollama)
    narrativa: bool = False
    modelo_ollama: str = "llama3.2"

    # Mecanismos psicológicos experimentales (apagados por defecto en el motor)
    filtro_interpretativo: bool = False
    reinterpretacion_receptor: bool = False
    boveda_mental: bool = False
    recalibracion_arquetipica: bool = False

    # Natalidad
    prob_repro_diaria: float = 0.007
    vinculo_min_repro: float = 0.55
    necesidades_max_repro: float = 0.45

    # Ritmo interno
    dias_hasta_clustering: int = 30
    dias_entre_checkpoints: int = 10

    # Ajustes finos (variable de entorno → valor); lo que falte usa el default
    ajustes: dict[str, float] = field(default_factory=dict)

    # Zona Liminal (intercambio de agentes entre simulaciones)
    liminal: bool = False
    liminal_host: str = "localhost"
    liminal_port: int = 8765

    # ── Validación ───────────────────────────────────────────────────────────

    def validar(self) -> list[str]:
        """Devuelve la lista de problemas (vacía si la config es válida)."""
        errores: list[str] = []
        if self.escenario not in ESCENARIOS:
            errores.append(f"Escenario desconocido: {self.escenario}")
        if ruta_poblacion(self.poblacion) is None:
            errores.append(f"No existe la población {self.poblacion}")
        if self.semilla < 0:
            errores.append("La semilla no puede ser negativa")
        if self.dias < 0:
            errores.append("Los días no pueden ser negativos")
        if self.recalibracion_arquetipica and not self.filtro_interpretativo:
            errores.append("La recalibración arquetípica necesita el filtro interpretativo")
        for nombre, v in (("prob_repro_diaria", self.prob_repro_diaria),
                          ("vinculo_min_repro", self.vinculo_min_repro),
                          ("necesidades_max_repro", self.necesidades_max_repro)):
            if not 0.0 <= v <= 1.0:
                errores.append(f"{nombre} debe estar entre 0 y 1")
        if self.dias_hasta_clustering < 1 or self.dias_entre_checkpoints < 1:
            errores.append("Los intervalos en días deben ser al menos 1")
        for var, valor in self.ajustes.items():
            p = _FINOS.get(var)
            if p is None:
                errores.append(f"Ajuste desconocido: {var}")
            elif not p[5] <= float(valor) <= p[6]:
                errores.append(f"{p[2]} debe estar entre {p[5]} y {p[6]}")
        return errores

    # ── Traducción al motor ──────────────────────────────────────────────────

    def entorno(self) -> dict[str, str]:
        """Variables de entorno que el motor lee al importarse."""
        b = lambda v: "1" if v else "0"  # noqa: E731
        return {
            "EDEN_MODE": self.escenario,
            "NARRATIVE_ENABLED": "true" if self.narrativa else "false",
            "OLLAMA_MODEL": self.modelo_ollama or "llama3.2",
            "INTERPRETIVE_FILTER_ENABLED": b(self.filtro_interpretativo),
            "COMM_REINTERPRETATION_ENABLED": b(self.reinterpretacion_receptor),
            "MENTAL_VAULT_ENABLED": b(self.boveda_mental),
            "ARCHETYPE_RECALIBRATION_ENABLED": b(self.recalibracion_arquetipica),
            "PROB_REPRO_DIARIA": repr(float(self.prob_repro_diaria)),
            "BOND_REPRO_MIN": repr(float(self.vinculo_min_repro)),
            "REPRO_NEEDS_MAX": repr(float(self.necesidades_max_repro)),
            "DAYS_UNTIL_CLUSTERING": str(int(self.dias_hasta_clustering)),
            "CHECKPOINT_INTERVAL": str(int(self.dias_entre_checkpoints)),
            **{var: (str(int(self.ajustes.get(var, p[4]))) if p[8]
                     else repr(float(self.ajustes.get(var, p[4]))))
               for var, p in _FINOS.items()},
            "PYTHONHASHSEED": "0",
            "PYTHONUNBUFFERED": "1",
            "PYTHONIOENCODING": "utf-8",
        }

    def dias_efectivos(self) -> int:
        return self.dias if self.dias > 0 else TOPE_EXTINCION_DIAS

    def resumen(self) -> str:
        """Descripción corta legible para la lista de corridas."""
        dur = f"{self.dias} días" if self.dias > 0 else "hasta la extinción"
        return f"{ESCENARIOS.get(self.escenario, self.escenario)} · {self.poblacion} · semilla {self.semilla} · {dur}"

    @classmethod
    def desde_dict(cls, d: dict) -> "CorridaConfig":
        validos = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in validos})


# ── Carpetas ──────────────────────────────────────────────────────────────────

def directorio_datos() -> Path:
    """Carpeta escribible del usuario.

    En desarrollo es `data/` del repo. Empaquetado (PyInstaller) la carpeta del
    programa puede no ser escribible (Archivos de programa), así que se usa
    Documentos/PsycheSimulacra. PSYCHE_DATOS_DIR la fija explícitamente.
    """
    base = os.environ.get("PSYCHE_DATOS_DIR")
    if base:
        d = Path(base)
    elif getattr(sys, "frozen", False):
        d = _carpeta_documentos() / "PsycheSimulacra"
    else:
        d = ROOT / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _carpeta_documentos() -> Path:
    """Documentos del usuario (en Windows, la real aunque OneDrive la haya movido)."""
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class _GUID(ctypes.Structure):
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                            ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

            # FOLDERID_Documents {FDD39AD0-238F-46AF-ADB4-6C85480369C7}
            guid = _GUID(0xFDD39AD0, 0x238F, 0x46AF,
                         (ctypes.c_ubyte * 8)(0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7))
            ruta = ctypes.c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None,
                                                          ctypes.byref(ruta)) == 0:
                try:
                    return Path(ruta.value)
                finally:
                    ctypes.windll.ole32.CoTaskMemFree(ruta)
        except Exception as e:
            print(f"[corridas] no se pudo ubicar Documentos: {e}", file=sys.stderr)
    docs = Path.home() / "Documents"
    return docs if docs.is_dir() else Path.home()


def directorio_corridas() -> Path:
    """Dónde viven las corridas. PSYCHE_CORRIDAS_DIR lo cambia."""
    base = os.environ.get("PSYCHE_CORRIDAS_DIR")
    d = Path(base) if base else directorio_datos() / "corridas"
    d.mkdir(parents=True, exist_ok=True)
    return d


def directorio_poblaciones_usuario() -> Path:
    """Poblaciones generadas desde el panel (las de fábrica están en data/seeds)."""
    d = directorio_datos() / "poblaciones"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ruta_poblacion(nombre: str) -> Path | None:
    """Resuelve el archivo de una población: primero las de fábrica, después las del usuario."""
    for base in (ROOT / "data" / "seeds", directorio_poblaciones_usuario()):
        p = base / nombre
        if p.is_file():
            return p
    return None


def listar_poblaciones() -> dict[str, Path]:
    """Nombre de archivo → ruta, de fábrica y generadas por el usuario."""
    out: dict[str, Path] = {}
    for base in (ROOT / "data" / "seeds", directorio_poblaciones_usuario()):
        for f in sorted(base.glob("*.yaml")):
            if not f.name.startswith("_"):
                out.setdefault(f.name, f)
    return out


def contar_personas(path: Path) -> int:
    try:
        return sum(1 for linea in path.read_text(encoding="utf-8").splitlines()
                   if linea.lstrip().startswith(("- id:", "- nombre:")))
    except OSError as e:
        print(f"[corridas] no se pudo leer la población {path}: {e}", file=sys.stderr)
        return 0


def generar_poblacion(n: int, semilla: int) -> Path:
    """Genera una población nueva de n personas (diversidad arquetípica amplia)."""
    import importlib.util
    if n < 2:
        raise ValueError("La población necesita al menos 2 personas")
    spec = importlib.util.spec_from_file_location(
        "generate_personas", ROOT / "scripts" / "generate_personas.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    out = directorio_poblaciones_usuario() / f"generada_{n}p_s{semilla}.yaml"
    mod.escribir_poblacion(n=n, seed=semilla, out=out)
    return out


def _slug(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[áàä]", "a", texto)
    texto = re.sub(r"[éèë]", "e", texto)
    texto = re.sub(r"[íìï]", "i", texto)
    texto = re.sub(r"[óòö]", "o", texto)
    texto = re.sub(r"[úùü]", "u", texto)
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto[:40] or "corrida"


def crear_corrida(cfg: CorridaConfig, base: Path | None = None,
                  ahora: datetime | None = None) -> Path:
    """Crea la carpeta de una corrida nueva con su config.json y estado inicial."""
    errores = cfg.validar()
    if errores:
        raise ValueError("; ".join(errores))
    base = base or directorio_corridas()
    ahora = ahora or datetime.now()
    if not cfg.nombre:
        cfg.nombre = f"{ESCENARIOS[cfg.escenario]} · semilla {cfg.semilla}"
    nombre_dir = f"{ahora:%Y-%m-%d_%H%M%S}_{cfg.escenario}_s{cfg.semilla}_{_slug(cfg.nombre)}"
    d = base / nombre_dir
    n = 2
    while d.exists():
        d = base / f"{nombre_dir}-{n}"
        n += 1
    d.mkdir(parents=True)
    escribir_json(d / ARCHIVO_CONFIG, {"creada": ahora.isoformat(timespec="seconds"),
                                       **asdict(cfg)})
    escribir_estado(d, fase="en_cola")
    return d


def leer_config(d: Path) -> CorridaConfig:
    return CorridaConfig.desde_dict(leer_json(d / ARCHIVO_CONFIG) or {})


def listar_corridas(base: Path | None = None) -> list[Path]:
    """Carpetas de corridas, de la más nueva a la más vieja."""
    base = base or directorio_corridas()
    return sorted((p for p in base.iterdir() if (p / ARCHIVO_CONFIG).is_file()),
                  key=lambda p: p.name, reverse=True)


def eliminar_corrida(d: Path) -> None:
    """Borra la carpeta de una corrida. Solo si NO está activa."""
    est = leer_estado(d)
    if est.get("fase") in FASES_ACTIVAS:
        raise RuntimeError("No se puede borrar una corrida en curso: detenela primero")
    shutil.rmtree(d)


def pedir_detencion(d: Path) -> None:
    (d / ARCHIVO_DETENER).write_text("detener\n", encoding="utf-8")


def detencion_pedida(d: Path) -> bool:
    return (d / ARCHIVO_DETENER).exists()


# ── Estado ────────────────────────────────────────────────────────────────────

def escribir_json(path: Path, data: dict) -> None:
    """Escritura atómica (tmp + replace): quien lee nunca ve un JSON a medias."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    os.replace(tmp, path)


def leer_json(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as e:
        print(f"[corridas] no se pudo leer {path}: {e}", file=sys.stderr)
        return None


def escribir_estado(d: Path, **campos) -> dict:
    """Mezcla `campos` sobre el estado actual y lo guarda."""
    est = leer_json(d / ARCHIVO_ESTADO) or {}
    est.update(campos)
    est["actualizado"] = datetime.now().isoformat(timespec="seconds")
    escribir_json(d / ARCHIVO_ESTADO, est)
    return est


def leer_estado(d: Path) -> dict:
    return leer_json(d / ARCHIVO_ESTADO) or {"fase": "desconocida"}


def serie_csv(d: Path) -> Path:
    """Serie diaria de métricas de emergencia de la corrida."""
    return d / "data" / "metrics" / "emergence_series.csv"


def leer_serie(d: Path, columnas: tuple[str, ...] = ("dia", "n_alive", "n_tribes")) -> dict[str, list[float]]:
    """Lee columnas de la serie diaria. Tolera archivo ausente o a medio escribir."""
    import csv
    out: dict[str, list[float]] = {c: [] for c in columnas}
    p = serie_csv(d)
    if not p.is_file():
        return out
    try:
        with open(p, encoding="utf-8", newline="") as f:
            for fila in csv.DictReader(f):
                try:
                    vals = [float(fila[c]) for c in columnas]
                except (KeyError, TypeError, ValueError):
                    continue
                for c, v in zip(columnas, vals):
                    out[c].append(v)
    except OSError as e:
        print(f"[corridas] no se pudo leer la serie de {d.name}: {e}", file=sys.stderr)
    return out


def comando_corrida(d: Path, ver: bool = False) -> list[str]:
    """Comando para lanzar el proceso de una corrida o su visor (sirve empaquetado)."""
    modo = "--ver" if ver else "--corrida"
    if getattr(sys, "frozen", False):
        return [sys.executable, modo, str(d)]
    return [sys.executable, str(ROOT / "main.py"), modo, str(d)]
