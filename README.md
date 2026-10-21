# PSYCHE SIMULACRA

Laboratorio computacional de emergencia del inconsciente colectivo.

Un sistema ABM (Agent-Based Model) donde 100 individuos psicológicamente complejos interactúan en un mundo físico real, generando jerarquías, tribus, símbolos, tabúes, mitos, estructuras culturales y leyendas sin que ninguno de estos fenómenos esté programado directamente.

**El inconsciente colectivo emerge — no se construye.**

---

## Concepto

Cada agente carga un vector arquetípico jungiano (12 arquetipos), rasgos dimensionales (Big Five + clínico), complejos activables, memoria episódica, sueños y vínculos sociales. Sus interacciones alimentan campos colectivos que acumulan carga simbólica. Cuando esa carga supera umbrales, cristaliza en proto-mitos con efectos conductuales reales. Las tribus que emergen desarrollan culturas materiales distintas y divergen psicológicamente a lo largo del tiempo.

El experimento busca responder:
- ¿Cuándo emerge el primer mito?
- ¿El tabú del incesto aparece antes o después del primer mito?
- ¿El héroe emerge del poder o de la narrativa?
- ¿La cooperación o la jerarquía aparece primero?
- ¿Cuánto tarda una tribu en desarrollar una identidad arquetípica diferenciable de otra?
- ¿Qué pasa con una sociedad cuando el orden que la sostenía se retira de golpe? (experimento EDEN)

---

## Arquitectura

```
[ Obsidian Vault ] <──> [ Motor Python ] <──> [ Panel NiceGUI (navegador) ]
  Perfiles vivos          ABM tick-based         Tandas de corridas en paralelo
  Red simbólica           Lógica psico-social    Monitor en vivo de la elegida
  Narrativa emergente     Mecánicas cuánticas    Visor de estado final
  Leyendas tribales       Tribus + Mitología     Comparación entre corridas
```

```
            Panel de corridas (python main.py, puerto 8080)
                 │  lanza procesos · lee estado.json · pide detener.flag
     ┌───────────┼──────────────────────────┐
     ▼           ▼                          ▼
 [Corrida 1]  [Corrida 2]   …          [Corrida N]
 proceso propio, carpeta propia (data/corridas/…): config.json, estado.json,
 BD SQLite, checkpoints, métricas, vault — y su propio monitor en vivo
```

```
[ Simulación A ]──┐                       ┌──[ Simulación B ]
  PSYCHE SIMULACRA│   WebSocket (ws://)   │  PSYCHE SIMULACRA
  + LiminalClient ├──> LIMINAL ZONE <─────┤  + LiminalClient
  + Portal Hex    │    Servidor central   │  + Portal Hex
                  └───────────────────────┘
```

### Dos núcleos sincrónicos + capa liminal (opcional)

```
SimulationClock (tick = 1 hora simulada)
        │
        ├─── priority=10 ──> WorldCore              (mundo físico)
        │                    Clima, terreno hexagonal, fauna, recursos, fuego
        │
        ├─── priority=20 ──> AgentCore              (agentes)
        │                    Psicología, decisiones cuánticas, interacciones
        │                    Tribus, cultura material, narrativa LLM
        │
        └─── priority=25 ──> AgentTransferHandler   (Zona Liminal, opcional)
                             Portal hex, cliente WebSocket, tránsito intersimulación
```

**Ciclo de un día simulado (24 ticks):**
1. `WorldCore` actualiza clima, recursos, fauna → produce `WorldSnapshot`
2. `AgentCore` lee el snapshot → cada agente colapsa estado cuántico → interacciones zonales
3. `AgentTransferHandler` (si activo) detecta agentes en el portal → los envía al servidor liminal
4. Al final del día: clustering tribal, construcción de estructuras, síntesis narrativa
5. Persistencia a SQLite + checkpoints JSON + vault Obsidian

### Cuatro capas del agente

| Capa | Contenido |
|------|-----------|
| Biológica | hambre, fatiga, sed, salud, edad, reproducción |
| Psicológica | 12 arquetipos jungianos, 6 complejos, Big Five + 9 rasgos clínicos, sueños, memoria episódica |
| Social | vínculos (grafo NetworkX), rol, deudas simbólicas, tribu |
| Simbólica | carga de campo colectivo, proto-símbolos, herencia cultural |

---

## Sistemas implementados

### Mundo físico
- **TerrainGrid** — grilla hexagonal 80×60 con 12 biomas (bosque, pradera, río, montaña, sabana, pantano, cueva, valle fértil, costa, desierto, colinas, lago)
- **ClimateSystem** — temperatura, precipitación, luminosidad, viento, eventos climáticos estacionales
- **ResourceSystem** — recursos por hex con regeneración estacional
- **FaunaSystem** — densidad con comportamiento estacional
- **FireSystem** — propagación, decaimiento, efecto del clima

