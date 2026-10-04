# Propuesta: ideas aplicables de JPAF (evolving_personality)

**Fecha:** 2026-10-04
**Estado:** P1 y P2 implementados el mismo día detrás de un flag apagado
(ver §6). P3 y la limpieza del código muerto siguen sin hacer. Nada está
activado por defecto ni validado con un A/B.
**Fuente:** <https://github.com/agent-topia/evolving_personality> (commit `517e357`,
2026-03-17), código del paper *Structured Personality Control and Adaptation
for LLM Agents* (arXiv 2601.10025).

---

## 1. Qué es JPAF y qué NO se toma

JPAF modela la personalidad de un agente LLM como un vector de pesos sobre las
8 funciones junguianas (Ti, Te, Fi, Fe, Ni, Ne, Si, Se) con tres mecanismos:
coordinación dominante-auxiliar, refuerzo-compensación y reflexión.

No se porta código ni datos, por cuatro razones:

- **Todo pasa por un LLM.** Tanto la elección de función como la decisión de
  reorganizar el tipo son prompts. Acá el loop de decisión es numérico y
  Ollama solo narra; un LLM en el loop rompe el offline y el rendimiento.
- **Viola el principio content-free.** JPAF instala desde afuera el vocabulario
  (8 funciones descritas en prosa, 16 tipos MBTI). Eso es exactamente lo que
  `core/agents/psyche/interpretive_filter.py` prohíbe en la Capa B.
- **El repo no tiene licencia.** No hay `LICENSE`: el código no se puede copiar.
  Las ideas del paper sí se pueden reimplementar.
- **Calidad de prototipo.** Reintentos `while` sin límite, cuatro funciones
  `reflection` casi duplicadas, accesos sin validar a la respuesta del LLM.

Lo que sí sirve son tres **patrones estructurales**, todos reimplementables en
numérico, sin dependencias nuevas y como Capa A (estructura, no vocabulario).

## 2. Estado actual del código que motiva las propuestas

Verificado leyendo el código el 2026-10-04 (`main` en `1ed117d`):

- **El vector arquetípico deriva de forma continua y mayormente hacia arriba.**
  Hay ~15 puntos que hacen `setattr(agent.archetypes, attr, min(1.0, current + delta))`
  directo: sueños (`agent.py:330`), consolidación del `MentalVault`
  (`agent.py:396`), sustancias (`agent.py:930`), impronta de apego y
  cristalización adolescente (`agent_core.py:4414`, `:4426`), rituales y
  cultura (`agent_core.py:726`, `culture_engine.py:281`,
  `tribe_manager.py:251`), zona liminal (`agent_transfer.py:477`). Los pesos
  no se normalizan (decisión explícita de `ArchetypeVector`), así que nada
  empuja hacia abajo salvo los deltas negativos de sueños/vault y el ruido
  gaussiano del hex liminal.
- **No existe la noción de "cambio de tipo".** `dominant()` es un `max()` sobre
  el vector: el dominante puede alternar día a día entre dos arquetipos con
  pesos casi iguales, sin histéresis ni evento que lo registre.
- **`ArchetypeVector.update_from_event` y `_TRANSFORMATIONS` son código muerto.**
  Nadie los llama; `agent.py:325` solo "toca" el método para silenciar un
  lint. Las 8 transformaciones por evento (trauma, traición, acto heroico…)
  nunca se aplican.
- **Los rasgos (`TraitProfile`) son casi fijos de por vida.** Solo cambian por
  herencia al nacer y por abstinencia de sustancias (`agent.py:969-972`).

## 3. Propuestas

### P1 — Acumulador de uso con reorganización por umbral

**Idea de JPAF:** el uso reciente de una función se suma en un acumulador
*separado* del peso base (+0,06 por uso). Solo cuando el acumulado cruza un
umbral (la auxiliar alcanza a la dominante, o una indiferenciada la supera) se
evalúa reorganizar el tipo. Si no se consolida, el acumulado decae ×0,2.

**Traducción numérica (sin LLM):**

- Nuevo estado por agente: `uso_reciente: dict[str, float]` paralelo a
  `ArchetypeVector`, que arranca en cero.
- Fuente del uso: `PerceivedEvent.archetype_activation`, que el
  `ResonanceOperator` ya calcula. No se inventa señal nueva.
- `dominant()` pasa a devolver un dominante **estable** (guardado), no el
  `max()` instantáneo.
- Chequeo diario: si `peso[x] + uso_reciente[x] >= peso[dominante]` para algún
  `x` no dominante, se abre una ventana de N días. Si la condición se sostiene
  toda la ventana → **reorganización**: `x` pasa a ser el dominante, el
  acumulado se vuelca a los pesos base y se emite un evento. Si no se
  sostiene → `uso_reciente *= 0.2`.
