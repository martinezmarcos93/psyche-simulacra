# Guía de uso — Laboratorio de sociedades simuladas

PSYCHE SIMULACRA simula pequeñas sociedades de personas con vida psicológica
propia (arquetipos, complejos, emociones, necesidades). Nadie les escribe la
historia: forman tribus, eligen chamanes, levantan estructuras, inventan
símbolos y dioses, se reproducen (poco) y mueren. Esta guía explica cómo usar
el panel para correr experimentos sin tocar código.

---

## 1. Abrir el programa

- **Windows (instalado):** doble clic en *Psyche Simulacra* (escritorio o menú
  Inicio). Se abre el navegador con el panel.
- **Desde el código:** `python main.py`.

El panel es una página web local (`http://127.0.0.1:8080`): no necesita
internet y nada sale de la computadora. Si se cierra la pestaña, las corridas
siguen; volver a abrir el programa las muestra de nuevo.

## 2. Conceptos

| Término | Qué es |
|---|---|
| **Corrida** | Una historia completa de una sociedad, de principio a fin. |
| **Población inicial** | Quiénes son las personas del día 1 (edades, perfiles psicológicos). |
| **Semilla** | Número que fija el azar. Misma semilla = mismo mundo y misma población inicial. Cambiar la semilla es "tirar los dados de nuevo". |
| **Réplica** | Repetir el mismo experimento con otra semilla, para saber si un resultado es un patrón o una casualidad. |
| **Escenario** | Las reglas del mundo (ver abajo). |

### Los tres escenarios

- **Mundo libre:** sin fuerza ordenadora. La sociedad se organiza sola.
- **Orden permanente:** una fuerza providencial (*Nomos*) asigna a cada
  persona una vocación, provee y pacifica durante toda la historia.
- **Edén:** el mismo orden, pero existe una figura tentadora (*la Serpiente*).
  Si logra que alguien desobedezca, el orden se retira de golpe y para siempre.
  El panel muestra el día y la persona que lo rompió.

Comparar *Orden permanente* contra *Edén* con la misma semilla es el
experimento central: dos sociedades idénticas cuya única diferencia es si el
orden puede romperse.

## 3. Lanzar una tanda

1. Marcar uno o más escenarios.
2. Elegir la población inicial (o generar una nueva en *Generar una población
   nueva*).
3. Elegir la semilla inicial y la cantidad de réplicas. Con 2 escenarios y
   3 réplicas se crean 6 corridas: semillas 1, 2 y 3 para cada escenario.
4. Duración: una cantidad de días o *hasta la extinción* (con un tope de 100
   años simulados).
5. **Lanzar.**

Las corridas que no entran en paralelo quedan *en cola* y arrancan solas a
medida que se libera lugar (se ajusta en *Avanzado → Corridas simultáneas*).

### Opciones (todas tienen valores por defecto razonables)

- **Mecanismos psicológicos:** capas experimentales de la psicología de las
  personas. Vienen apagadas.
- **Natalidad:** con los valores por defecto casi no nacen chicos y toda
  sociedad termina extinguiéndose por desgaste. Para estudiar sociedades que
  se renuevan, subir la probabilidad diaria de concebir (por ejemplo a 0,02)
  o bajar el vínculo mínimo de pareja.
- **Orden y Serpiente:** cuánto pesan la vocación impuesta y la tentación en
  cada decisión.
- **Mundo, cultura y mito:** letalidad de las catástrofes y facilidad con que
  nacen y se contagian los relatos míticos.
- **Narrativa con IA:** escribe crónicas, elegías y leyendas en texto. Requiere
  instalar [Ollama](https://ollama.com) (descarga varios GB la primera vez) y
  hace todo mucho más lento. No cambia la simulación: solo la narra.

## 4. Seguir las corridas

La tabla *Corridas* muestra, para cada una: estado, día, años, personas vivas,
cantidad de tribus y si el orden sigue vigente o cuándo se rompió.

- **Ver en vivo:** abre el monitor completo en otra pestaña (mapa, personas,
  red social, sueños, mitos, deidades, tendencias). Se puede abrir el de
  cualquier corrida que esté corriendo; las demás siguen por detrás.
- **Estado final:** para una corrida que ya terminó, abre el mismo monitor
  congelado en su último día.
- **Detener:** la corrida termina el día en curso y guarda todo.
- **Reanudar:** continúa una corrida detenida o interrumpida desde su último
  guardado.
- **Carpeta:** abre la carpeta con todos sus datos.
- **Borrar:** pide confirmación; no se puede deshacer.

## 5. Comparar

Marcar corridas en la tabla dibuja, en la sección *Comparar*, su población y
su cantidad de tribus a lo largo de los años.

## 6. Los datos de cada corrida

Cada corrida tiene su carpeta (en Windows: `Documentos\PsycheSimulacra\corridas`):

| Archivo | Contenido |
|---|---|
| `config.json` | Exactamente qué se configuró. Sirve para citar el experimento. |
| `estado.json` | Último estado: día, vivos, tribus, si el orden se rompió (día, persona, acción y perfil psicológico de quien lo rompió). |
| `data/metrics/emergence_series.csv` | Serie diaria de métricas (se abre con Excel o LibreOffice). |
| `data/metrics/emergence_summary.json` | Resumen estadístico de toda la corrida. |
| `data/metrics/eden_event.json` | Solo en Edén, si el orden se rompió: el acto de ruptura completo. |
| `data/db/simulation.db` | Base de datos completa (SQLite): personas, muertes, clima, cultura. |
| `vault/` | Notas por persona, tribu y colectivo (se pueden abrir con Obsidian). |
| `corrida.log` | Registro técnico; útil si algo falla. |

### Columnas principales de la serie diaria

| Columna | Lectura |
|---|---|
| `n_alive` | Personas vivas. |
| `n_tribes` | Tribus (una persona aislada cuenta como tribu de uno). |
| `n_tribes_multi` / `n_isolates` | Tribus reales (2 o más personas) / personas aisladas. |
| `imi`, `mig` | Cohesión psicológica de las tribus: cuánto explica la pertenencia tribal la psicología de cada uno. |
| `kl_mean` | Divergencia entre tribus: qué tan distintas son sus "culturas" psicológicas. |
| `behavioral_intra_tribe_dispersion` | Qué tan distinto se comportan entre sí los miembros de una misma tribu. |
| `vfe_global` | Incertidumbre del inconsciente colectivo (proxy de confusión). |
| `n_structures` | Estructuras levantadas (hogueras, murallas, altares, tótems). |
| `nomos_active` | `True` mientras el orden providencial está vigente (o si el escenario no lo tiene); `False` desde que se rompe. |

## 7. Buenas prácticas

- **Una sola corrida no prueba nada.** Usar réplicas (al menos 5–10 por
  escenario) antes de hablar de patrones.
- Para comparar escenarios, usar **las mismas semillas** en todos.
- Anotar el `config.json` de las corridas que se citan.
- Corridas largas con 100 personas pueden tardar entre media hora y una hora
  cada una; conviene lanzarlas y dejar la computadora trabajando.
