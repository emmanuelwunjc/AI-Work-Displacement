#!/usr/bin/env python3
"""generate_dashboard.py — Embed dashboard.json into a self-contained HTML dashboard."""
import json, os

with open("output/dashboard.json") as f:
    RAW = f.read()  # already minified

# ── helpers ───────────────────────────────────────────────────────────────────
def fmt(n):
    return f"{abs(int(n)):,}"

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI × Labor — Trucking Supply-Chain Impact</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:    #09090E;
  --bg2:   #111118;
  --bg3:   #18181F;
  --bg4:   #1E1E28;
  --border:#222232;
  --text:  #EAE5DC;
  --muted: #8A84A0;
  --dim:   #38364A;
  --loss:      #C8243E;
  --loss-bg:   rgba(200,36,62,.13);
  --gain:      #1B9160;
  --gain-bg:   rgba(27,145,96,.13);
  --amber:     #D49216;
  --teal:      #0AADB5;
  --nrca: #4F87F5;
  --nrci: #A855F7;
  --rc:   #EAB208;
  --rm:   #F87316;
  --nrm:  #22D3EE;
  --sidebar: 248px;
  --topbar:  62px;
  --font-d: 'Syne', sans-serif;
  --font-m: 'JetBrains Mono', monospace;
  --font-b: 'Libre Baskerville', serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;overflow:hidden;background:var(--bg);color:var(--text);font-family:var(--font-b);font-size:15px;line-height:1.5}}
::selection{{background:var(--teal);color:#000}}

::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:var(--dim);border-radius:3px}}

/* ── TOPBAR ── */
#topbar{{
  position:fixed;top:0;left:0;right:0;height:var(--topbar);z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 28px 0 calc(var(--sidebar) + 28px);
  background:rgba(9,9,14,.94);backdrop-filter:blur(18px);
  border-bottom:1px solid var(--border);
}}
#topbar .title{{
  font-family:var(--font-d);font-size:15px;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;color:var(--text);
}}
#topbar .title span{{color:var(--text)}}
.wave-toggle{{
  display:flex;align-items:center;gap:3px;
  background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:4px;
}}
.wave-btn{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;
  padding:8px 20px;border-radius:5px;cursor:pointer;
  border:none;background:transparent;color:var(--text);transition:all .2s;
}}
.wave-btn.active{{background:var(--teal);color:#000}}

/* ── SIDEBAR ── */
#sidebar{{
  position:fixed;left:0;top:var(--topbar);bottom:0;width:var(--sidebar);
  background:var(--bg2);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;z-index:50;
}}
.sidebar-logo{{
  padding:24px 22px 18px;
  font-family:var(--font-d);font-size:22px;font-weight:800;
  letter-spacing:-.03em;line-height:1;border-bottom:1px solid var(--border);
}}
.sidebar-logo span{{color:var(--teal)}}
.sidebar-logo sub{{
  display:block;font-size:12px;font-weight:500;letter-spacing:.1em;
  text-transform:uppercase;color:var(--text);margin-top:5px;
}}
nav{{flex:1;padding:12px 0;overflow-y:auto}}
.nav-section{{
  font-family:var(--font-d);font-size:12px;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;color:var(--text);padding:16px 22px 8px;
}}
.nav-item{{
  display:flex;align-items:center;gap:12px;padding:13px 22px;cursor:pointer;
  font-family:var(--font-d);font-size:14px;font-weight:500;
  color:var(--text);border-left:3px solid transparent;transition:all .15s;
}}
.nav-item:hover{{color:var(--text);background:var(--bg3)}}
.nav-item.active{{
  color:var(--text);border-left-color:var(--teal);
  background:linear-gradient(90deg,rgba(10,173,181,.1),transparent);
}}
.nav-item .nav-icon{{
  width:20px;height:20px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:15px;opacity:.6;
}}
.nav-item.active .nav-icon{{opacity:1}}
.filter-label{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text);margin-bottom:5px;
}}
select, input[type=text]{{
  width:100%;background:var(--bg3);border:1px solid var(--border);
  color:var(--text);border-radius:6px;padding:9px 12px;
  font-family:var(--font-d);font-size:13px;outline:none;
  transition:border-color .15s;-webkit-appearance:none;
}}
select:focus, input[type=text]:focus{{border-color:var(--teal);color:#fff}}
input[type=text]::placeholder{{color:var(--text)}}
select option{{background:var(--bg2);color:var(--text)}}
.sidebar-meta{{
  padding:14px 18px;border-top:1px solid var(--border);
  font-size:12px;color:var(--text);line-height:1.7;font-family:var(--font-d);
}}

/* ── MAIN ── */
#main{{position:fixed;left:var(--sidebar);top:var(--topbar);right:0;bottom:0;overflow:hidden}}
.view{{
  position:absolute;inset:0;overflow-y:auto;padding:22px 26px 40px;display:none;
}}
.view.active{{display:block}}

/* ── OVERVIEW ── */
.hero-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:26px}}
.hero-card{{
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;
  padding:24px 26px;position:relative;overflow:hidden;
}}
.hero-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px}}
.hero-card.loss::before{{background:var(--loss)}}
.hero-card.gain::before{{background:var(--gain)}}
.hero-card.amber::before{{background:var(--amber)}}
.hero-card.teal::before{{background:var(--teal)}}
.hero-card .hc-label{{
  font-family:var(--font-d);font-size:13px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--text);margin-bottom:12px;
}}
.hero-card .hc-val{{
  font-family:var(--font-m);font-size:40px;font-weight:600;
  letter-spacing:-.02em;line-height:1;
}}
.hero-card .hc-sub{{
  font-size:13px;color:var(--text);margin-top:10px;font-family:var(--font-d);line-height:1.5;
}}
.hero-card.loss .hc-val{{color:var(--loss)}}
.hero-card.gain .hc-val{{color:var(--gain)}}
.hero-card.amber .hc-val{{color:var(--amber)}}
.hero-card.teal .hc-val{{color:var(--teal)}}

.section-head{{
  font-family:var(--font-d);font-size:13px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text);
  margin-bottom:18px;display:flex;align-items:center;gap:12px;
}}
.section-head::after{{content:'';flex:1;height:1px;background:var(--border)}}

.sector-grid{{
  display:grid;grid-template-columns:repeat(4,1fr);
  gap:12px;margin-bottom:26px;
}}
.sector-card{{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:10px;padding:20px 22px 18px;cursor:default;
  transition:transform .15s,border-color .15s;
}}
.sector-card:hover{{transform:translateY(-2px);border-color:var(--dim)}}
.sector-card .sc-name{{
  font-family:var(--font-d);font-size:12px;font-weight:600;
  letter-spacing:.03em;color:var(--text);margin-bottom:10px;
  line-height:1.4;min-height:2.8em;
}}
.sc-value-row{{display:flex;align-items:baseline;gap:10px;margin-bottom:6px;flex-wrap:nowrap}}
.sector-card .sc-val{{
  font-family:var(--font-m);font-size:26px;font-weight:600;
  letter-spacing:-.02em;white-space:nowrap;
}}
.sector-card .sc-pct{{font-family:var(--font-m);font-size:22px;font-weight:500;white-space:nowrap}}
.sector-card .sc-industries{{font-family:var(--font-d);font-size:12px}}
.sector-card .sc-bar{{
  height:4px;border-radius:2px;margin-top:16px;background:var(--bg3);position:relative;overflow:hidden;
}}
.sector-card .sc-bar-fill{{
  position:absolute;top:0;height:100%;border-radius:2px;transition:width .6s ease;
}}
.sector-card.neg .sc-val{{color:var(--loss)}}
.sector-card.neg .sc-pct{{color:var(--loss)}}
.sector-card.neg .sc-bar-fill{{background:var(--loss)}}
.sector-card.pos .sc-val{{color:var(--gain)}}
.sector-card.pos .sc-pct{{color:var(--gain)}}
.sector-card.pos .sc-bar-fill{{background:var(--gain)}}
.sector-card.neu .sc-val{{color:var(--text)}}
.sector-card.neu .sc-pct{{color:var(--text)}}
.sector-card.neu .sc-bar-fill{{background:var(--muted)}}

/* ── IMPACT SUMMARY TABLE ── */
.impact-summary-table{{
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;margin-bottom:18px;
}}
.impact-summary-table table{{width:100%;border-collapse:collapse;table-layout:fixed}}
.impact-summary-table thead th{{
  background:var(--bg3);padding:14px 22px;
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--text);
  text-align:right;border-bottom:1px solid var(--border);white-space:nowrap;
}}
.impact-summary-table thead th:first-child{{text-align:left;width:160px}}
.impact-summary-table tbody td{{
  padding:18px 22px;border-bottom:1px solid rgba(34,34,50,.5);
  font-family:var(--font-m);font-size:16px;text-align:right;color:var(--text);
}}
.impact-summary-table tbody td:first-child{{font-family:var(--font-d);text-align:left;vertical-align:middle}}
.impact-summary-table .total-row td{{
  font-weight:700;font-size:18px;background:rgba(34,34,50,.3);border-bottom:none;
}}
.mult-tag{{
  display:inline-block;font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;padding:5px 12px;border-radius:4px;
}}
.mult-tag.direct  {{background:rgba(79,135,245,.15);color:var(--nrca)}}
.mult-tag.indirect{{background:rgba(234,178,8,.12);color:var(--rc)}}
.mult-tag.induced {{background:rgba(168,85,247,.12);color:var(--nrci)}}
.mult-tag.total   {{background:var(--bg3);color:var(--text)}}
.ist-scope{{
  padding:10px 22px 6px;font-family:var(--font-d);font-size:12px;
  border-top:1px solid var(--border);
}}
.ist-defs{{
  padding:6px 22px 14px;font-family:var(--font-d);font-size:12px;line-height:1.7;
}}