### Psicología de agentes
- **ArchetypeVector** — 12 pesos jungianos independientes (0→1): self, persona, sombra, anima/animus, héroe, sabio, trickster, madre, padre, niño divino, gobernante, rebelde
- **ComplexProfile** — 6 complejos activables por umbral contextual: inferioridad, abandono, poder, culpa, materno, trascendencia
- **TraitProfile** — Big Five + 9 dimensiones clínicas (ansiedad, impulsividad, disociación, empatía, paranoia, narcisismo, agresividad, etc.)
- **DreamGrammarEngine** — pool composicional de 5 capas (bioma × arquetipo × complejo × trauma × resonancia grupal); sueños únicos por agente; entrelazamiento nocturno entre pares con bond alto o `entangled=True`
- **LindBladChannel** — canal de decoherencia arquetípica T1/T2: relajación (decay al baseline) + represión activa (bias suprimido cuando el arquetipo supera el umbral)

### Mecánica cuántica de decisión
- **BehavioralSuperposition** — vector de probabilidades conductuales (cooperar, competir, aislar, manipular)
- **CollapseEngine** — colapso modulado por arquetipos, complejos, campo colectivo y entrelazamiento social

### Sistemas sociales
- **SocialNetwork** — grafo NetworkX con `bond_strength` ∈ [-1, 1], entrelazamiento cuántico termodinámico
- **InteractionEngine** — encuentros zonales: cooperación pura, conflicto/explotación, choque violento, manipulación
- **CollectiveField** — inconsciente colectivo global: 12 símbolos jungianos, `emotional_pressure`, `myth_pressure` (trauma sin narrativa), `confusion` epistémica; `ContextoEnunciativo` (temperatura × intencionalidad + ruido) controla cuándo y cómo colapsa un proto-mito
- **MythologyEngine** — cristalización N-dimensional probabilística: `ProtoMito` (proto-estado) gana coherencia con cada transmisión social hasta cristalizar en `MythCrystal`. 5 tipos Campbell (cosmogonía/teogonía/antropogonía/escatología/mito_moral) mapeados desde 11 pares simbólicos. La transmisión social ocurre en 3 de los 6 desenlaces posibles de un encuentro (choque violento, conflicto/explotación, cooperación pura), con intensidad relativa por tipo (`_MYTH_TRANSMISSION_INTENSITY`, calibrable por variable de entorno — ver `docs/experiments/`). Cuando los protagonistas mueren el mito se convierte en `Leyenda` de intensidad decreciente (0.998/día) que irradia efectos sobre toda la tribu

### Ecuación Personal (percepción y cognición individual)
- **InterpretiveFilter** (`INTERPRETIVE_FILTER_ENABLED=1`) — cada agente filtra el estímulo físico a través de 4 operadores content-free (atención, causa, evaluación afectiva, comparación social) antes de que llegue al colapso conductual; produce un `PerceivedEvent` con `valence`/`arousal` subjetivos y, por préstamo de vocabulario ya cristalizado (nunca inventado), `narrative_frame`/`attributed_cause`/`moral_judgment`. Desactivado por defecto — el experimento A/B no encontró efecto medible de divergencia cultural a la escala probada (ver `docs/experiments/`)
- **MentalVault** (`MENTAL_VAULT_ENABLED=1`, requiere el filtro ON) — mini cerebro por agente: grafo de nodos con enlazado probabilístico y resonancia emergente, expone `worldview_coherence()`. Desactivado por defecto, misma razón que arriba
- **ArchetypeRecalibrator** (`ARCHETYPE_RECALIBRATION_ENABLED=1`, requiere el filtro ON) — las vivencias de cada agente recalibran su vector arquetípico: la resonancia de cada `PerceivedEvent` se acumula aparte del vector, decae si no se repite y solo se consolida si se sostiene; el dominante es estable (histéresis) y su cambio es un evento de "reorganización". Desactivado por defecto y **experimental**: todavía no está calibrado (en las pruebas la población termina en monocultivo de `sombra`). Diseño: `docs/proposals/2026-10-04-jpaf-ideas-aplicables.md`
- Detalle completo de los dos primeros: `docs/AGENT_BRAIN.md`, `docs/MENTAL_VAULT.md`, `docs/EMERGENCE.md`

