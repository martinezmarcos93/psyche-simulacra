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

