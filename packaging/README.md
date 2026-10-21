# Empaquetado para Windows

Produce `dist/instalador/PsycheSimulacra-Setup-<versión>.exe`: instalador por
usuario (no pide administrador) con acceso directo en el escritorio y en el menú
Inicio.

## Construir (en una PC con Windows)

Requisitos: Python 3.11 o 3.12 en el PATH e [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```bat
packaging\build.bat
```

El script crea `.venv-build`, instala `requirements.txt` + `requirements-build.txt`
(PyInstaller), arma `dist\PsycheSimulacra\` y compila el instalador.

## Qué hace el ejecutable

`PsycheSimulacra.exe` es el mismo programa en cuatro papeles (ver `main.py`):

| Argumentos | Papel |
|---|---|
| (ninguno) | Panel de corridas; abre el navegador en `http://127.0.0.1:8080` |
| `--corrida <carpeta>` | Una corrida (la lanza el panel) |
| `--ver <carpeta>` | Visor del estado final (lo lanza el panel) |
| `--liminal-server …` | Servidor de la Zona Liminal (lo lanza el panel) |

Sin consola: la salida va a `Documentos\PsycheSimulacra\psyche.log` y la de cada
corrida a su `corrida.log`.

## Datos del usuario

`Documentos\PsycheSimulacra\` (se puede cambiar con la variable `PSYCHE_DATOS_DIR`):

- `corridas\` — una carpeta por corrida.
- `poblaciones\` — poblaciones generadas desde el panel.

Desinstalar **no** borra esta carpeta.

## Narrativa con IA (opcional)

Requiere [Ollama](https://ollama.com) instalado aparte. La primera corrida con
narrativa descarga el modelo (`llama3.2`, varios GB). El panel detecta si Ollama
está instalado y, si no, deshabilita la opción. Todo lo demás funciona sin Ollama.

## Verificado / pendiente

- Verificado (2026-10-21) construyendo con el mismo `.spec` en Linux: el
  ejecutable levanta el panel, lanza corridas en paralelo, el visor de estado
  final, genera poblaciones y levanta el servidor liminal.
- **Pendiente: probar el instalador en un Windows real** (rutas, `CREATE_NO_WINDOW`,
  antivirus/SmartScreen con un ejecutable sin firmar, Documentos redirigido a OneDrive).
- Sin ícono propio: si existe `packaging/psyche.ico` se usa.
