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
  display:grid;grid-template-columns:repeat(5,1fr);
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
.sector-card.neg .sc-bar-fill{{background:var(--loss)}}
.sector-card.pos .sc-val{{color:var(--gain)}}
.sector-card.pos .sc-bar-fill{{background:var(--gain)}}
.sector-card.neu .sc-val{{color:var(--text)}}
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
.stacked-wrap{{
  background:var(--bg2);border:1px solid var(--border);
  border-radius:10px;overflow:hidden;height:360px;position:relative;flex-shrink:0;
}}
#stacked-svg{{width:100%;height:100%;display:block}}
.stacked-tooltip{{
  position:absolute;pointer-events:none;
  background:rgba(9,9,14,.97);backdrop-filter:blur(12px);
  border:1px solid var(--border);border-radius:8px;
  padding:12px 16px;min-width:180px;display:none;z-index:10;
}}
.mt-name{{font-family:var(--font-d);font-size:14px;font-weight:700;color:var(--text);margin-bottom:6px}}
.mt-row{{display:flex;justify-content:space-between;gap:18px;font-family:var(--font-m);font-size:13px;margin-bottom:3px}}
.mt-key{{color:var(--text)}}
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
        <div class="hc-val" id="counter-llm">−228,153</div>
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
        <div class="section-head" style="margin-bottom:8px">Supply-Chain Footprint Job Change — Sorted Worst → Best · Callouts = Top Losing Sectors</div>
        <div class="stacked-wrap">
          <svg id="stacked-svg"></svg>
          <div class="stacked-tooltip" id="stacked-tooltip"></div>
        </div>
      </div>
      <div class="impact-bottom-3">
        <div class="impact-panel" style="overflow:hidden">
          <div class="impact-panel-title">Sector Job Change — Treemap</div>
          <div id="sector-impact-bars" style="flex:1;min-height:0;overflow:hidden"></div>
        </div>
        <div class="impact-panel">
          <div class="impact-panel-title">Sector × Task Type Heatmap</div>
          <div id="alm-heatmap" style="overflow-x:auto;overflow-y:auto;flex:1;min-height:0"></div>
          <div style="flex-shrink:0;border-top:1px solid var(--border);padding-top:12px;margin-top:10px">
            <div class="impact-panel-title">Job Loss by Task Type</div>
            <div id="alm-donut" style="display:flex;flex-direction:row;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap"></div>
          </div>
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
      <td><span class="alm-badge" style="background:${{almColor}}22;color:${{almColor}}">${{d.alm}}</span></td>
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
        <span style="color:${{almColor}}">${{ALM_LABEL[d.alm]}}</span>
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
  renderStackedBars();
  renderTreemap();
  renderHeatmap();
  renderDonut();
}}

