UI_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenTimeLogger</title>
<style>
:root{
  --bg0:#070b12; --bg1:#0a0f16; --bg2:#0f1622;
  --surface:rgba(255,255,255,.045);
  --surface-hi:rgba(255,255,255,.08);
  --surface-2:rgba(255,255,255,.03);
  --stroke:rgba(255,255,255,.09);
  --stroke-hi:rgba(255,255,255,.16);
  --text:#e8eef7; --muted:#93a1b5; --faint:#5c6b80;
  --accent:#34d399; --accent-2:#10b981; --accent-dim:#0d9488;
  --accent-glow:rgba(52,211,153,.16);
  --info:#60a5fa; --warn:#fbbf24; --danger:#f87171; --violet:#a78bfa;
  --radius:14px; --radius-sm:10px; --radius-lg:18px;
  --sel-bg:#111a28; --sel-bg-hi:#152133;
  --scroll:rgba(255,255,255,.14); --scroll-hi:rgba(255,255,255,.26);
  --shadow:0 10px 34px rgba(0,0,0,.35);
  --titlebar-h:38px;
}
[data-theme="light"]{
  --bg0:#eef1f6; --bg1:#f4f6fa; --bg2:#e7ebf2;
  --surface:rgba(255,255,255,.72);
  --surface-hi:rgba(255,255,255,.9);
  --surface-2:rgba(255,255,255,.55);
  --stroke:rgba(15,23,42,.08);
  --stroke-hi:rgba(15,23,42,.14);
  --text:#17202e; --muted:#5d6b80; --faint:#7b8aa0;
  --accent:#059669; --accent-2:#047857; --accent-dim:#0d9488;
  --accent-glow:rgba(5,150,105,.13);
  --info:#2563eb; --warn:#d97706; --danger:#dc2626; --violet:#7c3aed;
  --sel-bg:#ffffff; --sel-bg-hi:#f1f5f9;
  --scroll:rgba(15,23,42,.15); --scroll-hi:rgba(15,23,42,.28);
  --shadow:0 10px 30px rgba(15,23,42,.10);
}
*{box-sizing:border-box}
[hidden]{display:none !important}
html,body{height:100vh;height:100dvh;margin:0;overflow:hidden;color-scheme:dark}
html[data-theme="light"]{color-scheme:light}
body{
  font-family:"Segoe UI Variable Display","Segoe UI",system-ui,-apple-system,sans-serif;
  color:var(--text);font-size:14px;
  background:
    radial-gradient(900px 600px at 85% -10%, rgba(52,211,153,.10), transparent 60%),
    radial-gradient(800px 620px at -10% 105%, rgba(96,165,250,.08), transparent 60%),
    linear-gradient(155deg,var(--bg1),var(--bg2) 55%,var(--bg0));
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
html[data-theme="light"] body{
  background:
    radial-gradient(900px 600px at 85% -10%, rgba(5,150,105,.07), transparent 60%),
    radial-gradient(800px 620px at -10% 105%, rgba(37,99,235,.05), transparent 60%),
    linear-gradient(155deg,var(--bg1),var(--bg2));
}
*{scrollbar-width:thin;scrollbar-color:var(--scroll) transparent}
*::-webkit-scrollbar{width:9px;height:9px}
*::-webkit-scrollbar-thumb{background:var(--scroll);border-radius:999px}
*::-webkit-scrollbar-thumb:hover{background:var(--scroll-hi)}
*::-webkit-scrollbar-track{background:transparent}
svg{display:block}
.glass{
  background:var(--surface);
  backdrop-filter:blur(22px) saturate(150%);
  -webkit-backdrop-filter:blur(22px) saturate(150%);
  border:1px solid var(--stroke);
  border-radius:var(--radius-lg);
  box-shadow:var(--shadow), inset 0 1px 0 rgba(255,255,255,.05);
}
/* ---------- titlebar (custom, frameless) ---------- */
.titlebar{
  height:var(--titlebar-h);display:flex;align-items:center;gap:10px;
  padding:0 6px 0 14px;user-select:none;flex:none;position:relative;z-index:60;
  background:rgba(7,11,18,.55);backdrop-filter:blur(20px) saturate(150%);
  -webkit-backdrop-filter:blur(20px) saturate(150%);
  border-bottom:1px solid var(--stroke);
}
html[data-theme="light"] .titlebar{background:rgba(244,246,250,.72)}
.tb-title{font-weight:650;font-size:12.5px;letter-spacing:.2px}
.tb-sub{font-size:11px;color:var(--faint);margin-left:8px;letter-spacing:.1px}
.tb-center{flex:1;display:flex;justify-content:center}
.tb-badge{font-size:11px;color:var(--faint);letter-spacing:.4px}
.tb-actions{display:flex;align-items:center;gap:2px;margin-left:auto}
.tb-btn{
  width:40px;height:30px;display:grid;place-items:center;border:0;background:transparent;
  color:var(--muted);border-radius:8px;cursor:pointer;transition:.15s;
}
.tb-btn:hover{background:var(--surface-hi);color:var(--text)}
.tb-btn.close:hover{background:rgba(248,113,113,.16);color:#fecaca}
.tb-sep{width:1px;height:16px;background:var(--stroke);margin:0 4px}
/* ---------- shell ---------- */
.shell{display:grid;grid-template-columns:252px 1fr;gap:14px;height:calc(100dvh - var(--titlebar-h));padding:14px;overflow:hidden}
aside{display:flex;flex-direction:column;min-height:0;overflow:hidden;border-radius:var(--radius-lg)}
.brand{display:flex;align-items:center;gap:10px;padding:14px 14px 10px;flex:none}
.brand>div{min-width:0}
.brand-img{width:34px;height:34px;border-radius:10px;flex:none;object-fit:cover;box-shadow:0 3px 12px rgba(0,0,0,.3);font-size:0;color:transparent;overflow:hidden}
.tb-logo{width:22px;height:22px;border-radius:7px;object-fit:cover;flex:none;box-shadow:0 2px 8px rgba(0,0,0,.25);font-size:0;color:transparent;overflow:hidden}
.brand-t{font-weight:700;font-size:14px;letter-spacing:.1px;line-height:1.1;white-space:nowrap}
.brand-s{font-size:10.5px;color:var(--faint);letter-spacing:.14em;text-transform:uppercase;margin-top:2px}
.nav{display:flex;flex-direction:column;gap:2px;padding:6px 10px;flex:none}
.nav-item{
  display:flex;align-items:center;gap:10px;padding:9px 11px;border-radius:var(--radius-sm);
  border:1px solid transparent;background:transparent;color:var(--muted);cursor:pointer;
  font-family:inherit;font-size:13px;font-weight:560;transition:.15s;text-align:left;position:relative;
}
.nav-item:hover{color:var(--text);background:var(--surface-2)}
.nav-item.active{color:var(--text);background:var(--accent-glow);border-color:rgba(52,211,153,.22)}
html[data-theme="light"] .nav-item.active{border-color:rgba(5,150,105,.2)}
.nav-item .n-ico{flex:none;opacity:.85}
.nav-item .n-badge{
  margin-left:auto;font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:99px;
  background:rgba(52,211,153,.14);color:var(--accent);border:1px solid rgba(52,211,153,.2);
}
.side-section{padding:10px 16px 4px;font-size:10.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);flex:none}
.list{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:6px;margin:0 8px 6px;scrollbar-gutter:stable;overscroll-behavior:contain}
.list-inner{display:flex;flex-direction:column;gap:3px}
.si{display:flex;align-items:center;gap:9px;padding:10px 11px;border-radius:12px;cursor:pointer;border:1px solid transparent;transition:.13s}
.si:hover{background:var(--surface-2);border-color:var(--stroke)}
.si.sel{background:var(--surface-hi);border-color:var(--stroke-hi)}
.dot{flex:none;width:9px;height:9px;border-radius:50%}
.dot.big{width:12px;height:12px}
.si-b{min-width:0;flex:1}
.si-t{font-size:12.8px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2}
.si-s{font-size:11.4px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:6px}
.live{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--accent);animation:pulse 1.6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(52,211,153,.45)}50%{opacity:.55;box-shadow:0 0 0 5px rgba(52,211,153,0)}}
.empty{color:var(--faint);font-size:12.5px;text-align:center;padding:20px 10px;line-height:1.5}
.side-actions{padding:10px 12px 12px;display:flex;flex-direction:column;gap:8px;flex:none;border-top:1px solid var(--stroke);margin-top:auto}
/* ---------- buttons & inputs ---------- */
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:12px;
  padding:10px 15px;font-family:inherit;font-size:13.5px;font-weight:620;cursor:pointer;transition:.16s;
  color:var(--text);background:var(--surface-hi);border:1px solid var(--stroke);
}
.btn:hover{background:rgba(255,255,255,.12);transform:translateY(-1px)}
html[data-theme="light"] .btn:hover{background:rgba(15,23,42,.06)}
.btn:active{transform:translateY(0)}
.btn.primary{background:linear-gradient(180deg,#2fbf8f,#0d9b6f);border:1px solid rgba(52,211,153,.35);color:#04231a;box-shadow:0 6px 18px rgba(13,155,111,.28), inset 0 1px 0 rgba(255,255,255,.25)}
html[data-theme="light"] .btn.primary{color:#fff}
.btn.primary:hover{filter:brightness(1.07)}
.btn.ghost{background:transparent}
.btn.ghost:hover{background:var(--surface-2);border-color:var(--stroke-hi)}
.btn.warn{background:linear-gradient(180deg,rgba(251,191,36,.85),rgba(217,119,6,.85));color:#231303;border:1px solid rgba(251,191,36,.35)}
.btn.danger{background:rgba(248,113,113,.12);border:1px solid rgba(248,113,113,.3);color:#fecaca}
html[data-theme="light"] .btn.danger{color:#b91c1c}
.btn.danger:hover{background:rgba(248,113,113,.2)}
.btn.full{width:100%}
.btn.small{padding:7px 11px;font-size:12.5px;border-radius:10px}
.btn.icon{width:32px;height:32px;padding:0;border-radius:9px}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{padding:7px 13px;border:1px solid var(--stroke);border-radius:11px;background:var(--surface-2);color:var(--muted);font-family:inherit;font-size:12.6px;font-weight:600;cursor:pointer;transition:.14s}
.chip:hover{color:var(--text);background:var(--surface-hi)}
.chip.active{background:var(--accent-glow);color:var(--accent);border-color:rgba(52,211,153,.45);box-shadow:0 0 0 1px rgba(52,211,153,.25)}
html[data-theme="light"] .chip.active{color:var(--accent-2)}
.input{
  width:100%;background:var(--surface-2);border:1px solid var(--stroke);border-radius:11px;
  padding:10px 12px;color:var(--text);font-family:inherit;font-size:13.5px;outline:none;transition:.15s;color-scheme:dark;
}
.input:focus{border-color:rgba(52,211,153,.5);box-shadow:0 0 0 3px var(--accent-glow);background:var(--surface)}
.input::placeholder{color:var(--faint)}
select.input{cursor:pointer}
select.input option{background:var(--sel-bg);color:var(--text)}
.ta{resize:vertical;line-height:1.55;min-height:64px}
label{display:flex;flex-direction:column;gap:5px;font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--faint)}
label .input{font-weight:400;text-transform:none;letter-spacing:0;font-size:13.5px}
.ac-wrap{position:relative}
.ac-menu{position:absolute;top:calc(100% + 6px);left:0;right:0;background:var(--sel-bg);border:1px solid var(--stroke-hi);border-radius:12px;box-shadow:var(--shadow);padding:5px;max-height:210px;overflow-y:auto;z-index:40;display:none}
.ac-menu.open{display:block}
.ac-opt{padding:9px 11px;border-radius:9px;cursor:pointer;font-size:13px;transition:.12s}
.ac-opt:hover{background:var(--surface-hi)}
.ac-opt.active{background:var(--accent-glow);color:var(--accent)}
.cselect{position:relative}
.cselect-trigger{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;background:var(--surface-2);border:1px solid var(--stroke);border-radius:11px;padding:10px 12px;color:var(--text);font-family:inherit;font-size:13.5px;cursor:pointer;transition:.15s;text-align:left}
.cselect-trigger:hover{background:var(--surface);border-color:var(--stroke-hi)}
.cselect-trigger:focus{outline:none;border-color:rgba(52,211,153,.5);box-shadow:0 0 0 3px var(--accent-glow)}
.cselect-arrow{flex:none;opacity:.6;transition:.15s}
.cselect.open .cselect-arrow{transform:rotate(180deg)}
.cselect-menu{position:absolute;top:calc(100% + 6px);left:0;right:0;background:var(--sel-bg);border:1px solid var(--stroke-hi);border-radius:12px;box-shadow:var(--shadow);padding:5px;max-height:210px;overflow-y:auto;z-index:40;display:none}
.cselect.open .cselect-menu{display:block}
.copt{padding:9px 11px;border-radius:9px;cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:space-between;transition:.12s}
.copt:hover{background:var(--surface-hi)}
.copt.active{background:var(--accent-glow);color:var(--accent)}
/* ---------- main ---------- */
main{display:flex;flex-direction:column;min-height:0;overflow:hidden;border-radius:var(--radius-lg)}
.main-head{display:flex;align-items:center;gap:12px;padding:16px 20px 12px;flex:none;flex-wrap:wrap}
.mh-t{font-size:17px;font-weight:700;letter-spacing:.1px;display:flex;align-items:center;gap:9px}
.mh-s{font-size:12.5px;color:var(--muted);margin-top:2px}
.mh-actions{margin-left:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.main-scroll{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:4px 20px 20px;scrollbar-gutter:stable;overscroll-behavior:contain}
.cards{display:flex;flex-direction:column;gap:14px;max-width:860px;margin:0 auto;width:100%;padding-top:4px}
.card{padding:18px 20px}
.card-h{display:flex;align-items:center;gap:9px;margin-bottom:4px}
.card-t{font-size:14.5px;font-weight:700;letter-spacing:.1px}
.card-sub{font-size:12.5px;color:var(--muted);line-height:1.5;margin:4px 0 12px}
.muted{color:var(--muted);font-size:13px;line-height:1.55;margin:6px 0 14px}
.muted.small{font-size:12.5px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
@media (max-width:1000px){.grid4{grid-template-columns:1fr 1fr}.grid3{grid-template-columns:1fr 1fr}}
.row{display:flex;gap:10px;margin-top:12px;align-items:center;flex-wrap:wrap}
.row .grow{flex:1;min-width:160px}
.dhead{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.dh-t{font-size:17px;font-weight:700}
.dh-s{color:var(--muted);font-size:12.5px;margin-top:2px}
/* ---------- dashboard ---------- */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:4px}
@media (min-width:760px){.kpis{grid-template-columns:repeat(3,1fr)}}
.kpi{background:var(--surface-2);border:1px solid var(--stroke);border-radius:var(--radius);padding:13px 15px}
.kpi-v{font-size:21px;font-weight:700;letter-spacing:.2px;font-variant-numeric:tabular-nums}
.kpi-l{font-size:10.5px;color:var(--faint);text-transform:uppercase;letter-spacing:.09em;margin-top:3px;font-weight:700}
.kpi.hl .kpi-v{color:var(--accent)}
.chart-card{background:var(--surface-2);border:1px solid var(--stroke);border-radius:var(--radius);padding:14px 16px;overflow:hidden}
.chart-h{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px}
.chart-t{font-size:13px;font-weight:700}
.chart-note{font-size:11.5px;color:var(--faint)}
.chart{width:100%}
.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11.5px;color:var(--muted);margin-top:8px}
.legend span{display:flex;align-items:center;gap:5px}
.legend i{width:9px;height:9px;border-radius:3px;display:inline-block}
.heat-grid{display:grid;grid-template-columns:34px repeat(24,1fr);gap:3px;overflow-x:auto;padding-bottom:4px}
.heat-cell{height:15px;border-radius:3px;min-width:9px}
.heat-lab{font-size:9px;color:var(--faint);display:flex;align-items:center;justify-content:flex-end;padding-right:4px}
.heat-hr{font-size:8.5px;color:var(--faint);text-align:center}
.cat-row{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:10px;cursor:pointer;transition:.13s}
.cat-row:hover{background:var(--surface-2)}
.cat-row .cat-name{font-size:13px;font-weight:600;min-width:110px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cat-row .cat-val{margin-left:auto;font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.cat-bar{height:8px;border-radius:99px;background:var(--surface-hi);overflow:hidden;flex:1}
.cat-bar i{display:block;height:100%;border-radius:99px}
/* ---------- AI ---------- */
.ai-graph{display:flex;flex-direction:column;gap:0;margin:6px 0 14px;position:relative}
.ai-node{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:12px;border:1px solid transparent;position:relative;z-index:2}
.ai-node.cur{border-color:rgba(52,211,153,.35);background:var(--accent-glow)}
.ai-node.done{border-color:rgba(52,211,153,.18)}
.ai-node .ai-ico{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:var(--surface-hi);border:1px solid var(--stroke);flex:none;color:var(--muted)}
.ai-node.cur .ai-ico{color:var(--accent);border-color:rgba(52,211,153,.35)}
.ai-node.done .ai-ico{color:var(--accent)}
.ai-node .ai-nm{font-size:13.5px;font-weight:650}
.ai-node .ai-pp{font-size:11.5px;color:var(--muted);margin-top:1px;line-height:1.35}
.ai-node .ai-st{margin-left:auto;font-size:11px;color:var(--faint);font-weight:600;white-space:nowrap;display:flex;align-items:center;gap:4px}
.ai-edge{height:22px;width:2px;margin-left:28px;background:var(--stroke);position:relative;overflow:hidden}
.ai-edge.run::after{content:"";position:absolute;left:0;top:-100%;width:100%;height:100%;background:linear-gradient(180deg,transparent,var(--accent),transparent);animation:edgeflow 1.2s linear infinite}
@keyframes edgeflow{to{top:100%}}
.spinner{width:15px;height:15px;border-radius:50%;border:2px solid var(--stroke);border-top-color:var(--accent);animation:spin .8s linear infinite;display:inline-block;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
.model-card{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:11px;border:1px solid var(--stroke);cursor:pointer;transition:.13s;background:var(--surface-2)}
.model-card:hover{background:var(--surface)}
.model-card.sel{border-color:rgba(52,211,153,.45);background:var(--accent-glow)}
.model-card .mc-n{font-size:13px;font-weight:600}
.sev{font-size:10px;font-weight:700;padding:2px 8px;border-radius:99px;letter-spacing:.04em;text-transform:uppercase}
.sev.low{background:rgba(96,165,250,.14);color:var(--info);border:1px solid rgba(96,165,250,.25)}
.sev.medium{background:rgba(251,191,36,.14);color:var(--warn);border:1px solid rgba(251,191,36,.25)}
.sev.high{background:rgba(248,113,113,.14);color:var(--danger);border:1px solid rgba(248,113,113,.25)}
.sev.critical{background:rgba(248,113,113,.2);color:#ffb4b4;border:1px solid rgba(248,113,113,.4)}
.st{font-size:10.5px;font-weight:700;padding:2px 9px;border-radius:99px;text-transform:uppercase;letter-spacing:.03em}
.st.identified{background:rgba(167,139,250,.13);color:var(--violet);border:1px solid rgba(167,139,250,.28)}
.st.solved{background:rgba(52,211,153,.13);color:var(--accent);border:1px solid rgba(52,211,153,.3)}
.st.partially_solved{background:rgba(251,191,36,.13);color:var(--warn);border:1px solid rgba(251,191,36,.3)}
.tl-item{display:flex;gap:10px;position:relative;padding:0 0 14px}
.tl-item:not(:last-child)::before{content:"";position:absolute;left:9px;top:20px;bottom:-2px;width:2px;background:var(--stroke)}
.tl-dot{width:20px;height:20px;border-radius:50%;border:2px solid var(--stroke);display:grid;place-items:center;flex:none;background:var(--bg1);z-index:1;font-size:9px;font-weight:800;color:var(--muted)}
.tl-item.cur .tl-dot{border-color:var(--accent);box-shadow:0 0 0 4px var(--accent-glow);color:var(--accent)}
.tl-item .tl-b{flex:1;min-width:0}
.tl-item .tl-t{font-size:13px;font-weight:620;cursor:pointer}
.tl-item .tl-t:hover{color:var(--accent);text-decoration:underline}
.insight[data-step]{transition:.13s}
.insight[data-step]:hover{border-color:var(--stroke-hi)}
.tl-item.cur .tl-t{color:var(--accent)}
.tl-item .tl-n{font-size:11.5px;color:var(--muted);margin-top:1px}
.prop{display:flex;gap:10px;padding:10px 12px;border-radius:12px;border:1px solid var(--stroke);background:var(--surface-2);margin-top:8px}
.prop .prop-txt{font-size:12.8px;line-height:1.5;flex:1}
.prop .prop-btns{display:flex;gap:6px;align-items:flex-start}
.prop-ok,.prop-no{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;border:1px solid var(--stroke);background:transparent;color:var(--faint);cursor:pointer;transition:.13s}
.prop-ok:hover{border-color:rgba(52,211,153,.4);color:var(--accent)}
.prop-no:hover{border-color:rgba(248,113,113,.4);color:var(--danger)}
.prop.accepted{border-color:rgba(52,211,153,.4);background:rgba(52,211,153,.07)}
.prop.accepted .prop-ok{background:rgba(52,211,153,.15);color:var(--accent);border-color:rgba(52,211,153,.4)}
.prop.rejected{border-color:rgba(248,113,113,.3)}
.prop.rejected .prop-no{background:rgba(248,113,113,.12);color:var(--danger);border-color:rgba(248,113,113,.35)}
.insight{background:var(--surface-2);border:1px solid var(--stroke);border-radius:12px;padding:12px 14px;margin-top:10px}
.insight .in-t{font-size:13px;font-weight:650;display:flex;align-items:center;gap:8px}
.insight .in-s{font-size:12.5px;color:var(--muted);line-height:1.5;margin-top:5px}
.insight .in-ex{font-size:11.5px;color:var(--faint);background:var(--surface);border-radius:8px;padding:7px 10px;margin-top:7px;border-left:2px solid var(--stroke-hi);font-style:italic}
/* ---------- modal ---------- */
.modal-ov{position:fixed;inset:0;background:rgba(4,8,14,.55);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);display:grid;place-items:center;z-index:100;padding:24px;opacity:0;pointer-events:none;transition:.2s}
.modal-ov.open{opacity:1;pointer-events:auto}
.modal{width:min(560px,100%);max-height:84dvh;display:flex;flex-direction:column;border-radius:18px;overflow:hidden;background:var(--bg1);border:1px solid var(--stroke-hi);box-shadow:0 24px 70px rgba(0,0,0,.5)}
html[data-theme="light"] .modal{background:#fff}
.modal-h{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid var(--stroke);flex:none}
.modal-t{font-size:14.5px;font-weight:700;flex:1}
.modal-b{padding:16px 18px;overflow-y:auto}
.modal-f{padding:12px 18px;border-top:1px solid var(--stroke);display:flex;justify-content:flex-end;gap:8px;flex:none}
/* ---------- toasts ---------- */
#toasts{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;gap:8px;z-index:120;align-items:center;pointer-events:none}
.toast{padding:10px 15px;border-radius:12px;background:var(--bg1);border:1px solid var(--stroke-hi);box-shadow:var(--shadow);color:var(--text);font-size:13px;opacity:1;transition:.25s;pointer-events:auto;display:flex;gap:8px;align-items:center}
.toast.err{border-color:rgba(248,113,113,.45)}
.toast .t-ico{color:var(--accent)}
.toast.err .t-ico{color:var(--danger)}
.toast.out{opacity:0;transform:translateY(8px)}
.fade{animation:fade .22s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
/* mic */
.mic-btn{width:32px;height:32px;border-radius:10px;border:1px solid var(--stroke);background:var(--surface-2);color:var(--muted);display:grid;place-items:center;cursor:pointer;flex:none;transition:.14s}
.mic-btn:hover{color:var(--text);border-color:var(--stroke-hi)}
.mic-btn.rec{color:var(--danger);border-color:rgba(248,113,113,.45);background:rgba(248,113,113,.1);animation:pulse 1.4s ease-in-out infinite}
.rec-time{font-variant-numeric:tabular-nums;font-size:20px;font-weight:700;letter-spacing:.5px}
body.focus-mode aside{opacity:.6;filter:saturate(.9)}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms !important}}
</style>
<script>try{const k="otl-theme";const s=localStorage.getItem(k);const m=window.matchMedia&&matchMedia("(prefers-color-scheme: light)").matches;const t=s||(m?"light":"dark");document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>
</head>
<body>
<div class="titlebar" id="titlebar">
  <img id="tbLogo" class="tb-logo" alt="">
  <div class="tb-title">OpenTimeLogger</div>
  <div class="tb-sub">time, accounted for</div>
  <div class="tb-center"><div class="tb-badge" id="tbBadge"></div></div>
  <div class="tb-actions">
    <button class="tb-btn" id="themeBtn" title="Toggle theme" aria-label="Toggle theme">
      <svg class="icon-sun" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
      <svg class="icon-moon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" style="display:none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
    <span class="tb-sep"></span>
    <button class="tb-btn" id="tbMin" title="Minimize" aria-label="Minimize"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/></svg></button>
    <button class="tb-btn" id="tbMax" title="Maximize" aria-label="Maximize"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="5" width="14" height="14" rx="1.5"/></svg></button>
    <button class="tb-btn close" id="tbClose" title="Close" aria-label="Close"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  </div>
</div>
<div class="shell">
  <aside class="glass">
    <div class="brand">
      <img id="brandImg" class="brand-img" alt="OpenTimeLogger">
      <div><div class="brand-t">OpenTimeLogger</div><div class="brand-s">time, accounted for</div></div>
    </div>
    <div class="nav" id="nav">
      <button class="nav-item active" data-tab="active"><span class="n-ico" data-i="play"></span><span>Active</span><span class="n-badge" id="badgeActive" hidden></span></button>
      <button class="nav-item" data-tab="archive"><span class="n-ico" data-i="archive"></span><span>Archive</span></button>
      <button class="nav-item" data-tab="dashboard"><span class="n-ico" data-i="chart"></span><span>Dashboard</span></button>
      <button class="nav-item" data-tab="ai"><span class="n-ico" data-i="sparkles"></span><span>AI</span><span class="n-badge" id="badgeAi" hidden>new</span></button>
      <button class="nav-item" data-tab="export"><span class="n-ico" data-i="download"></span><span>Export</span></button>
    </div>
    <div class="side-section" id="sideSection">SESSIONS</div>
    <div class="list" id="sideList"><div class="list-inner" id="sideListInner"></div></div>
    <div class="side-actions">
      <button class="btn primary full" id="newBtn"><span data-i="plus" data-s="15"></span> Start session</button>
      <button class="btn ghost full" id="pastBtn">Log a finished session</button>
      <button class="btn ghost full" id="settingsBtn" style="justify-content:center"><span data-i="settings" data-s="13"></span><span style="font-size:12.5px">Settings</span></button>
    </div>
  </aside>
  <main class="glass" id="main"><div class="main-head" id="mainHead"></div><div class="main-scroll" id="mainScroll"></div></main>
</div>
<datalist id="dlCats"></datalist>
<datalist id="dlTags"></datalist>
<div id="modalRoot"></div>
<div id="toasts"></div>
<script>
const AVATAR_URI=null;
/* ============ state ============ */
let S={
  sessions:[], tab:"active", sel:null,
  exports:[], dash:{range:"30d",mode:"daily",cat:null,heat:"all"},
  ai:{cfg:null,agents:[],providers:[],ready:false,subview:"tasks",taskSel:null,stepSel:null,
      onb:{idx:0,provider:null,keyId:null,model:null,models:[],loading:false,testing:false,tested:false,custom:""},
      pipeline:{running:false,st:null},tasks:[],reports:[],insights:null},
  asr:{rec:false,secs:0},
};
let nsMode="now",deMode="now",docAccum={},activeSid=null,lastKey=0,docTick=null,renderQueued=false;
const DUR_OPTS=["Today","Last 3 days","Last 7 days","Last 12 days","Last 30 days","All time"];
/* ============ icons ============ */
const PATHS={
  play:"M6 4l14 8-14 8z",
  archive:"M3 5h18v4H3zM5 9v10h14V9M10 13h4",
  chart:"M4 20V10M10 20V4M16 20v-7M22 20H2",
  sparkles:"M12 3l1.6 4.6L18 9.2l-4.4 1.6L12 15.4l-1.6-4.6L6 9.2l4.4-1.6zM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z",
  download:"M12 3v12M6 11l6 6 6-6M4 21h16",
  plus:"M12 5v14M5 12h14",
  settings:"M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zM19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.9 2.9l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 1 1-4 0v-.1a1.6 1.6 0 0 0-2.7-1.1l-.1.1a2 2 0 1 1-2.9-2.9l.1-.1A1.6 1.6 0 0 0 4.6 15H4.5a2 2 0 1 1 0-4h.1a1.6 1.6 0 0 0 1.1-2.7l-.1-.1a2 2 0 1 1 2.9-2.9l.1.1a1.6 1.6 0 0 0 1.8.3H10a1.6 1.6 0 0 0 1-1.5V4a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.9 2.9l-.1.1a1.6 1.6 0 0 0-.3 1.8V10a1.6 1.6 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1z",
  clock:"M12 7v5l3 2M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z",
  mic:"M12 3a3 3 0 0 1 3 3v5a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3zM5 11a7 7 0 0 0 14 0M12 18v3",
  check:"M5 13l4 4L19 7",
  x:"M6 6l12 12M18 6L6 18",
  chevD:"M6 9l6 6 6-6", chevR:"M9 6l6 6-6 6",
  trash:"M3 6h18M8 6V4h8v2M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M10 11v6M14 11v6",
  edit:"M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z",
  refresh:"M21 12a9 9 0 1 1-2.6-6.4M21 3v6h-6",
  zap:"M13 2L3 14h8l-1 8 10-12h-8z",
  target:"M12 12m-9 0a9 9 0 1 0 18 0 9 9 0 1 0-18 0M12 12m-5 0a5 5 0 1 0 10 0 5 5 0 1 0-10 0M12 12m-1 0a1 1 0 1 0 2 0 1 1 0 1 0-2 0",
  layers:"M12 2l10 5-10 5L2 7zM2 12l10 5 10-5M2 17l10 5 10-5",
  route:"M6 19a3 3 0 1 0 0-6h8a3 3 0 1 0 0-6H8M9 6l-3 2 3 2M15 17l3-2-3-2",
  key:"M21 2l-9.6 9.6M15.5 7.5l3 3L22 7l-3-3zM11.4 11.6a5 5 0 1 1-6 6 5 5 0 0 1 6-6z",
  activity:"M22 12h-4l-3 8-6-16-3 8H2",
  flame:"M12 2c1 4-4 5.5-4 10a4 4 0 0 0 8 0c0-2-1.5-3-2-4 1.5.5 3 2 3 4.5A6 6 0 1 1 6 12c0-5 5-6 6-10z",
  hourglass:"M7 2h10M7 22h10M8 2v3l4 4 4-4V2M8 22v-3l4-4 4 4v3",
  brain:"M9.5 2a2.5 2.5 0 0 0-2.5 2.5v.5A3.5 3.5 0 0 0 4 8.5c0 .6.2 1.2.4 1.7A3.5 3.5 0 0 0 3 13.2c0 1.4.9 2.7 2.1 3.3a3.5 3.5 0 0 0 2.9 3.4 2.5 2.5 0 0 0 4.9.3 3.5 3.5 0 0 0 2.1-.7 2.5 2.5 0 0 0 5-.5 3.5 3.5 0 0 0 2-3.5 3.5 3.5 0 0 0-1-5.6A3.5 3.5 0 0 0 20 8.5a3.5 3.5 0 0 0-5-3.1A2.5 2.5 0 0 0 12 2z",
  info:"M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 16v-5M12 8h.01",
  alert:"M12 3L2 21h20zM12 9v5M12 17.5h.01",
  calendar:"M8 2v4M16 2v4M3 8h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z",
  file:"M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8zM14 2v6h6M9 14h6M9 18h6M9 10h2",
  moon:"M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z",
  sun:"M12 2v2M12 20v2M2 12h2M20 12h2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z",
  list:"M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01",
  send:"M22 2L11 13M22 2l-7 20-4-9-9-4z",
  box:"M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8",
  scan:"M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 12h10",
  pie:"M12 3a9 9 0 1 0 9 9h-9zM14 3.1A9 9 0 0 1 20.9 10H14z",
};
function I(name,size,cls){
  const p=PATHS[name]||PATHS.info; const s=size||16;
  return `<svg class="${cls||""}" width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="${p}"/></svg>`;
}
/* ============ utils ============ */
const $=(s,r=document)=>r.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const sessions=()=>S.sessions||[];
const byId=id=>sessions().find(s=>s.id===id);
function nowLocal(){const d=new Date();const p=n=>String(n).padStart(2,"0");return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate())+"T"+p(d.getHours())+":"+p(d.getMinutes());}
function localInput(iso){return iso?iso.slice(0,16):"";}
function fmt(iso){if(!iso)return "—";const d=new Date(iso);return d.toLocaleString(undefined,{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"});}
function fmtT(iso){if(!iso)return "";const d=new Date(iso);return d.toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"});}
function mins(a,b){if(!a||!b)return null;return Math.max(0,Math.round((new Date(b)-new Date(a))/60000));}
function fmtDur(m){if(m==null)return "—";if(m<60)return Math.round(m)+" min";const h=m/60;return (Math.round(h*10)/10)+" h";}
function pct(x){return (Math.round((x||0)*1000)/10)+"%";}
function catColor(c){let h=140;const s=String(c||"");if(s){h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;}return `hsl(${h} 62% 55%)`;}
function fmtDay(iso){if(!iso)return "";const d=new Date(iso+"T00:00:00");return d.toLocaleDateString(undefined,{day:"2-digit",month:"short"});}
function docMins(s){return Math.round((s.summary_seconds??s.doc_seconds??0)/60);}
function sessionName(s){
  if(s.kind==="daily-doc-summary")return "Documentation · "+fmtDay(s.summary_of);
  if(!s.category)return "Untitled session";
  if(s.tag)return s.category+": "+s.tag+(s.sub_tag?" + "+s.sub_tag:"");
  return s.category;
}
function toast(msg,type){
  const t=document.createElement("div");t.className="toast "+(type==="err"?"err":"");
  t.innerHTML=`<span class="t-ico">${I(type==="err"?"alert":"check",14)}</span><span>${esc(msg)}</span>`;
  document.getElementById("toasts").appendChild(t);
  setTimeout(()=>t.classList.add("out"),2600);setTimeout(()=>t.remove(),3000);
}
async function A(name,...args){
  try{
    if(window.pywebview&&pywebview.api&&pywebview.api[name]) return await pywebview.api[name](...args);
  }catch(e){console.warn(name,e);}
  return {error:"bridge unavailable"};
}
function scheduleRender(){if(renderQueued)return;renderQueued=true;requestAnimationFrame(()=>{renderQueued=false;render();});}
/* theme */
(function(){
  const key="otl-theme";let saved=null;
  try{saved=localStorage.getItem(key);}catch(e){}
  let pl=false;try{pl=window.matchMedia&&window.matchMedia("(prefers-color-scheme: light)").matches;}catch(e){}
  const initial=saved||(pl?"light":"dark");
  try{document.documentElement.setAttribute("data-theme",initial);}catch(e){}
  const upd=()=>{try{const c=document.documentElement.getAttribute("data-theme");const s=document.querySelector(".icon-sun"),m=document.querySelector(".icon-moon");if(s&&m){s.style.display=c==="dark"?"block":"none";m.style.display=c==="light"?"block":"none";}}catch(e){}};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",upd);else upd();
  window.__setTheme=next=>{try{document.documentElement.setAttribute("data-theme",next);}catch(e){}try{localStorage.setItem(key,next);}catch(e){}upd();};
})();
/* ============ render ============ */
function render(){
  document.querySelectorAll("#nav .nav-item").forEach(b=>b.classList.toggle("active",b.dataset.tab===S.tab));
  const running=sessions().filter(s=>!s.end&&s.kind!=="daily-doc-summary").length;
  const bA=document.getElementById("badgeActive");if(bA){bA.hidden=!running;bA.textContent=running;}
  const cats=getCats(),tags=getTags();
  document.getElementById("dlCats").innerHTML=cats.map(c=>`<option value="${esc(c)}">`).join("");
  document.getElementById("dlTags").innerHTML=tags.map(t=>`<option value="${esc(t)}">`).join("");
  if(S.sel&&!byId(S.sel))S.sel=null;
  renderSide();renderHead();renderMain();
}
let _catsCache=null,_catsKey="",_tagsCache=null,_tagsKey="";
function getCats(){const key=sessions().length+"|"+sessions().map(s=>s.category).join("|");if(_catsKey===key)return _catsCache;_catsCache=[...new Set(sessions().map(x=>x.category).filter(Boolean))].sort();_catsKey=key;return _catsCache;}
function getTags(){const key=sessions().length+"|"+sessions().map(s=>s.tag).join("|");if(_tagsKey===key)return _tagsCache;_tagsCache=[...new Set(sessions().map(x=>x.tag).filter(Boolean))].sort();_tagsKey=key;return _tagsCache;}
function renderHead(){
  const h=document.getElementById("mainHead");
  const titles={active:["Active","Running sessions and quick start"],archive:["Archive","Finished sessions — edit, reopen, delete"],dashboard:["Dashboard","Where your time actually goes"],ai:["AI Workspace","BYOK agents that read your logs"],export:["Export","Filtered Excel workbooks"]};
  const t=titles[S.tab]||["",""];
  h.innerHTML=`<div><div class="mh-t">${tabIco(S.tab)} ${esc(t[0])}</div><div class="mh-s">${esc(t[1])}</div></div><div class="mh-actions" id="headActions"></div>`;
  if(S.tab==="dashboard")headActionsDashboard();
  if(S.tab==="ai")headActionsAi();
  if(S.tab==="export")headActionsExport();
}
function tabIco(t){return t==="active"?I("play"):t==="archive"?I("archive"):t==="dashboard"?I("chart"):t==="ai"?I("sparkles"):I("download");}
function headActionsDashboard(){
  const el=document.getElementById("headActions");if(!el)return;
  const ranges=[["7d","7 days"],["30d","30 days"],["90d","90 days"],["all","All time"]];
  el.innerHTML=`<div class="chips">${ranges.map(r=>`<button class="chip ${S.dash.range===r[0]?"active":""}" data-r="${r[0]}">${r[1]}</button>`).join("")}</div>`;
  el.querySelectorAll(".chip").forEach(c=>c.addEventListener("click",()=>{S.dash.range=c.dataset.r;S.dash.cat=null;renderHead();loadDash();}));
}
function headActionsAi(){
  const el=document.getElementById("headActions");if(!el)return;
  el.innerHTML=`<button class="btn ghost small" id="aiSettingsBtn">${I("settings",13)} AI settings</button>`;
  const b=document.getElementById("aiSettingsBtn");if(b)b.addEventListener("click",()=>openAiSettings());
}
function headActionsExport(){
  const el=document.getElementById("headActions");if(!el)return;
  el.innerHTML=`<button class="btn ghost small" id="exRefresh">${I("refresh",13)} Refresh</button>`;
  const b=document.getElementById("exRefresh");if(b)b.addEventListener("click",loadExports);
}
function quickFactsHtml(){
  try{
    if(typeof DASH==="undefined"||!DASH||!DASH.overview)return `<div class="empty">Open the dashboard to compute facts.</div>`;
    const cats=DASH.categories||[];const top=cats[0];
    const wp=DASH.weekly_pattern||{};
    const fact=(l,v)=>`<div style="background:var(--surface-2);border:1px solid var(--stroke);border-radius:10px;padding:8px 11px"><div style="font-size:12.5px;font-weight:650">${esc(v)}</div><div style="font-size:10px;color:var(--faint);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-top:1px">${esc(l)}</div></div>`;
    return `<div style="display:flex;flex-direction:column;gap:7px;padding:2px">`
      +fact("Top category",top?top.category+" · "+fmtDur(top.minutes):"—")
      +fact("Peak",((wp.peak_weekday||"—")+" · "+(wp.peak_hour!=null?String(wp.peak_hour).padStart(2,"0")+":00":"—")))
      +fact("Doc share",pct(DASH.overview.doc_ratio||0))
      +fact("Sessions",String(DASH.overview.total_sessions||0))+`</div>`;
  }catch(e){return `<div class="empty">Open the dashboard to compute facts.</div>`;}
}
function renderSide(){
  const inner=document.getElementById("sideListInner");if(!inner)return;
  const sec=document.getElementById("sideSection");
  if(S.tab==="export"){
    if(sec)sec.textContent="RECENT EXPORTS";
    if(!S.exports.length){inner.innerHTML=`<div class="empty">No exports yet.<br><span style="font-size:11.5px;color:var(--faint)">Export from the Export tab — .xlsx files land here.</span></div>`;return;}
    inner.innerHTML=S.exports.map(ex=>`
      <div class="si" data-path="${esc(ex.path)}" title="${esc(ex.name)}">
        <span class="dot" style="background:var(--accent)"></span>
        <div class="si-b"><div class="si-t">${esc(ex.name)}</div><div class="si-s">${esc(ex.mtime_label)} · ${esc(ex.size_kb)} KB</div></div>
        <button class="btn icon small export-del" data-del="${esc(ex.path)}" title="Delete">${I("trash",12)}</button>
      </div>`).join("");
    return;
  }
  if(S.tab==="dashboard"){if(sec)sec.textContent="QUICK FACTS";inner.innerHTML=quickFactsHtml();return;}
  if(S.tab==="ai"){if(sec)sec.textContent="AI PIPELINE";inner.innerHTML=`<div class="empty">${S.ai.pipeline.running?"Pipeline is running — see progress in the main view.":(S.ai.tasks&&S.ai.tasks.length?S.ai.tasks.length+" task(s) ready — open one from the Tasks tab.":"Configure agents in the AI tab to unlock tasks & coach.")}</div>`;return;}
  const isActive=S.tab==="active";if(sec)sec.textContent=isActive?"RUNNING":"ARCHIVED";
  let items=sessions().filter(s=>isActive?(!s.end&&s.kind!=="daily-doc-summary"):(s.end&&s.kind!=="daily-doc-summary"));
  if(isActive)items=items.slice().sort((a,b)=>a.start.localeCompare(b.start));
  else items=items.slice().sort((a,b)=>b.start.localeCompare(a.start));
  if(!items.length){inner.innerHTML=`<div class="empty">${isActive?"No active sessions.":"Nothing archived yet."}</div>`;return;}
  inner.innerHTML=items.map(s=>{
    const title=sessionName(s);const sub=!s.end?("since "+fmtT(s.start)):(fmt(s.start)+" → "+fmtT(s.end));
    const meta=!s.end?`<span class="live"></span>`:"";
    return `<div class="si ${S.sel===s.id?"sel":""}" data-id="${s.id}">
      <span class="dot" style="background:${catColor(s.category)}"></span>
      <div class="si-b"><div class="si-t">${esc(title)}</div><div class="si-s">${meta}${esc(sub)}</div></div>
    </div>`;
  }).join("");
}
function renderMain(){
  const sc=document.getElementById("mainScroll");
  if(S.tab==="active"){
    const s=S.sel?byId(S.sel):null;
    if(s&&!s.end){sc.innerHTML=detailHtml(s);bindDetail(s);watchDoc(s);return;}
    sc.innerHTML=activeViewHtml();bindActiveView();
  }else if(S.tab==="archive"){
    const s=S.sel?byId(S.sel):null;
    if(s&&s.end){sc.innerHTML=detailHtml(s);bindDetail(s);watchDoc(s);return;}
    sc.innerHTML=archiveViewHtml();bindArchiveView();
  }else if(S.tab==="dashboard"){sc.innerHTML=dashboardHtml();bindDashboard();}
  else if(S.tab==="ai"){sc.innerHTML=aiHtml();bindAi();}
  else if(S.tab==="export"){sc.innerHTML=exportViewHtml();bindExport();loadExports();}
}
/* ============ active / archive views ============ */
function activeViewHtml(){
  return `<div class="cards">
    <div class="card glass fade" style="border-color:rgba(52,211,153,.3)">
      <div class="card-h">${I("play",15)}<div class="card-t">Start a session</div></div>
      <p class="card-sub">Logs a start time. Begin right now, or tell it when the session actually started.</p>
      <div class="chips" style="margin-bottom:12px">
        <button class="chip ${nsMode==="now"?"active":""}" data-v="now">Right now</button>
        <button class="chip ${nsMode==="at"?"active":""}" data-v="at">At time</button>
      </div>
      <input type="datetime-local" id="nsAt" class="input" value="${nowLocal()}" ${nsMode==="at"?"":"hidden"} style="margin-bottom:12px">
      <div class="grid3">
        <label>Category<div class="ac-wrap"><input list="dlCats" id="nsCat" class="input" placeholder="e.g. Research" autocomplete="off"><div class="ac-menu" id="ac-nsCat"></div></div></label>
        <label>Tag<div class="ac-wrap"><input list="dlTags" id="nsTag" class="input" placeholder="e.g. Paper text" autocomplete="off"><div class="ac-menu" id="ac-nsTag"></div></div></label>
        <label>Sub-tag<input id="nsSub" class="input" placeholder="optional"></label>
      </div>
      <label style="margin-top:12px">Describe (what you did)
        <div style="display:flex;gap:8px;align-items:flex-start"><textarea id="nsDesc" class="input ta" rows="2" placeholder="What did you work on?"></textarea><button class="mic-btn" id="micNs" title="Dictate">${I("mic",14)}</button></div>
      </label>
      <div class="row"><button class="btn primary full" id="nsGo">Start session</button></div>
    </div>
    <div class="card glass fade">
      <div class="card-h">${I("hourglass",15)}<div class="card-t">Log a finished session</div></div>
      <p class="card-sub">Backfill a session that already ended — give it a start and an end time.</p>
      <div class="grid2">
        <label>Started<input type="datetime-local" id="psStart" class="input" value="${nowLocal()}"></label>
        <label>Ended<input type="datetime-local" id="psEnd" class="input" value="${nowLocal()}"></label>
      </div>
      <div class="row"><button class="btn primary" id="psGo">Create finished session</button></div>
    </div>
  </div>`;
}
function archiveViewHtml(){
  const ended=sessions().filter(s=>s.end&&s.kind!=="daily-doc-summary");
  if(!ended.length)return `<div class="cards"><div class="card glass fade"><div class="empty">Nothing archived yet — end a session and it lands here.</div></div></div>`;
  return `<div class="cards">${ended.slice(0,40).map(s=>`
    <div class="card glass fade" style="cursor:pointer" data-id="${s.id}">
      <div style="display:flex;align-items:center;gap:10px">
        <span class="dot big" style="background:${catColor(s.category)}"></span>
        <div style="min-width:0;flex:1"><div class="card-t" style="font-size:13.5px">${esc(sessionName(s))}</div>
        <div class="card-sub" style="margin:2px 0 0">${esc(fmt(s.start))} → ${esc(fmtT(s.end))} · ${fmtDur(mins(s.start,s.end))} · doc ${docMins(s)} min</div></div>
        <span style="color:var(--faint)">${I("chevR",14)}</span>
      </div>
    </div>`).join("")}</div>`;
}
function detailHtml(s){
  const running=!s.end;
  const dur=running?null:mins(s.start,s.end);
  const endBlock=running?`
    <div class="card glass fade">
      <p class="muted small" style="margin:0 0 10px">End this session now, or set when it actually finished.</p>
      <div class="chips" style="margin-bottom:12px">
        <button class="chip ${deMode==="now"?"active":""}" data-v="now">Right now</button>
        <button class="chip ${deMode==="at"?"active":""}" data-v="at">At time</button>
      </div>
      <div class="row">
        <input type="datetime-local" id="deAt" class="input grow" value="${nowLocal()}" ${deMode==="at"?"":"hidden"}>
        <button class="btn warn" id="deGo">End session</button>
      </div>
    </div>`:`<div class="card glass fade"><div class="grid2" style="margin-bottom:0">
      <label>Started<input type="datetime-local" id="edStart" class="input" value="${localInput(s.start)}"></label>
      <label>Ended<input type="datetime-local" id="edEnd" class="input" value="${localInput(s.end)}"></label>
    </div></div>`;
  const headSub=running?'<span class="live"></span> Running since '+fmt(s.start):'Finished '+fmt(s.start)+" → "+fmt(s.end)+(dur!=null?"  ·  "+fmtDur(dur)+"":"");
  return `<div class="dhead">
    <span class="dot big" style="background:${catColor(s.category)}"></span>
    <div><div class="dh-t">${esc(sessionName(s))}</div><div class="dh-s">${headSub}</div></div>
  </div>
  ${endBlock}
  <div class="card glass fade" style="margin-top:12px">
    <div class="grid3">
      <label>Category<div class="ac-wrap"><input list="dlCats" id="edCat" class="input" value="${esc(s.category)}" autocomplete="off"><div class="ac-menu" id="ac-edCat"></div></div></label>
      <label>Tag<div class="ac-wrap"><input list="dlTags" id="edTag" class="input" value="${esc(s.tag)}" autocomplete="off"><div class="ac-menu" id="ac-edTag"></div></div></label>
      <label>Sub-tag<input list="dlTags" id="edSub" class="input" value="${esc(s.sub_tag)}"></label>
    </div>
    <label style="margin:12px 0">Describe (what you did)
      <div style="display:flex;gap:8px;align-items:flex-start"><textarea id="edDesc" class="input ta" rows="4">${esc(s.describe)}</textarea><button class="mic-btn" id="micEd" title="Dictate">${I("mic",14)}</button></div>
    </label>
    <label>Notes<textarea id="edNotes" class="input ta" rows="2">${esc(s.notes)}</textarea></label>
    <div class="row">
      <button class="btn primary" id="edSave">${running?"Save details":"Save changes"}</button>
      ${running?"":`<button class="btn ghost" id="edReopen">${I("refresh",13)} Reopen</button>`}
      <button class="btn danger" id="edDel">${I("trash",13)} Delete</button>
    </div>
  </div>`;
}
function bindActiveView(){
  bindStartChips();bindAutocomplete("nsCat","ac-nsCat",getCats);bindAutocomplete("nsTag","ac-nsTag",getTags);
  const mic=document.getElementById("micNs");if(mic)mic.addEventListener("click",()=>dictateInto("nsDesc"));
  const go=document.getElementById("nsGo");if(go)go.addEventListener("click",async()=>{
    const payload=nsMode==="now"?{type:"now"}:{type:"at",value:$("#nsAt").value};
    const data={category:$("#nsCat").value,tag:$("#nsTag").value,sub_tag:$("#nsSub").value,describe:$("#nsDesc").value};
    const r=await A("start_session",payload,data);
    if(r.error)return toast(r.error,"err");
    S.sessions=r.sessions||S.sessions;S.sel=null;scheduleRender();toast("Session started.");
  });
  const pg=document.getElementById("psGo");if(pg)pg.addEventListener("click",async()=>{
    const r=await A("log_past_session",{start:$("#psStart").value,end:$("#psEnd").value});
    if(r.error)return toast(r.error,"err");
    S.sessions=r.sessions||S.sessions;S.sel=null;scheduleRender();toast("Finished session logged.");
  });
}
function bindArchiveView(){
  document.querySelectorAll("#mainScroll .card[data-id]").forEach(c=>c.addEventListener("click",()=>{S.sel=c.dataset.id;scheduleRender();}));
}
function bindStartChips(){
  const cs=document.querySelectorAll("#mainScroll .chips .chip");if(!cs.length)return;
  cs.forEach(c=>c.addEventListener("click",()=>{
    const group=c.parentElement;group.querySelectorAll(".chip").forEach(x=>x.classList.toggle("active",x===c));
    if(group.parentElement.querySelector("#nsAt")){nsMode=c.dataset.v;const el=$("#nsAt");if(el)el.hidden=nsMode!=="at";}
    if(group.parentElement.querySelector("#deAt")){deMode=c.dataset.v;const el=$("#deAt");if(el)el.hidden=deMode!=="at";}
  }));
}
function bindDetail(s){
  bindAutocomplete("edCat","ac-edCat",getCats);bindAutocomplete("edTag","ac-edTag",getTags);
  const mic=document.getElementById("micEd");if(mic)mic.addEventListener("click",()=>dictateInto("edDesc"));
  if(s.end){
    const sv=$("#edSave");if(sv)sv.addEventListener("click",saveDetail);
    const ro=$("#edReopen");if(ro)ro.addEventListener("click",async()=>{
      const r=await A("reopen_session",s.id);
      if(r.error)toast(r.error,"err");else{S.sessions=r.sessions||S.sessions;S.sel=s.id;scheduleRender();toast("Session reopened — it is active again.");}
    });
    const dl=$("#edDel");if(dl)dl.addEventListener("click",del);
  }else{
    bindStartChips();
    const dg=$("#deGo");if(dg)dg.addEventListener("click",async()=>{
      const payload=deMode==="now"?{type:"now"}:{type:"at",value:$("#deAt").value};
      const r=await A("end_session",s.id,payload);
      if(r.error)toast(r.error,"err");else{S.sessions=r.sessions||S.sessions;S.sel=s.id;S.tab="archive";scheduleRender();toast("Session ended. Fill the details to finish.");}
    });
    const sv=$("#edSave");if(sv)sv.addEventListener("click",saveDetail);
    const dl=$("#edDel");if(dl)dl.addEventListener("click",del);
  }
}
async function saveDetail(){
  const s=byId(S.sel);if(!s)return;
  const fields={category:$("#edCat").value,tag:$("#edTag").value,sub_tag:$("#edSub").value,describe:$("#edDesc").value,notes:$("#edNotes").value,doc_seconds:Math.round(docAccum[S.sel]||0)};
  if(s.end){fields.start=$("#edStart").value;fields.end=$("#edEnd").value;}
  const r=await A("update_session",s.id,fields);
  if(r.error)toast(r.error,"err");else{S.sessions=r.sessions||S.sessions;scheduleRender();toast("Changes saved.");}
}
async function del(){
  if(!confirm("Delete this session permanently?"))return;
  const r=await A("delete_session",S.sel);
  if(r.error)toast(r.error,"err");else{delete docAccum[S.sel];S.sessions=r.sessions||S.sessions;S.sel=null;scheduleRender();toast("Session deleted.");}
}
function watchDoc(s){
  activeSid=s.id;
  if(!docTick){
    docTick=setInterval(()=>{
      const id=activeSid;if(!id)return;
      const cur=byId(id);if(!cur)return;
      if(cur.kind==="daily-doc-summary")return;
      if(!document.hasFocus())return;
      if(document.visibilityState!=="visible")return;
      const ae=document.activeElement;
      const focused=ae&&["edCat","edTag","edSub","edDesc","edNotes"].indexOf(ae.id)>=0;
      if(focused||(Date.now()-lastKey)<45000)docAccum[id]=(docAccum[id]||0)+1;
    },1000);
  }
  document.querySelectorAll("#edCat,#edTag,#edSub,#edDesc,#edNotes").forEach(el=>{
    el.addEventListener("input",()=>{lastKey=Date.now();});
  });
}
/* ============ exports ============ */
function exportViewHtml(){
  const pool=sessions().filter(s=>s.end&&!s.kind);
  const cats=[...new Set(pool.map(s=>s.category).filter(Boolean))].sort();
  const tags=[...new Set(pool.map(s=>s.tag).filter(Boolean))].sort();
  const cOpts=["All categories",...cats],tOpts=["All tags",...tags];
  const mkSelect=(id,opts,val)=>`
    <div class="cselect" data-id="${id}" data-value="${esc(val)}">
      <button type="button" class="cselect-trigger"><span>${esc(val)}</span>${I("chevD",14,"cselect-arrow")}</button>
      <div class="cselect-menu">${opts.map(o=>`<div class="copt ${o===val?"active":""}" data-v="${esc(o)}"><span>${esc(o)}</span>${o===val?I("check",14):""}</div>`).join("")}</div>
    </div>`;
  return `<div class="cards">
    <div class="card glass fade">
      <div class="card-h">${I("download",15)}<div class="card-t">Export to Excel</div></div>
      <p class="card-sub">Filter finished sessions by category, tag and date range. The workbook has 4 sheets: Sessions (with doc min), By Category, By Tag and Documentation daily.</p>
      <div class="grid3">
        <label>Category${mkSelect("exCat",cOpts,"All categories")}</label>
        <label>Tag${mkSelect("exTag",tOpts,"All tags")}</label>
        <label>Range${mkSelect("exDur",DUR_OPTS,"Last 12 days")}</label>
      </div>
      <label style="margin-top:10px">Export name (optional)<input id="exName" class="input" placeholder="Leave empty for auto: category_tag_YYYYMMDD_YYYYMMDD"></label>
      <p class="muted small" id="exPreview" style="margin:6px 0 0;opacity:.9"></p>
      <p class="muted" id="exCount"></p>
      <div class="row"><button class="btn primary" id="exGo">Export to Excel</button></div>
    </div>
  </div>`;
}
function bindCustomSelects(root,onChange){
  root.querySelectorAll(".cselect").forEach(cs=>{
    const trig=cs.querySelector(".cselect-trigger"),menu=cs.querySelector(".cselect-menu");
    trig.addEventListener("click",e=>{e.stopPropagation();const open=cs.classList.contains("open");document.querySelectorAll(".cselect.open").forEach(o=>{if(o!==cs)o.classList.remove("open");});cs.classList.toggle("open",!open);});
    menu.querySelectorAll(".copt").forEach(opt=>opt.addEventListener("click",()=>{
      const v=opt.dataset.v;cs.dataset.value=v;trig.querySelector("span").textContent=v;
      menu.querySelectorAll(".copt").forEach(o=>{const is=o.dataset.v===v;o.classList.toggle("active",is);const ch=o.querySelector("svg");if(ch&&!is)ch.remove();if(is&&!ch)o.insertAdjacentHTML("beforeend",I("check",14));});
      cs.classList.remove("open");if(onChange)onChange();
    }));
  });
  document.addEventListener("click",()=>document.querySelectorAll(".cselect.open").forEach(c=>c.classList.remove("open")),{once:false});
}
function getCSelectValue(id){const el=document.querySelector(`.cselect[data-id="${id}"]`);return el?el.dataset.value:"";}
function bindExport(){
  const sanitize=s=>{s=String(s||"").trim();if(!s||s==="All categories"||s==="All tags")return "all";s=s.replace(/[\\/*?:"<>|]/g,"-").replace(/\s+/g,"_").replace(/_+/g,"_").replace(/^[_-]+|[_-]+$/g,"");return s.slice(0,48)||"all";};
  const autoName=(cat,tag,dur)=>{
    const catS=sanitize(cat),tagS=sanitize(tag);const today=new Date();const end=today.toISOString().slice(0,10).replace(/-/g,"");
    const modeMap={"Today":0,"Last 3 days":3,"Last 7 days":7,"Last 12 days":12,"Last 30 days":30,"All time":Infinity};
    let start;
    if(dur==="All time"){const pool=sessions().filter(s=>s.end&&!s.kind);const tagged=pool.filter(s=>(cat==="All categories"||s.category===cat)&&(tag==="All tags"||s.tag===tag));if(tagged.length){start=new Date(Math.min(...tagged.map(r=>new Date(r.start)))).toISOString().slice(0,10).replace(/-/g,"");}else start=end;}
    else if(dur==="Today")start=end;
    else{const n=modeMap[dur]||0;const d=new Date(today.getTime()-n*86400000);start=d.toISOString().slice(0,10).replace(/-/g,"");}
    return `${catS}_${tagS}_${start}_${end}.xlsx`;
  };
  const refresh=()=>{
    const cat=getCSelectValue("exCat")||"All categories",tag=getCSelectValue("exTag")||"All tags",dur=getCSelectValue("exDur")||"Last 12 days";
    const now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
    const days={["Today"]:0,["Last 3 days"]:3,["Last 7 days"]:7,["Last 12 days"]:12,["Last 30 days"]:30,["All time"]:Infinity};
    const cutoff=dur==="Today"?today:new Date(now.getTime()-days[dur]*86400000);
    const n=sessions().filter(s=>{if(!s.end||s.kind)return false;if(cat!=="All categories"&&s.category!==cat)return false;if(tag!=="All tags"&&s.tag!==tag)return false;return new Date(s.start)>=cutoff;}).length;
    const el=document.getElementById("exCount");if(el)el.textContent=n?`${n} session(s) will be exported.`:"No sessions match this filter.";
    const prev=document.getElementById("exPreview");const exNameEl=document.getElementById("exName");
    const custom=(exNameEl?exNameEl.value:"").trim();const auto=autoName(cat,tag,dur);
    if(prev)prev.textContent=custom?`Will save as: ${sanitize(custom).replace(/\.xlsx$/i,"")}.xlsx  (auto would be ${auto})`:`Auto name: ${auto}`;
  };
  bindCustomSelects(document.getElementById("mainScroll"),refresh);
  refresh();
  const exNameEl=document.getElementById("exName");if(exNameEl)exNameEl.addEventListener("input",refresh);
  const go=document.getElementById("exGo");if(go)go.addEventListener("click",async()=>{
    const cat=getCSelectValue("exCat")||"All categories",tag=getCSelectValue("exTag")||"All tags",dur=getCSelectValue("exDur")||"Last 12 days";
    const exNameEl2=document.getElementById("exName");const custom=(exNameEl2?exNameEl2.value:"").trim();
    const r=await A("export_excel",cat,tag,dur,custom||null);
    if(r.error)return toast(r.error,"err");
    const name=String(r.path).split(/[\\/]/).pop();
    toast(`Exported ${r.count} session(s) — ${name}`);
    loadExports();
    try{await A("open_export",r.path);}catch(e){}
  });
}
async function loadExports(){
  const r=await A("list_exports");
  if(r&&!r.error)S.exports=r.exports||[];
  if(S.tab==="export")renderSide();
}
function bindAutocomplete(inputId,menuId,sourceFn){
  const inp=document.getElementById(inputId),menu=document.getElementById(menuId);
  if(!inp||!menu)return;
  function renderMenu(){
    const q=inp.value.trim().toLowerCase();
    const src=sourceFn().filter(v=>!q||v.toLowerCase().includes(q)).slice(0,8);
    if(!src.length){menu.innerHTML=`<div style="padding:9px 11px;color:var(--faint);font-size:12.5px">No matches</div>`;menu.classList.add("open");return;}
    menu.innerHTML=src.map(v=>`<div class="ac-opt" data-v="${esc(v)}">${esc(v)}</div>`).join("");
    menu.classList.add("open");
    menu.querySelectorAll(".ac-opt").forEach(o=>o.addEventListener("click",()=>{inp.value=o.dataset.v;menu.classList.remove("open");inp.focus();}));
  }
  inp.addEventListener("focus",renderMenu);inp.addEventListener("input",renderMenu);
  inp.addEventListener("blur",()=>setTimeout(()=>menu.classList.remove("open"),140));
}
/* ============ dashboard ============ */
let DASH=null;
async function loadDash(){
  const r=await A("dashboard_stats",S.dash.range);
  if(r.error){toast("Dashboard error: "+r.error,"err");return;}
  DASH=r;
  if(S.tab==="dashboard"){const sc=document.getElementById("mainScroll");sc.innerHTML=dashboardHtml();bindDashboard();}
}
function kpi(v,l,hl){return `<div class="kpi ${hl?"hl":""}"><div class="kpi-v">${v}</div><div class="kpi-l">${l}</div></div>`;}
function barChart(items,color,h,noValues){
  const W=640,H=h||180;const pad=36;
  const max=Math.max(1,...items.map(i=>i.value));
  const step=(W-pad*2)/Math.max(1,items.length);
  const bw=Math.min(60,step*0.62);
  const cols=Array.isArray(color)?color:items.map(()=>color);
  let s="";
  [0.25,0.5,0.75,1].forEach(f=>{
    const y=H-28-f*(H-56);
    s+=`<line x1="${pad}" y1="${y.toFixed(1)}" x2="${W-pad}" y2="${y.toFixed(1)}" stroke="#8b98ab" opacity=".18"/><text x="${pad-5}" y="${(y+3).toFixed(1)}" font-size="9" fill="#8b98ab" text-anchor="end">${esc(fmtDur(max*f))}</text>`;
  });
  items.forEach((it,i)=>{
    const bh=Math.max(3,(it.value/max)*(H-56));
    const x=pad+i*step+(step-bw)/2;const y=H-28-bh;
    s+=`<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" rx="5" fill="${cols[i%cols.length]}" opacity=".88"><title>${esc(it.label)}: ${fmtDur(it.value)}</title></rect>`;
    if(!noValues)s+=`<text x="${(x+bw/2).toFixed(1)}" y="${(y-6).toFixed(1)}" font-size="10" font-weight="600" fill="#aeb9c9" text-anchor="middle">${esc(fmtDur(it.value))}</text>`;
  });
  if(items.length<=8)items.forEach((it,i)=>{s+=`<text x="${(pad+i*step+step/2).toFixed(1)}" y="${H-10}" font-size="10" fill="#8b98ab" text-anchor="middle">${esc(it.label)}</text>`;});
  else{const every=Math.ceil(items.length/8);items.forEach((it,i)=>{if(i%every===0)s+=`<text x="${(pad+i*step+step/2).toFixed(1)}" y="${H-10}" font-size="9.5" fill="#8b98ab" text-anchor="middle">${esc(it.label)}</text>`;});}
  return `<svg class="chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">${s}<line x1="${pad}" y1="${H-28}" x2="${W-pad}" y2="${H-28}" stroke="#333f52" stroke-width="1"/></svg>`;
}
function lineChart(pts,color,h){
  const W=640,H=h||170;const pad=30;
  const max=Math.max(1,...pts.map(p=>p.value));
  const n=pts.length;if(!n)return `<div class="empty">No data</div>`;
  const step=(W-pad*2)/Math.max(1,n-1);
  const xy=pts.map((p,i)=>[pad+i*step,H-24-(p.value/max)*(H-46)]);
  let path="",dots="",labels="";
  xy.forEach((c,i)=>{path+=(i?"L":"M")+c[0].toFixed(1)+","+c[1].toFixed(1)+" ";dots+=`<circle cx="${c[0]}" cy="${c[1]}" r="3" fill="${color}"><title>${esc(pts[i].label)}: ${fmtDur(pts[i].value)}</title></circle>`;});
  const every=Math.ceil(n/7);
  pts.forEach((p,i)=>{if(i%every===0)labels+=`<text x="${xy[i][0]}" y="${H-8}" font-size="9.5" fill="#8b98ab" text-anchor="middle">${esc(p.label)}</text>`;});
  return `<svg class="chart" viewBox="0 0 ${W} ${H}"><path d="${path}Z" fill="${color}" opacity=".10" stroke="none"/><path d="${xy.map((c,i)=>(i?"L":"M")+c[0].toFixed(1)+","+c[1].toFixed(1)).join(" ")}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>${dots}${labels}<line x1="${pad}" y1="${H-24}" x2="${W-pad}" y2="${H-24}" stroke="#333f52"/></svg>`;
}
function dashboardHtml(){
  if(!DASH)return `<div class="cards"><div class="card glass fade" style="text-align:center"><span class="spinner"></span> <span style="margin-left:8px">Crunching your time…</span></div></div>`;
  const d=DASH;const ov=d.overview||{};
  const cats=d.categories||[];
  const activeCat=S.dash.cat?cats.find(c=>c.category===S.dash.cat):null;
  const heatCat=S.dash.heat==="all"?null:S.dash.heat;
  return `<div class="cards">
    <div class="kpis">
      ${kpi(fmtDur(ov.total_minutes||0),"Total time",true)}
      ${kpi(ov.total_sessions||0,"Sessions")}
      ${kpi(fmtDur(ov.total_doc_minutes||0),"Doc time")}
      ${kpi(pct(ov.doc_ratio),"Doc share")}
      ${kpi(fmtDur(ov.avg_session_min||0),"Avg session")}
      ${kpi(ov.active_count||0,"Active now")}
    </div>
    <div class="chart-card">
      <div class="chart-h"><div class="chart-t">Daily vs nightly</div><div class="chart-note">nightly = start 18:00–05:59</div></div>
      <div class="grid4" style="margin-bottom:10px">
        <div class="kpi"><div class="kpi-v">${(d.daily_nightly||{}).daily_count||0}</div><div class="kpi-l">Daytime sessions</div></div>
        <div class="kpi"><div class="kpi-v">${(d.daily_nightly||{}).nightly_count||0}</div><div class="kpi-l">Night sessions</div></div>
        <div class="kpi"><div class="kpi-v">${fmtDur((d.daily_nightly||{}).daily_minutes||0)}</div><div class="kpi-l">Daytime time</div></div>
        <div class="kpi"><div class="kpi-v">${fmtDur((d.daily_nightly||{}).nightly_minutes||0)}</div><div class="kpi-l">Night time</div></div>
      </div>
      ${barChart(((d.daily_nightly||{}).by_bucket||[]).map(b=>({label:b.bucket,value:b.minutes})),["#34d399","#34d399","#38bdf8","#38bdf8"],200)}
      <div class="legend"><span><i style="background:#34d399"></i>daytime (06–18)</span><span><i style="background:#38bdf8"></i>night (18–06)</span></div>
    </div>
    <div class="chart-card">
      <div class="chart-h"><div class="chart-t">Trend</div><div class="chips">
        <button class="chip ${S.dash.mode==="daily"?"active":""}" data-m="daily">Daily</button>
        <button class="chip ${S.dash.mode==="weekly"?"active":""}" data-m="weekly">Weekly</button>
        <button class="chip ${S.dash.mode==="monthly"?"active":""}" data-m="monthly">Monthly</button>
      </div></div>
      ${trendChartHtml(d,S.dash.mode)}
    </div>
    <div class="chart-card">
      <div class="chart-h"><div class="chart-t">${activeCat?"Sub-categories · "+esc(activeCat.category):"Categories"}</div>
      ${activeCat?`<button class="btn ghost small" id="catBack">Back to categories</button>`:`<div class="chart-note">click a category to drill into sub-categories</div>`}
      </div>
      ${categoryHtml(d,activeCat)}
    </div>
    <div class="chart-card">
      <div class="chart-h"><div class="chart-t">Documentation / work ratio</div><div class="chips">
        <button class="chip ${S.dash.mode==="weekly"?"active":""}" data-m="weekly">Weekly</button>
        <button class="chip ${S.dash.mode==="monthly"?"active":""}" data-m="monthly">Monthly</button>
      </div></div>
      ${docRatioHtml(d)}
    </div>
    <div class="chart-card">
      <div class="chart-h"><div class="chart-t">When do you work?</div>
        <select class="input" id="heatCat" style="width:180px;padding:7px 10px;font-size:12.5px">
          <option value="all">All categories</option>
          ${cats.slice(0,6).map(c=>`<option value="${esc(c.category)}" ${heatCat===c.category?"selected":""}>${esc(c.category)}</option>`).join("")}
        </select>
      </div>
      ${heatmapHtml(d,heatCat)}
    </div>
    <div class="grid2">
      <div class="chart-card"><div class="chart-h"><div class="chart-t">Session length</div></div>${durDistHtml(d)}</div>
      <div class="chart-card"><div class="chart-h"><div class="chart-t">Weekly rhythm</div></div>${weekPatternHtml(d)}</div>
    </div>
  </div>`;
}
function trendChartHtml(d,mode){
  const t=d.trends||{};const src=mode==="daily"?t.daily:mode==="weekly"?t.weekly:t.monthly;
  if(!src||!src.length)return `<div class="empty">No data in this range.</div>`;
  const pts=src.map(r=>({label:mode==="daily"?r.date.slice(5):mode==="weekly"?r.week_start.slice(5):r.month,value:r.minutes}));
  return lineChart(pts,"#34d399",190)+`<div class="legend"><span><i style="background:#34d399"></i>minutes</span></div>`;
}
function categoryHtml(d,activeCat){
  const cats=d.categories||[];
  if(activeCat){
    const subs=(activeCat.sub_tags||[]).filter(s=>s.sub_tag);
    const trend=((d.category_trends||{})[activeCat.category]||[]);
    const trendHtml=trend.length?lineChart(trend.map(p=>({label:p.period_key.slice(5),value:p.minutes})),catColor(activeCat.category),140)+`<div class="legend"><span><i style="background:${catColor(activeCat.category)}"></i>daily minutes · ${esc(activeCat.category)}</span></div>`:`<div class="empty">No trend data.</div>`;
    if(!subs.length)return trendHtml+`<div class="empty">No sub-tags under ${esc(activeCat.category)} yet.</div>`;
    const total=Math.max(1,...subs.map(s=>s.minutes));
    return trendHtml+subs.map(s=>`
      <div class="cat-row" style="cursor:default">
        <span class="cat-name" style="min-width:0">${esc(s.sub_tag||"—")}</span>
        <div class="cat-bar"><i style="width:${Math.round(s.minutes/total*100)}%;background:${catColor(activeCat.category)}"></i></div>
        <span class="cat-val">${fmtDur(s.minutes)} · ${s.sessions}×</span>
      </div>`).join("");
  }
  const max=Math.max(1,...cats.map(c=>c.minutes));
  if(!cats.length)return `<div class="empty">No sessions in this range.</div>`;
  return cats.map(c=>`
    <div class="cat-row" data-cat="${esc(c.category)}">
      <span class="cat-name">${esc(c.category)}</span>
      <div class="cat-bar"><i style="width:${Math.round(c.minutes/max*100)}%;background:${catColor(c.category)}"></i></div>
      <span class="cat-val">${fmtDur(c.minutes)} · ${c.sessions}× · ${Math.round((c.share||0)*100)}%</span>
    </div>`).join("");
}
function docRatioHtml(d){
  const t=d.doc_ratio_trend||{};
  const src=S.dash.mode==="monthly"?t.monthly:t.weekly;
  if(!src||!src.length)return `<div class="empty">No data in this range.</div>`;
  const pts=src.map(r=>({label:r.week_start?r.week_start.slice(5):r.month,value:Math.round((r.ratio||0)*1000)/10}));
  return lineChart(pts,"#60a5fa",170)+`<div class="legend"><span><i style="background:#60a5fa"></i>doc % of work time</span></div>`;
}
function heatmapHtml(d,heatCat){
  const hm=heatCat&&d.category_heatmap&&d.category_heatmap[heatCat]?d.category_heatmap[heatCat].minutes:d.heatmap.minutes;
  const max=Math.max(1,...hm.flat());
  const days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  let cells="";
  hm.forEach((row,di)=>{
    cells+=`<div class="heat-lab">${days[di]}</div>`;
    row.forEach((v,hi)=>{
      const t=v/max;const a=t>0?(0.12+t*0.88):0.05;
      cells+=`<div class="heat-cell" style="background:hsla(153,65%,50%,${a})" title="${days[di]} ${String(hi).padStart(2,"0")}:00 — ${fmtDur(v)}"></div>`;
    });
  });
  let hrs="";
  [0,3,6,9,12,15,18,21].forEach(h=>{hrs+=`<div class="heat-hr" style="grid-column:${h+2}">${String(h).padStart(2,"0")}</div>`;});
  return `<div class="heat-grid">${cells}${hrs}</div>`;
}
function durDistHtml(d){
  const items=d.duration_dist||[];
  const max=Math.max(1,...items.map(i=>i.count));
  const total=items.reduce((a,b)=>a+b.count,0);
  return items.map(it=>`
    <div class="cat-row" style="cursor:default">
      <span class="cat-name" style="min-width:70px">${esc(it.bucket)} min</span>
      <div class="cat-bar"><i style="width:${Math.round(it.count/max*100)}%;background:var(--violet)"></i></div>
      <span class="cat-val">${it.count} · ${total?Math.round(it.count/total*100):0}%</span>
    </div>`).join("");
}
function weekPatternHtml(d){
  const wp=d.weekly_pattern||{};
  const days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const items=days.map((l,i)=>({label:l,value:wp.per_weekday?wp.per_weekday[i]:0}));
  return barChart(items,"#a78bfa",150,true)+`<div class="chart-note">Peak: ${esc(wp.peak_weekday||"—")} around ${wp.peak_hour!=null?String(wp.peak_hour).padStart(2,"0")+":00":"—"}</div>`;
}
function bindDashboard(){
  const sc=document.getElementById("mainScroll");
  sc.querySelectorAll(".chart-card .chips .chip").forEach(c=>c.addEventListener("click",()=>{
    const m=c.dataset.m;if(m){S.dash.mode=m;renderMain();return;}
  }));
  sc.querySelectorAll(".cat-row[data-cat]").forEach(r=>r.addEventListener("click",()=>{S.dash.cat=r.dataset.cat;renderMain();}));
  const back=document.getElementById("catBack");if(back)back.addEventListener("click",()=>{S.dash.cat=null;renderMain();});
  const hc=document.getElementById("heatCat");if(hc)hc.addEventListener("change",()=>{S.dash.heat=hc.value;renderMain();});
}
/* ============ AI ============ */
async function aiBootstrap(){
  const [cfg,agents,providers]=await Promise.all([A("ai_get_config"),A("ai_agents"),A("ai_providers")]);
  if(cfg&&!cfg.error)S.ai.cfg=cfg;
  if(agents&&agents.agents)S.ai.agents=agents.agents;
  if(providers&&providers.providers)S.ai.providers=providers.providers;
  S.ai.ready=true;
  const st=await A("ai_pipeline_status");
  if(st&&!st.error){S.ai.pipeline.st=st;S.ai.pipeline.running=!!st.running;}
  if(st&&st.running)setInterval(pollPipeline,900);
  await aiRefresh();
}
async function aiRefresh(){
  const [tasks,reports,insights]=await Promise.all([A("ai_get_tasks"),A("ai_get_reports"),A("ai_get_insights")]);
  if(tasks&&!tasks.error)S.ai.tasks=tasks.tasks||[];
  if(reports&&!reports.error)S.ai.reports=reports.reports||[];
  if(insights&&!insights.error)S.ai.insights=insights.insights;
}
function aiHtml(){
  if(!S.ai.ready)return `<div class="cards"><div class="card glass fade" style="text-align:center"><span class="spinner"></span> <span style="margin-left:8px">Loading AI workspace…</span></div></div>`;
  const keys=Object.keys((S.ai.cfg&&S.ai.cfg.keys)||{});
  if(!keys.length&&!S.ai.pipeline.running&&!S.ai.tasks.length)return aiOnboardingHtml();
  return aiHubHtml();
}
function aiGraphHtml(opts){
  const agents=S.ai.agents;if(!agents.length)return "";
  const cur=opts&&opts.cur!=null?opts.cur:-1;
  const done=opts&&opts.done||[];
  const run=opts&&opts.run;
  const configured=(S.ai.cfg&&S.ai.cfg.agents)||{};
  return `<div class="ai-graph">${agents.map((a,i)=>{
    const ico=a.id==="session-analyzer"?"scan":a.id==="task-builder"?"layers":"brain";
    const st=run&&run.agent_id===a.id?run.message:(done.includes(a.id)?"done":(i===cur?"current":(a.id in configured?"configured":"")));
    const stCls=i===cur?"cur":(done.includes(a.id)?"done":"");
    return `${i>0?`<div class="ai-edge ${run?"run":""}"></div>`:""}
    <div class="ai-node ${stCls}">
      <div class="ai-ico">${I(ico,16)}</div>
      <div style="min-width:0"><div class="ai-nm">${esc(a.label)}</div><div class="ai-pp">${esc(a.purpose)}</div></div>
      <div class="ai-st">${st==="done"||st==="configured"?I("check",12)+" "+esc(st):(i===cur?`<span class="live"></span> current`:"pending")}</div>
    </div>`;
  }).join("")}</div>`;
}
function aiOnboardingHtml(){
  const onb=S.ai.onb;const agents=S.ai.agents;const providers=S.ai.providers;
  const agent=agents[onb.idx];
  const cfg=S.ai.cfg||{};const keys=cfg.keys||{};
  const provKeys=Object.values(keys).filter(k=>k.provider===onb.provider);
  const prev=agent&&((cfg.agents&&cfg.agents[agent.id])||{});
  const provLabel=providers.find(p=>p.id===onb.provider);
  return `<div class="cards">
    <div class="card glass fade">
      <div class="card-h">${I("sparkles",15)}<div class="card-t">Bring your own key</div></div>
      <p class="card-sub">Three agents read your logs. Each agent runs on <b>your</b> model — pick a provider and key per agent. Keys are stored in this machine's OS credential locker, never in files. Billing is yours: set a spend limit on each provider key — analysis runs only on your explicit actions plus the nightly pass.</p>
      ${aiGraphHtml({cur:onb.idx})}
      <div style="background:var(--surface-2);border:1px solid var(--stroke);border-radius:12px;padding:14px">
        <div style="margin-bottom:12px">
          <div style="display:flex;align-items:center;gap:8px">
            <span class="dot" style="background:var(--accent)"></span><b style="font-size:13.5px">${esc(agent?agent.label:"")}</b>
            <span style="font-size:11.5px;color:var(--faint)">agent ${onb.idx+1} of ${agents.length}</span>
          </div>
          <div style="font-size:11.5px;color:var(--faint);margin-top:3px;line-height:1.45">${esc(agent?agent.purpose:"")}</div>
        </div>
        <label style="margin-bottom:12px">Provider
          <div class="chips" style="margin-top:6px">${providers.map(p=>`<button class="chip ${onb.provider===p.id?"active":""}" data-p="${p.id}">${esc(p.label)}</button>`).join("")}</div>
        </label>
        <label style="margin-bottom:12px">API key
          <div style="display:flex;gap:8px;align-items:center">
            <select class="input" id="onbKey" style="flex:1">
              <option value="">— choose a key —</option>
              ${provKeys.map(k=>`<option value="${esc(k.id)}" ${onb.keyId===k.id?"selected":""}>${esc(k.label||k.id)}</option>`).join("")}
              ${prev&&prev.key_id&&!provKeys.find(k=>k.id===prev.key_id)?`<option value="${esc(prev.key_id)}" ${onb.keyId===prev.key_id?"selected":""}>${esc(prev.key_id)} (proposed)</option>`:""}
            </select>
            <button class="btn ghost small" id="onbAddKey">${I("plus",12)} Add</button>
          </div>
        </label>
        <div id="onbKeyForm" hidden style="margin-bottom:12px">
          <div class="grid2" style="margin-bottom:8px"><label>Label<input id="onbKeyLabel" class="input" placeholder="e.g. main"></label><label>Key<input id="onbKeyVal" class="input" placeholder="sk-…" type="password"></label></div>
          <button class="btn primary small" id="onbKeySave">Save key</button>
        </div>
        <label>Model
          <div style="display:flex;gap:8px;align-items:flex-start;margin-top:6px">
            <div id="onbModels" style="flex:1;display:flex;flex-direction:column;gap:6px;max-height:190px;overflow-y:auto">
              ${onb.loading?`<div style="display:flex;gap:8px;align-items:center;color:var(--muted);font-size:12.5px"><span class="spinner"></span> Scanning provider docs…</div>`
                :onb.models.map(m=>`<div class="model-card ${onb.model===m?"sel":""}" data-m="${esc(m)}"><div style="min-width:0"><div class="mc-n">${esc(m)}</div></div>${onb.model===m?I("check",13):""}</div>`).join("")
                ||(onb.provider?`<div class="empty">No models yet — load them.</div>`:`<div class="empty">Pick a provider to list models.</div>`)}
            </div>
            <button class="mic-btn" id="onbLoadModels" title="Load models">${I("refresh",13)}</button>
          </div>
          <input id="onbCustomModel" class="input" placeholder="or type a custom model name (at your own responsibility)" style="margin-top:8px">
        </label>
        <div class="row" style="margin-top:12px">
          <button class="btn primary" id="onbTest">${I("zap",13)} Test model</button>
          <span id="onbTestRes" style="font-size:12.5px;color:var(--muted)"></span>
        </div>
        <div class="row" style="margin-top:8px">
          ${onb.idx>0?`<button class="btn ghost" id="onbPrev">Back</button>`:""}
          <button class="btn primary" id="onbNext" ${onb.tested?"":"disabled"}>${onb.idx<agents.length-1?"Next agent":"Save & continue"} ${I("chevR",12)}</button>
        </div>
      </div>
      <p class="muted small" style="margin:10px 0 0">Next agents pre-fill this provider &amp; key as the proposed default — you can change per agent, or keep multiple keys per provider. ${provLabel&&provLabel.capabilities&&provLabel.capabilities.indexOf("asr")>=0?"This provider also serves dictation (ASR).":""}</p>
    </div>
  </div>`;
}
function aiHubHtml(){
  const st=S.ai.pipeline.st;
  const hasTasks=(S.ai.tasks&&S.ai.tasks.length);
  const hasInsights=!!S.ai.insights;
  return `<div class="cards">
    ${S.ai.pipeline.running?`<div class="card glass fade" style="border-color:rgba(52,211,153,.35)">
      <div class="card-h">${I("activity",15)}<div class="card-t">Pipeline running</div></div>
      ${aiGraphHtml({run:st})}
      <div style="font-size:12.5px;color:var(--muted)">${esc(st&&st.message||"Starting…")}</div>
    </div>`:""}
    <div class="chips">
      <button class="chip ${S.ai.subview==="tasks"?"active":""}" data-sv="tasks">Tasks</button>
      <button class="chip ${S.ai.subview==="coach"?"active":""}" data-sv="coach">Coach</button>
      <button class="chip ${S.ai.subview==="reports"?"active":""}" data-sv="reports">Session reports</button>
      <button class="chip ${S.ai.subview==="pipeline"?"active":""}" data-sv="pipeline">Pipeline</button>
    </div>
    ${S.ai.subview==="tasks"?aiTasksHtml():S.ai.subview==="coach"?aiCoachHtml():S.ai.subview==="reports"?aiReportsHtml():aiPipelineHtml(hasTasks,hasInsights)}
  </div>`;
}
function aiPipelineHtml(hasTasks,hasInsights){
  const st=S.ai.pipeline.st;
  const fails=st&&st.done&&st.results?Object.keys(st.results).filter(a=>st.results[a]&&st.results[a].error):[];
  return `<div class="card glass fade">
    <div class="card-h">${I("route",15)}<div class="card-t">Agent pipeline</div></div>
    <p class="card-sub">Runs: Session Analyzer → Task Builder → Coach. Each agent uses its configured model; edges animate while running.</p>
    ${aiGraphHtml({done:hasTasks?["session-analyzer","task-builder"]:[],run:S.ai.pipeline.running?S.ai.pipeline.st:null})}
    ${fails.length?`<div class="insight" style="border-color:rgba(248,113,113,.4)">
      <div class="in-t">${I("alert",13)} ${fails.length} agent(s) failed</div>
      ${fails.map(a=>`<div class="in-s" style="margin-top:6px"><b>${esc(a)}</b>: ${esc(st.results[a].error||"failed")}</div>
        <div class="row" style="margin-top:6px">
          <button class="btn primary small" data-fbauto="${esc(a)}">${I("zap",12)} Use best fallback</button>
          <button class="btn ghost small" data-fbrepair="${esc(a)}">${I("edit",12)} Repair model</button>
        </div>`).join("")}
    </div>`:""}
    <div class="row">
      <button class="btn primary" id="runPipeline" ${S.ai.pipeline.running?"disabled":""}>${I("play",13)} Run pipeline</button>
      <button class="btn ghost" id="onbReset">${I("settings",13)} Reconfigure agents</button>
    </div>
    ${S.ai.pipeline.st&&!S.ai.pipeline.running?`<div style="margin-top:10px;font-size:12.5px;color:var(--muted)">${esc(S.ai.pipeline.st.message||"")}</div>`:""}
  </div>`;
}
function aiTasksHtml(){
  const tasks=S.ai.tasks||[];
  if(!tasks.length)return `<div class="card glass fade"><div class="empty">No tasks yet.<br><span style="font-size:11.5px;color:var(--faint)">Run the pipeline — the Task Builder creates the timeline, challenges and steps from your logs.</span></div>
    <div style="text-align:center"><button class="btn primary" id="runPipelineT">${I("play",13)} Run pipeline</button></div></div>`;
  const selTask=S.ai.taskSel!=null?tasks[S.ai.taskSel]:null;
  if(selTask)return aiTaskDetailHtml(selTask);
  return tasks.map((t,i)=>`
    <div class="card glass fade" style="cursor:pointer" data-task="${i}">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:var(--surface-hi);border:1px solid var(--stroke)">${I("box",15)}</div>
        <div style="flex:1;min-width:0"><div class="card-t" style="font-size:13.5px">${esc(t.name||("Task "+(i+1)))}</div>
        <div class="card-sub" style="margin:2px 0 0">${(t.timeline||[]).length} phases · ${(t.challenges||[]).length} challenges · ${(t.steps||[]).length} steps</div></div>
        <span style="color:var(--faint)">${I("chevR",14)}</span>
      </div>
    </div>`).join("");
}
function aiTaskDetailHtml(t){
  const steps=t.steps||[];const challenges=t.challenges||[];
  const selStep=S.ai.stepSel;
  const activeChallenges=selStep!=null?challenges.filter(c=>(c.step_refs||[]).indexOf(Number(selStep))>=0||(c.step_refs||[]).map(String).indexOf(String(selStep))>=0):challenges;
  return `<div class="card glass fade">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
      <button class="btn ghost small" id="taskBack">Back to tasks</button>
      <div style="flex:1;min-width:0"><div class="card-t">${esc(t.name||"Task")}</div></div>
    </div>
    <div class="grid2">
      <div>
        <div class="chart-note" style="margin-bottom:8px">TIMELINE — click a phase</div>
        <div>${(t.timeline||[]).map((p,i)=>`
          <div class="tl-item ${i===selStep?"cur":""}">
            <div class="tl-dot">${i+1}</div>
            <div class="tl-b"><div class="tl-t" data-step="${i}">${esc(p.label)}</div>
            <div class="tl-n">${esc(p.status||"")}${p.note?" · "+esc(p.note):""}</div></div>
          </div>`).join("")||`<div class="empty">No phases yet.</div>`}
        </div>
        <div class="chart-note" style="margin:12px 0 8px">STEPS — click to filter challenges</div>
        <div>${steps.map((s,i)=>`<div class="insight" style="cursor:pointer;margin-top:6px;${i===selStep?"border-color:rgba(52,211,153,.4)":""}" data-step="${i}">
          <div class="in-t">${I("list",13)} ${esc(s.title||("Step "+(i+1)))}</div>
          <div class="in-s">${(s.log_refs||[]).map(l=>`<span style="display:inline-block;background:var(--surface-hi);border-radius:6px;padding:1px 7px;font-size:11px;margin:2px 4px 0 0">${esc(l.part||"")}</span>`).join("")||"no timelog parts"}</div>
        </div>`).join("")||`<div class="empty">No steps yet.</div>`}</div>
      </div>
      <div>
        <div class="chart-note" style="margin-bottom:8px">CHALLENGES ${selStep!=null?"· addressed by this step":""}</div>
        ${activeChallenges.map((c,i)=>`
          <div class="insight" style="margin-top:6px">
            <div class="in-t">${I("target",13)} ${esc(c.text||"")}</div>
            <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap">
              <span class="sev ${esc(c.severity||"medium")}">${esc(c.severity||"medium")}</span>
              <span class="st ${esc(c.status||"identified")}">${esc((c.status||"identified").replace("_"," "))}</span>
            </div>
            ${c.status==="partially_solved"?`
              <div class="in-s" style="margin-top:8px"><b style="color:var(--accent)">Done:</b> ${esc((c.done||[]).join(" · ")||"—")}</div>
              <div class="in-s"><b style="color:var(--warn)">Remaining:</b> ${esc((c.remaining||[]).join(" · ")||"—")}</div>`:""}
            ${(c.step_refs||[]).length?`<div class="in-s" style="margin-top:6px;font-size:11px">steps: ${c.step_refs.map(s=>`<span style="background:var(--surface-hi);border-radius:6px;padding:1px 7px;margin-right:4px">${esc(steps[s]&&steps[s].title||("Step "+s))}</span>`).join("")}</div>`:""}
          </div>`).join("")||`<div class="empty">No challenges.</div>`}
        <div class="chart-note" style="margin:12px 0 4px">PROPOSITIONS — check in/out to teach the pipeline</div>
        ${(t.propositions||[]).map((p,i)=>`
          <div class="prop ${p.accepted?"accepted":(p.rejected?"rejected":"")}">
            <div class="prop-txt">${esc(p.text)}</div>
            <div class="prop-btns">
              <button class="prop-ok" data-prop="${i}" title="Check in (consent-gated DPO training)">${I("check",13)}</button>
              <button class="prop-no" data-prop="${i}" title="Reject">${I("x",13)}</button>
            </div>
          </div>`).join("")||`<div class="empty">No propositions.</div>`}
      </div>
    </div>
  </div>`;
}
function aiCoachHtml(){
  const ins=S.ai.insights;
  const ideal=(S.ai.cfg&&S.ai.cfg.ideal_time)||{};
  const div=ins&&ins.time_division;
  return `<div class="card glass fade">
    <div class="card-h">${I("brain",15)}<div class="card-t">Work coach</div></div>
    <p class="card-sub">Independent read of your logs: logging style, timing patterns, time division, exhaustion signals. Regenerate any time.</p>
    ${ideal&&!ideal.set?`<div class="insight" style="border-color:rgba(251,191,36,.35)">
      <div class="in-t">${I("info",13)} Tell me your ideal hours</div>
      <div class="in-s">Set your ideal time-of-day / days in Settings so pattern analysis can compare against your target, not just the average.</div>
      <button class="btn warn small" id="coachIdeal" style="margin-top:8px">Set ideal time</button>
    </div>`:""}
    ${!ins?`<div class="empty">No insights yet. Run the pipeline (or just the coach) to generate them.<br><button class="btn primary" id="runCoach" style="margin-top:10px">${I("refresh",13)} Generate insights</button></div>`:`
      ${(ins.logging_style||[]).map(s=>`<div class="insight">
        <div class="in-t">${I("edit",13)} ${esc(s.issue||"")}</div>
        ${s.example_from_log?`<div class="in-ex">In your log: ${esc(s.example_from_log)}</div>`:""}
        <div class="in-s">${esc(s.suggestion||"")}</div>
      </div>`).join("")||""}
      ${(ins.time_optimization||[]).map(s=>`<div class="insight">
        <div class="in-t">${I("clock",13)} ${esc(s.pattern||"")}</div>
        ${s.evidence?`<div class="in-ex">Evidence: ${esc(s.evidence)}</div>`:""}
        <div class="in-s">${esc(s.suggestion||"")}</div>
      </div>`).join("")||""}
      ${div?`<div class="insight">
        <div class="in-t">${I("pie",13)} Time division</div>
        <div class="in-s">${esc(div.note||"")}</div>
        ${(div.categories||[]).map(c=>`<div class="cat-row" style="cursor:default">
          <span class="cat-name">${esc(c.name)}</span>
          <div class="cat-bar"><i style="width:${Math.min(100,Math.round((c.share||0)*100))}%;background:var(--accent)"></i></div>
          <span class="cat-val">${Math.round((c.share||0)*100)}%</span>
        </div>`).join("")}
      </div>`:""}
      ${(ins.exhaustion||[]).map(s=>`<div class="insight">
        <div class="in-t">${I("flame",13)} ${esc(s.pattern||"")}</div>
        ${s.evidence?`<div class="in-ex">Evidence: ${esc(s.evidence)}</div>`:""}
        <div class="in-s">${esc(s.suggestion||"")}</div>
      </div>`).join("")||""}
      <div class="row"><button class="btn primary" id="runCoach">${I("refresh",13)} Regenerate insights</button></div>`}
  </div>`;
}
function aiReportsHtml(){
  const reps=S.ai.reports||[];
  if(!reps.length)return `<div class="card glass fade"><div class="empty">No session reports yet — the Session Analyzer writes them.<br><button class="btn primary" id="runPipelineT" style="margin-top:10px">${I("play",13)} Run pipeline</button></div></div>`;
  return reps.map(r=>`<div class="card glass fade">
    <div class="card-t" style="font-size:13.5px">${esc(r.topic||"Session")}</div>
    ${r.questions&&r.questions.length?`<div class="card-sub" style="margin-top:6px"><b>Questions:</b> ${r.questions.map(q=>esc(q)).join(" · ")}</div>`:""}
    ${r.steps&&r.steps.length?`<div class="card-sub"><b>Steps:</b> ${r.steps.map(q=>esc(q)).join(" → ")}</div>`:""}
    ${r.numeric_metrics?`<div class="card-sub"><b>Metrics:</b> ${esc(typeof r.numeric_metrics==="string"?r.numeric_metrics:JSON.stringify(r.numeric_metrics))}</div>`:""}
    ${r.qualitative_results&&r.qualitative_results.length?`<div class="card-sub"><b>Results:</b> ${r.qualitative_results.map(q=>esc(q)).join(" · ")}</div>`:""}
  </div>`).join("");
}
/* ---------- AI logic ---------- */
function bindAi(){
  const sc=document.getElementById("mainScroll");
  sc.querySelectorAll(".chips .chip[data-sv]").forEach(c=>c.addEventListener("click",()=>{S.ai.subview=c.dataset.sv;S.ai.taskSel=null;S.ai.stepSel=null;renderMain();}));
  const runP=document.getElementById("runPipeline");if(runP)runP.addEventListener("click",startPipeline);
  const runPT=document.getElementById("runPipelineT");if(runPT)runPT.addEventListener("click",startPipeline);
  const runC=document.getElementById("runCoach");if(runC)runC.addEventListener("click",async()=>{
    runC.disabled=true;runC.innerHTML=`<span class="spinner"></span> Generating…`;
    const r=await A("ai_run_coach");
    runC.disabled=false;
    if(r&&!r.error){await aiRefresh();renderMain();toast("Insights regenerated.");}
    else toast((r&&r.error)||"Coach failed","err");
  });
  const reset=document.getElementById("onbReset");if(reset)reset.addEventListener("click",()=>{S.ai.onb={idx:0,provider:null,keyId:null,model:null,models:[],loading:false,testing:false,tested:false,custom:""};renderMain();});
  const taskBack=document.getElementById("taskBack");if(taskBack)taskBack.addEventListener("click",()=>{S.ai.taskSel=null;S.ai.stepSel=null;renderMain();});
  sc.querySelectorAll(".tl-t[data-step]").forEach(el=>el.addEventListener("click",()=>{S.ai.stepSel=+el.dataset.step;renderMain();}));
  sc.querySelectorAll(".insight[data-step]").forEach(el=>el.addEventListener("click",()=>{S.ai.stepSel=+el.dataset.step;renderMain();}));
  sc.querySelectorAll(".card[data-task]").forEach(c=>c.addEventListener("click",()=>{S.ai.taskSel=+c.dataset.task;S.ai.stepSel=null;renderMain();}));
  sc.querySelectorAll(".prop-ok,.prop-no").forEach(b=>b.addEventListener("click",async()=>{
    const task=S.ai.tasks[S.ai.taskSel];const p=task.propositions[+b.dataset.prop];
    const accept=b.classList.contains("prop-ok");
    const r=await A("ai_toggle_proposition",task.id,p.id,accept);
    if(r&&!r.error){S.ai.tasks=r.tasks||S.ai.tasks;renderMain();toast(accept?"Proposition checked in — saved for consent-gated DPO training.":"Proposition rejected.");}
  }));
  sc.querySelectorAll("[data-fbauto]").forEach(b=>b.addEventListener("click",async()=>{
    b.disabled=true;
    const r=await A("ai_fallback",b.dataset.fbauto);
    b.disabled=false;
    if(r&&r.ok){await A("ai_set_agent",b.dataset.fbauto,r.provider,r.key_id,r.model);S.ai.cfg=await A("ai_get_config");renderMain();toast(`Fallback applied: ${r.model} on ${r.provider}.`);}
    else toast((r&&r.error)||"No fallback available — repair the model manually.","err");
  }));
  sc.querySelectorAll("[data-fbrepair]").forEach(b=>b.addEventListener("click",()=>agentPickerModal(b.dataset.fbrepair)));
  if(sc.querySelector("#onbAddKey"))bindOnboarding();
  const coachIdeal=document.getElementById("coachIdeal");if(coachIdeal)coachIdeal.addEventListener("click",()=>openSettings("ideal"));
}
function bindOnboarding(){
  const onb=S.ai.onb;const sc=document.getElementById("mainScroll");
  sc.querySelectorAll(".chip[data-p]").forEach(c=>c.addEventListener("click",async()=>{
    onb.provider=c.dataset.p;onb.keyId=null;onb.model=null;onb.models=[];onb.tested=false;onb.custom="";
    const prev=(S.ai.cfg.agents&&S.ai.cfg.agents[S.ai.agents[onb.idx].id])||{};
    if(prev.provider===onb.provider){onb.keyId=prev.key_id||null;onb.model=prev.model||null;}
    renderMain();
  }));
  const add=document.getElementById("onbAddKey");if(add)add.addEventListener("click",()=>{const f=document.getElementById("onbKeyForm");if(f)f.hidden=!f.hidden;});
  const save=document.getElementById("onbKeySave");if(save)save.addEventListener("click",async()=>{
    const label=$("#onbKeyLabel").value.trim(),key=$("#onbKeyVal").value.trim();
    if(!key)return toast("Enter the API key","err");
    const r=await A("ai_add_key",onb.provider,label||"key-"+Date.now().toString(36),key);
    if(r&&!r.error){S.ai.cfg=await A("ai_get_config");onb.keyId=r.key_id;onb.tested=false;renderMain();toast("Key saved.");}
    else toast((r&&r.error)||"Could not save key","err");
  });
  const sel=document.getElementById("onbKey");if(sel)sel.addEventListener("change",()=>{onb.keyId=sel.value||null;onb.tested=false;renderMain();});
  const load=document.getElementById("onbLoadModels");if(load)load.addEventListener("click",loadOnbModels);
  const custom=document.getElementById("onbCustomModel");if(custom)custom.addEventListener("input",()=>{onb.custom=custom.value.trim();if(onb.custom){onb.model=onb.custom;onb.tested=false;renderMain();}});
  sc.querySelectorAll(".model-card[data-m]").forEach(m=>m.addEventListener("click",()=>{onb.model=m.dataset.m;onb.tested=false;renderMain();}));
  const test=document.getElementById("onbTest");if(test)test.addEventListener("click",async()=>{
    if(!onb.provider||!onb.keyId||!onb.model)return toast("Pick provider, key and model first","err");
    test.disabled=true;test.innerHTML=`<span class="spinner"></span> Testing…`;
    const r=await A("ai_test_model",onb.provider,onb.keyId,onb.model);
    test.disabled=false;test.innerHTML=`${I("zap",13)} Test model`;
    const res=document.getElementById("onbTestRes");
    if(r&&r.ok){onb.tested=true;if(res)res.innerHTML=`<span style="color:var(--accent)">${I("check",12)} OK · ${r.latency_ms} ms</span>`;renderMain();}
    else{if(res)res.innerHTML=`<span style="color:var(--danger)">${I("alert",12)} ${esc(r&&r.error||"failed")}</span>`;onb.tested=false;}
  });
  const prev=document.getElementById("onbPrev");if(prev)prev.addEventListener("click",()=>{onb.idx=Math.max(0,onb.idx-1);prefillAgent();renderMain();});
  const next=document.getElementById("onbNext");if(next)next.addEventListener("click",async()=>{
    const agent=S.ai.agents[onb.idx];
    const r=await A("ai_set_agent",agent.id,onb.provider,onb.keyId,onb.model);
    if(r&&!r.error){
      S.ai.cfg=await A("ai_get_config");
      if(onb.idx<S.ai.agents.length-1){onb.idx++;prefillAgent();renderMain();}
      else{toast("All agents configured. Run the pipeline.");S.ai.subview="pipeline";renderMain();}
    }else toast((r&&r.error)||"Could not save agent config","err");
  });
}
async function loadOnbModels(){
  const onb=S.ai.onb;
  if(!onb.provider)return toast("Pick a provider first","err");
  onb.loading=true;renderMain();
  const r=await A("ai_list_models",onb.provider,"chat");
  onb.loading=false;
  if(r&&!r.error){onb.models=r.models||[];if(!onb.models.length&&r.note)toast(r.note,"err");}
  else toast((r&&r.error)||"Could not list models","err");
  renderMain();
}
function prefillAgent(){
  const onb=S.ai.onb;const agent=S.ai.agents[onb.idx];
  onb.provider=null;onb.keyId=null;onb.model=null;onb.models=[];onb.tested=false;onb.custom="";
  const prev=(S.ai.cfg&&S.ai.cfg.agents&&S.ai.cfg.agents[agent.id])||{};
  if(prev.provider){onb.provider=prev.provider;onb.keyId=prev.key_id||null;onb.model=prev.model||null;}
  else{
    const last=(S.ai.cfg&&S.ai.cfg.agents&&S.ai.cfg.agents[S.ai.agents[onb.idx-1]&&S.ai.agents[onb.idx-1].id])||{};
    if(last.provider){onb.provider=last.provider;onb.keyId=last.key_id||null;}
  }
}
function startPipeline(){
  A("ai_start_pipeline").then(r=>{
    if(r&&!r.error){S.ai.pipeline.running=true;renderMain();pollPipeline();}
    else toast((r&&r.error)||"Could not start pipeline","err");
  });
}
async function pollPipeline(){
  const st=await A("ai_pipeline_status");
  if(st&&!st.error){
    S.ai.pipeline.st=st;S.ai.pipeline.running=!!st.running;
    if(S.tab==="ai"){renderMain();}
    if(!st.running){
      S.ai.pipeline.running=false;
      await aiRefresh();
      if(S.tab==="ai")renderMain();
      if(st.error)toast(st.error,"err");
      else if(st.message)toast(st.message);
    }
  }
}
/* ============ settings modal ============ */
function openModal(title,bodyHtml,footerHtml){
  const root=document.getElementById("modalRoot");
  root.innerHTML=`<div class="modal-ov open" id="modalOv"><div class="modal">
    <div class="modal-h">${I("settings",15)}<div class="modal-t">${esc(title)}</div><button class="tb-btn" id="modalX" title="Close">${I("x",13)}</button></div>
    <div class="modal-b">${bodyHtml}</div>
    ${footerHtml?`<div class="modal-f">${footerHtml}</div>`:""}
  </div></div>`;
  $("#modalX").addEventListener("click",closeModal);
  $("#modalOv").addEventListener("click",e=>{if(e.target.id==="modalOv")closeModal();});
}
function closeModal(){document.getElementById("modalRoot").innerHTML="";}
function openSettings(section){
  const cfg=S.ai.cfg||{};
  const ideal=cfg.ideal_time||{days:[1,2,3,4,5],start:"08:00",end:"18:00",set:false};
  const keys=cfg.keys||{};
  const asr=cfg.asr||{};
  const days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const body=`
    <div class="chips" style="margin-bottom:12px">
      <button class="chip ${!section||section==="general"?"active":""}" data-sec="general">General</button>
      <button class="chip ${section==="ideal"?"active":""}" data-sec="ideal">Ideal hours</button>
      <button class="chip ${section==="asr"?"active":""}" data-sec="asr">Dictation (ASR)</button>
      <button class="chip ${section==="dpo"?"active":""}" data-sec="dpo">Data & DPO</button>
    </div>
    <div id="secBody">${section==="ideal"?idealBody(ideal):section==="asr"?asrBody(cfg,keys,asr):section==="dpo"?dpoBody(cfg):generalBody(cfg)}</div>`;
  openModal("Settings",body,`<button class="btn ghost" id="modClose">Close</button>`);
  $("#modClose").addEventListener("click",closeModal);
  document.querySelectorAll("#modalOv .chip[data-sec]").forEach(c=>c.addEventListener("click",()=>openSettings(c.dataset.sec)));
  bindSecBody(section);
}
function generalBody(cfg){
  const agents=S.ai.agents||[];
  let theme="dark";try{theme=document.documentElement.getAttribute("data-theme")||"dark";}catch(e){}
  return `<div class="chart-note" style="margin-bottom:6px">AGENTS — click an agent to change its LLM (graph is vertically scrollable)</div>
  <div style="max-height:220px;overflow-y:auto;display:flex;flex-direction:column;gap:8px">
  ${agents.map(a=>{
    const c=(cfg.agents&&cfg.agents[a.id])||{};
    return `<div style="display:flex;align-items:center;gap:10px;background:var(--surface-2);border:1px solid var(--stroke);border-radius:11px;padding:10px 12px">
      <div style="flex:1;min-width:0"><div style="font-size:13px;font-weight:650">${esc(a.label)}</div>
      <div style="font-size:11.5px;color:var(--muted);margin-top:1px">${c.model?esc(c.model):"<i>not configured</i>"} · ${c.provider?esc(c.provider):""}</div></div>
      <button class="btn ghost small" data-agent="${a.id}">Change</button>
    </div>`;
  }).join("")}</div>
  <div class="chart-note" style="margin:10px 0 6px">THEME</div>
  <div class="chips"><button class="chip ${theme==="dark"?"active":""}" id="thDark">Dark</button><button class="chip ${theme==="light"?"active":""}" id="thLight">Light</button></div>
  <p class="muted small" style="margin-top:10px">App data lives next to the executable: sessions.json, ai_config.json (keys stored locally, plaintext on your disk), tasks.json, insights.json, dpo_dataset.jsonl.</p>`;
}
function idealBody(ideal){
  return `<p class="card-sub" style="margin-top:0">The coach compares your real activity against this target when you set it.</p>
  <label style="margin-bottom:10px">Work days
    <div class="chips" style="margin-top:6px">${["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((d,i)=>`<button class="chip ${(ideal.days||[]).indexOf(i+1)>=0?"active":""}" data-day="${i+1}">${d}</button>`).join("")}</div>
  </label>
  <div class="grid2"><label>Start<input id="idealStart" class="input" type="time" value="${esc(ideal.start||"08:00")}"></label>
  <label>End<input id="idealEnd" class="input" type="time" value="${esc(ideal.end||"18:00")}"></label></div>
  <div class="row"><button class="btn primary" id="idealSave">Save ideal hours</button></div>`;
}
function asrBody(cfg,keys,asr){
  const providers=S.ai.providers.filter(p=>(p.capabilities||[]).indexOf("asr")>=0);
  const allKeys=Object.values(keys);
  return `<p class="card-sub" style="margin-top:0">Dictate descriptions &amp; notes instead of typing. English only. Only models under 4% WER (per artificialanalysis.ai speech-to-text leaderboard) are selectable: whisper-1, gpt-4o-transcribe.</p>
  <label style="margin-bottom:10px">Provider
    <div class="chips" style="margin-top:6px">${providers.map(p=>`<button class="chip ${asr.provider===p.id?"active":""}" data-p="${p.id}">${esc(p.label)}</button>`).join("")||"<span style='font-size:12px;color:var(--faint)'>No ASR-capable provider yet (OpenAI / AvalAI).</span>"}</div>
  </label>
  <label style="margin-bottom:10px">Key
    <select class="input" id="asrKey">${allKeys.filter(k=>k.provider===asr.provider).map(k=>`<option value="${esc(k.id)}" ${asr.key_id===k.id?"selected":""}>${esc(k.label||k.id)}</option>`).join("")}</select>
  </label>
  <label>Model
    <select class="input" id="asrModel">${providers.find(p=>p.id===asr.provider)?(providers.find(p=>p.id===asr.provider).asr_models||[]).map(m=>`<option value="${esc(m)}" ${asr.model===m?"selected":""}>${esc(m)}</option>`).join(""):""}</select>
  </label>
  <div class="row"><button class="btn primary" id="asrSave">Save dictation config</button></div>`;
}
function dpoBody(cfg){
  return `<p class="card-sub" style="margin-top:0">If you consent, accepted/rejected propositions plus their session context are exported as preference rows for DPO training of the pipeline. Nothing leaves your machine unless you send the file yourself.</p>
  <div class="insight" style="margin-top:0">
    <div class="in-t">${I("shield",13)} Consent
      <span class="st ${cfg.consent_dpo?"solved":"identified"}">${cfg.consent_dpo?"consented":"not consented"}</span></div>
    <div class="in-s">Only rows with your explicit consent are collected.</div>
  </div>
  <div class="row">
    <button class="btn ${cfg.consent_dpo?"danger":"primary"}" id="dpoToggle">${cfg.consent_dpo?"Revoke consent":"Give consent"}</button>
    <button class="btn ghost" id="dpoExport">${I("download",13)} Export dataset</button>
  </div>`;
}
function bindSecBody(section){
  if(section==="general"){
    document.querySelectorAll("#modalOv .chip[data-agent]").forEach(b=>b.addEventListener("click",()=>agentPickerModal(b.dataset.agent)));
    const d=document.getElementById("thDark"),l=document.getElementById("thLight");
    if(d)d.addEventListener("click",()=>{window.__setTheme("dark");});
    if(l)l.addEventListener("click",()=>{window.__setTheme("light");});
  }
  if(section==="ideal"){
    const days=[];document.querySelectorAll("#modalOv .chip[data-day]").forEach(c=>c.addEventListener("click",()=>{c.classList.toggle("active");}));
    const sv=document.getElementById("idealSave");
    if(sv)sv.addEventListener("click",async()=>{
      const dsel=[...document.querySelectorAll("#modalOv .chip[data-day].active")].map(c=>+c.dataset.day);
      const r=await A("ai_set_ideal_time",dsel,$("#idealStart").value,$("#idealEnd").value);
      if(r&&!r.error){S.ai.cfg=await A("ai_get_config");closeModal();toast("Ideal hours saved.");}
      else toast((r&&r.error)||"Save failed","err");
    });
  }
  if(section==="asr"){
    document.querySelectorAll("#modalOv .chip[data-p]").forEach(c=>c.addEventListener("click",()=>openSettings("asr")));
    const sv=document.getElementById("asrSave");
    if(sv)sv.addEventListener("click",async()=>{
      const cfg=S.ai.cfg||{};
      cfg.asr={provider:(document.querySelector("#modalOv .chip[data-p].active")||{}).dataset?document.querySelector("#modalOv .chip[data-p].active").dataset.p:"",key_id:$("#asrKey").value,model:$("#asrModel").value};
      const r=await A("ai_save_config",cfg);
      if(r&&!r.error){S.ai.cfg=cfg;closeModal();toast("Dictation config saved.");}
      else toast((r&&r.error)||"Save failed","err");
    });
  }
  if(section==="dpo"){
    const tg=document.getElementById("dpoToggle");
    if(tg)tg.addEventListener("click",async()=>{
      const cfg=S.ai.cfg||{};
      const r=await A("ai_set_consent",!cfg.consent_dpo);
      if(r&&!r.error){S.ai.cfg=await A("ai_get_config");openSettings("dpo");toast("Consent updated.");}
    });
    const ex=document.getElementById("dpoExport");
    if(ex)ex.addEventListener("click",async()=>{
      const r=await A("ai_export_dpo");
      if(r&&r.ok)toast(`DPO dataset written: ${r.count} rows (${r.path})`);
      else toast((r&&r.error)||"Export failed","err");
    });
  }
}
function agentPickerModal(agentId){
  const cfg=S.ai.cfg||{};
  const cur=(cfg.agents&&cfg.agents[agentId])||{};
  const provSel=cur.provider||(S.ai.providers[0]&&S.ai.providers[0].id);
  const keys=Object.values(cfg.keys||{}).filter(k=>k.provider===provSel);
  const meta=S.ai.providers.find(p=>p.id===provSel);
  const body=`
    <label style="margin-bottom:10px">Provider
      <div class="chips" style="margin-top:6px">${S.ai.providers.map(p=>`<button class="chip ${provSel===p.id?"active":""}" data-ap="${p.id}">${esc(p.label)}</button>`).join("")}</div>
    </label>
    <label style="margin-bottom:10px">Key<select class="input" id="apKey">${keys.map(k=>`<option value="${esc(k.id)}" ${cur.key_id===k.id?"selected":""}>${esc(k.label||k.id)}</option>`).join("")}</select></label>
    <label>Model<input id="apModel" class="input" value="${esc(cur.model||"")}" placeholder="${esc((meta&&meta.chat_models||[]).join(", "))}"></label>
    <div class="row"><button class="btn primary" id="apSave">Save agent LLM</button><button class="btn ghost" id="apTest">${I("zap",12)} Test</button><span id="apRes" style="font-size:12px;color:var(--muted)"></span></div>`;
  openModal("Change agent model",body,`<button class="btn ghost" id="modClose2">Close</button>`);
  $("#modClose2").addEventListener("click",closeModal);
  document.querySelectorAll("#modalOv .chip[data-ap]").forEach(c=>c.addEventListener("click",()=>agentPickerModal(agentId)));
  const sv=document.getElementById("apSave");
  if(sv)sv.addEventListener("click",async()=>{
    const prov=document.querySelector("#modalOv .chip[data-ap].active").dataset.ap;
    const r=await A("ai_set_agent",agentId,prov,$("#apKey").value,$("#apModel").value.trim());
    if(r&&!r.error){S.ai.cfg=await A("ai_get_config");closeModal();toast("Agent model updated.");}
    else toast((r&&r.error)||"Save failed","err");
  });
  const ts=document.getElementById("apTest");
  if(ts)ts.addEventListener("click",async()=>{
    ts.disabled=true;ts.innerHTML=`<span class="spinner"></span>`;
    const prov=document.querySelector("#modalOv .chip[data-ap].active").dataset.ap;
    const r=await A("ai_test_model",prov,$("#apKey").value,$("#apModel").value.trim());
    ts.disabled=false;ts.innerHTML=`${I("zap",12)} Test`;
    const res=document.getElementById("apRes");
    if(r&&r.ok)res.innerHTML=`<span style="color:var(--accent)">OK · ${r.latency_ms} ms</span>`;
    else res.innerHTML=`<span style="color:var(--danger)">${esc(r&&r.error||"failed")}</span>`;
  });
}
function openAiSettings(){openSettings("general");}
/* ============ ASR dictation ============ */
let asrTimer=null;
async function dictateInto(textareaId){
  const cfg=S.ai.cfg||{};
  const asr=cfg.asr||{};
  if(!asr.provider||!asr.key_id||!asr.model){
    toast("Configure dictation first (Settings → Dictation).","err");
    openSettings("asr");
    return;
  }
  const r=await A("asr_begin");
  if(r.error){toast(r.error,"err");return;}
  S.asr.rec=true;S.asr.secs=0;
  openModal("Dictate",`
    <div style="text-align:center;padding:10px 0">
      <div style="width:64px;height:64px;border-radius:50%;margin:0 auto 12px;display:grid;place-items:center;background:rgba(248,113,113,.12);border:1px solid rgba(248,113,113,.4);color:var(--danger)">${I("mic",26)}</div>
      <div class="rec-time" id="recTime">00:00</div>
      <div style="font-size:12px;color:var(--muted);margin-top:4px">English · ${esc(asr.model)} · press stop when done</div>
    </div>`, `<button class="btn danger" id="recStop">${I("stop",13)} Stop & transcribe</button>`);
  asrTimer=setInterval(async()=>{
    const st=await A("asr_state");
    if(st&&st.recording){S.asr.secs=st.seconds;const el=document.getElementById("recTime");if(el)el.textContent=String(Math.floor(st.seconds/60)).padStart(2,"0")+":"+String(Math.floor(st.seconds%60)).padStart(2,"0");}
  },1000);
  const stop=document.getElementById("recStop");
  if(stop)stop.addEventListener("click",async()=>{
    clearInterval(asrTimer);S.asr.rec=false;
    stop.disabled=true;stop.innerHTML=`<span class="spinner"></span> Transcribing…`;
    const r=await A("asr_stop",asr.provider,asr.key_id,asr.model);
    closeModal();
    if(r&&r.ok){
      const ta=document.getElementById(textareaId);
      if(ta){ta.value=(ta.value?ta.value+"\\n":"")+r.text.trim();ta.dispatchEvent(new Event("input"));}
      toast("Transcribed.");
    }else toast((r&&r.error)||"Transcription failed","err");
  });
}
/* ============ init / chrome ============ */
document.getElementById("nav").addEventListener("click",e=>{
  const b=e.target.closest(".nav-item");if(!b)return;
  S.tab=b.dataset.tab;S.sel=null;S.ai.taskSel=null;S.ai.stepSel=null;
  const sl=document.getElementById("sideList");if(sl)sl.scrollTop=0;
  scheduleRender();
  if(S.tab==="dashboard")loadDash();
  if(S.tab==="ai"&&!S.ai.ready)aiBootstrap().then(()=>{if(S.tab==="ai")scheduleRender();});
  if(S.tab==="export")loadExports();
});
document.getElementById("newBtn").addEventListener("click",()=>{S.tab="active";S.sel=null;scheduleRender();document.getElementById("mainScroll").scrollTop=0;});
document.getElementById("pastBtn").addEventListener("click",()=>{S.tab="active";S.sel=null;scheduleRender();});
document.getElementById("settingsBtn").addEventListener("click",()=>openSettings("general"));
document.getElementById("themeBtn").addEventListener("click",()=>{
  const cur=document.documentElement.getAttribute("data-theme");
  window.__setTheme(cur==="dark"?"light":"dark");
});
document.getElementById("tbMin").addEventListener("click",()=>A("win_minimize"));
document.getElementById("tbMax").addEventListener("click",()=>A("win_maximize"));
document.getElementById("tbClose").addEventListener("click",()=>A("win_close"));
document.getElementById("sideList").addEventListener("click",async e=>{
  const delBtn=e.target.closest(".export-del");
  if(delBtn){
    e.stopPropagation();
    const p=delBtn.dataset.del;
    if(!confirm("Delete this export file permanently?\\n\\n"+p.split(/[\\/]/).pop()))return;
    const r=await A("delete_export",p);
    if(r&&r.error)return toast(r.error,"err");
    toast("Export deleted");
    S.exports=S.exports.filter(x=>x.path!==p);
    renderSide();
    return;
  }
  const exItem=e.target.closest(".si[data-path]");
  if(exItem){
    const p=exItem.dataset.path;
    const r=await A("open_export",p);
    if(r&&r.error)toast(r.error,"err");
    return;
  }
  const si=e.target.closest(".si[data-id]");
  if(si&&si.dataset.id){S.sel=si.dataset.id;scheduleRender();}
});
document.getElementById("mainScroll").addEventListener("focusin",e=>{
  if(e.target.matches&&e.target.matches("textarea, input"))document.body.classList.add("focus-mode");
});
document.getElementById("mainScroll").addEventListener("focusout",e=>{
  setTimeout(()=>{
    const ae=document.activeElement;
    if(!ae||!document.getElementById("mainScroll").contains(ae)||!ae.matches("textarea, input"))document.body.classList.remove("focus-mode");
  },80);
});
async function init(){
  document.querySelectorAll("[data-i]").forEach(el=>{try{el.innerHTML=I(el.dataset.i,+(el.dataset.s||16));}catch(e){}});
  const r=await A("get_state");
  if(r&&!r.error)S.sessions=r.sessions||[];
  const bi=document.getElementById("brandImg");if(bi&&AVATAR_URI)bi.src=AVATAR_URI;
  const tl=document.getElementById("tbLogo");if(tl&&AVATAR_URI)tl.src=AVATAR_URI;
  const tbBadge=document.getElementById("tbBadge");
  if(tbBadge){try{tbBadge.textContent=new Date().toLocaleDateString(undefined,{weekday:"long",day:"numeric",month:"short"});}catch(e){}}
  scheduleRender();
  aiBootstrap();
  loadExports();
}
if(window.pywebview){init();}else{window.addEventListener("pywebviewready",init);}


</script>
</body>
</html>
"""