/* ── MULTIPLIER STRIP ── */
.multiplier-strip{{
  display:grid;grid-template-columns:repeat(4,1fr);
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;margin-bottom:26px;
}}
.ms-cell{{padding:22px 24px;border-right:1px solid var(--border)}}
.ms-cell:last-child{{border-right:none}}
.ms-label{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;margin-bottom:12px;
}}
.ms-val{{font-family:var(--font-m);font-size:28px;font-weight:600;margin-bottom:10px}}
.ms-sub{{font-family:var(--font-d);font-size:12px;line-height:1.65;}}

/* ── EXPLORER ── */
.explorer-layout{{
  display:grid;grid-template-columns:minmax(0,1fr) 700px;
  gap:16px;height:calc(100vh - var(--topbar) - 84px);
}}
.table-wrap{{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:10px;overflow:hidden;display:flex;flex-direction:column;
}}
.table-scroll{{flex:1;overflow-y:auto;overflow-x:hidden}}
table{{width:100%;border-collapse:collapse;table-layout:fixed}}
thead th{{
  position:sticky;top:0;z-index:5;background:var(--bg3);
  padding:14px 16px;font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--text);
  text-align:left;border-bottom:1px solid var(--border);cursor:pointer;
  user-select:none;white-space:nowrap;overflow:hidden;
}}
thead th:hover{{color:var(--teal)}}
thead th.sorted{{color:var(--teal)}}
thead th.td-num{{text-align:right}}
tbody tr{{border-bottom:1px solid rgba(34,34,50,.6);cursor:pointer;transition:background .1s}}
tbody tr:hover{{background:var(--bg3)}}
tbody tr.selected{{background:rgba(10,173,181,.08);border-left:3px solid var(--teal)}}
tbody td{{
  padding:14px 16px;font-size:14px;
  color:var(--text);line-height:1.4;white-space:normal;overflow:visible;
}}
.col-name{{width:170px;min-width:170px;max-width:170px}}
.col-alm{{width:104px}}
.col-num{{width:116px}}
.td-num{{font-family:var(--font-m);font-size:14px;text-align:right}}
.td-loss{{color:var(--loss)}}
.td-gain{{color:var(--gain)}}
.td-neutral{{color:var(--text)}}
.alm-badge{{
  display:inline-block;font-family:var(--font-d);font-size:12px;
  font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  padding:5px 10px;border-radius:4px;white-space:nowrap;
}}
.table-status{{
  padding:13px 16px;font-family:var(--font-d);font-size:13px;
  color:var(--text);border-top:1px solid var(--border);
  display:flex;justify-content:space-between;align-items:center;
}}

/* Detail panel */
.detail-panel{{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:10px;overflow-y:auto;padding:30px;
  display:flex;flex-direction:column;gap:24px;
}}
.dp-empty{{
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  height:100%;color:var(--text);text-align:center;gap:14px;
}}
.dp-empty .dp-icon{{font-size:52px;opacity:.3}}
.dp-empty p{{font-family:var(--font-d);font-size:15px}}
.dp-name{{font-family:var(--font-d);font-size:26px;font-weight:700;line-height:1.3;color:var(--text);word-break:break-word}}
.dp-sector{{
  font-family:var(--font-d);font-size:13px;font-weight:600;
  letter-spacing:.05em;text-transform:uppercase;color:var(--text);margin-top:6px;
}}
.dp-kpis{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.dp-kpi{{background:var(--bg3);border-radius:10px;padding:20px}}
.dp-kpi-label{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--text);margin-bottom:10px;
}}
.dp-kpi-val{{font-family:var(--font-m);font-size:30px;font-weight:500;word-break:break-all}}
.dp-section-title{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.1em;text-transform:uppercase;color:var(--text);margin-bottom:14px;
}}
.impact-bars{{display:flex;flex-direction:column;gap:14px}}
.ib-row{{display:flex;flex-direction:column;gap:6px}}
.ib-label{{display:flex;justify-content:space-between;align-items:center}}
.ib-name{{font-family:var(--font-d);font-size:14px;color:var(--text)}}
.ib-vals{{font-family:var(--font-m);font-size:13px;display:flex;gap:10px}}
.ib-track{{height:10px;background:var(--bg);border-radius:5px;position:relative;overflow:hidden}}
.ib-pre{{position:absolute;top:0;left:0;height:100%;border-radius:5px;opacity:.35}}
.ib-post{{position:absolute;top:0;left:0;height:100%;border-radius:5px}}
.llm-box{{
  background:linear-gradient(135deg,rgba(200,36,62,.08),rgba(212,146,22,.06));
  border:1px solid rgba(200,36,62,.2);border-radius:10px;padding:22px;
}}
.llm-box-title{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--amber);margin-bottom:12px;
}}
.llm-box-val{{font-family:var(--font-m);font-size:34px;font-weight:500;color:var(--loss)}}
.llm-box-sub{{font-size:14px;color:var(--text);margin-top:8px;font-family:var(--font-d)}}

/* ── IMPACT MAP ── */
.impact-layout{{display:flex;flex-direction:column;gap:16px}}
.wf-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:0}}
.impact-bottom-3{{
  display:grid;grid-template-columns:1fr 1fr;
  gap:16px;min-height:440px;
}}
.impact-panel{{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:10px;padding:20px;overflow-y:auto;display:flex;flex-direction:column;
}}
.impact-panel-title{{
  font-family:var(--font-d);font-size:13px;font-weight:700;
  letter-spacing:.09em;text-transform:uppercase;color:var(--text);
  margin-bottom:16px;flex-shrink:0;
}}
/* Sector impact bars */
.sib-row{{
  display:grid;grid-template-columns:auto 1fr 70px;
  align-items:center;gap:8px;margin-bottom:9px;
}}
.sib-name{{
  font-family:var(--font-d);font-size:12px;color:var(--text);
  white-space:normal;line-height:1.4;
}}
.sib-track{{height:20px;background:var(--bg3);border-radius:4px;overflow:hidden;min-width:0}}
.sib-fill{{height:100%;border-radius:4px;transition:width .6s ease}}
.sib-fill.loss{{background:var(--loss)}}
.sib-fill.gain{{background:var(--gain)}}
.sib-val{{font-family:var(--font-m);font-size:12px;text-align:right;white-space:nowrap;color:var(--text)}}
/* Heatmap */
.heatmap-table{{width:100%;border-collapse:collapse;table-layout:fixed}}
.heatmap-th{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.05em;text-transform:uppercase;
  padding:7px 4px;text-align:center;border-bottom:1px solid var(--border);
  white-space:nowrap;overflow:hidden;
}}
.heatmap-name-th{{text-align:left;width:140px}}
.heatmap-td{{
  padding:6px 3px;text-align:center;font-family:var(--font-m);
  font-size:12px;color:var(--text);border:1px solid rgba(9,9,14,.5);white-space:nowrap;
}}
.heatmap-name{{
  font-family:var(--font-d);font-size:12px;color:var(--text);
  padding:5px 6px 5px 0;white-space:normal;line-height:1.4;
  border-bottom:1px solid rgba(34,34,50,.3);
}}
#donut-svg{{display:block}}

/* ── WAVE ANALYSIS ── */
.wave-layout{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:18px}}
.wave-panel{{
  background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:26px;
}}
.wp-title{{
  font-family:var(--font-d);font-size:17px;font-weight:700;
  letter-spacing:.07em;text-transform:uppercase;margin-bottom:8px;
}}
.wp-subtitle{{
  font-size:14px;margin-bottom:22px;font-family:var(--font-d);line-height:1.5;
}}
.llm-def-box{{
  background:rgba(212,146,22,.07);border:1px solid rgba(212,146,22,.22);
  border-radius:8px;padding:14px 16px;margin-bottom:16px;
  font-family:var(--font-d);font-size:13px;line-height:1.7;
}}
.llm-def-box strong{{color:var(--amber);font-weight:700}}
.alm-bars{{display:flex;flex-direction:column;gap:18px}}
.alm-bar-row{{display:flex;flex-direction:column;gap:0}}
.alm-bar-header{{
  display:flex;justify-content:space-between;align-items:baseline;
  font-family:var(--font-d);font-size:13px;color:var(--text);
  margin-bottom:6px;gap:8px;flex-wrap:wrap;row-gap:4px;
}}
.alm-bar-track{{height:22px;background:var(--bg3);border-radius:4px;position:relative;overflow:hidden}}
.alm-bar-fill{{
  position:absolute;top:0;left:0;height:100%;border-radius:4px;
  transition:width .8s cubic-bezier(.16,1,.3,1);
}}

.did-table{{width:100%;border-collapse:collapse;margin-top:10px;table-layout:fixed}}
.did-table col.c-pair    {{width:130px}}
.did-table col.c-industry{{width:auto}}
.did-table col.c-delta   {{width:82px}}
.did-table col.c-att     {{width:148px}}
.did-table col.c-reason  {{width:220px}}
.did-table th{{
  font-family:var(--font-d);font-size:12px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:var(--text);
  padding:12px 10px;border-bottom:1px solid var(--border);text-align:left;overflow:hidden;
}}
.did-table td{{
  padding:15px 10px;border-bottom:1px solid rgba(34,34,50,.5);
  font-size:13px;vertical-align:top;color:var(--text);overflow:hidden;
}}
.did-name-cell{{white-space:normal;line-height:1.5;overflow:visible}}
.did-att{{font-family:var(--font-m);font-size:24px;font-weight:600}}
.did-formula{{font-family:var(--font-m);font-size:12px;color:var(--text);margin-top:6px;line-height:1.7}}

