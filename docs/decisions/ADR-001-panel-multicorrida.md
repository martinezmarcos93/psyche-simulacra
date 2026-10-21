# ADR-001 — Panel multicorrida: un proceso y una carpeta por corrida

- **Fecha:** 2026-10-21
- **Estado:** propuesta (PR `feature/gui-multicorrida`, esperando revisión de Marcos)
- **Contexto de uso:** el experimento se presta a un sociólogo que lo va a usar en Windows,
  sin tocar código.

## Contexto

La GUI anterior (NiceGUI, `ui/psyche_ui.py`) corría **una** simulación dentro del
mismo proceso de la interfaz:

1. Todos los mecanismos del motor (`EDEN_ENABLED`, `INTERPRETIVE_FILTER_ENABLED`,
   `PROB_REPRO_DIARIA`, …) se leen de variables de entorno **al importar los
   módulos**. Dos simulaciones en un mismo proceso no pueden tener configuraciones
   distintas, y cambiar la configuración exige reiniciar.
2. Había una única BD (`data/db/simulation.db`), una carpeta de checkpoints y un
   vault: **"Nueva simulación" borraba la anterior** sin archivarla
   (`archive_simulation()` en `main.py` había quedado sin llamar desde el
   rediseño `3bdbc15`).
3. Varias simulaciones como hilos de un mismo proceso Python compiten por un solo
   núcleo (GIL).
4. EDEN solo se podía correr desde `scripts/run_eden_experiment.py`; el "control"
   (Nomos sin Serpiente) no existía fuera de ese script.

Se pidió: lanzar una o más simulaciones con todas las configuraciones posibles,
ver en vivo la que se elija mientras las demás corren por detrás y poder sacar
datos de todas.

## Decisión

- **Cada corrida es un proceso y una carpeta.** `core/runtime/corridas.py` define
  `CorridaConfig` (todo lo configurable), la traduce a variables de entorno y crea
  `data/corridas/<fecha>_<escenario>_s<semilla>_<nombre>/` con `config.json` y
  `estado.json`. El proceso (`main.py --corrida <carpeta>`, en
  `ui/corrida_worker.py`) fija el entorno **antes** de importar el motor, hace
  `chdir` a su carpeta (el motor resuelve todas sus rutas relativas a la carpeta
  actual, así que BD, checkpoints, métricas y vault quedan aislados sin tocar el
  motor) y sirve su propio monitor NiceGUI en un puerto libre.
- **El panel (`ui/hub.py`) no simula:** arma tandas (escenarios × réplicas),
  respeta un máximo de corridas simultáneas (cola), lee `estado.json` de cada
  carpeta, enlaza al monitor de la que se elija y compara series.
  Comunicación panel ↔ corrida solo por archivos (`estado.json`, `detener.flag`):
  funciona igual en Windows y Linux, sobrevive a reinicios del panel y no agrega
  dependencias.
- **El monitor existente se reutiliza** casi sin cambios (`build_monitor_page`
  recibe `hub_url`, `titulo` y `on_detener`). Ver en vivo "la que se elija" es
  abrir el puerto de esa corrida; el monitor solo trabaja cuando alguien lo mira.
- **Visor de estado final** (`main.py --ver`): reanuda desde una copia temporal
  del último checkpoint, con BD y vault descartables, sin correr el reloj
  (`WorldCore.refresh_snapshot`). No escribe nada en la carpeta de la corrida
  (cubierto por test).
- **EDEN con tres modos** (`EDEN_MODE=off|orden|eden`; `EDEN_ENABLED=1` queda
  como alias de `eden`).
- **Un único ejecutable**: `main.py` despacha panel / `--corrida` / `--ver` /
  `--liminal-server`, así PyInstaller produce un solo `.exe` que se relanza a sí
  mismo. Para eso `liminal_server` pasó a usar imports relativos (su paquete
  `core` chocaba con el del motor dentro del ejecutable); `python
  liminal_server/main.py` sigue funcionando.
- **Empaquetado sin datos dentro del programa**: empaquetado, corridas y
  poblaciones generadas van a `Documentos/PsycheSimulacra` (la carpeta del
  programa puede no ser escribible).

## Alternativas descartadas

- **Varias simulaciones como hilos en el proceso de la GUI:** imposible con flags
  leídos al importar, y una sola CPU efectiva.
- **Reescribir el monitor para leer de archivos/BD y mostrar cualquier corrida
  desde el panel:** mucho más trabajo (3 000 líneas de monitor ligadas a objetos
  vivos) y más carga; no hacía falta para "ver una en vivo, elegible".
- **Convertir los flags del motor en parámetros por instancia:** cambio grande y
  transversal al motor (decenas de módulos); el aislamiento por proceso da lo
  mismo sin tocarlo.

## Consecuencias

- Una corrida nueva nunca borra otra. Borrar es explícito y pide confirmación.
- Cada corrida guarda en `config.json` exactamente qué se usó: reproducible y
  citable.
- El costo es memoria: cada corrida activa es un proceso Python con NiceGUI
  (~150–250 MB). El límite de simultáneas (por defecto, núcleos − 1) lo acota.
- La GUI vieja (`build_launcher_page`, `_start_sim`, `launch_ui`) se eliminó; el
  botón "Cerrar" que mataba **todos** los procesos `ollama` del sistema se
  reemplazó por "Detener corrida", que solo detiene esa corrida.
- El build de Windows se verificó en Linux (mismo `.spec`): el ejecutable
  empaquetado lanza el panel, corridas, visor, generador de poblaciones y servidor
  liminal. **Falta probarlo en un Windows real.**