### Experimento EDEN (orden providencial y libre albedrío)
Lectura del mito del Edén trasladada al modelo: una fuerza ordenadora organiza la sociedad y una figura tentadora puede romperla. Se elige con `EDEN_MODE` (o desde el panel):
- **`off` — Mundo libre** (default): sin fuerza ordenadora; comportamiento histórico del motor.
- **`orden` — Orden permanente**: **Nomos** (`core/social/nomos.py`) asigna a cada agente una de cuatro vocaciones (guardián, cuidador, artesano, mediador), sorteando por agente si queda *en armonía* con su arquetipo o *en tensión* con él; la vocación compite como un canal más en el colapso conductual (`NOMOS_WEIGHT`), nunca decide sola.
- **`eden` — Edén**: además, la **Serpiente** (`core/social/serpent.py`) visita a los agentes elegibles (rebelde **y** trickster ≥ 0,6, o índice de individuación ≥ 0,7 — en las corridas observadas siempre disparó por este segundo camino) y, si cruzan su umbral de tentación, empuja su colapso (`SERPENT_WEIGHT`). Si un agente tentado resuelve un acto de desafío (competencia, aislamiento, manipulación), **el Nomos se apaga para siempre y para todos**. El evento queda en `data/metrics/eden_event.json` (día, agente, acción, vocación, armonía y perfil arquetípico completo) y la métrica `nomos_active` marca el antes/después.
- Ficha del experimento y resultados: `docs/experiments/2026-10-20-eden-libre-albedrio.md`. Corrida A/B headless: `scripts/run_eden_experiment.py`.

### Tribus y divergencia cultural
- **TribeManager** — clustering via `greedy_modularity_communities` (NetworkX) cada 30 días
- **CollectiveField local** — cada tribu tiene su propio inconsciente colectivo (ICL)
- **MythologyEngine** — instancia única y global (no una por tribu, a diferencia del `CollectiveField`); cada `MythCrystal` queda etiquetado con `tribe_id` para atribución. Ver `docs/EMERGENCE.md` §5
- **Deriva por bioma** — 0.001/día de push hacia arquetipos del bioma habitado (12 biomas × afinidades)

### Cultura material
- **CultureEngine** — 4 tipos de estructuras con auras psicológicas:
  - **Tótem** — radio 2, impulsa gobernante, permanente
  - **Altar** — radio 2, reduce ansiedad, impulsa sabio/self, permanente
  - **Muralla** — radio 1, tensa a forasteros (+0.025 ansiedad), permanente
  - **Hoguera** — radio 3, mejora humor, impulsa madre, dura 30 días
- Triggers basados en complejos y arquetipos tribales dominantes
- Cooldown de 50 días entre construcciones por tribu

### Narrativa con LLM
- **OllamaDaemon** — auto-arranca `ollama serve` si el puerto 11434 no responde; verifica e instala el modelo configurado; invocado por `run_simulation.py`, `visualizer.py` y por cada corrida del panel que tenga la narrativa activada (en el panel viene apagada por defecto)
- **NarratorEngine** — daemon en background procesando cola de eventos narrativos
- 4 tipos de leyendas generadas con Ollama (llama3.2 u otro modelo local):
  - **Mito fundacional** — al formarse una nueva tribu
  - **Crónica** — cada 100 días por tribu
  - **Elegía** — por muertes con arquetipo dominante ≥ 0.70
  - **Profecía** — al cristalizar un nuevo mito
- Fallback con plantillas si Ollama no está disponible
- Deduplicación por archivo y por sesión; persistencia entre reinicios

### Métricas de emergencia científica
- **KL Divergencia** — divergencia psicológica entre culturas tribales (simétrica, pairwise)
- **VFE proxy** — entropía de Shannon del campo colectivo (incertidumbre del inconsciente)
- **IMI** — fracción de varianza arquetípica explicada por membresía tribal; R² estilo Jain-Dubes
- **MIG** — Mean Information Gain: I(z_k;v)/H(z_k) sobre 12 dimensiones arquetípicas; cuantifica cuánta información aporta la tribu sobre la psicología individual (Chen et al. 2018)
- **Tribus reales vs. aislados** — `n_tribes_multi` (tribus de ≥2 miembros) y `n_isolates` (agentes sin vínculos fuertes, que el clustering cuenta como tribu de uno); `behavioral_kl_multi_mean` controla ese sesgo
- **`reorganizations_total`** (recalibración) y **`nomos_active`** (EDEN)
- **Divergencia conductual/de campo (inter-tribu) e idiosincrasia (intra-tribu)** — `behavioral_kl_mean`/`field_kl_mean` miden qué tan distinto actúan y sienten las tribus entre sí; `behavioral_intra_tribe_dispersion` mide la variación de conducta dentro de cada tribu — instrumento pensado para la Ecuación Personal (ver `docs/experiments/`)
- Exportación automática a `data/metrics/emergence_series.csv` y `emergence_summary.json`
- `scripts/run_robustness.py` — suite de N ejecuciones con semillas distintas, salida JSON con KL/VFE/IMI/MIG
- `scripts/plot_emergence.py` — genera PNG con 6 gráficas automáticas (KL, MIG, IMI, VFE, MIG vs tribus, supervivencia)

### Zona Liminal (tránsito intersimulación)

Sistema opcional que conecta múltiples instancias de PSYCHE SIMULACRA a través de un servidor WebSocket central. Permite que agentes de distintas simulaciones (en la misma PC o en PCs diferentes) se encuentren en un espacio compartido.

