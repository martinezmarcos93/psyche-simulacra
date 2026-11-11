# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller — PSYCHE SIMULACRA (carpeta con .exe, sin consola).

    pyinstaller packaging/psyche.spec --noconfirm

El mismo ejecutable cumple tres papeles según sus argumentos (ver main.py):
panel de corridas, proceso de una corrida (--corrida) y visor (--ver), además
del servidor de la Zona Liminal (--liminal-server).
"""
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent  # noqa: F821 (SPECPATH lo define PyInstaller)

datas = [
    (str(ROOT / "data" / "seeds"), "data/seeds"),
    # Se carga por ruta desde el panel ("Generar una población nueva")
    (str(ROOT / "scripts" / "generate_personas.py"), "scripts"),
    # La muestra el panel en /guia
    (str(ROOT / "docs" / "GUIA_DE_USO.md"), "docs"),
    # Ilustraciones del panel (se sirven en /assets)
    (str(ROOT / "assets"), "assets"),
]
datas += collect_data_files("nicegui")
datas += collect_data_files("plotly")

hiddenimports = []
for paquete in ("core", "persistence", "obsidian", "ui", "liminal_server", "config",
                "aiohttp", "websockets", "uvicorn", "nicegui"):
    hiddenimports += collect_submodules(paquete)
hiddenimports += ["yaml", "networkx", "scipy", "numpy", "mesa", "loguru"]

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["pygame", "streamlit", "matplotlib", "pandas", "pytest", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PsycheSimulacra",
    console=False,          # sin ventana de consola; la salida va a psyche.log
    icon=str(ROOT / "packaging" / "psyche.ico") if (ROOT / "packaging" / "psyche.ico").exists() else None,
)
coll = COLLECT(exe, a.binaries, a.datas, name="PsycheSimulacra")
