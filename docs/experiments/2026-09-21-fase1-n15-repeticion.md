# Experimento: repetición del A/B de Fase 1 con mayor poder estadístico (n=15)

**Fecha:** 2026-09-21 (sesión de continuación, rama `feature/ecuacion-personal-continuacion`)
**Referencia:** `docs/experiments/2026-09-21-fase1-ecuacion-personal.md` (experimento original, n=5)
**Motivación:** ese experimento dejó abierto explícitamente, en su sección
"Trabajo futuro", que n=5 semillas es insuficiente para distinguir "no hay
efecto" de "el efecto es real pero pequeño frente a la varianza entre
semillas" — la propia desviación estándar entre semillas superaba, en casi
todas las métricas, a la media de la diferencia pareada.

Este documento **no reemplaza** el original — lo extiende con más réplicas y
una métrica nueva (`behavioral_intra_q4`, ver `commit 575a9d8`) que el
experimento original no tenía disponible.

---

## Hipótesis

Sin cambios respecto al experimento original: activar `InterpretiveFilter`
(y opcionalmente `MentalVault`) debería producir una divergencia cultural
mediblemente mayor entre tribus. Adicionalmente, esta repetición evalúa una
hipótesis específica que quedó abierta (hipótesis 4 del documento original):
que el filtro aumenta la variación **intra-tribu** sin separar tribus entre
sí — invisible para `behavioral_kl_mean` solo, ahora visible con
`behavioral_intra_tribe_dispersion`.

## Variables

Las mismas del experimento original, más:
- `behavioral_intra_q4` (nueva): entropía normalizada [0,1] de la acción
  conductual dentro de cada tribu, promediada sobre el último cuartil.

## Método

- Mismo arnés (`scripts/ab_interpretive.py`), misma duración (300 días,
  agregación sobre el último cuartil), mismo escenario
  (`data/seeds/rich_culture_100.yaml`, 100 agentes).
- **Réplicas**: 15 semillas (42-56) × 3 condiciones (OFF / FILTER /
  FILTER+VAULT) = 45 corridas. Elegido n=15 (extremo inferior del rango
  n≥15-20 sugerido) por restricción de hardware real: esta máquina tiene 2
  núcleos lógicos: cada corrida de 300 días toma ~150-470s según contención,
  y correr en paralelo con otro cómputo (la calibración de mitología de esta
  misma sesión) degrada el throughput de ambos ~3x — se optó por correr todo
  en secuencia y priorizar completar n=15 sobre no completar n=20.
- Análisis: comparación pareada por semilla, igual que el experimento
  original (mismo diseño del arnés lo permite).
- Datos crudos: `data/metrics/ab_interpretive_fase1_n15_2026-09-21.jsonl`
  (gitignored, igual convención que el experimento original).

## Resultados

**Completada el 2026-10-04** sobre `main` en `1ed117d`, en una máquina de 4
núcleos: 45/45 corridas, sin errores, 300 días cada una, ~157-175 s por
corrida. Se corrieron tres instancias de `scripts/run_ab_batch.py` en paralelo
sobre rangos disjuntos de semillas (42-46, 47-51, 52-56) y se concatenaron
los tres archivos en `data/metrics/ab_interpretive_fase1_n15_2026-09-21.jsonl`
(el archivo de la corrida interrumpida del 21-sep no estaba en esta máquina,
así que se arrancó de cero). El paralelismo no afecta los resultados: cada
corrida es un subproceso determinista por semilla.

Es la primera corrida limpia posterior al fix de mitología (`a5f87e3`), a la
extensión de `on_social_transmission` y a la reinterpretación del receptor,
y la primera con las métricas intra/inter presentes en todas las filas.

Deltas pareados por semilla (condición − OFF). `p_signos` es el test de
signos bilateral, sin corrección por comparaciones múltiples.

### FILTER − OFF (n=15)

