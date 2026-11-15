"""Tema visual "Laboratorio de Fenómenos" para las interfaces NiceGUI de PSYCHE SIMULACRA.

Un observatorio, no un tablero: negro mineral, mucho espacio negativo, campos
separados por líneas finas en lugar de tarjetas, rótulos de instrumento en
versalitas y cifras en monoespaciada. Serif solo para la marca y los nombres
propios. El color es información: violeta = lo que el sistema interpreta
(psique), turquesa = lo que observa (fenómeno), y cada escenario conserva su
color en la tarjeta, la tabla y los gráficos.

Este módulo solo aporta estilos: no registra callbacks ni toca la simulación.
Las fuentes se sirven localmente desde /assets/fonts (funciona sin internet).
"""
from __future__ import annotations

# ── Tokens (también los usan los gráficos Plotly) ────────────────────────────
ABISMO = "#080B10"      # fondo: negro mineral
PIZARRA = "#10151D"     # superficies
PIZARRA_ALTA = "#151C26"  # superficies anidadas
RETICULA = "#232C3A"    # líneas y bordes
TIZA = "#E8EBF0"        # texto
NIEBLA = "#7D8795"      # texto secundario
IRIS = "#9A8CFF"        # psique / interpretación; acción principal y foco
TURQUESA = "#62D9C3"    # observación / fenómeno
LIQUEN = "#8BD07A"      # Mundo libre
AMBAR = "#F2B544"       # Orden permanente
GRANADA = "#FF5D73"     # Edén
ALERTA = "#FF6B5B"      # errores / peligro

COLOR_ESCENARIO = {"off": LIQUEN, "orden": AMBAR, "eden": GRANADA}

# Variantes por réplica dentro de un mismo escenario (de más a menos intenso)
TONOS_ESCENARIO = {
    "off": [LIQUEN, "#B5E3A8", "#5FA34F", "#D3F0CB"],
    "orden": [AMBAR, "#F8D387", "#C98D1F", "#FBE4B5"],
    "eden": [GRANADA, "#FF9AA8", "#D63A52", "#FFC2CB"],
}

# ── Mapa hexagonal ───────────────────────────────────────────────────────────
# Biomas en tonos apagados, para que personas y estructuras se lean encima.
BIOMAS: dict[str, str] = {
    "bosque_templado":  "#2F6B4F",
    "pradera_humeda":   "#6E9A5B",
    "rio_lago":         "#3E7FB8",
    "montana_alta":     "#8E97A6",
    "sabana_abierta":   "#C2A257",
    "pantano_costero":  "#4A7A72",
    "cueva":            "#454C5E",
    "valle_fertil":     "#4FAE7C",
    "costa_abierta":    "#5B93C4",
    "desierto_borde":   "#D1B06B",
    "colinas_suaves":   "#8C9B62",
    "lago_interior":    "#2C5F96",
}
BIOMA_DESCONOCIDO = "#5A5478"
MAPA_NIEBLA = "#0A0F19"        # hexes sin explorar
MAPA_CONTORNO = ABISMO         # borde de personas y estructuras
MAPA_PORTAL = "#C9BFFF"        # relleno del portal liminal (borde IRIS)
MAPA_TUMBA = "#B8C0CC"
MAPA_FAUNA = AMBAR
MAPA_FUEGO = ALERTA
MAPA_MUERTO = "#6B7688"
# tipo de estructura → (símbolo Plotly, color, tamaño)
MAPA_ESTRUCTURAS: dict[str, tuple[str, str, int]] = {
    "totem":    ("diamond",         "#C9A2FF", 16),
    "altar":    ("triangle-up",     AMBAR,     16),
    "muralla":  ("square",          "#9AA5B5", 14),
    "hoguera":  ("circle",          "#FF8A5B", 14),
    "refugio":  ("pentagon",        LIQUEN,    13),
    "marcador": ("cross-thin-open", NIEBLA,    12),
    "deposito": ("hexagon2-open",   "#C98D1F", 13),
}
MAPA_ESTRUCTURA_DESCONOCIDA = ("circle-open", NIEBLA, 12)

# ── Red social ───────────────────────────────────────────────────────────────
RED_ENTRELAZADO = IRIS
RED_LAZO_POSITIVO = LIQUEN
RED_LAZO_NEGATIVO = GRANADA
RED_MUERTO = NIEBLA
# Humor de cada persona (relleno del nodo): bajo, medio, alto
RED_HUMOR_BAJO, RED_HUMOR_MEDIO, RED_HUMOR_ALTO = GRANADA, AMBAR, LIQUEN
# Borde del nodo: una tribu, un color
RED_TRIBUS = ["#8FB3FF", "#F8D387", "#B9F0DC", "#C9A2FF", "#FF9AA8", "#7FD6E8", "#FF8A5B",
              "#8B7BFF", "#2FA37E", "#C98D1F", "#D63A52", "#5B93C4", "#E6EAF0"]

