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
/* Tables retain all columns on narrow screens; scroll the table, not the page. */
.ps-runs-table .q-table__middle,
.ps-agents-table .q-table__middle,
.ps-network-table {
  max-width: 100%;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scrollbar-width: thin;
  scrollbar-color: var(--ps-border-strong) var(--ps-surface-soft);
}
.ps-runs-table .q-table { min-width: 850px; }
.ps-agents-table .q-table { min-width: 760px; }
.ps-runs-table .q-table__middle::-webkit-scrollbar,
.ps-agents-table .q-table__middle::-webkit-scrollbar,
.ps-network-table::-webkit-scrollbar { height: 8px; }
.ps-runs-table .q-table__middle::-webkit-scrollbar-thumb,
.ps-agents-table .q-table__middle::-webkit-scrollbar-thumb,
.ps-network-table::-webkit-scrollbar-thumb {
  background: var(--ps-border-strong);
  border-radius: 8px;
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
.ps-monitor-panels > .q-tab-panel { padding: 14px 16px 28px; }
.ps-monitor-panels .q-tab-panel > .q-card { min-width: 0; }
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
.ps-summary-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.ps-summary-grid--three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.ps-monitor-header .ps-brand-mark { overflow-wrap: anywhere; }
.ps-empty-state {
  padding: 24px 16px;
  color: var(--ps-muted);
  text-align: center;
  border: 1px dashed var(--ps-border-strong);
  border-radius: 8px;
  background: rgba(5,11,20,.35);
}
.ps-empty-state strong { display: block; color: #c6a2f2; margin-bottom: 4px; }
.ps-run-name-field { min-width: 0 !important; }
.ps-run-name-field .q-field__native { min-width: 0; text-overflow: ellipsis; }
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
  .ps-monitor-header .nicegui-row.row { margin-left: 0 !important; min-width: 0; }
  .ps-monitor-header .nicegui-row.row > * { min-width: 0; }
  .ps-monitor-tabs .q-tab { padding-inline: 10px; min-width: auto; }
  .ps-monitor-panels > .q-tab-panel { padding: 8px 6px 18px; }
}


/* Phase 4: specialized observatory views */
.ps-map-plot, .ps-network-plot, .ps-liminal-plot {
  border: 1px solid rgba(59,80,106,.55);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(7,13,24,.32);
  box-shadow: inset 0 1px 0 rgba(214,177,109,.025), 0 8px 22px rgba(0,0,0,.12);
}
.ps-map-plot .modebar, .ps-network-plot .modebar, .ps-liminal-plot .modebar {
  opacity: .45;
  transition: opacity .16s ease;
}
.ps-map-plot:hover .modebar, .ps-network-plot:hover .modebar,
.ps-liminal-plot:hover .modebar { opacity: 1; }
.ps-network-table {
  border: 1px solid var(--ps-border);
  border-radius: 8px;
  background: rgba(7,13,24,.5);
}
.ps-network-table table { border-collapse: collapse; min-width: 620px; }
.ps-network-table th {
  position: sticky;
  top: 0;
  padding: 9px 10px !important;
  color: #c6a2f2 !important;
  background: #17243a;
  font-size: 10px !important;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.ps-network-table td {
  padding: 7px 10px !important;
  border-bottom: 1px solid rgba(59,80,106,.34);
  font-size: 12px;
}
.ps-network-table tr:hover td { background: rgba(154,93,224,.055); }
.ps-agents-table .q-table__middle { max-height: 62vh; }
.ps-agents-table .q-table tbody tr { cursor: pointer; }
.ps-agents-table .q-table tbody tr.selected,
.ps-agents-table .q-table tbody tr[aria-selected="true"] {
  background: rgba(154,93,224,.14) !important;
}
.ps-agent-dialog {
  width: min(640px, 92vw) !important;
  max-width: 92vw !important;
  padding: 12px;
}
.ps-agent-radar { max-width: 100%; }
.ps-lore-panel {
  line-height: 1.65;
  overflow-wrap: anywhere;
}
.ps-lore-panel table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
}
.ps-lore-panel th {
  padding: 8px 10px;
  color: #c6a2f2;
  background: rgba(23,36,58,.9);
  font-size: 10px;
  letter-spacing: .07em;
  text-align: left;
  text-transform: uppercase;
}
.ps-lore-panel td {
  padding: 7px 10px;
  border-bottom: 1px solid rgba(59,80,106,.36);
  color: #c6d0e0;
  vertical-align: top;
}
.ps-lore-panel tr:hover td { background: rgba(154,93,224,.055); }
.ps-lore-panel > div + div { border-top: 1px solid rgba(59,80,106,.26); }

/* Phase 5: accessibility and final responsive polish */
:focus-visible {
  outline: 2px solid var(--ps-violet-bright) !important;
  outline-offset: 3px;
}
.q-btn:focus-visible, .q-tab:focus-visible, .q-checkbox:focus-visible,
.q-radio:focus-visible, .q-toggle:focus-visible, .q-item:focus-visible {
  outline: 2px solid var(--ps-violet-bright) !important;
  outline-offset: 2px;
  z-index: 2;
}
.q-field--error .q-field__control:before,
.q-field--error .q-field__control:after {
  border-color: var(--ps-red) !important;
}
.q-field--error .q-field__bottom { color: var(--ps-red) !important; }
.q-tooltip {
  padding: 7px 10px !important;
  color: var(--ps-text) !important;
  background: #19293f !important;
  border: 1px solid var(--ps-border-strong);
  border-radius: 6px !important;
  font-size: 12px !important;
  box-shadow: 0 6px 18px rgba(0,0,0,.25);
}
.q-notification {
  border: 1px solid var(--ps-border-strong);
  border-radius: 8px !important;
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.q-table__bottom .q-btn:focus-visible,
.q-table__bottom .q-btn:hover { color: var(--ps-violet-bright) !important; }
.ps-lore-panel a { color: #c6a2f2; text-decoration-color: rgba(198,162,242,.5); }
.ps-lore-panel a:hover { color: #e5d4ff; text-decoration-color: currentColor; }
.ps-lore-panel code, .ps-monitor-panels code {
  padding: 2px 5px;
  border: 1px solid rgba(59,80,106,.55);
  border-radius: 4px;
  background: rgba(5,11,20,.6);
  color: #d6b16d;
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
@media (max-width: 760px) {
  .q-card { border-radius: 8px !important; }
  .q-table__container { max-width: 100%; }
  .ps-monitor-panels .q-tab-panel { padding-inline: 4px; }
  .ps-agent-dialog { max-height: 90vh; overflow-y: auto; }
  .ps-agent-radar { min-width: 0 !important; }
  .ps-lore-panel table { display: block; max-width: 100%; overflow-x: auto; }
}

@media (max-width: 760px) {
  .ps-map-plot, .ps-network-plot, .ps-liminal-plot { border-radius: 7px; }
  .ps-network-table table { min-width: 560px; }
  .ps-agent-dialog { padding: 6px; }
  .ps-agent-radar { height: 280px !important; }
}

@media (max-width: 760px) {
  .q-header { padding-inline: 12px !important; }
  .q-card { border-radius: 8px !important; }
  .q-card__section { padding: 14px !important; }
  .q-table { font-size: 12px; }
  .ps-summary-grid, .ps-summary-grid--three { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 8px !important; }
  .ps-monitor-header { align-items: flex-start !important; }
  .ps-monitor-header .ps-brand-mark { font-size: 1rem !important; letter-spacing: .06em !important; }
  .ps-monitor-tabs { overflow-x: auto; }
  .ps-monitor-tabs .q-tabs__content { justify-content: flex-start; min-width: max-content; }
  .ps-runs-table .q-table__middle, .ps-agents-table .q-table__middle { overflow-x: auto !important; }
  .ps-run-name-field { flex: 1 1 100% !important; width: 100%; }
  .ps-chart-frame, .ps-monitor-panels .js-plotly-plot { min-width: 0; }
}
@media (max-width: 420px) {
  .ps-summary-grid, .ps-summary-grid--three { grid-template-columns: minmax(0, 1fr) !important; }
}

/* Reconstruction direction: editorial occult observatory, brass linework and indigo glass. */
.ps-main-header { min-height:60px!important;padding:6px 22px!important;gap:15px!important;background:linear-gradient(100deg,rgba(27,13,48,.99),rgba(10,17,32,.98))!important;border-bottom:1px solid rgba(191,145,91,.4)!important; }
.ps-brand-seal { width:48px!important;height:48px!important;flex:0 0 48px; }
.ps-brand-mark { font-family:Georgia,"Times New Roman",serif!important;font-size:1.55rem!important;letter-spacing:.12em!important;white-space:nowrap; }
.ps-brand-subtitle { border-left:1px solid rgba(202,166,115,.4);padding-left:16px;color:#c6b3dc!important;white-space:nowrap; }
.ps-header-motto { color:#c9b9d8;font:italic 14px Georgia,serif;margin-right:18px; }
.ps-guide-link { color:#d9b8f3!important;text-decoration:underline;text-underline-offset:4px;white-space:nowrap; }
.ps-app-layout { gap:0!important;align-items:stretch!important;min-height:calc(100vh - 60px); }
.ps-sidebar { width:194px!important;min-width:194px!important;flex:0 0 194px;padding:18px 10px 16px;gap:6px!important;border-right:1px solid rgba(51,76,102,.48);background:linear-gradient(180deg,rgba(4,11,22,.98),rgba(5,13,25,.92));position:relative;overflow:hidden; }
.ps-nav-link { display:flex!important;align-items:center;min-height:46px;padding:0 14px;border:1px solid transparent;border-radius:6px;color:#c6d0e0!important;font:14px Georgia,serif;text-decoration:none!important;letter-spacing:.02em;transition:background .18s ease,border-color .18s ease; }
.ps-nav-link:hover { background:rgba(146,82,194,.12);border-color:rgba(163,111,218,.28); }
.ps-nav-active { background:linear-gradient(100deg,rgba(112,51,154,.38),rgba(38,24,62,.28));border-color:rgba(180,120,231,.5);color:#f2e6ff!important; }
.ps-sidebar-mandala { width:100%!important;max-width:180px;margin:auto auto 0;opacity:.85;filter:drop-shadow(0 0 16px rgba(192,142,76,.08)); }
.ps-sidebar-quote { color:#b8a9b9;font:italic 13px/1.55 Georgia,serif;text-align:center;padding:0 8px 6px; }
.ps-page-shell { max-width:none!important;flex:1 1 auto;min-width:0;padding:10px 12px 18px!important;gap:12px!important; }
.ps-dashboard-top { align-items:stretch!important;gap:12px!important; }
.ps-dashboard-main { flex:1 1 auto;min-width:0; }
.ps-hero-card { padding:14px 16px!important;border-color:rgba(58,81,111,.64)!important;background:linear-gradient(140deg,rgba(7,19,34,.98),rgba(5,14,27,.98))!important; }
.ps-hero-heading-row { gap:12px;margin-bottom:4px; }
.ps-hero-heading-row .ps-section-heading { font-family:Georgia,"Times New Roman",serif!important;font-size:1.55rem!important;font-weight:500!important;letter-spacing:.055em;text-transform:uppercase; }
.ps-section-description { max-width:780px;color:#b8c7dc!important;font:14px/1.5 Georgia,serif!important; }
.ps-quick-config { border-color:rgba(184,145,96,.42)!important;color:#d8c4a3!important;flex:0 0 auto; }
.ps-scenario-grid { grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:10px!important;margin-top:10px; }
.ps-scenario-card { position:relative;isolation:isolate;overflow:hidden;min-height:140px!important;padding:14px 12px 12px 108px!important;border-radius:7px!important;background:linear-gradient(110deg,rgba(18,26,49,.98),rgba(8,18,32,.96))!important;border:1px solid rgba(64,85,115,.78)!important; }
.ps-scenario-card:before { content:"";position:absolute;z-index:-1;left:4px;top:50%;transform:translateY(-50%);width:104px;height:104px;background-position:center;background-repeat:no-repeat;background-size:contain;opacity:.92; }
.ps-scenario-off:before { background-image:url('/assets/scenario-mundo-libre.svg'); }
.ps-scenario-orden:before { background-image:url('/assets/scenario-orden.svg'); }
.ps-scenario-eden:before { background-image:url('/assets/scenario-eden.svg'); }
.ps-scenario-card .q-checkbox { position:absolute;top:10px;right:10px; }
.ps-scenario-card .q-checkbox__label { font:600 17px Georgia,serif;color:#f0dfc2;padding-right:20px; }
.ps-scenario-card .ps-scenario-description { padding-left:0;font:12px/1.4 Georgia,serif!important;color:#b8c7dc!important; }
.ps-scenario-card:has(.q-checkbox__inner--truthy) { border-color:#b17ae0!important;box-shadow:inset 0 0 0 1px rgba(177,122,224,.2),0 0 22px rgba(133,69,185,.12)!important; }
.ps-primary-fields { display:grid!important;grid-template-columns:minmax(160px,1.25fr) minmax(90px,.65fr) minmax(78px,.55fr) minmax(170px,1.35fr);gap:10px!important;align-items:end;margin-top:10px;padding:10px 12px!important;background:rgba(4,13,24,.62);border-color:rgba(59,80,106,.55)!important; }
.ps-primary-fields>* { min-width:0!important;width:100%!important; }
.ps-duration-row { margin-top:8px; }
.ps-config-section { margin-block:5px!important; }
.ps-launch-btn { background:linear-gradient(105deg,#67349a,#8e3f9d)!important;border:1px solid #a56ad1!important;font:600 15px Georgia,serif!important;letter-spacing:.08em!important;text-transform:uppercase; }
.ps-lab-status-card { width:286px!important;min-width:260px!important;flex:0 0 286px;padding:14px 13px!important;background:linear-gradient(160deg,rgba(7,18,32,.98),rgba(5,13,24,.98))!important;border-color:rgba(58,81,111,.65)!important; }
.ps-lab-status-title { font:600 17px Georgia,serif;color:#eee1c7;padding-bottom:10px;border-bottom:1px solid rgba(59,80,106,.45);width:100%; }
.ps-status-list { width:100%;gap:0!important; }
.ps-status-row { width:100%;min-height:37px;gap:7px!important;border-bottom:1px solid rgba(59,80,106,.26); }
.ps-status-icon { width:22px;color:#b7a0da;font-size:17px; }
.ps-status-name { color:#c5d1e0;font:12px Georgia,serif; }
.ps-status-value { color:#6ce0ad;font-size:11px;white-space:nowrap; }
.ps-status-dot { font-size:10px; }
.ps-status-dot.is-ready { color:#3ee2a0; }
.ps-status-dot.is-idle { color:#d6b16d; }
.ps-active-runs { padding:10px 0 3px; }
.ps-active-count { color:#d5b5f4;font:26px Georgia,serif; }
.ps-status-caption { color:#8fa4c0!important;font:12px/1.45 Georgia,serif!important; }
.ps-status-art { width:100%!important;max-height:190px;object-fit:contain;border:1px solid rgba(59,80,106,.55);border-radius:5px;background:radial-gradient(ellipse,rgba(129,83,154,.12),transparent 68%); }
.ps-dashboard-bottom { align-items:stretch!important;gap:12px!important; }
.ps-runs-card { flex:1.55 1 0;min-width:0; }
.ps-compare-card { flex:1 1 0;min-width:0; }
.ps-runs-card,.ps-compare-card { padding:12px!important; }
.ps-runs-card .q-table { min-width:700px; }
.ps-runs-card .q-table__middle { overflow-x:auto; }
.ps-compare-card .js-plotly-plot { min-width:0; }
.ps-main-header .q-img__image { object-fit:contain!important; }
@media(max-width:1200px){.ps-header-motto{display:none!important}.ps-dashboard-top{flex-wrap:wrap!important}.ps-lab-status-card{width:100%!important;flex:1 1 100%;min-width:0!important}.ps-status-art{max-height:110px}}
@media(max-width:900px){.ps-brand-seal{width:36px!important;height:36px!important;flex-basis:36px}.ps-brand-mark{font-size:1.1rem!important;letter-spacing:.05em!important}.ps-brand-subtitle{display:none!important}.ps-dashboard-bottom{flex-wrap:wrap!important}.ps-runs-card,.ps-compare-card{flex:1 1 100%}.ps-scenario-card{padding-left:92px!important}.ps-scenario-card:before{width:86px;height:86px}.ps-primary-fields{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:600px){.ps-sidebar{display:none!important}.ps-main-header{padding-inline:10px!important;gap:8px!important}.ps-brand-mark{font-size:1rem!important;white-space:normal}.ps-guide-link{font-size:11px!important}.ps-page-shell{padding:8px!important}.ps-hero-card{padding:12px 10px!important}.ps-hero-heading-row .ps-section-heading{font-size:1.15rem!important}.ps-quick-config{display:none!important}.ps-scenario-grid{grid-template-columns:minmax(0,1fr)!important}.ps-scenario-card{min-height:108px!important;padding:12px 10px 10px 100px!important}.ps-scenario-card:before{width:94px;height:94px;left:0}.ps-primary-fields{grid-template-columns:minmax(0,1fr) minmax(0,1fr);padding:8px!important}.ps-primary-fields>*:nth-child(4){grid-column:1/-1}.ps-dashboard-top{gap:8px!important}.ps-lab-status-card{padding:10px!important}.ps-header-motto{display:none!important}}

"""


def apply_theme(ui) -> None:
    """Inyecta el tema en la página actual; seguro de invocar por página."""
    ui.add_head_html(f"<style id='psyche-simulacra-theme'>{THEME_CSS}</style>")
    ui.query("body").classes("bg-gray-950 text-gray-100")

