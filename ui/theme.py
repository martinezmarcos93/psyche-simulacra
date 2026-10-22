"""Tema visual "Instrumento" para las interfaces NiceGUI de PSYCHE SIMULACRA.

Una consola de investigación: fondo azul pizarra con retícula de laboratorio,
tipografía Instrument (serif para títulos, sans para la interfaz) y el color
usado como información: cada escenario tiene su color y lo conserva en la
tarjeta, la tabla y los gráficos.

Este módulo solo aporta estilos: no registra callbacks ni toca la simulación.
Las fuentes se sirven localmente desde /assets/fonts (funciona sin internet).
"""
from __future__ import annotations

# ── Tokens (también los usan los gráficos Plotly) ────────────────────────────
ABISMO = "#0E1420"      # fondo
PIZARRA = "#161E2C"     # superficies
PIZARRA_ALTA = "#1C2638"  # superficies anidadas
RETICULA = "#2A3547"    # líneas y bordes
TIZA = "#E6EAF0"        # texto
NIEBLA = "#8B97AA"      # texto secundario
IRIS = "#8B7BFF"        # acción principal / foco
LIQUEN = "#4FD1A5"      # Mundo libre
AMBAR = "#F2B544"       # Orden permanente
GRANADA = "#FF5D73"     # Edén
ALERTA = "#FF6B5B"      # errores / peligro

COLOR_ESCENARIO = {"off": LIQUEN, "orden": AMBAR, "eden": GRANADA}

# Variantes por réplica dentro de un mismo escenario (de más a menos intenso)
TONOS_ESCENARIO = {
    "off": [LIQUEN, "#8FE6C5", "#2FA37E", "#B9F0DC"],
    "orden": [AMBAR, "#F8D387", "#C98D1F", "#FBE4B5"],
    "eden": [GRANADA, "#FF9AA8", "#D63A52", "#FFC2CB"],
}

FUENTE_UI = "'Instrument Sans', system-ui, sans-serif"
FUENTE_TITULO = "'Instrument Serif', Georgia, serif"

PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": TIZA, "family": FUENTE_UI, "size": 12},
}


