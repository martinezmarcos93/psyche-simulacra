# Punto de control

<!-- PUNTO-DE-CONTROL -->
**Actualizado:** 2026-11-15

**Tarea actual:** rediseño «Laboratorio de Fenómenos» mergeado a `main` (`adba984`):
fases 1–2 y la pestaña «Mundo» como principal del monitor. Detalle del 14/11 en
`docs/handoffs/2026-11-14.md`.

**Decisiones de Marcos (15/11):**
- Natalidad: los valores quedan configurables por el usuario; **no cambiar defaults**.
- Modelo de adicción: todavía no se toca.
- Mapa: pidió más explicación de `docs/proposals/2026-11-14-mapa-observatorio-revision.md`
  antes de elegir qué entra.

**Próximo paso:** según lo que elija del mapa, empezar por la capa «memoria del
territorio» (marcas de `core/world/psychic_geography.py`) y el halo liminal.

**Pendientes:**
- Probar el instalador en un Windows real (`packaginguild.bat`).
- Narrativa en la entrega al sociólogo: recomendado apagada (ya es el default).
- Ramas viejas `ui/reconstruction-observatory` y `ui/tema-instrumento`: ya están en
  `main`; borrarlas si Marcos da el OK.

**Bloqueos:** ninguno.

**Notas:** suite completa ~40 min con `PYTHONHASHSEED=0` (582 passed el 14/11); no hay CI.
<!-- /PUNTO-DE-CONTROL -->
