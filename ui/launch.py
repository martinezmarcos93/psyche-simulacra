#!/usr/bin/env python3
"""ui/launch.py — Atajo al panel de corridas (equivalente a `python main.py`)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    from ui.hub import lanzar_panel
    lanzar_panel()


if __name__ == "__main__":
    main()