- **`sim_identity`** — cada simulación genera un `SIM_ID` único persistido en `data/sim_id.txt`
- **`PortalHex`** — hexágono portal de posición determinista (depende del seed); se renderiza como nodo estrella en el mapa
- **`LiminalClient`** — cliente WebSocket asyncio; se conecta al servidor liminal en background
- **`AgentTransferHandler`** — registrado en el `SimulationClock` a `priority=25`; cuando un agente pisa el portal activa `agent.in_liminal = True`, lo suspende del ciclo de actualización local y lo envía al servidor
- **`liminal_server/`** — servidor WebSocket headless (Python + asyncio + websockets) con mapa hexagonal propio 30×20, registro de simulaciones y agentes, reloj liminal, y endpoint HTTP `/state`. La visualización se realiza en el tab **Liminal** del dashboard NiceGUI
- Agentes en tránsito desaparecen del mapa local y aparecen en el tab Liminal del observatorio con el color de su simulación de origen
- Los agentes regresan automáticamente tras `LIMINAL_RETURN_AFTER_TICKS` ticks liminales

### Persistencia y observabilidad
- **SQLite** (WAL) — snapshots de agentes, clima, escenario, muertes, sesiones
- **CheckpointManager** — guardado atómico JSON cada 10 días + al apagar
- **Obsidian Vault** — sincronización diaria: `vault/Personas/`, `vault/Colectivo/`, `vault/Tribus/`, `vault/Colectivo/Leyendas/`
- **Panel de corridas NiceGUI** (`python main.py`, puerto 8080) — lanza y sigue varias corridas en paralelo, cada una aislada en su carpeta; abre el **monitor en vivo** de la que se elija (9 tabs: mapa hexagonal, red social cuántica, campo colectivo, tendencias, inspector de agentes, sueños, civilización y Zona Liminal) o el **visor de estado final** de una corrida terminada. Detalle en *Ejecución*
- **Visualizador Pygame** (`scripts/visualizer.py`) — mapa hexagonal en tiempo real con zoom y panning; alternativa ligera al dashboard web

---

## Escala temporal

```
1 tick = 1 hora simulada
1 día  = 24 ticks
```

Velocidad real (100 agentes, medida 2026-10):

| Modo | Velocidad aproximada |
|------|----------------------|
| Corrida del panel, sin narrativa (BD + vault) | ~0,5–1 s por día simulado (más rápido a medida que la población baja) |
| Headless de investigación (`run_eden_experiment.py`, `ab_interpretive.py`) | ~0,4–0,5 s por día |
| Con narrativa LLM (Ollama) | dominado por el LLM: puede llegar a ~1 min por día |

Una sociedad de 100 personas hasta la extinción (~12–19 años simulados) tarda del orden de media hora a una hora sin narrativa.

---

## Estructura del proyecto