function renderStackedBars() {{
  const svg = document.getElementById('stacked-svg');
  if (!svg) return;
  const W = svg.clientWidth || 900;
  const H = svg.clientHeight || 360;
  const PAD = {{l:66, r:200, t:20, b:68}};
  const w = W - PAD.l - PAD.r;
  const h = H - PAD.t - PAD.b;

  const sectors = SECTORS.slice().sort((a,b) => {{
    const aChg = currentWave==='llm'
      ? INDUSTRIES.filter(i=>i.sector===a.Sector).reduce((s,i)=>s+i.llm_chg_emp,0)
      : a.Job_Change;
    const bChg = currentWave==='llm'
      ? INDUSTRIES.filter(i=>i.sector===b.Sector).reduce((s,i)=>s+i.llm_chg_emp,0)
      : b.Job_Change;
    return aChg - bChg;
  }});

  const allChg = sectors.map(s => currentWave==='llm'
    ? INDUSTRIES.filter(i=>i.sector===s.Sector).reduce((a,b)=>a+b.llm_chg_emp,0)
    : s.Job_Change);

  const yMin = Math.min(0, Math.min(...allChg));
  const yMax = Math.max(0, Math.max(...allChg));
  const yPad = Math.abs(yMin) * 0.08;
  const yRange = (yMax - yMin) + yPad * 2;
  const yS = v => PAD.t + (1 - (v - yMin + yPad) / yRange) * h;
  const yZero = yS(0);

  const barW = w / sectors.length;
  const barGap = 1.5;

  let markup = '';

  // Grid lines
  const absMax = Math.max(Math.abs(yMin), yMax);
  const rawStep = absMax / 3;
  const mag = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const step = Math.ceil(rawStep / mag) * mag;
  const ticks = [];
  for (let v = Math.ceil(yMin/step)*step; v <= yMax+step*0.1; v += step) ticks.push(v);

  ticks.forEach(v => {{
    const y = yS(v);
    markup += `<line x1="${{PAD.l}}" y1="${{y.toFixed(1)}}" x2="${{(PAD.l+w).toFixed(1)}}" y2="${{y.toFixed(1)}}" stroke="${{v===0?'#38364A':'#1a1a24'}}" stroke-width="${{v===0?1.5:0.8}}"/>`;
    const label = v === 0 ? '0' : (v>0?'+':'')+(Math.abs(v)>=1000?(v/1000).toFixed(0)+'K':v);
    markup += `<text x="${{(PAD.l-6).toFixed(1)}}" y="${{(y+4.5).toFixed(1)}}" fill="#EAE5DC" font-size="12" font-family="JetBrains Mono" text-anchor="end">${{label}}</text>`;
  }});

  // Bars + callouts for top 3 losers
  const callouts = [];
  sectors.forEach((s, i) => {{
    const chg = allChg[i];
    const x = PAD.l + i * barW;
    const bw = Math.max(1, barW - barGap);
    const isLoss = chg < 0;
    const barTopY = isLoss ? yZero : yS(chg);
    const barBotY = isLoss ? yS(chg) : yZero;
    const bh = Math.max(2, barBotY - barTopY);
    const color = isLoss ? '#C8243E' : '#1B9160';
    const cx = x + barW / 2;

    markup += `<rect x="${{(x+barGap/2).toFixed(1)}}" y="${{barTopY.toFixed(1)}}" width="${{bw.toFixed(1)}}" height="${{bh.toFixed(1)}}" fill="${{color}}" fill-opacity="0.82" class="sbar" data-sector="${{s.Sector}}" data-chg="${{chg.toFixed(0)}}" style="cursor:pointer"/>`;

    // X-axis labels (angled, below zero line)
    const sname = s.Sector.replace('Manufacturing — ','Mfg·').replace('Agriculture & Natural Resources','Agri & Nat.Res').replace(' & ',' & ');
    const short = sname.length > 13 ? sname.slice(0,12)+'…' : sname;
    markup += `<text x="${{cx.toFixed(1)}}" y="${{(yZero+10).toFixed(1)}}" fill="#EAE5DC" font-size="12" font-family="Syne" text-anchor="end" transform="rotate(-42 ${{cx.toFixed(1)}} ${{(yZero+10).toFixed(1)}})" opacity="0.9">${{short}}</text>`;

    if (isLoss && callouts.length < 3) callouts.push({{cx, barTopY, sector:s.Sector, chg}});
  }});

  // Draw callout annotations
  callouts.forEach((c, i) => {{
    const bx = PAD.l + w + 14;
    const by = PAD.t + i * 86 + 10;
    markup += `<line x1="${{c.cx.toFixed(1)}}" y1="${{c.barTopY.toFixed(1)}}" x2="${{bx}}" y2="${{(by+14).toFixed(1)}}" stroke="#C8243E" stroke-width="0.9" stroke-dasharray="3,2" opacity="0.55"/>`;
    markup += `<rect x="${{bx}}" y="${{by}}" width="178" height="44" rx="5" fill="#1E1E28" stroke="#C8243E" stroke-width="0.8" stroke-opacity="0.5"/>`;
    const name = c.sector.replace('Manufacturing — ','Mfg ').replace('Agriculture & Natural Resources','Agri & Nat. Res.');
    const short = name.length > 22 ? name.slice(0,21)+'…' : name;
    markup += `<text x="${{(bx+10).toFixed(1)}}" y="${{(by+17).toFixed(1)}}" fill="#EAE5DC" font-size="12" font-family="Syne" font-weight="600">${{short}}</text>`;
    markup += `<text x="${{(bx+10).toFixed(1)}}" y="${{(by+34).toFixed(1)}}" fill="#C8243E" font-size="12" font-family="JetBrains Mono">${{parseInt(c.chg).toLocaleString()}} jobs</text>`;
  }});

  markup += `<text x="14" y="${{(PAD.t+h/2).toFixed(0)}}" fill="#fff" font-size="12" font-weight="600" font-family="Syne" text-anchor="middle" transform="rotate(-90 14 ${{(PAD.t+h/2).toFixed(0)}})">Job Change</text>`;
  markup += `<text x="${{(PAD.l+w/2).toFixed(0)}}" y="${{(H-4).toFixed(0)}}" fill="#fff" font-size="12" font-weight="600" font-family="Syne" text-anchor="middle">← Biggest Losers · 23 sectors sorted · Best Performers →</text>`;

  svg.innerHTML = markup;

  const tt = document.getElementById('stacked-tooltip');
  svg.querySelectorAll('.sbar').forEach(el => {{
    el.addEventListener('mouseenter', e => {{
      el.setAttribute('fill-opacity','1');
      const chg = parseInt(el.dataset.chg);
      tt.style.display = 'block';
      tt.innerHTML = `<div class="mt-name">${{el.dataset.sector}}</div>
        <div class="mt-row"><span class="mt-key">Job Change</span><span class="${{sign(chg)}}">${{chg>=0?'+':''}}${{chg.toLocaleString()}}</span></div>`;
      const rec = svg.getBoundingClientRect();
      tt.style.left = (e.clientX - rec.left + 14) + 'px';
      tt.style.top  = Math.max(4, e.clientY - rec.top - 40) + 'px';
    }});
    el.addEventListener('mousemove', e => {{
      const rec = svg.getBoundingClientRect();
      tt.style.left = (e.clientX - rec.left + 14) + 'px';
      tt.style.top  = Math.max(4, e.clientY - rec.top - 40) + 'px';
    }});
    el.addEventListener('mouseleave', () => {{
      el.setAttribute('fill-opacity','0.82');
      tt.style.display = 'none';
    }});
  }});
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
      ${{alms.map(a=>`<th class="heatmap-th" style="color:${{ALM_COLOR[a]}}">${{a}}</th>`).join('')}}
    </tr></thead>
    <tbody>${{rows}}</tbody>
  </table>`;
}}

function renderDonut() {{
  const el = document.getElementById('alm-donut');
  if (!el) return;
  const alms = ['NRC-A','NRC-I','RC','RM','NRM'];

  const data = alms.map(a => {{
    const inds = INDUSTRIES.filter(i=>i.alm===a);
    const chg = currentWave==='llm'
      ? inds.reduce((s,i)=>s+i.llm_chg_emp,0)
      : inds.reduce((s,i)=>s+i.chg_emp,0);
    return {{alm:a, chg, label:ALM_LABEL[a]}};
  }}).filter(d=>d.chg<0);

  const total = data.reduce((s,d)=>s+Math.abs(d.chg),0);
  const R=54, r=32, cx=62, cy=62;

  let startAngle = -Math.PI/2;
  let paths = '';
  data.forEach(d => {{
    const frac = Math.abs(d.chg)/total;
    const endAngle = startAngle + frac*2*Math.PI;
    const x1=(cx+R*Math.cos(startAngle)).toFixed(2), y1=(cy+R*Math.sin(startAngle)).toFixed(2);
    const x2=(cx+R*Math.cos(endAngle)).toFixed(2),   y2=(cy+R*Math.sin(endAngle)).toFixed(2);
    const xi1=(cx+r*Math.cos(startAngle)).toFixed(2), yi1=(cy+r*Math.sin(startAngle)).toFixed(2);
    const xi2=(cx+r*Math.cos(endAngle)).toFixed(2),   yi2=(cy+r*Math.sin(endAngle)).toFixed(2);
    const large = frac>0.5?1:0;
    const color = ALM_COLOR[d.alm];
    paths += `<path d="M${{x1}},${{y1}} A${{R}},${{R}} 0 ${{large}},1 ${{x2}},${{y2}} L${{xi2}},${{yi2}} A${{r}},${{r}} 0 ${{large}},0 ${{xi1}},${{yi1}} Z" fill="${{color}}" opacity="0.87"><title>${{d.alm}}: ${{(frac*100).toFixed(1)}}%</title></path>`;
    startAngle = endAngle;
  }});

  paths += `<text x="${{cx}}" y="${{cy-3}}" fill="#EAE5DC" font-size="13" font-family="JetBrains Mono" text-anchor="middle" font-weight="600">${{(total/1000).toFixed(0)}}K</text>`;
  paths += `<text x="${{cx}}" y="${{cy+13}}" fill="#8A84A0" font-size="12" font-family="Syne" text-anchor="middle">lost</text>`;

  const legend = data.map(d =>
    `<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
      <div style="width:10px;height:10px;border-radius:2px;background:${{ALM_COLOR[d.alm]}};flex-shrink:0"></div>
      <span style="font-family:var(--font-d);font-size:12px;color:var(--text)">${{d.alm}}: ${{(Math.abs(d.chg)/total*100).toFixed(1)}}%</span>
    </div>`
  ).join('');

  el.innerHTML = `<svg width="124" height="124" viewBox="0 0 124 124">${{paths}}</svg>
    <div style="padding:0 4px">${{legend}}</div>`;
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
  const rect = el.getBoundingClientRect();
  const W = Math.max(rect.width || 280, 200);
  const H = Math.max(rect.height || 280, 200);
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
  const svgParts = rects.map(r => {{
    const color = r.chg < 0 ? '#C8243E' : '#1B9160';
    const alpha = Math.max(0.45, Math.min(0.85, 0.5 + r.value/items[0].value*0.35));
    const name = abbrev(r.name);
    const val = (r.chg>=0?'+':'') + (Math.abs(r.chg)>=1000?(r.chg/1000).toFixed(1)+'K':Math.round(r.chg).toString());
    const showName = r.h>=34 && r.w>=50;
    const showVal  = r.h>=20 && r.w>=36;
    const midX = (r.x + r.w/2).toFixed(1);
    const midY = (r.y + r.h/2).toFixed(1);
    const nameY = showName && showVal ? (r.y+r.h/2-8).toFixed(1) : midY;
    const valY  = showName && showVal ? (r.y+r.h/2+10).toFixed(1) : midY;
    return `<rect x="${{(r.x+1).toFixed(1)}}" y="${{(r.y+1).toFixed(1)}}" width="${{Math.max(0,r.w-2).toFixed(1)}}" height="${{Math.max(0,r.h-2).toFixed(1)}}" fill="${{color}}" fill-opacity="${{alpha.toFixed(2)}}" rx="3">
        <title>${{r.name}}: ${{val}} jobs</title></rect>
      ${{showName ? `<text x="${{midX}}" y="${{nameY}}" fill="#EAE5DC" font-size="12" font-family="Syne" font-weight="700" text-anchor="middle" dominant-baseline="middle">${{name}}</text>` : ''}}
      ${{showVal  ? `<text x="${{midX}}" y="${{valY}}"  fill="#EAE5DC" font-size="12" font-family="JetBrains Mono" text-anchor="middle" dominant-baseline="middle">${{val}}</text>` : ''}}`;
  }});
  el.innerHTML = `<svg width="${{W}}" height="${{H}}" viewBox="0 0 ${{W}} ${{H}}" style="display:block">${{svgParts.join('')}}</svg>`;
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
          <span style="color:${{color}};font-weight:700;font-family:var(--font-d)">${{alm}}</span>
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

with open("dashboard.html", "w") as f:
    f.write(HTML)

size = os.path.getsize("dashboard.html") / 1024
print(f"→ dashboard.html  ({size:.0f} KB)")
