# Punto de control

<!-- PUNTO-DE-CONTROL -->
**Actualizado:** 2026-11-15

**Tarea actual:** ninguna en curso. Rediseño «Laboratorio de Fenómenos» ya en `main`
(`adba984`); solo existe la rama `main`. Detalle en `docs/handoffs/2026-11-15.md`.

**Próximo paso:** preguntarle a Marcos qué capas del mapa entran
(`docs/proposals/2026-11-14-mapa-observatorio-revision.md`). Recomendado empezar por
A (memoria del territorio: marcas de `core/world/psychic_geography.py`) y B (halo
liminal), ambas solo en `_build_hex_map` de `ui/psyche_ui.py`.

**Decisiones tomadas (15/11):** natalidad configurable por el usuario, no cambiar
defaults; modelo de adicción, todavía no.

**Pendientes:**
- Probar el instalador en un Windows real (`packaginguild.bat`).
- Narrativa en la entrega al sociólogo: recomendado apagada (ya es el default).
- Punto 3 de la propuesta WorldBox: intervenciones programadas.

**Bloqueos:** ninguno.

**Archivos en curso:** ninguno.

**Notas:** suite completa ~40 min con `PYTHONHASHSEED=0`; no hay CI.
<!-- /PUNTO-DE-CONTROL -->