```
psyche-simulacra/
│
├── ui/
│   ├── __init__.py
│   ├── app_state.py               AppState — singleton thread-safe (runner + runtime)
│   ├── db_reader.py               Lecturas no bloqueantes de DB SQLite y checkpoint JSON
│   ├── hub.py                     Panel de corridas (tandas, cola, tabla, comparar, guía)
│   ├── corrida_worker.py          Proceso de UNA corrida: simula + sirve su monitor (o visor)
│   ├── launch.py                  Atajo al panel (= python main.py)
│   └── psyche_ui.py               Monitor NiceGUI de una corrida (9 tabs)
│
├── core/
│   ├── time/
│   │   └── simulation_clock.py        SimulationClock, TimePoint
│   ├── interface/
│   │   ├── world_action.py
│   │   ├── world_snapshot.py
│   │   └── action_result.py
│   ├── world/
│   │   ├── climate.py                 ClimateSystem
│   │   ├── terrain.py                 TerrainGrid hexagonal 80x60
│   │   ├── resources.py               ResourceSystem
│   │   ├── fauna.py                   FaunaSystem
│   │   ├── fire.py                    FireSystem
│   │   ├── culture_engine.py          CultureEngine (estructuras + auras)
│   │   └── world_core.py              WorldCore (orquestador)
│   ├── agents/
│   │   ├── agent.py                   Agent (4 capas)
│   │   ├── needs.py                   NeedsSystem
│   │   ├── schedule.py                ScheduleSystem
│   │   ├── agent_core.py              AgentCore (orquestador)
│   │   ├── psyche/
│   │   │   ├── archetypes.py          ArchetypeVector (12 jungianos + individuacion + MID + fidelidad)
│   │   │   ├── complexes.py           ComplexProfile (6 complejos)
│   │   │   ├── traits.py              TraitProfile (Big Five + clinico)
│   │   │   ├── dreams.py              DreamGrammarEngine (5 capas, sueños compartidos)
│   │   │   ├── interpretive_filter.py InterpretiveFilter (Ecuación Personal, Fase 1)
│   │   │   ├── recalibration.py       ArchetypeRecalibrator (experimental)
│   │   │   └── lindblad.py            LindBladChannel T1/T2 (decoherencia arquetipica)
│   │   └── quantum/
│   │       ├── superposition.py       BehavioralSuperposition
│   │       └── collapse.py            CollapseEngine
│   ├── social/
│   │   ├── interaction.py             InteractionEngine
│   │   ├── network.py                 SocialNetwork (NetworkX)
│   │   ├── collective_field.py        CollectiveField
│   │   ├── mythology.py               MythologyEngine
│   │   ├── nomos.py                   Nomos — orden providencial (EDEN)
│   │   ├── serpent.py                 Serpiente — tentación y switch (EDEN)
│   │   └── tribe_manager.py           TribeManager + ICL local
│   ├── narrative/
│   │   ├── config.py                  OLLAMA_BASE_URL, modelo, flags
│   │   ├── ollama_client.py           Cliente HTTP sin dependencias externas
│   │   ├── prompts.py                 4 constructores de prompt en espanol
│   │   ├── narrator.py               NarratorEngine (queue + worker en hilo)
│   │   └── daemon.py                  OllamaDaemon (auto-start + ensure_model)
│   ├── metrics/
│   │   ├── emergence.py              EmergenceMetrics (KL, VFE, IMI, MIG)
│   │   └── exporter.py               MetricsExporter (CSV + JSON)
│   ├── runtime/
│   │   └── corridas.py               CorridaConfig, carpetas, estado y entorno de cada corrida
│   ├── liminal/                      Zona Liminal — cliente y portal
│   │   ├── sim_identity.py           SIM_ID persistido (data/sim_id.txt)
│   │   ├── portal_hex.py             PortalHex — posición determinista por seed
│   │   ├── liminal_client.py         LiminalClient — WebSocket asyncio
│   │   └── agent_transfer.py         AgentTransferHandler — tick handler
│   └── simulation.py                 SimulationRunner (orquestador principal)
│
├── persistence/
│   ├── database.py                   DatabaseManager (SQLite WAL)
│   ├── checkpoint.py                 CheckpointManager
│   ├── write_buffer.py               WriteBuffer (batching)
│   └── session_log.py                SessionLog
│
├── obsidian/
│   ├── reader.py                     Lee frontmatter YAML
│   ├── writer.py                     Escribe Personas, Tribus, Colectivo
│   └── sync.py                       Sincronizacion bidireccional
│
├── vault/                            Vault de Obsidian (generado en runtime)
│   ├── Personas/                     Un .md por agente
│   ├── Colectivo/                    Campo, mitologia, cultura material
│   │   └── Leyendas/                 Narrativa generada por LLM
│   ├── Tribus/                       Un .md por tribu
│   └── Meta/                         Log de simulacion
│
├── data/
│   ├── db/simulation.db              Historial SQLite completo
│   ├── checkpoints/                  Estados JSON guardados
│   ├── metrics/                      Series temporales de emergencia
│   │   ├── emergence_series.csv
│   │   └── emergence_summary.json
│   ├── corridas/                     Una carpeta por corrida del panel (no versionada)
│   ├── poblaciones/                  Poblaciones generadas desde el panel (no versionada)
│   ├── archive/                      Simulaciones completadas (sistema anterior)
│   └── seeds/
│       ├── initial_personas.yaml     15 agentes beta (perfiles extremos)
│       ├── 100_personas.yaml         100 agentes (generados proceduralmente)
│       ├── rich_culture_100.yaml     100 agentes (variante de cultura rica)
│       └── eden_pilot_10.yaml        10 agentes — piloto del experimento EDEN
│
├── scripts/
│   ├── run_simulation.py             Motor headless (argparse completo)
│   ├── generate_personas.py          Generador procedural de agentes YAML
│   ├── run_robustness.py             Suite de N ejecuciones paralelas
│   ├── plot_emergence.py             Reporte PNG con 6 graficas (KL, MIG, IMI, VFE, scatter, supervivencia)
│   ├── run_eden_experiment.py        A/B EDEN headless (control vs. tratamiento, pareado por semilla)
│   ├── ab_interpretive.py, ab_sweep.py, run_ab_batch.py   A/B de la Ecuación Personal
│   └── visualizer.py                 Visualizador Pygame en tiempo real
│
├── packaging/                        Instalador Windows: PyInstaller (.spec) + Inno Setup + build.bat
│
├── docs/                             Arquitectura, experimentos, decisiones (ADR), handoffs, guía de uso
│
├── tests/                            560 tests (pytest)
│   ├── test_agent.py
│   ├── test_network.py
│   ├── test_quantum.py
│   ├── test_persistence.py
│   ├── test_simulation.py
│   ├── test_social.py
│   ├── test_obsidian.py
│   ├── test_metrics.py              KL divergence, VFE, IMI, exporter
│   ├── test_nomos.py, test_serpent.py, test_eden_integration.py   Experimento EDEN
│   ├── test_recalibration.py        Recalibración arquetípica
│   └── test_corridas.py             Panel multicorrida (incluye corrida real de punta a punta)
│
├── src/                              Documentos de diseno originales
│   └── archive/                      Roadmaps completados
│
├── liminal_server/                   Servidor LIMINAL ZONE (paquete; lo levanta el panel o se corre aparte)
│   ├── main.py                       Punto de entrada (python liminal_server/main.py)
│   ├── config.py                     Host, puerto, seed, PROTOCOL_VERSION
│   ├── requirements.txt
│   ├── core/
│   │   ├── liminal_world.py          Mapa hexagonal 30×20 del espacio liminal
│   │   ├── liminal_clock.py          Reloj propio del servidor
│   │   ├── simulation_registry.py    Simulaciones conectadas
│   │   └── agent_registry.py         Agentes presentes en la zona
│   ├── transport/
│   │   └── websocket_server.py       Servidor WebSocket (websockets + asyncio)
│   └── protocol/
│       └── schemas.py                Tipos de mensajes del protocolo
│
├── main.py                           Punto de entrada único: panel / --corrida / --ver / --liminal-server
├── pyproject.toml
└── requirements.txt
```