/* ── ANIMATIONS ── */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
.fade-up{{animation:fadeUp .4s ease both}}
.fade-up-1{{animation-delay:.05s}}
.fade-up-2{{animation-delay:.1s}}
.fade-up-3{{animation-delay:.15s}}
.fade-up-4{{animation-delay:.2s}}

.empty-state{{
  display:flex;align-items:center;justify-content:center;
  height:200px;color:var(--text);font-family:var(--font-d);font-size:14px;
}}

/* ── GLOBAL TOOLTIP ── */
#alm-tt{{
  position:fixed;z-index:2000;pointer-events:none;display:none;
  background:rgba(9,9,14,.97);backdrop-filter:blur(14px);
  border:1px solid var(--border);border-radius:8px;
  padding:9px 15px;font-family:var(--font-d);font-size:13px;
  color:var(--text);white-space:nowrap;
  box-shadow:0 6px 28px rgba(0,0,0,.5);
}}
#alm-tt .tt-code{{font-weight:700;margin-right:6px}}
[data-tt]{{cursor:default}}
</style>
</head>
<body>

<!-- TOP BAR -->
<div id="topbar">
  <div class="title">AI <span>×</span> Labor — Trucking Supply-Chain Footprint</div>
  <div class="wave-toggle">
    <button class="wave-btn active" data-wave="current" onclick="setWave('current')">Current Wave (AV)</button>
    <button class="wave-btn" data-wave="llm" onclick="setWave('llm')">LLM Next Wave</button>
  </div>
</div>

<!-- SIDEBAR -->
<div id="sidebar">
  <div class="sidebar-logo">AI×Labor<span>.</span><sub>Trucking Footprint · IMPLAN I-O</sub></div>
  <nav>
    <div class="nav-section">Views</div>
    <div class="nav-item active" onclick="showView('overview')">
      <span class="nav-icon">◈</span> Overview
    </div>
    <div class="nav-item" onclick="showView('explorer')">
      <span class="nav-icon">⊞</span> Industry Explorer
    </div>
    <div class="nav-item" onclick="showView('exposure')">
      <span class="nav-icon">▦</span> Impact Map
    </div>
    <div class="nav-item" onclick="showView('waves')">
      <span class="nav-icon">⟴</span> Wave Analysis
    </div>
    <div class="nav-section">Filters</div>
    <div style="padding:0 16px 10px">
      <div class="filter-label">Search</div>
      <input type="text" id="global-search" placeholder="Industry name…" oninput="onSearch()">
    </div>
    <div style="padding:0 16px 10px">
      <div class="filter-label">Sector</div>
      <select id="sector-filter" onchange="onFilter()"><option value="">All sectors</option></select>
    </div>
    <div style="padding:0 16px 10px">
      <div class="filter-label">Task Type</div>
      <select id="alm-filter" onchange="onFilter()">
        <option value="">All types</option>
        <option value="NRC-A">NRC Analytic</option>
        <option value="NRC-I">NRC Interpersonal</option>
        <option value="RC">Routine Cognitive</option>
        <option value="RM">Routine Manual</option>
        <option value="NRM">Non-routine Manual</option>
      </select>
    </div>
    <div style="padding:0 16px 16px">
      <div class="filter-label">Direction</div>
      <select id="dir-filter" onchange="onFilter()">
        <option value="">Winners &amp; losers</option>
        <option value="losers">Losers only</option>
        <option value="winners">Winners only</option>
      </select>
    </div>
  </nav>
  <div class="sidebar-meta">
    IMPLAN I-O 2024 · US National<br>505 industries · 23 sectors<br>
    Source: EY analysis · Pre_E / Post_E model runs
  </div>
</div>

<!-- MAIN -->
<div id="main">

  <!-- VIEW: OVERVIEW -->
  <div id="view-overview" class="view active">
    <div class="hero-row">
      <div class="hero-card loss fade-up">
        <div class="hc-label">Net Jobs at Risk — AV Wave</div>
        <div class="hc-val" id="counter-jobs">−52,231</div>
        <div class="hc-sub">Full- and part-time jobs lost across trucking's 6.59M-job supply-chain footprint</div>
      </div>
      <div class="hero-card loss fade-up fade-up-1">
        <div class="hc-label">Supply-Chain Contraction</div>
        <div class="hc-val">−0.79%</div>
        <div class="hc-sub">Of trucking's total economic footprint — direct workers, suppliers, and household spending</div>
      </div>
      <div class="hero-card amber fade-up fade-up-2">
        <div class="hc-label">LLM Wave — Next Scenario</div>
        <div class="hc-val" id="counter-llm" style="color:var(--loss)">−228,153</div>
        <div class="hc-sub">4.4× the AV impact — shifts from manual to cognitive and office workers</div>
      </div>
      <div class="hero-card teal fade-up fade-up-3">
        <div class="hc-label">Output Impact</div>
        <div class="hc-val">≈ $0</div>
        <div class="hc-sub">AV preserves trucking output via productivity gains — jobs fall but freight still moves</div>
      </div>
    </div>

    <div class="section-head">Primary Economic Impact — Industry: Trucking Transportation</div>
    <div class="impact-summary-table">
      <table>
        <thead>
          <tr>
            <th>Impact Type</th>
            <th>Employment</th>
            <th>Labor Income</th>
            <th>Value Added (GDP)</th>
            <th>Output</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><span class="mult-tag direct">Direct</span></td>
            <td class="td-loss">−69,084</td>
            <td class="td-loss">−$7.0B</td>
            <td class="td-loss">−$6.0B</td>
            <td>$0</td>
          </tr>
          <tr>
            <td><span class="mult-tag indirect">Indirect &amp; Induced</span></td>
            <td class="td-gain">+16,854</td>
            <td class="td-gain">+$1.0B</td>
            <td class="td-gain">+$2.0B</td>
            <td class="td-gain">+$3.0B</td>
          </tr>
          <tr class="total-row">
            <td><span class="mult-tag total">Total Net</span></td>
            <td class="td-loss">−52,231</td>
            <td class="td-loss">−$5.0B</td>
            <td class="td-loss">−$4.0B</td>
            <td>≈ $0</td>
          </tr>
        </tbody>
      </table>
      <div class="ist-scope">United States (US Totals) · IMPLAN I-O 2024 · Autonomous Vehicle shock scenario · Pre-AI 2024 baseline</div>
      <div class="ist-defs">
        <strong>Employment</strong> — Full- and part-time jobs (headcount) &nbsp;·&nbsp;
        <strong>Labor Income</strong> — Salaries, wages, and benefits &nbsp;·&nbsp;
        <strong>Value Added (GDP)</strong> — Labor income + property income + taxes on production &nbsp;·&nbsp;
        <strong>Output</strong> — Value added + intermediate inputs (broadest activity measure)
      </div>
    </div>
    <div class="multiplier-strip">
      <div class="ms-cell">
        <div class="ms-label">Employment Multiplier</div>
        <div class="ms-val">0.756×</div>
        <div class="ms-sub">For every 100 direct trucking jobs eliminated, 76 net jobs are lost economy-wide — supplier and household gains partially cushion the blow.</div>
      </div>
      <div class="ms-cell">
        <div class="ms-label">GDP per Direct Job Lost</div>
        <div class="ms-val td-loss">−$57,901</div>
        <div class="ms-sub">Each direct trucking job lost removes $57,901 in annual value added — concentrated in Transportation &amp; Logistics and downstream supply sectors.</div>
      </div>
      <div class="ms-cell">
        <div class="ms-label">Labor Income per Direct Job Lost</div>
        <div class="ms-val td-loss">−$72,376</div>
        <div class="ms-sub">Each direct job lost reduces total economy-wide labor income by $72,376 — roughly 1.4× the median trucker wage — as suppliers and local businesses feel the ripple.</div>
      </div>
      <div class="ms-cell">
        <div class="ms-label">Occupation at Risk</div>
        <div class="ms-val" style="font-size:22px;line-height:1.2">876,539<br><span style="font-size:14px;font-weight:400">heavy truck drivers</span></div>
        <div class="ms-sub">Of trucking's 2.43M direct workers, 876K are heavy truck drivers — the occupation most directly displaced by AV. Dispatchers, mechanics, and loaders are largely unaffected.</div>
      </div>
    </div>

    <div class="section-head">Supply-Chain Footprint by Sector — 23 sectors</div>
    <div class="sector-grid" id="sector-grid"></div>
  </div>

  <!-- VIEW: EXPLORER -->
  <div id="view-explorer" class="view">
    <div class="explorer-layout">
      <div class="table-wrap">
        <div class="table-scroll">
          <table id="industry-table">
            <colgroup>
              <col class="col-name">
              <col class="col-alm">
              <col class="col-num">
              <col class="col-num">
              <col class="col-num">
            </colgroup>
            <thead>
              <tr>
                <th onclick="sortBy('name')">Industry</th>
                <th onclick="sortBy('alm')">Type</th>
                <th onclick="sortBy('chg_emp')" class="td-num sorted">Δ Jobs</th>
                <th onclick="sortBy('pct_emp')" class="td-num">%</th>
                <th onclick="sortBy('mean_wage')" class="td-num">Avg Wage</th>
              </tr>
            </thead>
            <tbody id="table-body"></tbody>
          </table>
        </div>
        <div class="table-status">
          <span id="table-count" style="font-family:var(--font-d)"></span>
          <span style="font-family:var(--font-m);font-size:13px;color:var(--text)">Click row for detail</span>
        </div>
      </div>
      <div class="detail-panel" id="detail-panel">
        <div class="dp-empty">
          <div class="dp-icon">◎</div>
          <p>Select an industry<br>to see full breakdown</p>
        </div>
      </div>
    </div>
  </div>

  <!-- VIEW: IMPACT MAP -->
  <div id="view-exposure" class="view">
    <div class="impact-layout">
      <div style="flex-shrink:0">
        <div class="section-head" style="margin-bottom:12px">Multiplier Waterfall — Direct · Indirect &amp; Induced · Net Total · All Four Metrics</div>
        <div id="waterfall-container" style="display:grid;grid-template-columns:1fr 1fr;gap:12px"></div>
      </div>
      <div class="impact-bottom-3">
        <div style="display:flex;flex-direction:column;gap:12px">
          <div class="impact-panel" style="overflow:hidden;flex:2;min-height:0">
            <div class="impact-panel-title">Sector Job Change — Treemap</div>
            <div id="sector-impact-bars" style="flex:1;min-height:0;overflow:hidden"></div>
          </div>
          <div class="impact-panel" style="flex:1;min-height:0">
            <div class="impact-panel-title">Job Loss by Task Type</div>
            <div id="alm-donut" style="display:flex;flex-direction:row;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap;flex:1"></div>
          </div>
        </div>
        <div class="impact-panel">
          <div class="impact-panel-title">Sector × Task Type Heatmap</div>
          <div id="alm-heatmap" style="overflow-x:auto;overflow-y:auto;flex:1;min-height:0"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- VIEW: WAVE ANALYSIS -->
  <div id="view-waves" class="view">
    <div class="wave-layout">
      <div class="wave-panel">
        <div class="wp-title" style="color:var(--teal)">Current AI Wave</div>
        <div class="wp-subtitle">Autonomous vehicle shock — concentrated in Routine Manual sectors</div>
        <div class="alm-bars" id="wave-current-bars"></div>
      </div>
      <div class="wave-panel">
        <div class="wp-title" style="color:var(--amber)">LLM Next Wave</div>
        <div class="llm-def-box">
          <strong>What is the Next Wave?</strong> Large language models automate cognitive knowledge work — analysis, writing, legal review, code generation, data processing — unlike the current AV wave which targets physical and manual labor.<br><br>
          <strong>Timeframe:</strong> 2025–2030 transition horizon (1–5 year adoption curve) &nbsp;·&nbsp;
          <strong>Shock rates (Acemoglu 2023):</strong> Routine Cognitive −15% &nbsp;·&nbsp; NRC-Analytic −8% &nbsp;·&nbsp; NRC-Interpersonal −5% &nbsp;·&nbsp; Manual workers: unaffected
        </div>
        <div class="wp-subtitle">Projected employment change by task type, assuming full shock realization</div>
        <div class="alm-bars" id="wave-llm-bars"></div>
      </div>
    </div>

    <div class="section-head">Difference-in-Differences Lab</div>
    <div style="background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden">
      <div style="padding:16px 18px;border-bottom:1px solid var(--border);font-family:var(--font-d);font-size:14px;color:var(--text)">
        ATT = (Post<sub>treated</sub> − Pre<sub>treated</sub>) − (Post<sub>control</sub> − Pre<sub>control</sub>)
        &nbsp;·&nbsp; Pre-computed pairs from our I-O model
      </div>
      <table class="did-table" id="did-table">
        <colgroup>
          <col class="c-pair">
          <col class="c-industry">
          <col class="c-industry">
          <col class="c-delta">
          <col class="c-delta">
          <col class="c-att">
          <col class="c-reason">
        </colgroup>
        <thead>
          <tr>
            <th>Pair</th>
            <th>Treated Industry</th>
            <th>Control Industry</th>
            <th class="td-num">Treated Δ</th>
            <th class="td-num">Control Δ</th>
            <th>ATT</th>
            <th>Rationale</th>
          </tr>
        </thead>
        <tbody id="did-body"></tbody>
      </table>
    </div>
  </div>

