# Experimento EDEN — libre albedrío tras el retiro del orden providencial

**Fecha:** 2026-10-20
**Commit base:** `30ec495` (rama `experiment/eden-libre-albedrio`)
**Roadmap:** sesión de especulación 2026-10-20 (ver `docs/handoffs/` si se escribió
handoff de cierre) — no hay roadmap previo en `src/`, es un experimento nuevo.

---

> **Actualización 2026-10-21:** EDEN entró a `main` junto con el panel
> multicorrida (ADR-001). Los tres escenarios se eligen con `EDEN_MODE=off|orden|eden`
> (`EDEN_ENABLED=1` = `eden`) o desde el panel (*Mundo libre / Orden permanente / Edén*),
> que permite correr las réplicas pareadas por semilla sin scripts. En el panel, la
> semilla 2 del piloto de 10 agentes reproduce el switch del día 66 (`brennus`).
> Corrida a escala del 2026-10-20 (100 agentes hasta extinción, semilla 1):
> `simulacion/_reportes/2026-10-20-eden-100-extincion/`.

## Premisa

Lectura del mito cristiano de la prueba: Dios crea, ordena y sostiene a los
humanos; el cuerpo y sus deseos ya están presentes desde el principio; la
prueba es ver si, teniendo cuerpo, se sigue obedeciendo cuando la ley deja de
imponerse. Trasladado a PSYCHE SIMULACRA: una fuerza providencial (`Nomos`)
organiza, provee y pacifica una sociedad de agentes psicológicamente completos
(ya tienen complejos, sombra, rasgos clínicos, necesidades biológicas — "el
cuerpo" no hay que diseñarlo, ya existe). Un interruptor retira esa fuerza de
forma abrupta y total. La pregunta no es narrativa, es medible: ¿la sociedad
que queda se parece a la que había, o se reorganiza?

## Hipótesis

1. **Anomia, no libertad instantánea**: tras el switch, `CollectiveField.confusion`
   y `emotional_pressure` suben antes de estabilizarse — la pérdida de orden
   desorganiza antes de que (si acaso) un orden nuevo emerja.
2. **La cohesión tribal explicada por Nomos era parcialmente impuesta**: IMI/MIG
   deberían caer o, al menos, dejar de crecer al mismo ritmo tras el switch —
   si la pertenencia tribal seguía explicando igual la psicología individual
   sin el refuerzo providencial, la cohesión era genuina, no solo forzada.
3. **Los agentes "en tensión" (ver `Nomos.en_armonia`) se desvían primero y más
   fuerte** que los "en armonía" — el conflicto latente entre vocación impuesta
   y arquetipo real predice quién rompe antes el patrón de conducta previo.
4. **El acto de ruptura puede generar mito sobre sí mismo**: si el
   `MythologyEngine` cristaliza un `mito_moral` o `escatología` anclado
   temporalmente cerca del día del switch, es la prueba más fuerte de que el
   sistema no solo reacciona — narra su propia pérdida de orden sin que nadie
   lo haya escrito.
5. **La cooperación bajo Nomos no era puramente genuina**: si `bond_strength`
   medio cae tras el switch más de lo explicable por mortalidad/azar, parte de
   la cohesión social previa dependía del canal de vocación, no solo de la
   psique nativa de cada agente.

## Variables

- **Independiente**: condición — `control` (Nomos activo todo el run, sin
  Serpiente, el orden nunca se rompe) / `tratamiento` (Nomos + Serpiente, el
  switch dispara cuando emerja — día variable, no fijo).
- **Dependientes** (todas ya instrumentadas, `core/metrics/emergence.py`):
  `kl_mean`, `mig`, `imi` (divergencia/cohesión arquetípica tribal),
  `vfe_global` (proxy de incertidumbre del inconsciente colectivo),
  `behavioral_kl_mean`, `behavioral_intra_tribe_dispersion` (divergencia e
  idiosincrasia conductual), `field_kl_mean` (divergencia de campos locales),
  `n_tribes`, `n_alive`. Más el evento mismo: `eden_event` (día, agente,
  acción de desafío, vocación, si estaba en armonía o en tensión, snapshot
  arquetípico completo).
- **Controles**: mismo `seed_file` + `seed` entre `control` y `tratamiento` de
  una misma réplica (mismo mundo, misma población inicial — la única
  diferencia es si la Serpiente existe). `Nomos(seed=seed+100)` y
  `Serpiente(seed=seed+101)` derivados del seed de la réplica, reproducibles.

## Método

- **Arnés**: `scripts/run_eden_experiment.py`, modo headless (clock + WorldCore
  + AgentCore desnudos, sin BD/narrativa/Obsidian/UI — mismo criterio que
  `ab_interpretive.py`/`run_robustness.py`, ver `docs/ARCHITECTURE.md` §6).
- **Análisis**: ventana de `_VENTANA_DIAS = 60` días anclada al evento (no al
  calendario) — el switch no cae en un día fijo, depende de cuándo la
  Serpiente encuentra y tienta a un agente elegible y ese agente resuelve
  desafío en su propio colapso. Para `control` no hay evento: se reporta el
  run completo como baseline sin ventana "post".
- **Escalas, en dos pasadas** (acordado con Marcos 2026-10-20):
  - **Piloto**: `data/seeds/eden_pilot_10.yaml` (10 agentes, seed=42),
    varias semillas de réplica, para calibrar si los umbrales de elegibilidad
    (`_REBELDE_MIN`/`_TRICKSTER_MIN`/`_INDIVIDUACION_MIN` en `serpent.py`,
    `_TENTACION_UMBRAL`) dejan pasar un switch en un horizonte razonable de
    días, o si hay que recalibrarlos.
  - **Confirmatoria**: `data/seeds/100_personas.yaml`, N réplicas vía el mismo
    arnés (o adaptando `run_robustness.py`), para ver si el patrón del piloto
    aguanta a escala y con más diversidad psicológica inicial.
- **Dónde corre**: ambas pasadas se dejan para la PC personal de Marcos — esta
  máquina (equipo de oficina) resultó demasiado lenta incluso para la suite de
  tests completa (~20 min para 480 tests). El smoke test de este commit (1
  semilla, 5 días, 10 agentes) sí corrió acá solo para verificar que el arnés
  no tiene errores de plomería.

## Resultados

**Preliminar (1 réplica de 2, piloto n=10)** — corrida real vía
`run_eden_experiment.py`, `data/seeds/eden_pilot_10.yaml`, 90 días, semillas
1 y 2 (control + tratamiento c/u → 4 corridas). Salida en
`data/experiments/eden_pilot_v1/` (local, no versionada — ver `.gitignore`).
Confirmatoria (n=100) todavía PENDIENTE.

- **Semilla 1**: el switch no disparó en 90 días (ni camino rebelde/trickster
  ni individuado cruzaron umbral en esta corrida).
- **Semilla 2**: el switch disparó el **día 66**, agente `brennus`, acción de
  desafío `aislamiento`, vocación `mediador` (en tensión). Importante: no fue
  por el camino rebelde/trickster (quedaron bajos: 0.18/0.26) sino por el
  **camino individuado** — `self=0.98` y `sombra=1.00` convergieron a casi el
  mismo valor (tensión mínima), lo que `individuacion_index()` lee como
  integración alta (Self que absorbió a la Sombra en vez de reprimirla, no
  "ausencia de sombra"). Esos valores NO estaban en el YAML inicial — son el
  resultado de ~66 días de vida simulada (trauma/aislamiento empujando self y
  sombra, ver `_TRANSFORMATIONS` en `archetypes.py`). Esto confirma que el
  mecanismo dispara con psicologías nacidas normales, sin necesitar un perfil
  extremo desde el día 0 (a diferencia del ejemplo forzado usado para
  verificar el circuito en `tests/test_eden_integration.py`).

**Corrección a una nota interna previa**: un chequeo rápido sobre los
arquetipos *del día 0* de `eden_pilot_10.yaml` y de `100_personas.yaml` no
encontró ningún agente elegible (máximo individuación observado: 0.50 contra
el umbral de 0.70). Esa nota era correcta sobre el día 0 pero incompleta: no
tiene en cuenta que los arquetipos derivan con la vida simulada. El resultado
de la semilla 2 arriba muestra que la deriva sí puede cruzar el umbral sin
ayuda. Sigue siendo una observación de n=1 corrida exitosa sobre 2 — no
alcanza para saber con qué frecuencia pasa esto a 90 días, ni si el camino
rebelde/trickster alguna vez dispara en una población generada
proceduralmente (en las corridas vistas hasta ahora, nunca fue ese camino).

Lo que sigue sin alcanzar (igual que antes): más réplicas del piloto para
estimar la tasa de disparo, y la confirmatoria a n=100.

Mientras tanto, lo que SÍ está verificado (ver
`tests/test_eden_integration.py`): con un agente forzado a perfil
rebelde/trickster extremo, el circuito completo (vocación asignada → Serpiente
tienta → colapso nativo del agente resuelve desafío → switch dispara → Nomos
se apaga global y abruptamente → el evento queda registrado) corre de punta a
punta en una población de juguete (5 agentes, 30 días). Eso confirma que el
*mecanismo* funciona; no dice nada todavía sobre si el *patrón* (anomia,
desviación diferencial, mitologización del evento) aparece con psicologías
generadas al azar en vez de forzadas a mano.

## Próximos pasos

1. Ampliar el piloto a más semillas (≥10, no solo 1 y 2) sobre
   `eden_pilot_10.yaml` para estimar la tasa de disparo real — con 2 semillas
   ya se vio 1 de 2, insuficiente para saber si es ~50% o una casualidad.
   Si la tasa queda muy baja incluso con más semillas, recalibrar
   `_PROB_CONTACTO_DIARIO`/umbrales de elegibilidad en `serpent.py` (en
   particular revisar si el camino rebelde/trickster es alcanzable alguna vez
   por deriva natural, dado que en las corridas vistas hasta ahora solo
   disparó el camino individuado).
2. Con el piloto calibrado, correr la confirmatoria sobre `100_personas.yaml`.
3. Completar la sección de Resultados con los datos agregados (no solo la
   primera réplica exitosa).
4. Decidir con Marcos si algo de esto se generaliza al tronco principal del
   proyecto o queda archivado como experimento de rama.