---

## Instalacion

```bash
pip install -e ".[dev]"          # desarrollo + tests
pip install -e .                 # solo produccion
pip install -e ".[dashboard]"    # con Streamlit
```

**Usuarios de Windows sin Python:** instalador `PsycheSimulacra-Setup-<versión>.exe`,
que se construye con `packaging\build.bat` (ver [`packaging/README.md`](packaging/README.md)).
Los datos del usuario van a `Documentos\PsycheSimulacra`.

**Dependencias opcionales:**
- `pygame` — para el visualizador en tiempo real
- Ollama con `llama3.2` descargado — para narrativa LLM local
  ```bash
  ollama pull llama3.2
  ```

---

## Ejecucion

### Panel de corridas (recomendado)

```bash
python main.py
```

Abre `http://127.0.0.1:8080` en el navegador. Desde el panel se arman **tandas
de corridas**: uno o más escenarios × N réplicas (semillas consecutivas), con
todos los mecanismos, la natalidad y los ajustes finos del motor configurables.
Cada corrida es un **proceso propio con su carpeta** (`data/corridas/<fecha>_<escenario>_s<semilla>_…/`:
`config.json`, `estado.json`, BD, checkpoints, métricas y vault), así que varias
corren en paralelo sin pisarse y una nueva nunca borra las anteriores.

| Escenario | `EDEN_MODE` | Qué es |
|---|---|---|
| Mundo libre | `off` | Sin Nomos ni Serpiente (comportamiento histórico del motor) |
| Orden permanente | `orden` | Nomos activo todo el run, sin Serpiente (control del experimento EDEN) |
| Edén | `eden` | Nomos + Serpiente: el orden puede romperse (tratamiento) |

En la tabla de corridas: **Ver en vivo** abre el monitor completo de la corrida
elegida (las demás siguen por detrás), **Estado final** abre el monitor congelado
de una corrida terminada (sin modificar su carpeta), y se puede detener, reanudar,
abrir la carpeta o borrar. **Comparar** superpone población y tribus de las
corridas marcadas. La guía para quien no conoce el código está en
[`docs/GUIA_DE_USO.md`](docs/GUIA_DE_USO.md) (también en el panel, enlace *Guía de uso*).
Arquitectura y motivos: [`docs/decisions/ADR-001-panel-multicorrida.md`](docs/decisions/ADR-001-panel-multicorrida.md).

El monitor de cada corrida tiene 9 tabs:

| Tab | Contenido |
|-----|-----------|
| Resumen | Temperatura, estación, carrying capacity, presión de recursos, tensión colectiva (presión emocional / mítica / confusión), muertes recientes |
| Tendencias | Gráficos históricos: emociones, población, clima con bandas de eventos extremos (A1), recursos · Métricas de emergencia: KL divergencia, VFE, IMI (A2) |
| ICL | Gauges de estado del campo (B1) · Carga memética de símbolos con tribu dominante (B2) · Proto-mitos en gestación y mitos activos (B3) · Léxico tribal emergente |
| Red Social | Grafo cuántico spring-layout agrupado por tribu (C1) · Tabla top-20 aristas con filtro tribu (C2) · Stats de red: clusters, hub, entrelazados (C3) |
| Agentes | Inspector filtrable por tribu / arquetipo / estado (G2) · Click en fila → radar arquetípico 12 ejes (G1) |
| Sueños | Frecuencia de arquetipos en sueños vs carga ICL (E1) · Tabla de sueños entrelazados / pares shared_with (E2) · Registro por individuo y por tribu |
| Civilización | Estructuras construidas · Tecnologías materializadas · Memoria cultural y cadena de transmisión (F2) |
| Mapa | Todo el terreno 80×60 WebGL con fog-of-war (D1) · Agentes coloreados por arquetipo (D2) · 7 capas toggle (D3) |
| Zona Liminal | Solo si se activó el servidor liminal al iniciar |

