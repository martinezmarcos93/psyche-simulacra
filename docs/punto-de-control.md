# Punto de control

<!-- PUNTO-DE-CONTROL -->
**Actualizado:** 2026-11-10

**Estado:** `main` es la única rama. Contiene el panel multicorrida, EDEN, la
recalibración arquetípica y el tema visual "Instrumento" (squash `8b35d71` de
`ui/reconstruction-observatory` + `ui/tema-instrumento`, ambas borradas).

**Próximo paso:** construir y probar el instalador en un Windows real
(`packaging\build.bat`): SmartScreen sin firma, Documentos en OneDrive, antivirus.

**Pendientes:**
- Pasar a la paleta del tema los colores propios del mapa (biomas) y de la red social.
- Natalidad casi nula con los valores por defecto: decidir valores recomendados.
- Decidir si la entrega al sociólogo lleva narrativa (Ollama) o no (hoy viene apagada).
- Qué datos comparar entre corridas además de población y tribus.

**Bloqueos:** ninguno.

**Notas:** suite completa ~30 min con `PYTHONHASHSEED=0`; no hay CI en GitHub.
<!-- /PUNTO-DE-CONTROL -->
