# Mapa del observatorio: revisión de la propuesta "WorldBox → Psyche"

**Fecha:** 2026-11-14 · **Estado:** revisión técnica para que Marcos decida qué entra.
Complementa `2026-11-10-worldbox-ideas-aplicables.md` y el rediseño "Laboratorio de
Fenómenos" (rama `ui/laboratorio-fenomenos`).

## Conclusión

La idea central es correcta: el mapa tiene que mostrar **qué está pasando** y no solo
**dónde están las cosas**. Y buena parte ya se puede hacer **sin tocar la simulación**,
porque el motor produce más datos espaciales de los que el mapa dibuja hoy. Lo más
valioso, y lo que nadie mencionó, es que la **memoria del territorio ya existe**:
`core/world/psychic_geography.py` marca cada hex como zona traumática, lugar sagrado,
zona maldita, cicatriz ecológica o ruina, con carga simbólica, día de origen y tribu.
El mapa actual no la muestra.

Una regla para filtrar todo lo demás: **el mapa solo dibuja lo que la simulación
produjo**. Si una capa necesita inventar un fenómeno que el motor no modela, no va.
Esa es la doctrina del proyecto ("la interfaz observa, no controla") llevada al mapa.

## Idea por idea

| # | Idea | Veredicto | Con qué datos | Costo |
|---|------|-----------|---------------|-------|
| 1 | Territorio con estado; capas, no todo a la vez | **Sí** | Bioma (`terrain`), recursos por hex (`ResourceSystem.get_hex_summary`), marcas psíquicas. Temperatura y humedad son globales, no por hex: no inventarlas | Bajo |
| 2 | Zonas de influencia difusas por tribu | **Sí, primero** | Posición de cada persona + tribu (`agent_to_tribe`). Densidad por tribu suavizada sobre la grilla; color de la tribu con opacidad según densidad | Bajo |
| 3 | Asentamientos que crecen (aldea → centro cultural) | **Sí, derivado** | Estructuras con tribu y estado + personas en un radio. El nivel se **calcula** (cantidad de estructuras activas y población cercana), no se agrega al motor | Medio |
| 4 | Caminos y migraciones | **Sí** | `agent_snapshots` guarda la posición diaria de cada persona en la BD. El centro de cada tribu día a día da su ruta; `tribe_flows.csv` dice cuándo hubo movimiento | Medio |
| 5 | El mapa reacciona a los acontecimientos | **Sí, acotado** | Nacimientos, muertes, cismas, mitos y catástrofes tienen día y lugar. Un pulso breve en el hex donde ocurrió. **"Guerra entre tribus" no**: el motor no tiene violencia organizada entre tribus (solo choques entre dos personas), así que dibujar frentes de batalla sería inventar | Medio |
| 6 | Biomas que evolucionan (explotado → abandonado → regenerado) | **Parcial** | El agotamiento sale de los recursos por hex; "cicatriz ecológica" ya es una marca psíquica. El ciclo completo de deforestación no existe en el motor: mostrar agotamiento y cicatriz, no más | Bajo |
| 7 | Población viva al hacer zoom | **Parcial** | Ya están todos los datos (humor, arquetipo, tribu, vínculos). El límite es Plotly: re-dibujar por nivel de zoom exige escuchar el zoom desde NiceGUI | Alto |
| 8 | Niebla cognitiva (baja observabilidad) | **Más adelante** | Hoy la niebla es "no explorado". Una "observabilidad" necesita definirse primero (¿cuántos datos hay de ese hex? ¿cuánto tiempo sin presencia?). Sin esa definición sería decorado. Vale un ADR chico | Medio |
| 9 | Fenómenos liminales con campo de influencia | **Sí** | `liminal_hexes` tiene coordenada y misterio. Un halo radial cuyo radio y opacidad dependan del misterio | Bajo |
| 10 | Zoom semántico en 4 niveles | **Más adelante** | Conceptualmente es lo mejor de la propuesta, pero con Plotly es un parche. Si se hace, conviene pasar el mapa a un canvas propio (SVG/Canvas con NiceGUI), y eso es un proyecto aparte | Alto |
| — | Mapa en el 60–70 % del monitor | **Sí** | Es diseño de página: va con la fase 3 del rediseño | Bajo |

## Orden propuesto

1. **Capa "memoria del territorio"** (marcas psíquicas) y **halo liminal**: datos que ya
   existen y no se ven. Es lo que más cambia la lectura del mapa por menos trabajo.
2. **Influencia por tribu** difusa y **asentamientos derivados**.
3. **Mapa al 60–70 %** del monitor, con las capas en un costado (fase 3 del rediseño).
4. **Rutas de migración** desde la BD, ligadas a una línea de tiempo (la "Temporal Rail").
5. Recién después, con un ADR: **niebla cognitiva** y **zoom semántico**, que piden
   definir qué es "observabilidad" y probablemente salir de Plotly.

Todo lo de los puntos 1 a 4 es capa de presentación: lee el estado y no lo modifica,
así que no afecta la reproducibilidad de las corridas ni los tests del motor.

## Lo que no tomaría

- **Fronteras rígidas y jurisdicción.** Las tribus de Psyche son clusters de vínculos
  que se recalculan cada 30 días; una frontera dura afirmaría un territorio que el
  modelo no tiene.
- **Guerras, ciudades con nombre propio, reinos.** Son mecánicas de WorldBox escritas a
  mano. Si aparecen en el mapa sin existir en el motor, el mapa deja de ser un
  instrumento.