### Motor headless (maxima velocidad)

```bash
# Nueva sesion con 100 agentes, correr hasta extincion
python scripts/run_simulation.py --seeds-file data/seeds/100_personas.yaml --days 0

# Reanudar desde ultimo checkpoint
python scripts/run_simulation.py --resume --days 0

# Reanudar N dias mas
python scripts/run_simulation.py --resume --days 500
```

### Visualizador Pygame

```bash
python scripts/visualizer.py --resume --fps 10 --days 0
```

### Zona Liminal (multijugador experimental)

En el panel, *Avanzado → Zona Liminal* antes de lanzar. Si el servidor es
`localhost`, el panel lo levanta solo; el tab **Zona Liminal** aparece en el
monitor de cada corrida conectada. Dos o más corridas conectadas al mismo
servidor intercambian personas.

**Flujo típico en la misma PC (desarrollo/pruebas):**
1. `python main.py` → *Avanzado* → activar Zona Liminal → lanzar dos o más corridas → *Ver en vivo* → tab Zona Liminal

**Flujo entre dos PCs:** el servidor liminal puede iniciarse manualmente en el host:
```bash
python liminal_server/main.py --host 0.0.0.0 --port 8765 --seed 0
```

Aparece un hexágono estrella en el mapa — ese es el portal. Cuando un agente lo pisa, desaparece del mapa local y aparece en el tab Liminal del observatorio.

**Dependencias del servidor (instalar una vez):**
```bash
cd liminal_server
pip install -r requirements.txt
```

### Dashboard Streamlit (arqueológico, archivado)

El dashboard Streamlit fue reemplazado por el Observatorio NiceGUI. El código fuente
se conserva en `src/archive/dashboard_app.py` como referencia histórica.

### Generar nuevas semillas de agentes

```bash
python scripts/generate_personas.py --n 100 --seed 42
python scripts/generate_personas.py --n 50 --seed 7 --output data/seeds/grupo_pequeno.yaml
```

### Suite de robustez

```bash
python scripts/run_robustness.py --runs 10 --days 200
# Resultados en data/metrics/robustez.json
```

---

## Tests

```bash
python -m pytest                        # 560 tests (~32 min)
python -m pytest -v                     # verbose
python -m pytest --tb=short             # traceback corto
python -m pytest tests/test_metrics.py -v   # solo metricas de emergencia
```

---

## Variables de entorno

```bash
# Narrativa LLM
OLLAMA_BASE_URL=http://localhost:11434   # default
OLLAMA_MODEL=llama3.2                    # default
OLLAMA_TIMEOUT=120                       # segundos
NARRATIVE_ENABLED=1                      # 0 para desactivar

# Simulación
CHECKPOINT_INTERVAL=10                   # días entre checkpoints automáticos
DAYS_UNTIL_CLUSTERING=30                # días hasta primer clustering tribal
LETHALITY_FACTOR=1.0                     # letalidad de catástrofes (<1: menos muertes, más trauma)

# Natalidad
PROB_REPRO_DIARIA=0.007                  # probabilidad diaria de concebir por par elegible
BOND_REPRO_MIN=0.55                      # vínculo mínimo de la pareja
REPRO_NEEDS_MAX=0.45                     # hambre/sed máxima para concebir
REPRO_COOLDOWN_DIAS=180                  # descanso tras un nacimiento

# Experimento EDEN
EDEN_MODE=off                            # off | orden | eden  (EDEN_ENABLED=1 = eden)
NOMOS_WEIGHT=0.20                        # peso de la vocación impuesta en el colapso
SERPENT_WEIGHT=0.20                      # peso de la tentación en el colapso

# Ecuación Personal (desactivada por defecto — ver docs/experiments/)
INTERPRETIVE_FILTER_ENABLED=0            # 1 activa el InterpretiveFilter
MENTAL_VAULT_ENABLED=0                   # 1 activa el MentalVault (requiere el filtro ON)
ARCHETYPE_RECALIBRATION_ENABLED=0        # 1 activa la recalibración arquetípica (requiere el filtro ON)
INTERPRETIVE_WEIGHT=0.15                 # peso del filtro en el colapso
RECALIBRATION_GAIN=1.0                   # intensidad de la recalibración

# Mitología (calibración — ver docs/experiments/)
MYTH_CONTEXT_THRESHOLD=0.25              # umbral de contexto para nacer un proto-mito
MYTH_TRANSMISSION_CHOQUE_VIOLENTO=1.00       # intensidad de transmisión — choque violento
MYTH_TRANSMISSION_CONFLICTO_EXPLOTACION=0.50 # intensidad de transmisión — conflicto/explotación
MYTH_TRANSMISSION_COOPERACION_PURA=0.25      # intensidad de transmisión — cooperación pura

# Panel de corridas
PSYCHE_HUB_PORT=8080                     # puerto del panel
PSYCHE_DATOS_DIR=                        # carpeta de datos del usuario (default: data/; empaquetado: Documentos/PsycheSimulacra)
PSYCHE_ABRIR_NAVEGADOR=1                 # 0 = no abrir el navegador (pruebas)
```