</div>

<div id="alm-tt"></div>
<script type="application/json" id="raw-data">{RAW}</script>
<script>
// ── DATA ─────────────────────────────────────────────────────────────────────
const D = JSON.parse(document.getElementById('raw-data').textContent);
const INDUSTRIES = D.industries;
const SECTORS    = D.sectors;
const DID_PAIRS  = D.did_pairs;

// ── COLORS ───────────────────────────────────────────────────────────────────
const ALM_COLOR = {{
  'NRC-A': '#4F87F5',
  'NRC-I': '#A855F7',
  'RC':    '#EAB208',
  'RM':    '#F87316',
  'NRM':   '#22D3EE',
}};
const ALM_LABEL = {{
  'NRC-A': 'Cognitive Analytic',
  'NRC-I': 'Cognitive Interpersonal',
  'RC':    'Routine Cognitive',
  'RM':    'Routine Manual',
  'NRM':   'Non-routine Manual',
}};
const ALM_TT = {{
  'NRC-A': 'NRC-A · Non-Routine Cognitive — Analytic',
  'NRC-I': 'NRC-I · Non-Routine Cognitive — Interpersonal',
  'RC':    'RC · Routine Cognitive',
  'RM':    'RM · Routine Manual',
  'NRM':   'NRM · Non-Routine Manual',
}};

// ── GLOBAL ALM TOOLTIP ───────────────────────────────────────────────────────
(function() {{
  const tt = document.getElementById('alm-tt');
  document.addEventListener('mouseover', e => {{
    const el = e.target.closest('[data-tt]');
    if (!el) {{ tt.style.display='none'; return; }}
    tt.innerHTML = el.dataset.tt;
    tt.style.display = 'block';
  }});
  document.addEventListener('mousemove', e => {{
    if (tt.style.display === 'none') return;
    const x = e.clientX + 16, y = e.clientY - 44;
    tt.style.left = Math.min(x, window.innerWidth - tt.offsetWidth - 8) + 'px';
    tt.style.top  = Math.max(8, y) + 'px';
  }});
  document.addEventListener('mouseout', e => {{
    if (e.target.closest('[data-tt]') && !e.relatedTarget?.closest('[data-tt]'))
      tt.style.display = 'none';
  }});
}})();

// ── STATE ────────────────────────────────────────────────────────────────────
let currentWave = 'current';
let sortKey = 'chg_emp';
let sortDir = 1; // 1=asc, -1=desc
let filtered = INDUSTRIES.slice();
let selectedIndustry = null;

// ── HELPERS ──────────────────────────────────────────────────────────────────
const fmt  = n => n == null ? '—' : Math.abs(n) >= 1e6
  ? (n/1e6).toFixed(1)+'M'
  : Math.abs(n) >= 1e3
  ? Number(n).toLocaleString('en-US',{{maximumFractionDigits:0}})
  : Number(n).toFixed(1);
const fmtW = n => n ? '$'+Math.round(n/1000)+'K' : '—';
const fmtP = n => (n >= 0 ? '+' : '') + Number(n).toFixed(2) + '%';
const sign  = n => n < 0 ? 'td-loss' : n > 0 ? 'td-gain' : 'td-neutral';
const signS = n => n < 0 ? '−' : n > 0 ? '+' : '';

function animateCounter(el, target, duration=1800) {{
  if (!el) return;
  const start = performance.now();
  const step = t => {{
    const p = Math.min((t - start) / duration, 1);
    const e = 1 - Math.pow(1 - p, 3);
    el.textContent = (target < 0 ? '−' : '+') + Math.round(Math.abs(target * e)).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  }};
  requestAnimationFrame(step);
}}

// ── WAVE TOGGLE ──────────────────────────────────────────────────────────────
function setWave(w) {{
  currentWave = w;
  document.querySelectorAll('.wave-btn').forEach(b => b.classList.toggle('active', b.dataset.wave === w));
  renderView(currentView);
}}

// ── NAVIGATION ───────────────────────────────────────────────────────────────
let currentView = 'overview';
function showView(name) {{
  currentView = name;
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('view-' + name).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n => {{
    if (n.getAttribute('onclick')?.includes(name)) n.classList.add('active');
  }});
  renderView(name);
}}

function renderView(name) {{
  if (name === 'overview')  renderOverview();
  if (name === 'explorer')  renderTable();
  if (name === 'exposure')  renderImpact();
  if (name === 'waves')     renderWaves();
}}

// ── OVERVIEW ─────────────────────────────────────────────────────────────────
function renderOverview() {{
  const netJobs = currentWave === 'current' ? -52231 : D.summary.llm_wave.net_jobs;
  animateCounter(document.getElementById('counter-jobs'), netJobs);
  animateCounter(document.getElementById('counter-llm'), D.summary.llm_wave.net_jobs);
  renderSectorGrid();
}}

