"""Tema visual compartido para las interfaces NiceGUI de PSYCHE SIMULACRA.

Este módulo solo aporta estilos: no registra callbacks ni modifica el estado
de la simulación, sus parámetros o sus datos.
"""
from __future__ import annotations


THEME_CSS = r"""
:root {
  color-scheme: dark;
  --ps-bg: #070d18;
  --ps-surface: #101c2c;
  --ps-surface-raised: #142338;
  --ps-surface-soft: #0b1523;
  --ps-border: #26384d;
  --ps-border-strong: #3b506a;
  --ps-text: #e5eaf4;
  --ps-muted: #91a2bb;
  --ps-violet: #9a5de0;
  --ps-violet-bright: #bf8cff;
  --ps-gold: #d6b16d;
  --ps-green: #46d6a0;
  --ps-amber: #e8b866;
  --ps-red: #f07178;
}

html, body, body.body, #q-app {
  background: var(--ps-bg) !important;
  color: var(--ps-text);
}
body, .q-field, .q-table, .q-tab, .q-btn, .q-item, .q-checkbox,
.q-radio, .q-toggle, .q-expansion-item {
  font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
body {
  background-image:
    radial-gradient(ellipse at 15% 0%, rgba(102, 55, 153, .12), transparent 38%),
    radial-gradient(ellipse at 100% 12%, rgba(37, 90, 126, .09), transparent 32%) !important;
}
.q-header {
  background: rgba(24, 18, 43, .97) !important;
  border-bottom: 1px solid rgba(154, 93, 224, .45);
  box-shadow: 0 5px 22px rgba(0, 0, 0, .22);
  backdrop-filter: blur(14px);
}
.q-page, .q-page-container {
  background: transparent !important;
}
.q-card {
  color: var(--ps-text) !important;
  background: linear-gradient(145deg, rgba(17, 29, 46, .98), rgba(11, 21, 35, .98)) !important;
  border: 1px solid var(--ps-border) !important;
  border-radius: 10px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .15) !important;
}
.q-card .q-card {
  background: var(--ps-surface-raised) !important;
  border-color: var(--ps-border-strong) !important;
  box-shadow: none !important;
}
.q-separator { background: var(--ps-border) !important; }
.text-gray-100, .text-gray-200, .text-white { color: var(--ps-text) !important; }
.text-gray-300, .text-gray-400, .text-gray-500 { color: var(--ps-muted) !important; }
.text-purple-200, .text-purple-300 { color: #c6a2f2 !important; }
.bg-gray-950, .bg-gray-900 { background: transparent !important; }
.bg-gray-800 { background: var(--ps-surface-raised) !important; }
.text-green-400 { color: var(--ps-green) !important; }
.text-yellow-400, .text-amber-400 { color: var(--ps-amber) !important; }
.text-red-400 { color: var(--ps-red) !important; }

.q-btn {
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: .015em;
  transition: background .16s ease, border-color .16s ease, transform .16s ease;
}
.q-btn:not(.q-btn--flat):not(.q-btn--outline) {
  box-shadow: 0 4px 14px rgba(105, 48, 166, .18);
}
.q-btn:hover { transform: translateY(-1px); }
.q-btn--outline:before { border-color: var(--ps-border-strong) !important; }
.q-btn--flat:hover { background: rgba(154, 93, 224, .12) !important; }

.q-field--outlined .q-field__control:before { border-color: var(--ps-border-strong) !important; }
.q-field--outlined .q-field__control:hover:before { border-color: var(--ps-violet) !important; }
.q-field--focused .q-field__control:after { border-color: var(--ps-violet-bright) !important; }
.q-field__label, .q-field__native, .q-field__input { color: var(--ps-text) !important; }
.q-field__bottom { color: var(--ps-muted) !important; }
.q-field--filled .q-field__control { background: rgba(7, 13, 24, .62) !important; }
.q-menu, .q-select__dialog, .q-date, .q-time {
  background: var(--ps-surface-raised) !important;
  color: var(--ps-text) !important;
  border: 1px solid var(--ps-border-strong);
  border-radius: 8px;
}
.q-item { min-height: 38px; }
.q-item--active, .q-item--active .q-item__label { color: var(--ps-violet-bright) !important; }
.q-checkbox__inner--truthy, .q-radio__inner--truthy, .q-toggle__inner--truthy {
  color: var(--ps-violet-bright) !important;
}
.q-checkbox__bg { border-radius: 4px; }

.q-expansion-item {
  border: 1px solid rgba(59, 80, 106, .66);
  border-radius: 8px;
  overflow: hidden;
  margin-block: 5px;
  background: rgba(16, 28, 44, .45);
}
.q-expansion-item__container > .q-item {
  min-height: 48px;
  padding-inline: 14px;
}
.q-expansion-item__container > .q-item:hover { background: rgba(154, 93, 224, .07); }
.q-expansion-item__content { border-top: 1px solid rgba(59, 80, 106, .4); }
.q-expansion-item__content > div { padding: 14px; }

.q-table__container {
  background: rgba(9, 17, 29, .72) !important;
  border: 1px solid var(--ps-border);
  border-radius: 8px;
  overflow: hidden;
}
.q-table thead tr { background: rgba(25, 38, 58, .96); }
.q-table th {
  color: #c6a2f2 !important;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.q-table tbody td { border-color: rgba(59, 80, 106, .42) !important; }
.q-table tbody tr:hover { background: rgba(154, 93, 224, .07) !important; }
.q-table__bottom { color: var(--ps-muted); }

.q-tabs { color: var(--ps-muted); }
.q-tab { min-height: 42px; font-weight: 600; }
.q-tab--active { color: var(--ps-violet-bright) !important; }
.q-tab__indicator { background: var(--ps-violet-bright) !important; height: 2px !important; }
.q-badge { border-radius: 4px; font-weight: 650; letter-spacing: .01em; }
.q-tooltip { background: #1b2940 !important; color: var(--ps-text) !important; border: 1px solid var(--ps-border); }
.q-dialog__inner > div {
  background: var(--ps-surface) !important;
  color: var(--ps-text) !important;
  border: 1px solid var(--ps-border-strong);
  border-radius: 10px;
}
a { color: #c6a2f2; }
a:hover { color: var(--ps-violet-bright); }

.ps-shell-title {
  color: var(--ps-text);
  font-weight: 750;
  letter-spacing: .13em;
  text-transform: uppercase;
}
.ps-eyebrow {
  color: var(--ps-gold);
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: .13em;
  text-transform: uppercase;
}
.ps-panel-title { color: #d9c2f6; font-weight: 700; }
.ps-muted { color: var(--ps-muted); }

/* Phase 2: experiment launcher */
.ps-page-shell { max-width: 1320px !important; padding: 28px 24px 44px !important; gap: 22px !important; }
.ps-brand-mark { color: #f0e7ff !important; text-shadow: 0 0 24px rgba(191,140,255,.18); }
.ps-brand-subtitle { color: #a9b8ce !important; }
.ps-hero-card { border-color: #35425d !important; background: linear-gradient(145deg,#121f31,#0b1523) !important; }
.ps-section-heading { color: #e5d4ff !important; font-size: 1.15rem !important; font-weight: 750 !important; }
.ps-section-kicker { color: var(--ps-gold) !important; font-size: .68rem !important; font-weight: 750 !important; letter-spacing: .16em; text-transform: uppercase; }
.ps-section-description { max-width: 880px; line-height: 1.65 !important; }
.ps-scenario-grid { display: grid !important; grid-template-columns: repeat(3,minmax(0,1fr)); align-items: stretch; }
.ps-scenario-card { min-width: 0 !important; min-height: 128px; border: 1px solid #304159 !important; border-radius: 9px !important; background: #142338 !important; transition: border-color .18s ease,transform .18s ease !important; }
.ps-scenario-card:hover { border-color: #9a72c5 !important; transform: translateY(-2px); }
.ps-scenario-description { line-height: 1.55 !important; padding-left: 30px; }
.ps-primary-fields { padding: 16px; border: 1px solid rgba(59,80,106,.5); border-radius: 8px; background: rgba(5,12,22,.34); }
.ps-duration-row { padding: 10px 14px; border-radius: 8px; background: rgba(5,12,22,.42); border: 1px solid rgba(59,80,106,.5); }
.ps-config-section { margin-block: 7px !important; background: rgba(14,25,41,.66) !important; }
.ps-run-summary { padding: 12px 15px; border: 1px solid rgba(154,93,224,.32); border-radius: 7px; background: rgba(95,51,135,.13); color: #d8baff !important; font-weight: 650; line-height: 1.5; }
.ps-launch-btn { min-width: 156px; min-height: 42px; padding-inline: 22px !important; }
.ps-runs-card,.ps-compare-card { background: linear-gradient(145deg,#111e2e,#0b1523) !important; }
.ps-chart-frame { border: 1px solid rgba(59,80,106,.55); border-radius: 8px; overflow: hidden; background: rgba(7,13,24,.35); }
@media (max-width: 900px) { .ps-scenario-grid { grid-template-columns: 1fr; } .ps-scenario-card { min-height: auto; } }


/* Phase 3: live observatory */
.ps-monitor-header {
  min-height: 62px;
  padding-top: 10px !important;
  padding-bottom: 10px !important;
  gap: 16px !important;
  background: rgba(17, 16, 34, .96) !important;
  border-bottom: 1px solid rgba(154, 93, 224, .42);
}
.ps-monitor-header .ps-brand-mark { letter-spacing: .12em; }
.ps-monitor-tabs {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(13, 22, 37, .97) !important;
  border-bottom: 1px solid var(--ps-border-strong);
  box-shadow: 0 7px 18px rgba(0,0,0,.16);
  backdrop-filter: blur(12px);
}
.ps-monitor-tabs .q-tab { padding: 0 16px; }
.ps-monitor-panels { background: transparent !important; }
.ps-monitor-panels > .q-panel > .q-panel__content { padding: 14px 16px 28px; }
.ps-monitor-panels .q-tab-panel { background: transparent !important; }
.ps-monitor-panels .q-separator { opacity: .72; }
.ps-stat-card {
  position: relative;
  min-height: 88px;
  border-color: rgba(59,80,106,.62) !important;
  background: linear-gradient(145deg, rgba(22,36,56,.96), rgba(12,22,36,.98)) !important;
  transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease !important;
}
.ps-stat-card:hover {
  border-color: rgba(154,93,224,.6) !important;
  box-shadow: 0 10px 24px rgba(0,0,0,.2) !important;
}
.ps-stat-card .text-xl, .ps-stat-card .text-lg { letter-spacing: -.025em; }
.ps-stat-card .text-xs { letter-spacing: .09em !important; }
.ps-pressure-card { min-height: 82px; }
.ps-monitor-panels .q-log {
  border: 1px solid var(--ps-border);
  border-radius: 7px;
  background: rgba(5,11,20,.72) !important;
  line-height: 1.55;
}
.ps-monitor-panels .js-plotly-plot { border-radius: 8px; }
.ps-monitor-panels .plot-container { border-radius: 8px; }
.ps-monitor-panels .main-svg { overflow: visible; }
.ps-monitor-panels .modebar { opacity: .42; transition: opacity .15s ease; }
.ps-monitor-panels .js-plotly-plot:hover .modebar { opacity: .95; }
.ps-monitor-panels .q-btn { min-height: 32px; }
.ps-monitor-panels .q-field--dense .q-field__control { min-height: 34px; }
@media (max-width: 900px) {
  .ps-monitor-header { flex-wrap: wrap; gap: 8px !important; }
  .ps-monitor-header .q-row { margin-left: 0 !important; }
  .ps-monitor-tabs .q-tab { padding-inline: 10px; min-width: auto; }
  .ps-monitor-panels > .q-panel > .q-panel__content { padding: 8px 6px 18px; }
}

@media (max-width: 760px) {
  .q-header { padding-inline: 12px !important; }
  .q-card { border-radius: 8px !important; }
  .q-card__section { padding: 14px !important; }
  .q-table { font-size: 12px; }
}
"""


def apply_theme(ui) -> None:
    """Inyecta el tema en la página actual; seguro de invocar por página."""
    ui.add_head_html(f"<style id='psyche-simulacra-theme'>{THEME_CSS}</style>")
    ui.query("body").classes("bg-gray-950 text-gray-100")

