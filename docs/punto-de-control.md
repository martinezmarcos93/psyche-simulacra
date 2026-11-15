# Punto de control

<!-- PUNTO-DE-CONTROL -->
**Actualizado:** 2026-11-14

**Tarea actual:** cerrados los pendientes del 13/11 (detalle en `docs/handoffs/2026-11-14.md`):
flujos en el panel, bug de muertes de la prehistoria, paleta del mapa y la red, natalidad
(causa raíz: fatiga crónica por abstinencia; nuevo ajuste `REPRO_FATIGA_MAX`).

**Próximo paso:** que Marcos decida (1) defaults de natalidad, (2) si mergea la rama
`ui/laboratorio-fenomenos` (worktree `~/src/psyche-laboratorio`, rebase antes), (3) qué
entra del mapa según `docs/proposals/2026-11-14-mapa-observatorio-revision.md`.
Después: punto 3 de la propuesta WorldBox (intervenciones programadas).

**Pendientes:**
- Probar el instalador en un Windows real (`packaginguild.bat`).
- Modelo de adicción: la abstinencia sin techo agota a toda la población (decisión de modelo).
- Narrativa en la entrega al sociólogo: recomendado apagada (ya es el default).

**Bloqueos:** ninguno.

**Notas:** suite completa ~35–45 min con `PYTHONHASHSEED=0`; no hay CI en GitHub.
`scripts/calibrar_natalidad.py`: con 100 personas, ~1 año simulado cada 20–25 min.
<!-- /PUNTO-DE-CONTROL -->