| Métrica | OFF_mean | delta_mean | delta_std | n_pos | n_neg | p_signos |
|---|---|---|---|---|---|---|
| kl_mean_q4 (arquetípico) | 0.0792 | +0.0002 | 0.0375 | 9 | 6 | 0.61 |
| mig_q4 | 0.4194 | -0.0673 | 0.1143 | 5 | 10 | 0.30 |
| imi_q4 | 0.2600 | -0.0366 | 0.1459 | 6 | 9 | 0.61 |
| **behavioral_kl_q4** | 9.8264 | **-1.6075** | 1.7511 | 2 | 13 | 0.007 |
| behavioral_intra_q4 | 0.7288 | +0.0396 | 0.0605 | 10 | 5 | 0.30 |
| field_kl_q4 | 1.7487 | +0.1346 | 0.3366 | 8 | 7 | 1.00 |
| **valence_std_q4** | 0 | **+0.1322** | 0.0343 | 15 | 0 | <0.001 |
| **arousal_std_q4** | 0 | **+0.0573** | 0.0068 | 15 | 0 | <0.001 |
| valence_std_intra_q4 | 0 | +0.0861 | 0.0298 | 15 | 0 | <0.001 |
| valence_std_inter_q4 | 0 | +0.0768 | 0.0238 | 15 | 0 | <0.001 |
| **n_tribes_q4** | 20.77 | **-5.84** | 5.89 | 2 | 13 | 0.007 |
| final_alive | 86.1 | +0.73 | 6.30 | 8 | 6 | 0.79 |

### FILTER+VAULT − OFF (n=15)

| Métrica | OFF_mean | delta_mean | delta_std | n_pos | n_neg | p_signos |
|---|---|---|---|---|---|---|
| kl_mean_q4 (arquetípico) | 0.0792 | -0.0108 | 0.0490 | 8 | 7 | 1.00 |
| mig_q4 | 0.4194 | -0.0571 | 0.1402 | 5 | 10 | 0.30 |
| imi_q4 | 0.2600 | -0.0399 | 0.1780 | 6 | 9 | 0.61 |
| behavioral_kl_q4 | 9.8264 | -1.1359 | 1.9199 | 5 | 10 | 0.30 |
| behavioral_intra_q4 | 0.7288 | +0.0184 | 0.0921 | 8 | 7 | 1.00 |
| field_kl_q4 | 1.7487 | +0.3068 | 0.6495 | 12 | 3 | 0.035 |
| **valence_std_q4** | 0 | **+0.1419** | 0.0317 | 15 | 0 | <0.001 |
| **arousal_std_q4** | 0 | **+0.0526** | 0.0091 | 15 | 0 | <0.001 |
| valence_std_intra_q4 | 0 | +0.0916 | 0.0274 | 15 | 0 | <0.001 |
| valence_std_inter_q4 | 0 | +0.0938 | 0.0435 | 15 | 0 | <0.001 |
| worldview_coh_q4 | 0 | +0.7198 | 0.1595 | 15 | 0 | <0.001 |
| **n_tribes_q4** | 20.77 | **-5.11** | 5.10 | 2 | 13 | 0.007 |
| final_alive | 86.1 | -2.67 | 8.60 | 5 | 9 | 0.42 |

### Control del confound por número de tribus

| | FILTER | VAULT |
|---|---|---|
| r(Δ behavioral_kl, Δ n_tribes) entre semillas | 0.95 | 0.68 |
| r(Δ mig, Δ n_tribes) | 0.82 | 0.72 |
| r(Δ kl_mean, Δ n_tribes) | 0.79 | 0.33 |
| Δ behavioral_kl ajustado por n_tribes | -0.01 (8+ / 7−) | +0.26 (9+ / 6−) |

Transversalmente (45 corridas) r(n_tribes, behavioral_kl) = 0.78. El ajuste
resta a cada corrida `0.274 × n_tribes` (pendiente de la regresión lineal
sobre las 45 corridas) antes de calcular el delta pareado. Es un control
aproximado: la pendiente se estima con las mismas corridas que se ajustan.

## Interpretación y decisión

**1. El gate arquetípico sigue sin cumplirse.** `kl_mean_q4`, `mig_q4` e
`imi_q4` no muestran dirección consistente en ninguna de las dos condiciones
(p ≥ 0.30). Coincide con n=5 y con n=20
(`2026-09-21-fase1-ecuacion-personal-n20.md`), ahora sobre el código con la
mitología activa. La conclusión "sin divergencia arquetípica medible" se
**sostiene**.

