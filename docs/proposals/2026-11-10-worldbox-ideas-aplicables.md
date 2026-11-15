# WorldBox: ideas aplicables a psyche-simulacra

**Fecha:** 2026-11-10 · **Estado:** borrador para que Marcos lo analice (sin commitear).

## Conclusión

WorldBox sirve más como **instrumento de observación y control experimental** que como
fuente de mecánicas. Psyche ya modela la psicología con más detalle (arquetipos,
complejos, duelo, sueños, léxico emergente, cismas). WorldBox es un sandbox con reglas
escritas a mano, y copiar sus mecánicas iría contra la tesis de que el inconsciente
"emerge, no se construye". Donde sí aporta: cómo organiza a los grupos, qué cuenta y
cómo deja intervenir el mundo.

## Lo que más sirve

### 1. Separar las pertenencias de un agente (arquitectura, requiere ADR)

En WorldBox, reino, cultura, religión, idioma, clan y familia son objetos distintos.
Cada uno tiene sus miembros y rasgos, y se divide por su cuenta cuando es viejo y grande
y aparece un miembro ambicioso o inspirado (0.50.5).

En psyche casi todo cuelga de la tribu: léxico (`core/social/emergent_lexicon.py`,
`TribalLexicon`), mitos, ICL, memoria cultural. Y la tribu se recalcula por clustering
de modularidad cada 30 días (`TribeManager`), así que si una tribu se parte, su cultura
se parte con ella.

Separar "tribu" (quién convive) de "culto/mito" y "lengua" (qué se comparte)
permitiría medir:
- si un mito sobrevive a la tribu que lo creó;
- si una palabra cruza fronteras;
- cuánto tarda una tribu en tener una identidad diferenciable (pregunta del README).

### 2. Contadores de flujo por tribu (barato; cierra un pendiente)

WorldBox (0.50–0.51) cuenta por reino: altas, bajas, mudanzas y migraciones;
nacimientos, muertes y muertes violentas como totales; renombre acumulado. También
anota las catástrofes en el historial.

Responde casi directo al pendiente "qué datos comparar entre corridas además de
población y tribus". Implementación: columnas nuevas en la serie CSV de cada corrida
(`core/runtime/corridas.py`, `leer_serie`), que el panel ya sabe comparar.

### 3. Intervenciones programadas en la línea de tiempo

WorldBox tiene "leyes del mundo" (interruptores con nombre, reordenables), "eras" (fases
de al menos ~30 años que cambian las condiciones del mundo) y poderes de dios.

En psyche, el switch de EDEN ya es exactamente esto, pero está programado aparte.
Propuesta: que la configuración de una corrida incluya una lista de intervenciones,
por ejemplo "día 60: retirar Nomos" o "día 120: catástrofe en el bioma X"
(`core/world/catastrophe.py` ya existe). Así una tanda prueba la misma intervención con
varias semillas, y cada intervención queda registrada como evento.

### 4. Crónica unificada del mundo

Un solo registro de hitos con su día: nace una tribu, hay un cisma, cristaliza un mito,
cae una catástrofe, muere un líder. En el panel se podría recorrer y comparar entre
corridas. Las piezas ya existen (`event_bus`, `CulturalMemory`, `LegendsExporter`),
pero no están reunidas en un mismo lugar.

## Utilidad media

- **Renombre por tribu:** psyche tiene `prestigio` por agente, pero no un valor
  acumulado por grupo. Usarlo solo como métrica, no como requisito para que algo pase.
  Ayuda con "¿el héroe emerge del poder o de la narrativa?".
- **Libros como memoria fijada en un objeto:** en WorldBox, un relato guardado en un
  objeto no se deforma como el oral. Con `DistortionEngine` y los objetos sagrados, el
  experimento sale casi solo: ¿fijar el mito reduce su deriva?
- **Lecciones de calibración que WorldBox tuvo que aprender:**
  - bajar cuánto heredan los hijos de cada padre y la tasa de mutación (0.50.5–0.50.6);
  - exigir antigüedad, tamaño y un miembro ambicioso para dividir un grupo, porque si no
    se dividían demasiado (0.50.5).

  Sirven como referencia para los umbrales de cisma (`_PRE_CISMA_THRESH`,
  `_CISMA_THRESH` en `core/agents/agent_core.py`).
- **Ideas para el panel:**
  - hacer clic en una tribu o un mito en el mapa y ver su ficha;
  - capas de color en el mapa (tribu, arquetipo dominante, mito);
  - seguir a un agente favorito durante toda la corrida;
  - gráficos con escalas largas y tooltip con la diferencia respecto del valor anterior.

## Lo que no conviene traer

- **"Plots"** (conspiraciones con barra de progreso que terminan en guerra, alianza o
  división): son resultados escritos de antemano y contradicen la emergencia. A lo sumo,
  un *detector* de conspiraciones que aparezcan solas.
- **Especies, subespecies y fenotipos:** psyche tiene una sola especie.
- **Felicidad como un número de -100 a 100:** psyche ya es más rica (necesidades, duelo,
  complejos).
- **Poderes de dios como juego:** solo valen como intervención experimental (punto 3).

## Orden sugerido

1. Punto 2 (chico, cierra un pendiente).
2. Punto 3.
3. Punto 1, con ADR antes de tocar código.

## Fuentes

- Changelog oficial de WorldBox (0.50–0.51): https://www.superworldbox.com/changelog
- WorldBox en Steam: https://store.steampowered.com/app/1206560/WorldBox_-_God_Simulator/
- Wiki: Ages — https://the-official-worldbox-wiki.fandom.com/wiki/Ages
- Wiki: Books — https://the-official-worldbox-wiki.fandom.com/wiki/Books
- Wiki: Happiness — https://the-official-worldbox-wiki.fandom.com/wiki/Happiness
- Wiki: Powers — https://the-official-worldbox-wiki.fandom.com/wiki/Powers
- Wiki: Culture Traits — https://the-official-worldbox-wiki.fandom.com/wiki/Culture_Traits
- Game8 (clanes): https://indie.game8.co/news/worldbox-god-simulator-dev-teased-new-clan-features-as-part-of-an-upcoming-major-update/
- TV Tropes: https://tvtropes.org/pmwiki/pmwiki.php/VideoGame/WorldBox