function renderSectorGrid() {{
  const grid = document.getElementById('sector-grid');
  const maxAbs = Math.max(...SECTORS.map(s => Math.abs(s.Job_Change)));
  grid.innerHTML = SECTORS
    .slice().sort((a,b) => a.Job_Change - b.Job_Change)
    .map(s => {{
      const cls = s.Job_Change < -10 ? 'neg' : s.Job_Change > 10 ? 'pos' : 'neu';
      const barW = Math.min(100, Math.abs(s.Job_Change) / maxAbs * 100).toFixed(1);
      const chgVal = currentWave === 'llm'
        ? INDUSTRIES.filter(i=>i.sector===s.Sector).reduce((a,b)=>a+b.llm_chg_emp,0)
        : s.Job_Change;
      return `<div class="sector-card ${{cls}}">
        <div class="sc-name">${{s.Sector}}</div>
        <div class="sc-value-row">
          <span class="sc-val">${{signS(chgVal)}}${{fmt(Math.abs(chgVal))}}</span>
          <span class="sc-pct">${{fmtP(s.Pct_Change)}}</span>
        </div>
        <div class="sc-industries">${{s.Industries}} industries</div>
        <div class="sc-bar"><div class="sc-bar-fill" style="width:${{barW}}%"></div></div>
      </div>`;
    }}).join('');
}}

// ── EXPLORER ─────────────────────────────────────────────────────────────────
function populateSectorFilter() {{
  const sel = document.getElementById('sector-filter');
  [...new Set(INDUSTRIES.map(i=>i.sector))].sort().forEach(s => {{
    const o = document.createElement('option');
    o.value = o.textContent = s;
    sel.appendChild(o);
  }});
}}

function onSearch() {{
  applyFilters();
  if (currentView !== 'explorer') showView('explorer');
  else renderTable();
}}
function onFilter() {{
  applyFilters();
  if (currentView !== 'explorer') showView('explorer');
  else renderTable();
}}

function applyFilters() {{
  const q   = document.getElementById('global-search').value.toLowerCase();
  const sec = document.getElementById('sector-filter').value;
  const alm = document.getElementById('alm-filter').value;
  const dir = document.getElementById('dir-filter').value;
  filtered = INDUSTRIES.filter(d => {{
    if (q && !d.full.toLowerCase().includes(q)) return false;
    if (sec && d.sector !== sec) return false;
    if (alm && d.alm !== alm) return false;
    if (dir === 'losers'  && d.chg_emp >= 0) return false;
    if (dir === 'winners' && d.chg_emp <= 0) return false;
    return true;
  }});
  filtered.sort((a,b) => (a[sortKey] - b[sortKey]) * sortDir);
}}

function sortBy(key) {{
  if (sortKey === key) sortDir *= -1;
  else {{ sortKey = key; sortDir = key === 'chg_emp' ? 1 : -1; }}
  document.querySelectorAll('thead th').forEach(th => th.classList.remove('sorted'));
  event.target.classList.add('sorted');
  applyFilters();
  renderTable();
}}

function renderTable() {{
  const body = document.getElementById('table-body');
  const show = filtered.slice(0, 300);
  body.innerHTML = show.map(d => {{
    const chg = currentWave === 'llm' ? d.llm_chg_emp : d.chg_emp;
    const cls = sign(chg);
    const almColor = ALM_COLOR[d.alm] || '#888';
    return `<tr onclick="selectIndustry('${{d.full.replace(/'/g,"\\'")}}')">
      <td title="${{d.full}}">${{d.name}}</td>
      <td><span class="alm-badge" style="background:${{almColor}}22;color:${{almColor}}" data-tt="${{ALM_TT[d.alm]}}">${{d.alm}}</span></td>
      <td class="td-num ${{cls}}">${{chg>=0?'+':''}}${{fmt(chg)}}</td>
      <td class="td-num ${{cls}}">${{fmtP(d.pct_emp)}}</td>
      <td class="td-num">${{fmtW(d.mean_wage)}}</td>
    </tr>`;
  }}).join('');
  document.getElementById('table-count').textContent =
    `${{filtered.length}} industries` + (filtered.length > 300 ? ' (showing 300)' : '');
}}

function selectIndustry(fullName) {{
  selectedIndustry = INDUSTRIES.find(i => i.full === fullName);
  document.querySelectorAll('#table-body tr').forEach(tr => tr.classList.remove('selected'));
  event.currentTarget?.classList.add('selected');
  renderDetailPanel();
}}

function renderDetailPanel() {{
  const d = selectedIndustry;
  if (!d) return;
  const chg = currentWave === 'llm' ? d.llm_chg_emp : d.chg_emp;
  const almColor = ALM_COLOR[d.alm];
  const maxEmp = Math.max(d.pre_emp_d, d.pre_emp_i, d.pre_emp_ind);

  const impactRows = [
    ['Direct',   d.pre_emp_d,   d.post_emp_d],
    ['Indirect', d.pre_emp_i,   d.post_emp_i],
    ['Induced',  d.pre_emp_ind, d.post_emp_ind],
  ].map(([label, pre, post]) => {{
    const max = Math.max(d.pre_emp_d, d.pre_emp_i, d.pre_emp_ind, 1);
    const preW = (pre/max*100).toFixed(1);
    const postW = (post/max*100).toFixed(1);
    const delta = post - pre;
    return `<div class="ib-row">
      <div class="ib-label">
        <span class="ib-name">${{label}}</span>
        <div class="ib-vals">
          <span style="color:var(--text)">${{fmt(pre)}}</span>
          <span>→</span>
          <span class="${{sign(delta)}}">${{fmt(post)}}</span>
        </div>
      </div>
      <div class="ib-track">
        <div class="ib-pre" style="width:${{preW}}%;background:${{almColor}}"></div>
        <div class="ib-post" style="width:${{postW}}%;background:${{almColor}}"></div>
      </div>
    </div>`;
  }}).join('');

  document.getElementById('detail-panel').innerHTML = `
    <div>
      <div class="dp-name">${{d.name}}</div>
      <div class="dp-sector">
        ${{d.sector}} &nbsp;·&nbsp;
        <span style="color:${{almColor}}" data-tt="${{ALM_TT[d.alm]}}">${{ALM_LABEL[d.alm]}}</span>
      </div>
    </div>
    <div class="dp-kpis">
      <div class="dp-kpi">
        <div class="dp-kpi-label">Pre-AI Employment</div>
        <div class="dp-kpi-val">${{fmt(d.pre_emp)}}</div>
      </div>
      <div class="dp-kpi">
        <div class="dp-kpi-label">Job Change</div>
        <div class="dp-kpi-val ${{sign(chg)}}" style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap">
          <span>${{chg>=0?'+':''}}${{fmt(chg)}}</span>
          <span style="font-size:22px;font-weight:500">${{fmtP(d.pct_emp)}}</span>
        </div>
      </div>
      <div class="dp-kpi">
        <div class="dp-kpi-label">Avg Annual Wage</div>
        <div class="dp-kpi-val">${{fmtW(d.mean_wage)}}</div>
      </div>
      <div class="dp-kpi">
        <div class="dp-kpi-label">AI Risk Score</div>
        <div class="dp-kpi-val" style="color:${{almColor}}">${{(d.risk*100).toFixed(0)}}%</div>
      </div>
    </div>
    <div>
      <div class="dp-section-title">Employment Breakdown — Direct / Indirect / Induced</div>
      <div class="impact-bars">${{impactRows}}</div>
    </div>
    <div>
      <div class="dp-section-title">Output Impact</div>
      <div style="display:flex;gap:10px">
        <div class="dp-kpi" style="flex:1">
          <div class="dp-kpi-label">Pre-AI Output</div>
          <div class="dp-kpi-val" style="font-size:18px">$${{(d.pre_out/1e9).toFixed(1)}}B</div>
        </div>
        <div class="dp-kpi" style="flex:1">
          <div class="dp-kpi-label">Output Change</div>
          <div class="dp-kpi-val ${{sign(d.chg_out)}}" style="font-size:18px">${{d.chg_out>=0?'+':''}}$${{(d.chg_out/1e6).toFixed(0)}}M</div>
        </div>
      </div>
    </div>
    <div class="llm-box">
      <div class="llm-box-title">LLM Next Wave Projection</div>
      <div class="llm-box-val">${{d.llm_chg_emp>=0?'+':''}}${{fmt(d.llm_chg_emp)}} jobs</div>
      <div class="llm-box-sub">Shock rate: ${{(d.llm_shock_rate*100).toFixed(0)}}% &nbsp;·&nbsp; Source: Acemoglu (2023)</div>
    </div>
  `;
}}

// ── IMPACT MAP ───────────────────────────────────────────────────────────────
function renderImpact() {{
  renderWaterfall();
  renderTreemap();
  renderHeatmap();
  renderJobLossPies();
}}

