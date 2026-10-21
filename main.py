#!/usr/bin/env python3
"""main.py — Llave maestra de PSYCHE SIMULACRA.

    python main.py                       → panel de corridas (navegador, puerto 8080)
    python main.py --corrida <carpeta>   → proceso de UNA corrida (lo lanza el panel)
    python main.py --ver <carpeta>       → visor del estado final de una corrida terminada
    python main.py --liminal-server ...  → servidor de la Zona Liminal (lo lanza el panel)

Un único punto de entrada para que funcione igual empaquetado (PyInstaller):
el ejecutable se relanza a sí mismo con estos argumentos.
"""

import sys
from pathlib import Path

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))

# Empaquetado sin consola (PyInstaller --windowed) stdout/stderr son None y
# NiceGUI/uvicorn fallan al escribir: se redirigen a un log en la carpeta de datos.
if sys.stdout is None or sys.stderr is None:
    from core.runtime.corridas import directorio_datos
    _log = open(directorio_datos() / "psyche.log", "a", encoding="utf-8", buffering=1)
    sys.stdout = sys.stdout or _log
    sys.stderr = sys.stderr or _log

# Windows: la consola por defecto usa cp1252 y no puede imprimir el emoji
# narrativo que loguean algunos subsistemas (objetos sagrados, deidades).
for _stream in (sys.stdout, sys.stderr):
    if getattr(_stream, "encoding", None) and _stream.encoding.lower() != "utf-8" \
            and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv[:1] in (["--corrida"], ["--ver"]):
        if len(argv) < 2:
            sys.exit(f"Uso: main.py {argv[0]} <carpeta>")
        from ui.corrida_worker import ejecutar
        ejecutar(argv[1], ver=(argv[0] == "--ver"))
        return

    if argv[:1] == ["--liminal-server"]:
        from liminal_server.main import main as servidor_liminal
        sys.argv = ["liminal_server", *argv[1:]]
        servidor_liminal()
        return

    from ui.hub import lanzar_panel
    lanzar_panel()


if __name__ in {"__main__", "__mp_main__"}:
    main()