- La regla determinista de "sostenido N días" reemplaza al prompt de reflexión.

**Qué aporta:** histéresis (se acaba el flip-flop), un evento discreto y
observable de transformación de carácter, y separación entre estado
transitorio y estructura. Es content-free: no nombra ni interpreta nada, solo
define *cuándo* cambia la estructura.

**Riesgos:** cambia la dinámica de todo lo que lee `dominant()`
(`AttentionOperator`, impronta de apego, hex liminal, métricas arquetípicas).
Va detrás de un flag `ARCHETYPE_REORG_ENABLED=0` con comportamiento
byte-idéntico cuando está apagado (verificable con `tests/test_reproducibility.py`)
y necesita su propio A/B.

**Métricas nuevas sugeridas:** reorganizaciones por agente y por vida, tiempo
de permanencia del dominante, distribución de dominantes por tribu en el tiempo.

### P2 — Compensación: lo indiferenciado se activa cuando lo dominante falla

**Idea de JPAF:** cuando dominante y auxiliar no alcanzan para la situación, se
diferencia una función desde el inconsciente para compensar.

**Traducción numérica:** si el agente acumula resultados negativos sostenidos
(valencia media negativa del `PerceivedEvent` durante una ventana) mientras
actúa bajo su dominante, se suma uso a los arquetipos de **menor** peso en
`uso_reciente`. Con P1 en pie, esa presión puede terminar en reorganización.

**Antecedente en el código:** el hex liminal ya hace algo parecido en espíritu
(`agent_core.py:3655-3667`, ruido solo sobre los arquetipos "dormidos", nunca
sobre el dominante), pero atado a la geografía, no al fracaso.

**Depende de P1** (necesita el acumulador). Mismo flag o uno propio.

### P3 — Test de activación dirigida

**Idea de JPAF:** baterías de escenas diseñadas para evocar una función
concreta, midiendo la tasa de activación correcta.

**Traducción:** generar `Stimulus` sintéticos por cada `kind` de
`ARCHETYPE_ATTENTION` (`core/social/perception.py:30`) y comprobar, sobre una
población de psiques variadas, que `ResonanceOperator.activation` enciende los
arquetipos esperados y **solo** esos, y que la magnitud ordena según el peso
previo. Va como test en `tests/test_interpretive_filter.py`.

**Qué aporta:** validez de constructo barata para la Fase 1, independiente de
los A/B de 300 días. No cambia la simulación, no necesita flag.

### Hallazgo colateral — código muerto en `archetypes.py`

No viene de JPAF sino de la lectura para esta propuesta: decidir si
`update_from_event`/`_TRANSFORMATIONS` se conectan a los eventos reales
(trauma, traición, testigo de muerte…) o se eliminan junto con el "touch" de
`agent.py:325`. Si se conectan, deberían escribir en el acumulador de P1 y no
directamente en los pesos base.

## 4. Orden sugerido y condiciones

| Paso | Qué | Condición | Tamaño |
|---|---|---|---|
| 1 | P3 (test de activación) | Ninguna; se puede hacer ya | Chico, reversible |
| 2 | Resolver el código muerto | Ninguna | Chico |
| 3 | P1 (acumulador + reorganización) | Ver §5 | Mediano, detrás de flag, con A/B propio |
| 4 | P2 (compensación) | P1 implementado y medido | Chico sobre P1 |

No se agregan dependencias en ningún paso.

## 5. Relación con los experimentos abiertos

La repetición n=15 del A/B de Fase 1 se completó el 2026-10-04
(`docs/experiments/2026-09-21-fase1-n15-repeticion.md`). Lo que cambia para
esta propuesta:

- **La Fase 1 queda cerrada sin efecto arquetípico medible.** P1 no puede
  justificarse como "la continuación natural de un mecanismo que funcionó";
  es una hipótesis distinta (el cambio discreto de dominante produce
  divergencia que la deriva continua no produce) y necesita su propio gate.
- **El filtro reduce el número de tribus (~21 → ~15) y eso confunde todas las
  métricas de divergencia inter-tribu.** Cualquier A/B de P1 tiene que
  controlar `n_tribes` desde el diseño; si no, repite el mismo problema.
- **Antes de P1 conviene entender por qué baja el número de tribus.** Es una
  pregunta más barata y más informativa que un mecanismo nuevo. Las tribus
  salen de la red de vínculos (`TribeManager.update_tribes`), no del
  arquetipo dominante, así que P1 solo las afectaría de forma indirecta, a
  través de cómo el dominante sesga la interacción social.