function renderWaterfall() {{
  const container = document.getElementById('waterfall-container');
  if (!container) return;

  // All four impact metrics — AV current wave values from IMPLAN model
  // Employment: D=-69,084 | I+Ind=+16,854 | Total=-52,231
  // Labor Income: D=-7.0B | I+Ind=+2.0B | Total=-5.0B
  // Value Added: D=-6.0B | I+Ind=+2.0B | Total=-4.0B
  // Output: D=$0 (AV preserves output via productivity) | I+Ind=+3.0B | Total≈$0
  const LLM_EMP_D  = INDUSTRIES.filter(i=>i.alm==='RM').reduce((s,i)=>s+i.llm_chg_emp,0);
  const LLM_EMP_II = INDUSTRIES.filter(i=>i.alm!=='RM').reduce((s,i)=>s+i.llm_chg_emp,0);
  const LLM_TOTAL  = INDUSTRIES.reduce((s,i)=>s+i.llm_chg_emp,0);

  const METRICS = [
    {{
      label: 'Employment',
      sub: 'Full- & part-time jobs',
      direct:   currentWave==='llm' ? LLM_EMP_D  : -69084,
      ii:       currentWave==='llm' ? LLM_EMP_II : 16854,
      total:    currentWave==='llm' ? LLM_TOTAL  : -52231,
      fmtV: v => {{
        if (v === 0) return '0';
        const abs = Math.abs(v);
        const s = v >= 0 ? '+' : '−';
        return s + (abs >= 1000 ? (abs/1000).toFixed(0)+'K' : abs.toFixed(0));
      }},
      color: v => v < 0 ? '#C8243E' : v > 0 ? '#1B9160' : '#38364A',
      unitY: v => Math.abs(v)>=1000?(v<0?'−':'+')+(Math.abs(v)/1000).toFixed(0)+'K':(v<0?'−':'+')+Math.abs(v).toFixed(0),
    }},
    {{
      label: 'Labor Income',
      sub: 'Salaries, wages & benefits',
      direct: currentWave==='llm' ? -9.0  : -7.0,
      ii:     currentWave==='llm' ?  2.5  :  2.0,
      total:  currentWave==='llm' ? -6.5  : -5.0,
      fmtV: v => v===0 ? '$0' : (v>=0?'+$':'-$')+Math.abs(v).toFixed(1)+'B',
      color: v => v < 0 ? '#C8243E' : v > 0 ? '#1B9160' : '#38364A',
      unitY: v => (v<0?'-$':'$')+Math.abs(v).toFixed(1)+'B',
    }},
    {{
      label: 'Value Added (GDP)',
      sub: 'Labor income + property income + taxes',
      direct: currentWave==='llm' ? -8.0  : -6.0,
      ii:     currentWave==='llm' ?  2.5  :  2.0,
      total:  currentWave==='llm' ? -5.5  : -4.0,
      fmtV: v => v===0 ? '$0' : (v>=0?'+$':'-$')+Math.abs(v).toFixed(1)+'B',
      color: v => v < 0 ? '#C8243E' : v > 0 ? '#1B9160' : '#38364A',
      unitY: v => (v<0?'-$':'$')+Math.abs(v).toFixed(1)+'B',
    }},
    {{
      label: 'Output',
      sub: 'Value added + intermediate inputs',
      direct: 0,
      ii:     currentWave==='llm' ? 4.0 : 3.0,
      total:  0,
      fmtV: v => v===0 ? '≈$0' : (v>=0?'+$':'-$')+Math.abs(v).toFixed(1)+'B',
      color: v => v < 0 ? '#C8243E' : v > 0 ? '#1B9160' : '#38364A',
      unitY: v => v===0?'$0':(v<0?'-$':'$')+Math.abs(v).toFixed(1)+'B',
      note: 'AV preserves output via productivity gains',
    }},
  ];

  const cW = container.clientWidth || 800;
  const panelW = Math.floor((cW - 12) / 2);
  const PH = 230;
  const PAD = {{l:58, r:18, t:54, b:42}};

  container.innerHTML = METRICS.map(m => {{
    const bw = panelW - PAD.l - PAD.r;
    const bh = PH - PAD.t - PAD.b;

    // Waterfall steps: 0 → direct → direct+ii (running sum) → total (anchored at 0)
    const runDirect = m.direct;
    const runII    = m.direct + m.ii;
    const allPts   = [0, runDirect, runII, m.total];
    const rawMin   = Math.min(...allPts);
    const rawMax   = Math.max(...allPts);
    const span     = rawMax - rawMin || 1;
    const yPad     = span * 0.16;
    const yMin     = rawMin - yPad;
    const yMax     = rawMax + yPad;
    const yRange   = yMax - yMin;
    const yS       = v => PAD.t + (1 - (v - yMin) / yRange) * bh;
    const yZero    = yS(0);

    // 3 bars: Direct, I+Ind (floating), Total
    const nBars = 3;
    const segW  = bw / (nBars * 2 + 1);
    const barW  = segW * 1.6;
    const bars  = [
      {{label:'Direct',       x: PAD.l + segW * 1,   lo: Math.min(0, runDirect), hi: Math.max(0, runDirect),  val: m.direct, float: false}},
      {{label:'I + Ind', x: PAD.l + segW * 3, lo: Math.min(runDirect, runII), hi: Math.max(runDirect, runII), val: m.ii, float: true, floatBase: runDirect}},
      {{label:'Net Total',    x: PAD.l + segW * 5,   lo: Math.min(0, m.total),  hi: Math.max(0, m.total),   val: m.total, float: false}},
    ];

    let s = '';

    // Subtle grid lines at reasonable ticks
    const nTicks = 4;
    const tickStep = span / nTicks;
    const mag = Math.pow(10, Math.floor(Math.log10(Math.max(tickStep,0.001))));
    const niceStep = Math.ceil(tickStep / mag) * mag;
    for (let v = Math.floor(rawMin/niceStep)*niceStep; v <= rawMax + niceStep*0.1; v += niceStep) {{
      const yt = yS(v);
      if (yt < PAD.t || yt > PAD.t+bh) continue;
      s += `<line x1="${{PAD.l}}" y1="${{yt.toFixed(1)}}" x2="${{(PAD.l+bw).toFixed(1)}}" y2="${{yt.toFixed(1)}}" stroke="${{Math.abs(v)<0.0001?'#38364A':'#1a1a24'}}" stroke-width="${{Math.abs(v)<0.0001?1.5:0.7}}"/>`;
      if (Math.abs(v) < 0.0001 || Math.abs((yt-yS(0))/(bh||1)) > 0.08)
        s += `<text x="${{(PAD.l-5).toFixed(1)}}" y="${{(yt+4).toFixed(1)}}" fill="#8A84A0" font-size="12" font-family="JetBrains Mono" text-anchor="end">${{m.unitY(v)}}</text>`;
    }}

    // Zero line (always shown)
    if (yZero >= PAD.t && yZero <= PAD.t+bh)
      s += `<line x1="${{PAD.l}}" y1="${{yZero.toFixed(1)}}" x2="${{(PAD.l+bw).toFixed(1)}}" y2="${{yZero.toFixed(1)}}" stroke="#38364A" stroke-width="1.5"/>`;

    // Connector dashes between bars
    // Bar 0 → Bar 1: connect at the running total after direct
    const connY01 = yS(runDirect);
    s += `<line x1="${{(bars[0].x + barW/2 + 2).toFixed(1)}}" y1="${{connY01.toFixed(1)}}" x2="${{(bars[1].x - barW/2 - 2).toFixed(1)}}" y2="${{connY01.toFixed(1)}}" stroke="#38364A" stroke-width="1" stroke-dasharray="5,3"/>`;
    // Bar 1 → Bar 2: connect at zero (total anchors at zero)
    s += `<line x1="${{(bars[1].x + barW/2 + 2).toFixed(1)}}" y1="${{yZero.toFixed(1)}}" x2="${{(bars[2].x - barW/2 - 2).toFixed(1)}}" y2="${{yZero.toFixed(1)}}" stroke="#38364A" stroke-width="1" stroke-dasharray="5,3"/>`;

    // Draw each bar
    bars.forEach((b, bi) => {{
      const y1 = yS(b.hi);
      const y2 = yS(b.lo);
      const barH = Math.max(2, y2 - y1);
      const color = m.color(b.val);
      const valStr = m.fmtV(b.val);
      const valColor = m.color(b.val);

      // Bar rect with subtle stroke
      s += `<rect x="${{(b.x - barW/2).toFixed(1)}}" y="${{y1.toFixed(1)}}" width="${{barW.toFixed(1)}}" height="${{barH.toFixed(1)}}" fill="${{color}}" fill-opacity="0.78" rx="4" stroke="${{color}}" stroke-opacity="0.3" stroke-width="1"/>`;

      // Value label — above bar if negative (bar goes down), below if positive
      const labelAbove = b.val < 0 || (b.float && b.val < 0);
      const valY = b.val < 0 ? y1 - 7 : y2 + 16;
      const clampedValY = Math.max(PAD.t + 14, Math.min(PAD.t + bh - 4, valY));
      s += `<text x="${{b.x.toFixed(1)}}" y="${{clampedValY.toFixed(1)}}" fill="${{valColor}}" font-size="13" font-family="JetBrains Mono" font-weight="700" text-anchor="middle">${{valStr}}</text>`;

      // Bar label below chart
      const lines = b.label.split('\\n');
      lines.forEach((line, li) =>
        s += `<text x="${{b.x.toFixed(1)}}" y="${{(PAD.t + bh + 16 + li*14).toFixed(1)}}" fill="#8A84A0" font-size="12" font-family="Syne" font-weight="600" text-anchor="middle">${{line}}</text>`
      );
    }});

    // Panel title + subtitle
    s += `<text x="${{(PAD.l + bw/2).toFixed(1)}}" y="20" fill="#EAE5DC" font-size="14" font-family="Syne" font-weight="700" text-anchor="middle">${{m.label}}</text>`;
    s += `<text x="${{(PAD.l + bw/2).toFixed(1)}}" y="36" fill="#8A84A0" font-size="12" font-family="Syne" text-anchor="middle">${{m.sub}}</text>`;

    // Output note overlay (special case)
    const noteHtml = m.note
      ? `<div style="font-family:var(--font-d);font-size:12px;color:var(--amber);text-align:center;padding:4px 8px 8px;line-height:1.5">${{m.note}}</div>`
      : '';

    return `<div style="background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden">
      <svg width="${{panelW}}" height="${{PH}}" viewBox="0 0 ${{panelW}} ${{PH}}" style="display:block">${{s}}</svg>
      ${{noteHtml}}
    </div>`;
  }}).join('');
}}