Todas estas variables (y `EDEN_MODE`, `NOMOS_WEIGHT`, `SERPENT_WEIGHT`) se configuran por corrida desde el panel (`python main.py`), sin editar archivos: cada corrida guarda en su `config.json` exactamente lo que usó.

---

## Stack tecnico

| Componente | Tecnología |
|------------|-----------|
| Motor ABM | SimulationClock propio (tick-based, sin Mesa) |
| Grafos sociales | NetworkX |
| Vault | PyYAML (frontmatter Obsidian) |
| Persistencia | SQLite stdlib (WAL mode) |
| Observatorio principal | NiceGUI 3.x (browser, tiempo real) |
| Visualización de datos | Plotly (gráficos, mapa hexagonal, red social) |
| Visualizador alternativo | Pygame (`scripts/visualizer.py`) |
| Narrativa LLM | Ollama (llama3.2, cliente stdlib sin deps externas) |
| Zona Liminal (red) | websockets + asyncio (servidor headless) / threading (cliente) |
| Distribución Windows | PyInstaller + Inno Setup (`packaging/`) |
| Tests | pytest (560 tests) |

---

## Documentacion de diseno

Los documentos de diseño están en `src/` y `docs/`:

| Archivo | Contenido |
|---------|-----------|
| `docs/ARCHITECTURE.md` | Flujo de un tick y de un día simulado, componentes y dependencias, modos de ejecución, persistencia |
| `docs/AGENT_BRAIN.md` | El cerebro digital de un agente: percepción, InterpretiveFilter, memoria/sueños, decisión, disociación |
| `docs/ARCHETYPES.md` | Recorrido completo activación → resonancia → campo → cristalización → mito → conducta |
| `docs/MENTAL_VAULT.md` | El mini cerebro por agente (Fase 2 de la Ecuación Personal) |
| `docs/EMERGENCE.md` | Qué está diseñado vs. qué emerge en cada subsistema — checklist de auditoría |
| `docs/GUIA_DE_USO.md` | Guía del panel para quien no conoce el código (también en el panel, *Guía de uso*) |
| `docs/decisions/` | Decisiones de arquitectura (ADR-001: panel multicorrida) |
| `docs/DEVELOPMENT_LOG.md` | Bitácora técnica sesión a sesión |
| `docs/experiments/` | Experimentos con hipótesis, método, datos e interpretación (A/B de la Ecuación Personal, calibración de mitología, EDEN) |
| `packaging/README.md` | Cómo construir el instalador de Windows |
| `docs/handoffs/` | Handoffs de cierre de sesión — estado y pendientes para retomar |
| `docs/Liminal_Zone.md` | Arquitectura de la Zona Liminal |
| `src/01-PSYCHE_IDEAS_IMPLEMENTACION.md` | Backlog de ideas con estimaciones |
| `src/02-PSYCHE_ORIGEN_INCONSCIENTE.md` | Teoria del inconsciente colectivo |
| `src/03-PSYCHE_BETA_SCOPE.md` | MVP: criterios de exito |
| `src/04-PSYCHE_SISTEMA_VIDA.md` | Nacimiento, muerte, herencia |
| `src/05-PSYCHE_LECCIONES_SIMULACIONES.md` | Lecciones de Sims, RimWorld, Spore |
| `src/06-PSYCHE_ESCENARIO_INICIAL.md` | Mundo hexagonal: 12 biomas |
| `src/07-PSYCHE_AUDITORIA_PERSISTENCIA.md` | Esquema de BD y checkpoints |
| `src/08-PSYCHE_EL_MUNDO.md` | Diseno completo de recursos y biomas |
| `src/09-PSYCHE_ARQUITECTURA_NUCLEOS.md` | WorldCore + AgentCore |
| `src/10-PSYCHE_SIMULATION_CLOCK.md` | SimulationClock |
| `src/archive/00-ROADMAP_ORIGINAL_v1_COMPLETADO.md` | Roadmap original completado |
| `src/archive/ROADMAP5.1.md` | Roadmap 5 — simulación completa: tribus, mitos, métricas |
| `src/archive/ROADMAP5.2.md` | Roadmap 5.2 — observatorio NiceGUI: todos los bloques A→H |

---

*El inconsciente colectivo no se programa. Emerge.*
