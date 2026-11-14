# Punto de control

<!-- PUNTO-DE-CONTROL -->
**Actualizado:** 2026-11-13

**Tarea actual:** punto 2 de `docs/proposals/2026-11-10-worldbox-ideas-aplicables.md`
(contadores de flujo por tribu), elegido por Marcos el 13/11. Implementado en
`core/metrics/flujos.py` + columnas nuevas en `DayMetrics` + `tribe_flows.csv`;
tests en `tests/test_flujos.py`. Suite completa 574 passed (13/11); commiteado y
pusheado a `main`. Detalle en `docs/handoffs/2026-11-13.md`.

**Próximo paso:** mostrar los flujos en el panel multicorrida (`ui/hub.py`, hoy solo
grafica `n_alive` y `n_tribes`); después, punto 3 (intervenciones programadas).

**Pendientes:**
- Probar el instalador en un Windows real (`packaging\build.bat`).
- Pasar a la paleta del tema los colores propios del mapa (biomas) y de la red social.
- Natalidad casi nula con los valores por defecto: decidir valores recomendados.
- Decidir si la entrega al sociólogo lleva narrativa (Ollama) o no (hoy viene apagada).
- Revisar: tras la prehistoria `_death_cursor` vuelve a 0, así que las muertes de la
  prehistoria podrían registrarse en la BD el día 1 (los flujos no tienen ese problema).

**Bloqueos:** ninguno.

**Notas:** suite completa ~30 min con `PYTHONHASHSEED=0`; no hay CI en GitHub.
<!-- /PUNTO-DE-CONTROL -->