function renderHeatmap() {{
  const el = document.getElementById('alm-heatmap');
  if (!el) return;
  const alms = ['NRC-A','NRC-I','RC','RM','NRM'];

  const allVals = [];
  SECTORS.forEach(s => alms.forEach(a => {{
    const inds = INDUSTRIES.filter(i=>i.sector===s.Sector&&i.alm===a);
    const chg = currentWave==='llm'
      ? inds.reduce((acc,i)=>acc+i.llm_chg_emp,0)
      : inds.reduce((acc,i)=>acc+i.chg_emp,0);
    allVals.push(chg);
  }}));
  const maxV = Math.max(...allVals.map(Math.abs), 1);

  function cellColor(v) {{
    if (Math.abs(v) < 5) return 'rgba(56,54,74,0.3)';
    const t = Math.min(1, Math.abs(v) / maxV);
    return v < 0
      ? `rgba(200,36,62,${{(t*0.75+0.18).toFixed(2)}})`
      : `rgba(27,145,96,${{(t*0.75+0.18).toFixed(2)}})`;
  }}

  const sectors = SECTORS.slice().sort((a,b) => {{
    const aChg = currentWave==='llm'
      ? INDUSTRIES.filter(i=>i.sector===a.Sector).reduce((s,i)=>s+i.llm_chg_emp,0)
      : a.Job_Change;
    const bChg = currentWave==='llm'
      ? INDUSTRIES.filter(i=>i.sector===b.Sector).reduce((s,i)=>s+i.llm_chg_emp,0)
      : b.Job_Change;
    return aChg - bChg;
  }});

  const rows = sectors.map(s => {{
    const cells = alms.map(a => {{
      const inds = INDUSTRIES.filter(i=>i.sector===s.Sector&&i.alm===a);
      const chg = currentWave==='llm'
        ? inds.reduce((acc,i)=>acc+i.llm_chg_emp,0)
        : inds.reduce((acc,i)=>acc+i.chg_emp,0);
      const disp = Math.abs(chg)<5 ? '—' : (chg>=0?'+':'')+(Math.abs(chg)>=1000?(chg/1000).toFixed(1)+'K':chg.toFixed(0));
      const textColor = Math.abs(chg)<5 ? 'var(--muted)' : '#EAE5DC';
      return `<td class="heatmap-td" style="background:${{cellColor(chg)}};color:${{textColor}}" title="${{s.Sector}} × ${{a}}: ${{chg.toFixed(0)}} jobs">${{disp}}</td>`;
    }}).join('');
    const sname = s.Sector.replace('Manufacturing — ','Mfg ').replace('Agriculture & Natural Resources','Agri & Nat.Res.');
    return `<tr><td class="heatmap-name" title="${{s.Sector}}">${{sname}}</td>${{cells}}</tr>`;
  }}).join('');

  el.innerHTML = `<table class="heatmap-table">
    <thead><tr>
      <th class="heatmap-th heatmap-name-th">Sector</th>
      ${{alms.map(a=>`<th class="heatmap-th" style="color:${{ALM_COLOR[a]}}" data-tt="${{ALM_TT[a]}}">${{a}}</th>`).join('')}}
    </tr></thead>
    <tbody>${{rows}}</tbody>
  </table>`;
}}

function renderJobLossPies() {{
  const el = document.getElementById('alm-donut');
  if (!el) return;

  // Shared donut builder
  function makePie(slices, centerTop, centerBot) {{
    const R=52, r=30, cx=58, cy=58;
    let ang = -Math.PI/2;
    let paths = '';
    slices.forEach(d => {{
      const end = ang + d.frac * 2 * Math.PI;
      const x1=(cx+R*Math.cos(ang)).toFixed(2),  y1=(cy+R*Math.sin(ang)).toFixed(2);
      const x2=(cx+R*Math.cos(end)).toFixed(2),  y2=(cy+R*Math.sin(end)).toFixed(2);
      const i1=(cx+r*Math.cos(ang)).toFixed(2), j1=(cy+r*Math.sin(ang)).toFixed(2);
      const i2=(cx+r*Math.cos(end)).toFixed(2), j2=(cy+r*Math.sin(end)).toFixed(2);
      const lg = d.frac>0.5?1:0;
      paths += `<path d="M${{x1}},${{y1}} A${{R}},${{R}} 0 ${{lg}},1 ${{x2}},${{y2}} L${{i2}},${{j2}} A${{r}},${{r}} 0 ${{lg}},0 ${{i1}},${{j1}} Z" fill="${{d.color}}" opacity="0.85"><title>${{d.label}}: ${{d.detail}}</title></path>`;
      ang = end;
    }});
    paths += `<text x="${{cx}}" y="${{cy-3}}" fill="#EAE5DC" font-size="13" font-family="JetBrains Mono" text-anchor="middle" font-weight="600">${{centerTop}}</text>`;
    paths += `<text x="${{cx}}" y="${{cy+13}}" fill="#8A84A0" font-size="12" font-family="Syne" text-anchor="middle">${{centerBot}}</text>`;
    return `<svg width="116" height="116" viewBox="0 0 116 116">${{paths}}</svg>`;
  }}

  function makeLegend(slices) {{
    return slices.map(d =>
      `<div style="display:flex;align-items:center;gap:6px;margin-bottom:5px">
        <div style="width:10px;height:10px;border-radius:2px;background:${{d.color}};flex-shrink:0"></div>
        <span style="font-family:var(--font-d);font-size:12px;color:var(--text)">${{d.label}}: ${{d.detail}}</span>
      </div>`
    ).join('');
  }}

  // ── PIE 1: By Task Type ────────────────────────────────────────────────────
  const alms = ['NRC-A','NRC-I','RC','RM','NRM'];
  const rawTask = alms.map(a => {{
    const chg = INDUSTRIES.filter(i=>i.alm===a)
      .reduce((s,i)=>s+(currentWave==='llm'?i.llm_chg_emp:i.chg_emp),0);
    return {{label:a, chg, abs:Math.abs(chg), color:ALM_COLOR[a]}};
  }});
  const taskLoss = rawTask.filter(d=>d.chg<0);
  const taskTotal = taskLoss.reduce((s,d)=>s+d.abs,0);
  const taskSlices = taskLoss.map(d=>({{...d, frac:d.abs/taskTotal, detail:(d.abs/taskTotal*100).toFixed(1)+'%'}}));

  // ── PIE 2: By D/I/Ind Channel ─────────────────────────────────────────────
  // AV wave I-O model values; LLM wave uses same D/I/Ind structure scaled
  const isLlm = currentWave==='llm';
  const diiSlices = [
    {{label:'Direct',   abs: isLlm?Math.abs(D.summary.llm_wave.net_jobs*0.90):69084, chg:-1, color:'#C8243E'}},
    {{label:'Indirect', abs: isLlm?Math.abs(D.summary.llm_wave.net_jobs*0.25):41222, chg: 1, color:'#1B9160'}},
    {{label:'Induced',  abs: isLlm?Math.abs(D.summary.llm_wave.net_jobs*0.35):24368, chg:-1, color:'#D49216'}},
  ];
  const diiTotal = diiSlices.reduce((s,d)=>s+d.abs,0);
  diiSlices.forEach(d => {{
    d.frac   = d.abs / diiTotal;
    d.detail = (d.chg<0?'−':'+') + Math.round(d.abs).toLocaleString();
  }});

  const pie1svg = makePie(taskSlices, (taskTotal/1000).toFixed(0)+'K', 'by type');
  const pie2svg = makePie(diiSlices,  (diiTotal /1000).toFixed(0)+'K', 'by channel');

  el.innerHTML = `
    <div style="display:flex;gap:20px;align-items:flex-start;justify-content:space-around;width:100%;flex-wrap:wrap">
      <div style="display:flex;flex-direction:column;align-items:center;gap:8px;flex:1;min-width:180px">
        <div style="font-family:var(--font-d);font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text)">By Task Type</div>
        <div style="display:flex;align-items:center;gap:12px">
          ${{pie1svg}}
          <div>${{makeLegend(taskSlices)}}</div>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:8px;flex:1;min-width:180px">
        <div style="font-family:var(--font-d);font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text)">By Impact Channel</div>
        <div style="display:flex;align-items:center;gap:12px">
          ${{pie2svg}}
          <div>${{makeLegend(diiSlices)}}</div>
        </div>
        <div style="font-family:var(--font-d);font-size:12px;color:var(--amber);text-align:center">Direct shock · Indirect gain · Induced loss</div>
      </div>
    </div>`;
}}