# Sello visible en el panel y en el monitor: postura epistemológica de la interfaz
# (pausar o cambiar la velocidad no altera el estado del mundo simulado).
MODO_OBSERVACION = "<b>●</b> Modo observación<br>la interfaz no modifica el mundo"

LEYENDA_FONDO = "rgba(14,20,32,.72)"   # ABISMO translúcido


def color_humor(humor: float) -> str:
    """Color del humor de una persona (0–1) en la red social."""
    return RED_HUMOR_BAJO if humor < 0.35 else RED_HUMOR_MEDIO if humor < 0.65 else RED_HUMOR_ALTO


FUENTE_UI = "'Instrument Sans', system-ui, sans-serif"
FUENTE_TITULO = "'Instrument Serif', Georgia, serif"
# Cifras, IDs, semillas, días y registros. Fuentes del sistema: funciona sin internet
# (Cascadia Mono/Consolas en Windows, DejaVu Sans Mono en Linux).
FUENTE_MONO = "ui-monospace, 'Cascadia Mono', 'JetBrains Mono', Consolas, 'DejaVu Sans Mono', monospace"

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
  --abismo: #080B10;
  --pizarra: #10151D;
  --pizarra-alta: #151C26;
  --reticula: #232C3A;
  --reticula-suave: rgba(35, 44, 58, .6);
  --tiza: #E8EBF0;
  --niebla: #7D8795;
  --iris: #9A8CFF;
  --iris-tenue: rgba(154, 140, 255, .13);
  --turquesa: #62D9C3;
  --turquesa-tenue: rgba(98, 217, 195, .12);
  --liquen: #8BD07A;
  --ambar: #F2B544;
  --granada: #FF5D73;
  --alerta: #FF6B5B;
  --ui: 'Instrument Sans', system-ui, sans-serif;
  --titulo: 'Instrument Serif', Georgia, serif;
  --mono: ui-monospace, 'Cascadia Mono', 'JetBrains Mono', Consolas, 'DejaVu Sans Mono', monospace;
}