**2. La idiosincrasia afectiva se replica (15/15) y no queda contenida dentro
de la tribu.** `valence_std_intra` y `valence_std_inter` suben en magnitudes
parecidas. Esto contradice la hipótesis 4 del experimento original en su
forma fuerte ("la variación queda solo intra-tribu"): el filtro también
separa las medias afectivas entre tribus.

**3. Hallazgo nuevo: el filtro reduce el número de tribus.** De ~20.8 a ~15
en el último cuartil (13/15 semillas, p=0.007, en ambas condiciones), sin
cambio en la población viva. Ningún experimento anterior lo reportó como
resultado.

**4. La baja de `behavioral_kl_q4` es, en su mayor parte, consecuencia del
punto 3 y no un efecto conductual propio.** El delta de `behavioral_kl` casi
coincide con el delta de `n_tribes` semilla a semilla (r=0.95 en FILTER) y
desaparece al ajustar por número de tribus (-0.01, 8+/7−). La hipótesis del
documento n=20 ("el ruido individual se cancela en el agregado de la tribu")
no hace falta para explicar el dato: con menos tribus, más grandes, la KL
media entre pares baja sola. `behavioral_intra_q4` tampoco sube de forma
consistente (10/5 y 8/7).

**5. El vault no agrega efecto conductual medible sobre el filtro solo.**
Sus diferencias propias son `worldview_coh_q4` (definicional: solo existe con
vault) y un `field_kl_q4` algo mayor (12/3, p=0.035 sin corregir — débil).

**Decisión:** se mantiene **no activar los flags por defecto**. La Fase 1
queda cerrada como "sin efecto arquetípico medible a 300 días"; no se
justifican más réplicas del mismo diseño.

## Limitaciones

- `n_tribes_q4` confunde todas las métricas de divergencia entre tribus de
  este arnés. Mientras no se controle en el diseño (por ejemplo comparando a
  número de tribus fijo, o con métricas ponderadas por tamaño), ningún delta
  de KL inter-tribu es interpretable por sí solo.
- No se investigó **por qué** el filtro reduce el número de tribus. Es la
  pregunta abierta más concreta que deja este experimento. Pista sin
  verificar: `TribeManager.update_tribes` clusteriza por comunidades sobre la
  red de vínculos y cuenta a **cada agente aislado como una tribu de un solo
  miembro**. Con ~86 vivos y ~21 "tribus" en OFF, una parte de ese número
  pueden ser aislados; si el filtro cambia cuántos agentes quedan sin
  vínculos fuertes, `n_tribes` se mueve sin que cambie ninguna tribu real.
  Separar tribus de ≥2 miembros de aislados en las métricas lo resolvería.
- 300 días, un solo escenario (`rich_culture_100.yaml`). Tests de signos sin
  corrección por comparaciones múltiples.
- **El pareo por semilla no fue exacto** (detectado después, el mismo
  2026-10-04). Dos corridas de `main` con la misma semilla y condición dan
  resultados distintos a 300 días (idénticos hasta el día 80), porque
  `hash()` de cadenas cambia entre procesos. Con `PYTHONHASHSEED=0` son
  idénticas. Afecta a este experimento y a los de n=5 y n=20: cada par
  comparte mundo y población inicial pero no la trayectoria aleatoria
  completa. Los tests de signos siguen siendo válidos; lo que se pierde es
  potencia. `run_ab_batch.py` y `ab_sweep.py` ahora fijan la variable.
- **`behavioral_kl_q4` está inflado por los aislados** (también detectado
  después). Un agente solo tiene una distribución de acción de un único
  valor, y su KL contra cualquier tribu se dispara por el epsilon. En la
  semilla 42, OFF: 11,1 con aislados contra 2,07 comparando solo tribus de
  tres o más miembros, y de las ~24 "tribus" ~13,6 son aislados. Confirma la
  pista del punto anterior. Métricas nuevas: `n_isolates`, `n_tribes_multi`,
  `behavioral_kl_multi_mean`.