function squarifyLayout(items, x, y, w, h) {{
  if (!items.length) return [];
  const total = items.reduce((s,d) => s+d.value, 0);
  const result = [];
  let remaining = items.slice();
  let rx=x, ry=y, rw=w, rh=h;
  while (remaining.length) {{
    if (remaining.length === 1) {{
      result.push({{...remaining[0], x:rx, y:ry, w:rw, h:rh}});
      break;
    }}
    const remTotal = remaining.reduce((s,d)=>s+d.value,0);
    const isWide = rw >= rh;
    let row = [remaining[0]];
    let rowSum = remaining[0].value;
    const worstAR = (items, sum, cross) => items.reduce((worst,d) => {{
      const size = cross * d.value / sum;
      const stripe = isWide ? rw * sum / remTotal : rh * sum / remTotal;
      return Math.max(worst, Math.max(stripe/Math.max(size,0.01), size/Math.max(stripe,0.01)));
    }}, 0);
    for (let i=1; i<remaining.length; i++) {{
      const cross = isWide ? rh : rw;
      const curAR = worstAR(row, rowSum, cross);
      const newRow = [...row, remaining[i]];
      const newSum = rowSum + remaining[i].value;
      const newAR = worstAR(newRow, newSum, cross);
      if (newAR > curAR && row.length >= 1) break;
      row = newRow; rowSum = newSum;
    }}
    const stripe = isWide ? rw * rowSum / remTotal : rh * rowSum / remTotal;
    let pos = isWide ? ry : rx;
    row.forEach(d => {{
      const size = (isWide ? rh : rw) * d.value / rowSum;
      if (isWide) {{ result.push({{...d, x:rx, y:pos, w:stripe, h:size}}); pos+=size; }}
      else         {{ result.push({{...d, x:pos, y:ry, w:size,   h:stripe}}); pos+=size; }}
    }});
    if (isWide) {{ rx+=stripe; rw-=stripe; }} else {{ ry+=stripe; rh-=stripe; }}
    remaining = remaining.slice(row.length);
  }}
  return result;
}}

function renderTreemap() {{
  const el = document.getElementById('sector-impact-bars');
  if (!el) return;
  // Defer to next frame so flex layout has resolved before we measure
  requestAnimationFrame(() => {{
    const W = Math.max(el.offsetWidth  || 280, 100);
    const H = Math.max(el.offsetHeight || 280, 100);
    _doRenderTreemap(el, W, H);
  }});
}}
function _doRenderTreemap(el, W, H) {{
  const items = SECTORS.map(s => {{
    const chg = currentWave==='llm'
      ? INDUSTRIES.filter(i=>i.sector===s.Sector).reduce((a,b)=>a+b.llm_chg_emp,0)
      : s.Job_Change;
    return {{name:s.Sector, chg, value:Math.max(1, Math.abs(chg))}};
  }}).sort((a,b)=>b.value-a.value);
  const rects = squarifyLayout(items, 0, 0, W, H);
  const abbrev = n => n
    .replace('Manufacturing — ','Mfg ')
    .replace('Agriculture & Natural Resources','Agri & Nat.Res')
    .replace('Professional & Business Services','Prof & Business')
    .replace('Healthcare & Social Assistance','Healthcare')
    .replace('Arts, Entertainment & Recreation','Arts & Rec')
    .replace('Transportation & Logistics','Transport & Log')
    .replace('Personal Services & Repair','Personal Svc')
    .replace('Government & Non-profit','Gov & Nonprofit')
    .replace('Information & Technology','Info & Tech');
  // Build clipPaths and cells separately so defs can go at top of SVG
  const clipDefs = rects.map((r, ri) =>
    `<clipPath id="tmc${{ri}}"><rect x="${{(r.x+2).toFixed(1)}}" y="${{(r.y+2).toFixed(1)}}" width="${{Math.max(0,r.w-4).toFixed(1)}}" height="${{Math.max(0,r.h-4).toFixed(1)}}"/></clipPath>`
  ).join('');

  const cells = rects.map((r, ri) => {{
    const color = r.chg < 0 ? '#C8243E' : '#1B9160';
    const alpha = Math.max(0.45, Math.min(0.85, 0.5 + r.value/items[0].value*0.35));
    const name  = abbrev(r.name);
    const val   = (r.chg>=0?'+':'') + (Math.abs(r.chg)>=1000?(r.chg/1000).toFixed(1)+'K':Math.round(r.chg).toString());
    // Only show text when cell is large enough to read comfortably
    const showName = r.w >= 96 && r.h >= 46;
    const showVal  = r.w >= 68 && r.h >= 30;
    const cp  = `clip-path="url(#tmc${{ri}})"`;
    const midX = (r.x + r.w/2).toFixed(1);
    const nameY = (r.y + r.h/2 - (showVal ? 9 : 0)).toFixed(1);
    const valY  = (r.y + r.h/2 + (showName ? 11 : 0)).toFixed(1);
    return `<rect x="${{(r.x+1).toFixed(1)}}" y="${{(r.y+1).toFixed(1)}}" width="${{Math.max(0,r.w-2).toFixed(1)}}" height="${{Math.max(0,r.h-2).toFixed(1)}}" fill="${{color}}" fill-opacity="${{alpha.toFixed(2)}}" rx="3"><title>${{r.name}}: ${{val}} jobs</title></rect>
    ${{showName ? `<text x="${{midX}}" y="${{nameY}}" fill="#EAE5DC" font-size="12" font-family="Syne" font-weight="700" text-anchor="middle" dominant-baseline="middle" ${{cp}}>${{name}}</text>` : ''}}
    ${{showVal  ? `<text x="${{midX}}" y="${{valY}}"  fill="#EAE5DC" font-size="12" font-family="JetBrains Mono" text-anchor="middle" dominant-baseline="middle" ${{cp}}>${{val}}</text>`  : ''}}`;
  }});

  el.innerHTML = `<svg width="${{W}}" height="${{H}}" viewBox="0 0 ${{W}} ${{H}}" style="display:block"><defs>${{clipDefs}}</defs>${{cells.join('')}}</svg>`;
}}

// ── WAVE ANALYSIS ─────────────────────────────────────────────────────────────
function renderWaves() {{
  const alms = ['NRC-A','NRC-I','RC','RM','NRM'];

  // Compute totals per ALM
  const currentTotals = {{}};
  const llmTotals = {{}};
  alms.forEach(a => {{
    const inds = INDUSTRIES.filter(i=>i.alm===a);
    currentTotals[a] = inds.reduce((s,i)=>s+i.chg_emp, 0);
    llmTotals[a]     = inds.reduce((s,i)=>s+i.llm_chg_emp, 0);
  }});

  const maxAbs = Math.max(...Object.values(currentTotals).map(Math.abs),
                          ...Object.values(llmTotals).map(Math.abs));

  function barRow(alm, val, maxV) {{
    const pct = Math.abs(val) / maxV * 100;
    const color = ALM_COLOR[alm];
    const cls = val < 0 ? 'td-loss' : 'td-gain';
    return `<div class="alm-bar-row">
      <div class="alm-bar-header">
        <span>
          <span style="color:${{color}};font-weight:700;font-family:var(--font-d)" data-tt="${{ALM_TT[alm]}}">${{alm}}</span>
          <span style="color:var(--text);font-size:14px;margin-left:8px;font-family:var(--font-d)">${{ALM_LABEL[alm]}}</span>
        </span>
        <span class="${{cls}}" style="font-family:var(--font-m);font-size:14px;white-space:nowrap">${{val>=0?'+':''}}${{fmt(val)}}</span>
      </div>
      <div class="alm-bar-track">
        <div class="alm-bar-fill" style="width:${{pct.toFixed(1)}}%;background:${{color}};opacity:${{val<0?1:.85}}"></div>
      </div>
    </div>`;
  }}

  document.getElementById('wave-current-bars').innerHTML =
    alms.map(a => barRow(a, currentTotals[a], maxAbs)).join('');
  document.getElementById('wave-llm-bars').innerHTML =
    alms.map(a => barRow(a, llmTotals[a], maxAbs)).join('');

  // DiD table
  const body = document.getElementById('did-body');
  body.innerHTML = DID_PAIRS.map(p => {{
    const attCls = sign(p.ATT);
    return `<tr>
      <td><strong style="font-family:var(--font-d)">${{p.pair}}</strong><br>
          <span style="font-size:12px;color:var(--text)">${{p.wave}}</span></td>
      <td class="did-name-cell" title="${{p.treated}}">${{p.treated}}</td>
      <td class="did-name-cell" title="${{p.control}}">${{p.control}}</td>
      <td class="td-num ${{sign(p.treated_chg)}}">${{p.treated_chg>=0?'+':''}}${{parseInt(Math.abs(p.treated_chg)).toLocaleString()}}</td>
      <td class="td-num ${{sign(p.control_chg)}}">${{p.control_chg>=0?'+':''}}${{parseInt(Math.abs(p.control_chg)).toLocaleString()}}</td>
      <td>
        <div class="did-att ${{attCls}}">${{p.ATT>=0?'+':''}}${{parseInt(Math.abs(p.ATT)).toLocaleString()}}</div>
        <div class="did-formula">
          = (${{parseInt(p.treated_post).toLocaleString()}} − ${{parseInt(p.treated_pre).toLocaleString()}})<br>
          − (${{parseInt(p.control_post).toLocaleString()}} − ${{parseInt(p.control_pre).toLocaleString()}})
        </div>
      </td>
      <td style="font-size:13px;color:var(--text);max-width:220px;line-height:1.6">${{p.rationale}}</td>
    </tr>`;
  }}).join('');
}}

// ── INIT ─────────────────────────────────────────────────────────────────────
populateSectorFilter();
applyFilters();
renderOverview();
</script>
</body>
</html>"""

with open("index.html", "w") as f:
    f.write(HTML)

size = os.path.getsize("index.html") / 1024
print(f"→ index.html  ({size:.0f} KB)")