/* ── Base ─────────────────────────────────────────────────────────────── */
html, body, body.body, #q-app {
  background-color: var(--abismo) !important;
  color: var(--tiza);
}
body {
  /* Retícula de laboratorio: papel milimetrado muy tenue */
  background-image:
    radial-gradient(ellipse at 50% -10%, rgba(154,140,255,.07), transparent 60%),
    linear-gradient(rgba(125,135,149,.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(125,135,149,.025) 1px, transparent 1px) !important;
  background-size: 100% 100%, 48px 48px, 48px 48px !important;
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
.text-green-300, .text-green-400 { color: var(--turquesa) !important; }
.text-blue-300 { color: #8FB3FF !important; }
.text-yellow-300, .text-yellow-400, .text-amber-400 { color: var(--ambar) !important; }
.text-red-400 { color: var(--alerta) !important; }

/* ── Superficies: jerarquía por borde, no por sombra ─────────────────── */
/* Campos, no tarjetas: el contenido se separa con una línea fina arriba y aire. */
.q-card {
  color: var(--tiza) !important;
  background: transparent !important;
  border: 0 !important;
  border-top: 1px solid var(--reticula) !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}
.q-card .q-card {
  background: rgba(16,21,29,.7) !important;
  border: 1px solid var(--reticula) !important;
  border-radius: 6px !important;
}
.q-separator { background: var(--reticula) !important; }

/* ── Controles ────────────────────────────────────────────────────────── */
.q-btn { border-radius: 4px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase !important; font-size: 12.5px; }
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
  border: 0;
  border-radius: 0;
  overflow: hidden;
}
.q-table thead tr { background: transparent; }
.q-table th {
  color: var(--niebla) !important;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  border-bottom: 1px solid var(--reticula) !important;
}
.q-table tbody td { border-color: transparent !important; font-variant-numeric: tabular-nums; }
.q-table tbody td:first-child { font-family: var(--mono); font-size: 12.5px; }
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
  display: inline-flex; align-items: center; gap: 7px;
  padding: 0; border-radius: 0;
  font-family: var(--mono); font-size: 11.5px; font-weight: 500; line-height: 20px;
  letter-spacing: .08em; text-transform: uppercase;
  border: 0;
  background: transparent;
}
.ps-fase::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.ps-fase--corriendo, .ps-fase--iniciando { color: var(--turquesa); }
.ps-fase--corriendo::before { animation: ps-latido 1.6s ease-in-out infinite; }
.ps-fase--en_cola, .ps-fase--pausada, .ps-fase--deteniendo { color: var(--ambar); }
.ps-fase--terminada { color: var(--niebla); }
.ps-fase--extinta { color: var(--granada); }
.ps-fase--detenida { color: #B6A58C; }
.ps-fase--error, .ps-fase--interrumpida { color: var(--alerta); }
@keyframes ps-latido { 0%, 100% { opacity: 1; box-shadow: 0 0 0 0 currentColor; } 50% { opacity: .45; box-shadow: 0 0 0 4px transparent; } }

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
  background: rgba(8,11,16,.88) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--reticula) !important;
  box-shadow: none !important;
}
/* Sello institucional: la interfaz observa, no modifica el mundo */
.ps-modo-observacion {
  font-family: var(--mono); font-size: 10.5px; line-height: 1.35; letter-spacing: .14em;
  text-transform: uppercase; color: var(--niebla); text-align: right;
  padding-left: 12px; border-left: 1px solid var(--reticula); white-space: nowrap;
}
.ps-modo-observacion b { color: var(--turquesa); font-weight: 500; }
.ps-ruta {
  font-family: var(--mono); font-size: 11px; letter-spacing: .16em; text-transform: uppercase;
  color: var(--niebla); white-space: nowrap;
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
.ps-brand-subtitle { color: var(--niebla) !important; font-family: var(--mono); font-size: 11px !important; letter-spacing: .16em; text-transform: uppercase; white-space: nowrap; }
.ps-guide-link { color: var(--tiza) !important; font-size: 11.5px; letter-spacing: .12em; text-transform: uppercase; text-decoration: none; padding: 6px 12px; border: 1px solid var(--reticula); border-radius: 4px; }
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
  border-radius: 0; border-left: 1px solid transparent; color: var(--niebla) !important;
  font-size: 11.5px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
  text-decoration: none !important;
}
.ps-nav-link:hover { border-left-color: var(--turquesa); }
.ps-nav-link:hover { color: var(--tiza) !important; background: rgba(139,151,170,.08); }

.ps-page-shell { flex: 1 1 auto; min-width: 0; max-width: 1360px; padding: 36px 40px 64px !important; gap: 44px !important; }
.ps-dashboard-top { align-items: flex-start !important; gap: 20px !important; }
.ps-dashboard-main { flex: 1 1 auto; min-width: 0; }

.ps-hero-card, .ps-runs-card, .ps-compare-card { padding: 22px 0 0 !important; width: 100%; min-width: 0; }
.ps-hero-heading-row { margin-bottom: 2px; }
/* Rótulo de instrumento: versalitas finas con una regla que se extiende */
.ps-section-heading {
  display: flex !important; align-items: center; gap: 14px; width: 100%;
  font-family: var(--ui) !important;
  font-size: 12px !important; line-height: 1.2 !important;
  font-weight: 600 !important; letter-spacing: .2em !important; text-transform: uppercase !important;
  color: var(--tiza) !important; margin-bottom: 6px;
}
.ps-section-heading::after { content: ""; flex: 1; height: 1px; background: var(--reticula); }
.ps-section-description { max-width: 70ch; color: var(--niebla) !important; font-size: 14px !important; line-height: 1.6 !important; }