P3 y la limpieza del código muerto no dependen de nada de esto.

## 6. Implementación (2026-10-04, rama `feature/recalibracion-arquetipica`)

**Qué se construyó:** `core/agents/psyche/recalibration.py`
(`ArchetypeRecalibrator`, uno por agente), activado con
`ARCHETYPE_RECALIBRATION_ENABLED=1` y solo si el filtro está encendido.
Tests en `tests/test_recalibration.py`.

| Pieza | Qué hace |
|---|---|
| Acumulador | Suma la resonancia de cada `PerceivedEvent` aparte del vector |
| Decaimiento | La experiencia pierde 10 % por día |
| Consolidación | Experiencia sobre el umbral 5 días seguidos → pasa al peso base, redistribuyendo desde el resto |
| Dominante estable | Solo cambia si otro lo supera por 0,03 durante 7 días; el cambio se cuenta y se anota en `episodic_log` |
| Compensación (P2) | Si la valencia reciente cae bajo la línea de base del propio agente, presión a los 2 arquetipos menos desarrollados y contra el dominante |
| Conservación | La suma del vector se mantiene en el presupuesto del primer día |

Dos piezas no estaban en la propuesta original y salieron de medir:

- **Conservación.** Sin ella el vector satura: a 300 días, con solo el filtro,
  el peso medio pasa de ~0,38 a ~0,68 y cada agente tiene ~2 arquetipos en
  1,0. Con varios empatados en el techo, `dominant()` devuelve el primero en
  el orden del dict, no el más vivido. Con conservación: peso medio ~0,415 y
  ~0,3 arquetipos saturados por agente.
- **Malestar relativo.** La valencia vivida es muy positiva (mediana ~+0,65),
  así que un umbral absoluto de "valencia negativa" disparaba la compensación
  en el 0,3 % de los días-agente. Relativa a la línea de base propia: 8-28 %.

**Con el flag apagado el resultado es idéntico a `main`** (300 días, semilla
42, `PYTHONHASHSEED=0`, todas las métricas compartidas).

### Qué se midió con el flag encendido (semillas 42 y 43, 300 días)

Son diagnósticos de una o dos semillas, no un A/B.

- **Reorganizaciones:** ~2,1-2,5 por agente en 300 días; casi ningún agente
  queda sin ninguna.
- **Monocultivo de sombra.** Entre el 89 % y el 92 % de los agentes termina
  con `sombra` como dominante. Sin recalibración, con solo el filtro, `sombra`
  ya es la moda (42-55 %).
- **El canal de percepción es minoritario.** La consolidación movió en total
  entre 16 y 98 puntos de peso (sumados sobre toda la población), según haya o
  no encuentros sociales. Los sistemas que escriben directo al vector mueven
  mucho más — medido con solo el filtro, semilla 42, 300 días:

| Fuente | Neto sobre la población | Arquetipos principales |
|---|---|---|
| `Agent._consume_substance` | +174,6 | persona +63,6, madre +52,9, trickster +30,2, gobernante −40,0 |
| `Agent._process_dream` | +76,3 | anima_animus +39,0, sombra +37,3, self +31,4, persona −17,9 |
| `TribeManager._apply_biome_drift` | +41,1 | madre +9,8, heroe +9,6 |
| `AgentCore._generate_offspring` | +28,3 | (herencia; no es deriva) |
| `AgentCore.on_tick` | +18,2 | sabio +18,2 |
| resto | < 6 | |

**Lectura:** hoy las "vivencias" que más recalibran a un agente son consumir
sustancias y soñar, no lo que percibe. La recalibración por percepción
funciona mecánicamente, pero pesa poco frente a esas dos fuentes, y la
conservación convierte su sesgo acumulado en un dominante casi único.

### Decisiones abiertas antes de un A/B

1. **Qué hacer con sustancias y sueños.** Opciones: (a) pasarlos por el
   acumulador, para que también decaigan y necesiten sostenerse; (b) bajar sus
   magnitudes; (c) dejarlos y aceptar el monocultivo como resultado. La (a) es
   la coherente con "un solo mecanismo", pero cambia tablas existentes.
2. **Calibración.** Los umbrales y ventanas de `recalibration.py` se eligieron
   a ojo; solo `RECALIBRATION_GAIN` es configurable por entorno.
3. **Diseño del A/B.** Tiene que usar `behavioral_kl_multi_q4` y
   `n_tribes_multi_q4` en lugar de las métricas con aislados, y correr con
   `PYTHONHASHSEED` fijo (los orquestadores ya lo fijan).