THEME_CSS = r"""
@font-face {
  font-family: 'Instrument Sans';
  font-style: normal; font-display: swap; font-weight: 400 700;
  src: url('/assets/fonts/instrument-sans-latin-wght-normal.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC,
                 U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193,
                 U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Instrument Sans';
  font-style: normal; font-display: swap; font-weight: 400 700;
  src: url('/assets/fonts/instrument-sans-latin-ext-wght-normal.woff2') format('woff2');
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF,
                 U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF,
                 U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}
@font-face {
  font-family: 'Instrument Serif';
  font-style: normal; font-display: swap; font-weight: 400;
  src: url('/assets/fonts/instrument-serif-latin-400-normal.woff2') format('woff2');
}

:root {
  color-scheme: dark;
  --abismo: #0E1420;
  --pizarra: #161E2C;
  --pizarra-alta: #1C2638;
  --reticula: #2A3547;
  --reticula-suave: rgba(42, 53, 71, .55);
  --tiza: #E6EAF0;
  --niebla: #8B97AA;
  --iris: #8B7BFF;
  --iris-tenue: rgba(139, 123, 255, .14);
  --liquen: #4FD1A5;
  --ambar: #F2B544;
  --granada: #FF5D73;
  --alerta: #FF6B5B;
  --ui: 'Instrument Sans', system-ui, sans-serif;
  --titulo: 'Instrument Serif', Georgia, serif;
}

/* ── Base ─────────────────────────────────────────────────────────────── */
html, body, body.body, #q-app {
  background-color: var(--abismo) !important;
  color: var(--tiza);
}
body {
  /* Retícula de laboratorio: papel milimetrado muy tenue */
  background-image:
    linear-gradient(rgba(139,151,170,.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139,151,170,.045) 1px, transparent 1px) !important;
  background-size: 24px 24px !important;
  font-feature-settings: "tnum" 1;
}
body, .q-field, .q-table, .q-tab, .q-btn, .q-item, .q-checkbox, .q-radio,
.q-toggle, .q-expansion-item, .q-badge, .q-notification, .q-tooltip, input, select {
  font-family: var(--ui) !important;
}
.q-page, .q-page-container { background: transparent !important; }
a { color: var(--iris); }
a:hover { color: #B3A8FF; }
::selection { background: var(--iris-tenue); }

/* Utilidades de Tailwind que usa el código: se reasignan a los tokens */
.text-gray-100, .text-gray-200, .text-white { color: var(--tiza) !important; }
.text-gray-300, .text-gray-400, .text-gray-500 { color: var(--niebla) !important; }
.text-purple-200, .text-purple-300 { color: #C9C1FF !important; }
.bg-gray-950, .bg-gray-900, .bg-purple-950, .bg-purple-900 { background: transparent !important; }
.bg-gray-800 { background: var(--pizarra-alta) !important; }
.text-green-300, .text-green-400 { color: var(--liquen) !important; }
.text-blue-300 { color: #8FB3FF !important; }
.text-yellow-300, .text-yellow-400, .text-amber-400 { color: var(--ambar) !important; }
.text-red-400 { color: var(--alerta) !important; }

/* ── Superficies: jerarquía por borde, no por sombra ─────────────────── */
.q-card {
  color: var(--tiza) !important;
  background: var(--pizarra) !important;
  border: 1px solid var(--reticula) !important;
  border-radius: 14px !important;
  box-shadow: none !important;
}
.q-card .q-card {
  background: var(--pizarra-alta) !important;
  border-radius: 10px !important;
}
.q-separator { background: var(--reticula) !important; }

/* ── Controles ────────────────────────────────────────────────────────── */
.q-btn { border-radius: 8px; font-weight: 600; letter-spacing: 0; text-transform: none !important; }
.q-btn--flat:hover, .q-btn--outline:hover { background: var(--iris-tenue) !important; }
.q-btn--outline:before { border-color: var(--reticula) !important; }
.q-field__label { color: var(--niebla) !important; }
.q-field__native, .q-field__input { color: var(--tiza) !important; }
.q-field--standard .q-field__control:before { border-bottom-color: var(--reticula) !important; }
.q-field--standard .q-field__control:hover:before { border-bottom-color: var(--niebla) !important; }
.q-field--focused .q-field__control:after { border-color: var(--iris) !important; }
.q-field--focused .q-field__label { color: var(--iris) !important; }
.q-field--error .q-field__control:after, .q-field--error .q-field__control:before { border-color: var(--alerta) !important; }
.q-field__bottom { color: var(--niebla) !important; }
.q-menu, .q-select__dialog {
  background: var(--pizarra-alta) !important;
  color: var(--tiza) !important;
  border: 1px solid var(--reticula);
  border-radius: 10px;
}
.q-item--active, .q-item--active .q-item__label { color: var(--iris) !important; }
.q-checkbox__inner--truthy, .q-radio__inner--truthy, .q-toggle__inner--truthy { color: var(--iris) !important; }
.q-toggle__inner--truthy .q-toggle__track { opacity: .55; }

.q-expansion-item {
  border-top: 1px solid var(--reticula);
  background: transparent;
}
.q-expansion-item:last-of-type { border-bottom: 1px solid var(--reticula); }
.q-expansion-item__container > .q-item { min-height: 50px; padding-inline: 4px; }
.q-expansion-item__container > .q-item:hover { background: rgba(139,151,170,.05); }
.q-expansion-item__container > .q-item .q-item__label { font-weight: 550; }
.q-expansion-item--expanded > .q-expansion-item__container > .q-item { color: #C9C1FF; }
.q-expansion-item__content > div { padding: 4px 4px 18px; }

.q-tooltip {
  background: var(--pizarra-alta) !important;
  color: var(--tiza) !important;
  border: 1px solid var(--reticula);
  border-radius: 8px !important;
  font-size: 12px !important;
}
.q-notification { border-radius: 10px !important; }
.q-dialog__inner > div {
  background: var(--pizarra) !important;
  color: var(--tiza) !important;
  border: 1px solid var(--reticula);
  border-radius: 14px;
}

/* ── Tablas ───────────────────────────────────────────────────────────── */
.q-table__container {
  background: transparent !important;
  border: 1px solid var(--reticula);
  border-radius: 10px;
  overflow: hidden;
}
.q-table thead tr { background: rgba(28,38,56,.8); }
.q-table th {
  color: var(--niebla) !important;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: .01em;
  text-transform: none;
}
.q-table tbody td { border-color: var(--reticula-suave) !important; font-variant-numeric: tabular-nums; }
.q-table tbody tr:hover { background: rgba(139,123,255,.06) !important; }
.q-table__bottom { color: var(--niebla); }
.ps-runs-table .q-table__middle, .ps-agents-table .q-table__middle, .ps-network-table {
  max-width: 100%; overflow-x: auto; overscroll-behavior-x: contain;
  scrollbar-width: thin; scrollbar-color: var(--reticula) transparent;
}
.ps-runs-table .q-table { min-width: 860px; }
.ps-agents-table .q-table { min-width: 760px; }

/* Píldoras de estado de una corrida */
.ps-fase {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 2px 9px; border-radius: 999px;
  font-size: 12px; font-weight: 600; line-height: 20px;
  border: 1px solid currentColor;
  background: transparent;
}
.ps-fase::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.ps-fase--corriendo, .ps-fase--iniciando { color: var(--iris); }
.ps-fase--corriendo::before { animation: ps-latido 1.6s ease-in-out infinite; }
.ps-fase--en_cola, .ps-fase--pausada, .ps-fase--deteniendo { color: var(--ambar); }
.ps-fase--terminada { color: var(--niebla); }
.ps-fase--extinta { color: var(--granada); }
.ps-fase--detenida { color: #B6A58C; }
.ps-fase--error, .ps-fase--interrumpida { color: var(--alerta); }
@keyframes ps-latido { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }

/* Marca de escenario (punto de color) */
.ps-esc { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; vertical-align: 1px; }
.ps-esc--off { background: var(--liquen); }
.ps-esc--orden { background: var(--ambar); }
.ps-esc--eden { background: var(--granada); }

/* ── Panel: estructura ───────────────────────────────────────────────── */
.ps-main-header {
  min-height: 64px !important;
  padding: 0 28px !important;
  gap: 14px !important;
  background: rgba(14,20,32,.86) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--reticula) !important;
  box-shadow: none !important;
}
.ps-brand-seal {
  width: 30px !important; height: 30px !important; flex: 0 0 30px;
  background: var(--iris);
  -webkit-mask: url('/assets/psyche-seal.svg') center / contain no-repeat;
          mask: url('/assets/psyche-seal.svg') center / contain no-repeat;
}
.ps-brand-mark {
  font-family: var(--titulo) !important;
  font-size: 1.6rem !important; font-weight: 400 !important;
  letter-spacing: .01em !important; text-transform: none !important;
  color: var(--tiza) !important; white-space: nowrap;
}
.ps-brand-subtitle { color: var(--niebla) !important; font-size: 14px !important; white-space: nowrap; }
.ps-guide-link { color: var(--tiza) !important; font-size: 14px; text-decoration: none; padding: 6px 12px; border: 1px solid var(--reticula); border-radius: 8px; }
.ps-guide-link:hover { border-color: var(--iris); }

.ps-app-layout { gap: 0 !important; align-items: stretch !important; min-height: calc(100vh - 64px); }
.ps-sidebar {
  width: 196px !important; min-width: 196px !important; flex: 0 0 196px;
  padding: 24px 12px !important; gap: 2px !important;
  border-right: 1px solid var(--reticula);
  position: sticky; top: 64px; align-self: flex-start; height: calc(100vh - 64px);
}
.ps-nav-link {
  display: flex !important; align-items: center; min-height: 40px; padding: 0 12px;
  border-radius: 8px; color: var(--niebla) !important;
  font-size: 14px; font-weight: 550; text-decoration: none !important;
}
.ps-nav-link:hover { color: var(--tiza) !important; background: rgba(139,151,170,.08); }

.ps-page-shell { flex: 1 1 auto; min-width: 0; max-width: 1360px; padding: 28px 28px 48px !important; gap: 20px !important; }
.ps-dashboard-top { align-items: flex-start !important; gap: 20px !important; }
.ps-dashboard-main { flex: 1 1 auto; min-width: 0; }

.ps-hero-card, .ps-runs-card, .ps-compare-card { padding: 26px 28px !important; width: 100%; min-width: 0; }
.ps-hero-heading-row { margin-bottom: 2px; }
.ps-section-heading {
  font-family: var(--titulo) !important;
  font-size: 2rem !important; line-height: 1.1 !important;
  font-weight: 400 !important; letter-spacing: 0 !important; text-transform: none !important;
  color: var(--tiza) !important;
}
.ps-section-description { max-width: 70ch; color: var(--niebla) !important; font-size: 14px !important; line-height: 1.6 !important; }

/* Escenarios: el glifo se pinta con el color del escenario */
.ps-scenario-grid { display: grid !important; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px !important; margin: 18px 0 6px; }
.ps-scenario-card {
  --esc: var(--niebla);
  position: relative; min-width: 0 !important; min-height: 132px;
  padding: 16px 16px 16px 92px !important;
  background: var(--pizarra-alta) !important;
  border: 1px solid var(--reticula) !important;
  border-radius: 12px !important;
  transition: border-color .15s ease, background .15s ease;
}
.ps-scenario-off { --esc: var(--liquen); }
.ps-scenario-orden { --esc: var(--ambar); }
.ps-scenario-eden { --esc: var(--granada); }
.ps-scenario-card::before {
  content: ""; position: absolute; left: 14px; top: 18px; width: 62px; height: 62px;
  background: var(--esc); opacity: .55;
  -webkit-mask: var(--glifo) center / contain no-repeat; mask: var(--glifo) center / contain no-repeat;
}
.ps-scenario-off::before { --glifo: url('/assets/scenario-mundo-libre.svg'); }
.ps-scenario-orden::before { --glifo: url('/assets/scenario-orden.svg'); }
.ps-scenario-eden::before { --glifo: url('/assets/scenario-eden.svg'); }
.ps-scenario-card .q-checkbox { margin: -6px 0 2px -8px; }
.ps-scenario-card .q-checkbox__label { font-family: var(--titulo); font-size: 1.35rem; color: var(--tiza); }
.ps-scenario-card .q-checkbox__inner--truthy { color: var(--esc) !important; }
.ps-scenario-description { color: var(--niebla) !important; font-size: 13px !important; line-height: 1.5 !important; }
.ps-scenario-card:has(.q-checkbox__inner--truthy) {
  border-color: var(--esc) !important;
  background: linear-gradient(0deg, color-mix(in srgb, var(--esc) 7%, transparent), color-mix(in srgb, var(--esc) 7%, transparent)), var(--pizarra-alta) !important;
}
.ps-scenario-card:has(.q-checkbox__inner--truthy)::before { opacity: 1; }

.ps-primary-fields { display: grid !important; grid-template-columns: 1.4fr .7fr .6fr 1.5fr; gap: 16px !important; align-items: end; margin: 8px 0 14px; }
.ps-primary-fields > * { min-width: 0 !important; width: 100% !important; }
.ps-duration-row { margin: 4px 0 10px; }
.ps-run-summary { color: var(--niebla) !important; font-size: 14px !important; margin-top: 18px; }
.ps-launch-btn, .ps-accion {
  min-height: 44px; padding: 0 26px !important; font-size: 15px !important;
  color: #120F2E !important;
}
.ps-launch-btn:hover, .ps-accion:hover { filter: brightness(1.12); }
.q-btn.ps-accion.ps-pausada { background: var(--ambar) !important; }
.ps-accion { min-height: 30px; padding: 0 12px !important; font-size: 13px !important; }

/* Estado del laboratorio */
.ps-lab-status-card { width: 270px !important; flex: 0 0 270px; padding: 22px 20px !important; position: sticky; top: 92px; }
.ps-lab-status-title { font-family: var(--titulo); font-size: 1.35rem; color: var(--tiza); margin-bottom: 6px; }
.ps-status-list { width: 100%; gap: 0 !important; }
.ps-status-row { width: 100%; min-height: 38px; gap: 10px !important; border-bottom: 1px solid var(--reticula-suave); }
.ps-status-icon { width: 16px; color: var(--niebla); font-size: 13px; }
.ps-status-name { color: var(--niebla); font-size: 13px; }
.ps-status-value { color: var(--tiza); font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }
.ps-status-dot { font-size: 9px; color: var(--reticula); }
.ps-status-dot.is-ready { color: var(--liquen); }
.ps-status-dot.is-idle { color: var(--niebla); }
.ps-status-dot.is-off { color: var(--alerta); }
.ps-active-runs { padding: 16px 0 2px; }
.ps-panel-title { color: var(--niebla); font-size: 13px; }
.ps-active-count { font-family: var(--titulo); font-size: 2.4rem; line-height: 1; color: var(--tiza); font-variant-numeric: tabular-nums; }
.ps-status-caption { color: var(--niebla) !important; font-size: 12px !important; line-height: 1.5; }

.ps-chart-frame { border-top: 1px solid var(--reticula); margin-top: 8px; }

/* ── Monitor de una corrida ───────────────────────────────────────────── */
.ps-monitor-header {
  min-height: 60px; padding: 8px 24px !important; gap: 18px !important;
  background: rgba(14,20,32,.9) !important; backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--reticula); box-shadow: none !important;
}
.ps-monitor-header .ps-brand-mark { font-size: 1.35rem !important; }
.ps-monitor-stats > * { white-space: nowrap; font-variant-numeric: tabular-nums; }
.ps-monitor-tabs {
  position: sticky; top: 0; z-index: 10;
  background: rgba(14,20,32,.92) !important; backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--reticula);
}
.ps-monitor-tabs .q-tab { text-transform: none; font-size: 14px; font-weight: 550; color: var(--niebla); }
.q-tab--active { color: var(--tiza) !important; }
.q-tab__indicator { background: var(--iris) !important; height: 2px !important; }
.q-tab .q-tab__label { text-transform: none; }
.ps-monitor-panels, .ps-monitor-panels .q-tab-panel { background: transparent !important; }
.ps-monitor-panels > .q-tab-panel { padding: 18px 20px 32px; }
.ps-stat-card { min-height: 92px; }
.ps-stat-card .text-xs { text-transform: none !important; letter-spacing: 0 !important; font-size: 13px !important; color: var(--niebla) !important; }
.ps-stat-card .text-xl, .ps-stat-card .text-lg {
  font-family: var(--titulo); font-weight: 400 !important; font-size: 2rem !important;
  line-height: 1.1; color: var(--tiza) !important; font-variant-numeric: tabular-nums;
}
.ps-pressure-card .text-lg { font-size: 1.8rem !important; }
.ps-summary-grid { grid-template-columns: repeat(4, minmax(0,1fr)); }
.ps-summary-grid--three { grid-template-columns: repeat(3, minmax(0,1fr)); }
/* Subtítulos del monitor: sin mayúsculas forzadas */
.ps-monitor-panels .uppercase {
  text-transform: none !important; letter-spacing: 0 !important;
  font-size: 13px !important; font-weight: 600; color: var(--niebla) !important;
}
.ps-monitor-panels .q-log { border: 1px solid var(--reticula); border-radius: 10px; background: rgba(14,20,32,.6) !important; }
.ps-monitor-panels .modebar { opacity: .35; transition: opacity .15s ease; }
.ps-monitor-panels .js-plotly-plot:hover .modebar { opacity: 1; }
.ps-map-plot, .ps-network-plot, .ps-liminal-plot { border: 1px solid var(--reticula); border-radius: 12px; overflow: hidden; }
.ps-network-table { border: 1px solid var(--reticula); border-radius: 10px; }
.ps-network-table table { border-collapse: collapse; min-width: 620px; }
.ps-network-table th { padding: 9px 10px !important; color: var(--niebla) !important; background: var(--pizarra-alta); font-size: 12px !important; text-align: left; }
.ps-network-table td { padding: 7px 10px !important; border-bottom: 1px solid var(--reticula-suave); font-size: 13px; }
.ps-agents-table .q-table__middle { max-height: 62vh; }
.ps-agents-table tbody tr { cursor: pointer; }
.ps-lore-panel { line-height: 1.6; overflow-wrap: anywhere; }
.ps-lore-panel th { padding: 8px 10px; color: var(--niebla); background: var(--pizarra-alta); font-size: 12px; text-align: left; }
.ps-lore-panel td { padding: 7px 10px; border-bottom: 1px solid var(--reticula-suave); vertical-align: top; }
.ps-lore-panel table { width: 100%; border-collapse: collapse; }

/* ── Accesibilidad ────────────────────────────────────────────────────── */
:focus-visible { outline: 2px solid var(--iris) !important; outline-offset: 3px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}

/* ── Anchos intermedios y celular ─────────────────────────────────────── */
@media (max-width: 1200px) {
  .ps-dashboard-top { flex-wrap: wrap !important; }
  .ps-lab-status-card { position: static; width: 100% !important; flex: 1 1 100%; }
}
@media (max-width: 900px) {
  .ps-brand-subtitle { display: none !important; }
  .ps-scenario-grid { grid-template-columns: 1fr; }
  .ps-primary-fields { grid-template-columns: repeat(2, minmax(0,1fr)); }
  .ps-monitor-header { flex-wrap: wrap; gap: 8px !important; }
  .ps-monitor-stats { order: 10; flex: 1 1 100% !important; margin-left: 0 !important; gap: 14px !important; }
  .ps-monitor-tabs { overflow-x: auto; }
}
@media (max-width: 700px) {
  .ps-sidebar { display: none !important; }
  .ps-main-header { padding: 0 14px !important; }
  .ps-page-shell { padding: 14px !important; }
  .ps-hero-card, .ps-runs-card, .ps-compare-card { padding: 18px 16px !important; }
  .ps-section-heading { font-size: 1.6rem !important; }
  .ps-primary-fields > *:nth-child(4) { grid-column: 1 / -1; }
  .ps-summary-grid, .ps-summary-grid--three { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
  .ps-monitor-panels > .q-tab-panel { padding: 10px 6px 20px; }
}
@media (max-width: 420px) {
  .ps-summary-grid, .ps-summary-grid--three { grid-template-columns: minmax(0,1fr) !important; }
}
"""


def apply_theme(ui) -> None:
    """Inyecta el tema en la página actual; seguro de invocar por página."""
    # Colores de marca de Quasar: botones, casillas, radios e interruptores
    ui.colors(primary=IRIS, secondary=PIZARRA_ALTA, accent=IRIS, dark=ABISMO,
              positive=LIQUEN, negative=ALERTA, warning=AMBAR, info="#8FB3FF")
    ui.add_head_html(f"<style id='psyche-simulacra-theme'>{THEME_CSS}</style>")
    ui.query("body").classes("bg-gray-950 text-gray-100")