/* Escenarios: el glifo se pinta con el color del escenario */
.ps-scenario-grid { display: grid !important; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px !important; margin: 18px 0 6px; }
.ps-scenario-card {
  --esc: var(--niebla);
  position: relative; min-width: 0 !important; min-height: 132px;
  padding: 16px 16px 16px 92px !important;
  background: transparent !important;
  border: 1px solid var(--reticula) !important;
  border-radius: 4px !important;
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
.ps-scenario-card .q-checkbox__label { font-family: var(--titulo); font-size: 1.45rem; color: var(--tiza); }
.ps-scenario-card .q-checkbox__inner--truthy { color: var(--esc) !important; }
.ps-scenario-description { color: var(--niebla) !important; font-size: 13px !important; line-height: 1.5 !important; }
.ps-scenario-card:has(.q-checkbox__inner--truthy) {
  border-color: var(--esc) !important;
  background: linear-gradient(0deg, color-mix(in srgb, var(--esc) 6%, transparent), color-mix(in srgb, var(--esc) 6%, transparent)) !important;
}
.ps-scenario-card:has(.q-checkbox__inner--truthy)::before { opacity: 1; }

.ps-primary-fields { display: grid !important; grid-template-columns: 1.4fr .7fr .6fr 1.5fr; gap: 16px !important; align-items: end; margin: 8px 0 14px; }
.ps-primary-fields > * { min-width: 0 !important; width: 100% !important; }
.ps-duration-row { margin: 4px 0 10px; }
.ps-run-summary { color: var(--niebla) !important; font-family: var(--mono); font-size: 12.5px !important; margin-top: 18px; }

/* Protocolo: las secciones de configuración se numeran como pasos (01, 02, …) */
.ps-hero-card { counter-reset: protocolo; }
.ps-config-section:not(.ps-herramienta) > .q-expansion-item__container > .q-item .q-item__label::before {
  counter-increment: protocolo; content: counter(protocolo, decimal-leading-zero);
  font-family: var(--mono); color: var(--turquesa); margin-right: 16px; letter-spacing: .04em;
}
.ps-config-section .q-item__label { letter-spacing: .1em; text-transform: uppercase; font-size: 12.5px; }
.ps-config-section:not(.ps-herramienta) .q-item__section--avatar { display: none; }
.ps-herramienta .q-item__label { color: var(--niebla); }
.ps-launch-btn, .ps-accion {
  min-height: 44px; padding: 0 26px !important; font-size: 15px !important;
  color: #120F2E !important;
}
.ps-launch-btn:hover, .ps-accion:hover { filter: brightness(1.12); }
.q-btn.ps-accion.ps-pausada { background: var(--ambar) !important; }
.ps-accion { min-height: 30px; padding: 0 12px !important; font-size: 13px !important; }

/* Estado del laboratorio */
.ps-lab-status-card { width: 270px !important; flex: 0 0 270px; padding: 22px 0 0 !important; position: sticky; top: 92px; }
.ps-lab-status-title { font-size: 11px; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--tiza); margin-bottom: 6px; }
.ps-status-list { width: 100%; gap: 0 !important; }
.ps-status-row { width: 100%; min-height: 38px; gap: 10px !important; border-bottom: 1px solid var(--reticula-suave); }
.ps-status-icon { width: 16px; color: var(--niebla); font-size: 13px; }
.ps-status-name { color: var(--niebla); font-size: 11px; letter-spacing: .12em; text-transform: uppercase; }
.ps-status-value { color: var(--tiza); font-family: var(--mono); font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }
.ps-status-dot { font-size: 9px; color: var(--reticula); }
.ps-status-dot.is-ready { color: var(--turquesa); }
.ps-status-dot.is-idle { color: var(--niebla); }
.ps-status-dot.is-off { color: var(--alerta); }
.ps-active-runs { padding: 16px 0 2px; }
.ps-panel-title { color: var(--niebla); font-size: 13px; }
.ps-active-count { font-family: var(--mono); font-size: 2rem; font-weight: 300; line-height: 1; color: var(--tiza); }
.ps-status-caption { color: var(--niebla) !important; font-size: 12px !important; line-height: 1.5; }

.ps-chart-frame { border-top: 1px solid var(--reticula); margin-top: 8px; }

/* ── Monitor de una corrida ───────────────────────────────────────────── */
.ps-monitor-header {
  min-height: 60px; padding: 8px 24px !important; gap: 18px !important;
  background: rgba(8,11,16,.9) !important; backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--reticula); box-shadow: none !important;
}
.ps-monitor-stats > * { font-family: var(--mono) !important; font-size: 12px !important; letter-spacing: .08em; text-transform: uppercase; }
.ps-monitor-header .ps-brand-mark { font-size: 1.35rem !important; }
.ps-monitor-stats > * { white-space: nowrap; font-variant-numeric: tabular-nums; }
.ps-monitor-tabs {
  position: sticky; top: 0; z-index: 10;
  background: rgba(8,11,16,.92) !important; backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--reticula);
}
.ps-monitor-tabs .q-tab { font-size: 11.5px; font-weight: 600; letter-spacing: .14em; color: var(--niebla); }
.ps-monitor-tabs .q-tab .q-tab__label { text-transform: uppercase !important; }
.q-tab--active { color: var(--tiza) !important; }
.q-tab__indicator { background: var(--turquesa) !important; height: 1px !important; }
.q-tab .q-tab__label { text-transform: none; }
.ps-monitor-panels, .ps-monitor-panels .q-tab-panel { background: transparent !important; }
.ps-monitor-panels > .q-tab-panel { padding: 18px 20px 32px; }
/* Instrumentos: rótulo arriba, regla fina, cifra grande en monoespaciada */
.ps-stat-card { min-height: 92px; border: 0 !important; border-top: 1px solid var(--reticula) !important; border-radius: 0 !important; background: transparent !important; }
.ps-stat-card .text-xs { text-transform: uppercase !important; letter-spacing: .16em !important; font-size: 10.5px !important; color: var(--niebla) !important; }
.ps-stat-card .text-xl, .ps-stat-card .text-lg {
  font-family: var(--mono); font-weight: 300 !important; font-size: 1.9rem !important;
  line-height: 1.15; color: var(--tiza) !important;
}
.ps-pressure-card .text-lg { font-size: 1.8rem !important; }
.ps-summary-grid { grid-template-columns: repeat(4, minmax(0,1fr)); }
.ps-summary-grid--three { grid-template-columns: repeat(3, minmax(0,1fr)); }
/* Subtítulos del monitor: sin mayúsculas forzadas */
.ps-monitor-panels .uppercase {
  text-transform: uppercase !important; letter-spacing: .16em !important;
  font-size: 11px !important; font-weight: 600; color: var(--niebla) !important;
}
.ps-monitor-panels .q-log { border: 0; border-left: 1px solid var(--reticula); border-radius: 0; background: transparent !important; font-family: var(--mono); font-size: 12px; }
.ps-monitor-panels .modebar { opacity: .35; transition: opacity .15s ease; }
.ps-monitor-panels .js-plotly-plot:hover .modebar { opacity: 1; }
/* El mundo es el objeto observado: sin caja, solo un marco de esquinas */
.ps-map-plot, .ps-network-plot, .ps-liminal-plot {
  border: 0; border-radius: 0; overflow: hidden; position: relative;
  background:
    linear-gradient(var(--niebla), var(--niebla)) top left / 14px 1px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) top left / 1px 14px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) top right / 14px 1px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) top right / 1px 14px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) bottom left / 14px 1px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) bottom left / 1px 14px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) bottom right / 14px 1px no-repeat,
    linear-gradient(var(--niebla), var(--niebla)) bottom right / 1px 14px no-repeat;
}
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

/* Pestaña «Mundo»: mapa protagonista + columna de capas (instrumentación) */
.ps-mundo { gap: 28px !important; }
.ps-mundo-mapa { flex: 1 1 72%; min-width: 0; }
.ps-mundo-capas { flex: 0 0 220px; padding-top: 6px; border-top: 1px solid var(--reticula); }
.ps-instrumento-rotulo { font-size: 10.5px; font-weight: 600; letter-spacing: .2em; text-transform: uppercase; color: var(--tiza); margin: 10px 0 6px; }
.ps-instrumento-nota { font-family: var(--mono); font-size: 10.5px; line-height: 1.5; color: var(--niebla); margin-top: 14px; }
@media (max-width: 900px) {
  .ps-mundo { flex-wrap: wrap !important; }
  .ps-mundo-capas { flex: 1 1 100%; }
}

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
  .ps-brand-subtitle, .ps-modo-observacion { display: none !important; }
  .ps-scenario-grid { grid-template-columns: 1fr; }
  .ps-primary-fields { grid-template-columns: repeat(2, minmax(0,1fr)); }
  .ps-monitor-header { flex-wrap: wrap; gap: 8px !important; }
  .ps-monitor-stats { order: 10; flex: 1 1 100% !important; margin-left: 0 !important; gap: 14px !important; }
  .ps-monitor-tabs { overflow-x: auto; }
}
@media (max-width: 700px) {
  .ps-sidebar { display: none !important; }
  .ps-main-header { padding: 0 14px !important; }
  .ps-page-shell { padding: 16px !important; gap: 28px !important; }
  .ps-hero-card, .ps-runs-card, .ps-compare-card { padding: 16px 0 0 !important; }
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
    ui.colors(primary=IRIS, secondary=PIZARRA_ALTA, accent=TURQUESA, dark=ABISMO,
              positive=TURQUESA, negative=ALERTA, warning=AMBAR, info="#8FB3FF")
    ui.add_head_html(f"<style id='psyche-simulacra-theme'>{THEME_CSS}</style>")
    ui.query("body").classes("bg-gray-950 text-gray-100")
