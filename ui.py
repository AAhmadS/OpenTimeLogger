UI_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Interval</title>
<style>
:root{
  --bg1:#0c111a; --bg2:#161e2d;
  --glass:rgba(255,255,255,.055);
  --glass-hi:rgba(255,255,255,.085);
  --stroke:rgba(255,255,255,.12);
  --stroke-hi:rgba(255,255,255,.20);
  --text:#eef2f7; --muted:#8d9aaf; --muted2:#6e7d94;
  --accent:#5ec27f; --accent-dim:#3a8658; --accent-glow:rgba(94,194,127,.20);
  --info:#67b3ff; --warn:#ffb86b; --danger:#ff6b6b;
  --radius:16px; --radius-lg:20px;
  --select-bg:#1a2534; --select-bg-hi:#1e2e42;
  --scroll-thumb:rgba(255,255,255,.16);
  --scroll-thumb-hi:rgba(255,255,255,.26);
}
[data-theme="light"]{
  --bg1:#f4f6f8; --bg2:#e9edf1;
  --glass:rgba(255,255,255,.68);
  --glass-hi:rgba(255,255,255,.82);
  --stroke:rgba(0,0,0,.07);
  --stroke-hi:rgba(0,0,0,.11);
  --text:#1a1f26; --muted:#6b7a90; --muted2:#8a9ab0;
  --accent:#3d8a5c; --accent-dim:#2f6b47; --accent-glow:rgba(61,138,92,.14);
  --info:#3a86d8; --warn:#c47a2a; --danger:#d94f4f;
  --select-bg:#ffffff; --select-bg-hi:#f1f4f8;
  --scroll-thumb:rgba(0,0,0,.14);
  --scroll-thumb-hi:rgba(0,0,0,.22);
}
*{box-sizing:border-box}
[hidden]{display:none !important}
html,body{height:100vh;height:100dvh;margin:0;overflow:hidden;color-scheme:dark}
html[data-theme="light"]{color-scheme:light}
html[data-theme="light"] body{
  background:
    radial-gradient(1100px 750px at 88% -12%, rgba(94,194,127,.10), transparent 62%),
    radial-gradient(950px 700px at -12% 108%, rgba(103,179,255,.08), transparent 60%),
    radial-gradient(700px 500px at 44% 62%, rgba(255,184,107,.05), transparent 60%),
    linear-gradient(160deg,var(--bg1),var(--bg2));
}
html[data-theme="light"] .glass{
  background:var(--glass);
  backdrop-filter:blur(22px) saturate(145%);
  -webkit-backdrop-filter:blur(22px) saturate(145%);
  border:1px solid var(--stroke);
  box-shadow:0 8px 32px rgba(0,0,0,.08), inset 0 1px 0 rgba(255,255,255,.7);
}
html[data-theme="light"] .brand-img{
  border:1px solid rgba(0,0,0,.08);
  box-shadow:0 2px 10px rgba(0,0,0,.06);
}
html[data-theme="light"] .input{color-scheme:light}
html[data-theme="light"] .ac-menu,
html[data-theme="light"] .cselect-menu{background:#ffffff;border-color:rgba(0,0,0,.08);box-shadow:0 16px 36px rgba(0,0,0,.12)}
html[data-theme="light"] .toast{background:rgba(255,255,255,.92);border-color:rgba(0,0,0,.08);color:var(--text)}
body{
  font-family:"Segoe UI Variable","Segoe UI",system-ui,-apple-system,sans-serif;
  color:var(--text);
  background:
    radial-gradient(1100px 750px at 88% -12%, rgba(94,194,127,.22), transparent 62%),
    radial-gradient(950px 700px at -12% 108%, rgba(103,179,255,.18), transparent 60%),
    radial-gradient(700px 500px at 44% 62%, rgba(255,184,107,.07), transparent 60%),
    linear-gradient(160deg,var(--bg1),var(--bg2));
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
/* scrollbars — dark, inside bounds */
*{scrollbar-width:thin;scrollbar-color:var(--scroll-thumb) transparent}
*::-webkit-scrollbar{width:8px;height:8px}
*::-webkit-scrollbar-thumb{background:var(--scroll-thumb);border-radius:999px}
*::-webkit-scrollbar-thumb:hover{background:var(--scroll-thumb-hi)}
*::-webkit-scrollbar-track{background:transparent}
.glass{
  background:var(--glass);
  backdrop-filter:blur(22px) saturate(145%);
  -webkit-backdrop-filter:blur(22px) saturate(145%);
  border:1px solid var(--stroke);
  border-radius:var(--radius-lg);
  box-shadow:0 8px 32px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.06);
}
.app{display:grid;grid-template-columns:280px 1fr;gap:16px;height:100vh;height:100dvh;padding:16px;overflow:hidden}
/* ------- side menu (fixed scroller) ------- */
aside{
  display:flex;flex-direction:column;min-height:0;overflow:hidden;
}
.brand{display:flex;align-items:center;gap:11px;padding:16px 16px 12px;flex:none;position:relative}
.brand-img{width:30px;height:30px;border-radius:50%;flex:none;object-fit:contain;padding:4px;border:1px solid rgba(255,255,255,.14);background:radial-gradient(circle at 35% 30%, rgba(94,194,127,.92), rgba(46,110,71,.92));box-shadow:0 3px 12px rgba(0,0,0,.28)}
[data-theme="light"] .brand-img{background:radial-gradient(circle at 35% 30%, rgba(94,194,127,.14), rgba(255,255,255,.9));border-color:rgba(0,0,0,.06)}
.brand-title{font-weight:700;letter-spacing:.15px;font-size:15px;line-height:1}
.brand-sub{font-size:11px;color:var(--muted);letter-spacing:.12px;margin-top:2px;font-weight:500}
.theme-toggle{margin-left:auto;width:30px;height:30px;border-radius:10px;display:grid;place-items:center;background:rgba(255,255,255,.06);border:1px solid var(--stroke);cursor:pointer;transition:.16s;color:var(--muted);flex:none}
.theme-toggle:hover{background:var(--glass-hi);color:var(--text);border-color:var(--stroke-hi)}
.theme-toggle svg{pointer-events:none}
[data-theme="light"] .theme-toggle{background:rgba(0,0,0,.04);border-color:rgba(0,0,0,.07)}
.segmented{display:flex;gap:4px;margin:6px 12px 6px;padding:4px;background:rgba(255,255,255,.045);border:1px solid var(--stroke);border-radius:13px;flex:none}
.seg{flex:1;padding:7px 0;border:0;border-radius:10px;background:transparent;color:var(--muted);font-family:inherit;font-size:12.5px;font-weight:620;cursor:pointer;transition:.16s}
.seg:hover{color:var(--text);background:rgba(255,255,255,.04)}
.seg.active{background:rgba(255,255,255,.11);color:var(--text);box-shadow:0 1px 8px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.10)}
.side-section{padding:6px 14px 2px;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted2);flex:none}
.list{flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:8px;margin:0 8px 8px;scrollbar-gutter:stable;overscroll-behavior:contain;content-visibility:auto;contain:layout paint;will-change:scroll-position}
.list-inner{display:flex;flex-direction:column;gap:2px}
.si{display:flex;align-items:center;gap:10px;padding:11px 12px;border-radius:13px;cursor:pointer;border:1px solid transparent;transition:.14s;contain:layout paint}
.si:hover{background:rgba(255,255,255,.045);border-color:rgba(255,255,255,.06)}
.si.sel{background:var(--glass-hi);border-color:var(--stroke-hi);box-shadow:0 3px 14px rgba(0,0,0,.22)}
.dot{flex:none;width:10px;height:10px;border-radius:50%;box-shadow:0 0 0 4px rgba(255,255,255,.05)}
.dot.big{width:13px;height:13px;box-shadow:0 0 0 5px rgba(255,255,255,.05)}
.si-b{min-width:0;flex:1}
.si-t{font-size:13.2px;font-weight:620;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.2}
.si-s{font-size:11.8px;color:var(--muted);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:6px}
.si-meta{font-size:11px;color:var(--muted2)}
.live{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--accent);flex:none;animation:pulse 1.6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(94,194,127,.45)}50%{opacity:.55;box-shadow:0 0 0 5px rgba(94,194,127,0)}}
.empty{color:var(--muted);font-size:12.8px;text-align:center;padding:22px 10px;line-height:1.5}
.exports-list{display:flex;flex-direction:column;gap:6px;padding:0 0 6px}
.export-item{display:flex;align-items:center;gap:10px;padding:10px 11px;border-radius:12px;cursor:pointer;border:1px solid transparent;background:rgba(255,255,255,.03);transition:.14s;position:relative}
.export-item:hover{background:rgba(255,255,255,.07);border-color:var(--stroke)}
.export-ico{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;background:rgba(94,194,127,.14);border:1px solid rgba(94,194,127,.20);flex:none}
.export-ico svg{opacity:.9}
.export-name{font-size:12.8px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.export-sub{font-size:11.4px;color:var(--muted);margin-top:2px}
.export-size{font-size:11px;color:var(--muted2);margin-left:auto;flex:none}
.export-del{flex:none;width:26px;height:26px;border-radius:8px;display:grid;place-items:center;background:transparent;border:1px solid transparent;color:var(--muted2);cursor:pointer;transition:.14s;margin-left:6px}
.export-del:hover{background:rgba(255,107,107,.14);border-color:rgba(255,107,107,.28);color:#ffb4b4}
.export-del svg{pointer-events:none}
.side-actions{padding:10px 12px 12px;display:flex;flex-direction:column;gap:8px;flex:none;border-top:1px solid rgba(255,255,255,.06);margin-top:auto}
/* ------- buttons / inputs (dropdowns fixed) ------- */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:13px;padding:11px 16px;font-family:inherit;font-size:13.8px;font-weight:620;cursor:pointer;transition:.16s;color:var(--text);background:rgba(255,255,255,.08);box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}
.btn:hover{background:rgba(255,255,255,.12);transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn.primary{background:linear-gradient(180deg,rgba(94,194,127,.88),rgba(53,128,82,.92));box-shadow:0 6px 18px rgba(46,110,71,.32), inset 0 1px 0 rgba(255,255,255,.22)}
.btn.primary:hover{filter:brightness(1.06)}
.btn.warn{background:linear-gradient(180deg,rgba(255,184,107,.78),rgba(197,116,52,.88));box-shadow:0 6px 18px rgba(197,116,52,.28), inset 0 1px 0 rgba(255,255,255,.20)}
.btn.danger{background:rgba(255,107,107,.14);border:1px solid rgba(255,107,107,.32)}
.btn.danger:hover{background:rgba(255,107,107,.22)}
.btn.ghost{background:transparent;border:1px solid var(--stroke)}
.btn.ghost:hover{background:rgba(255,255,255,.06);border-color:var(--stroke-hi)}
.btn.full{width:100%}
.btn.small{padding:8px 12px;font-size:13px;border-radius:11px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{padding:7px 13px;border:1px solid var(--stroke);border-radius:11px;background:rgba(255,255,255,.035);color:var(--muted);font-family:inherit;font-size:12.8px;font-weight:600;cursor:pointer;transition:.14s}
.chip:hover{color:var(--text);background:rgba(255,255,255,.06)}
.chip.active{background:rgba(255,255,255,.12);color:var(--text);border-color:var(--stroke-hi)}
.input{width:100%;background:rgba(255,255,255,.05);border:1px solid var(--stroke);border-radius:12px;padding:11px 13px;color:var(--text);font-family:inherit;font-size:14px;outline:none;transition:.15s;color-scheme:dark}
.input:focus{border-color:rgba(94,194,127,.45);box-shadow:0 0 0 3px var(--accent-glow);background:rgba(255,255,255,.07)}
.input::placeholder{color:var(--muted2)}
/* native select — dark glass, no white dropdown */
select.input{
  background:var(--select-bg);
  border-color:var(--stroke);
  appearance:auto;
  cursor:pointer;
}
select.input:hover{background:var(--select-bg-hi)}
select.input option, select.input optgroup{
  background:var(--select-bg);
  color:var(--text);
}
.ta{resize:vertical;line-height:1.5}
label{display:flex;flex-direction:column;gap:6px;font-size:11.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
label .input, label .ac-wrap .input{font-weight:400;text-transform:none;letter-spacing:0;font-size:14px}
/* custom autocomplete */
.ac-wrap{position:relative}
.ac-menu{
  position:absolute;top:calc(100% + 8px);left:0;right:0;
  background:#1a2534;border:1px solid rgba(255,255,255,.12);border-radius:13px;
  box-shadow:0 16px 36px rgba(0,0,0,.45), 0 2px 10px rgba(0,0,0,.25);
  padding:6px;max-height:220px;overflow-y:auto;z-index:30;display:none;
}
.ac-menu.open{display:block}
.ac-opt{padding:10px 12px;border-radius:10px;cursor:pointer;font-size:13.5px;color:var(--text);transition:.12s}
.ac-opt:hover{background:rgba(255,255,255,.07)}
.ac-opt.active{background:rgba(94,194,127,.16)}
.ac-empty{padding:10px 12px;color:var(--muted);font-size:13px;text-align:center}
/* custom select (for export filters — dark glass, replaces white native dropdown) */
.cselect{position:relative}
.cselect-trigger{
  width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;
  background:var(--select-bg);border:1px solid var(--stroke);border-radius:12px;
  padding:11px 12px 11px 13px;color:var(--text);font-family:inherit;font-size:14px;
  cursor:pointer;transition:.15s;text-align:left;
}
.cselect-trigger:hover{background:var(--select-bg-hi);border-color:var(--stroke-hi)}
.cselect-trigger:focus{outline:none;border-color:rgba(94,194,127,.45);box-shadow:0 0 0 3px var(--accent-glow)}
.cselect-trigger .ph{color:var(--muted2)}
.cselect-arrow{flex:none;opacity:.6;transition:.15s}
.cselect.open .cselect-arrow{transform:rotate(180deg)}
.cselect-menu{
  position:absolute;top:calc(100% + 8px);left:0;right:0;
  background:#1a2534;border:1px solid rgba(255,255,255,.13);border-radius:13px;
  box-shadow:0 16px 36px rgba(0,0,0,.45);padding:6px;max-height:220px;overflow-y:auto;z-index:30;display:none;
}
.cselect.open .cselect-menu{display:block}
.copt{padding:10px 12px;border-radius:10px;cursor:pointer;font-size:13.5px;color:var(--text);transition:.12s;display:flex;align-items:center;justify-content:space-between}
.copt:hover{background:rgba(255,255,255,.07)}
.copt.active{background:rgba(94,194,127,.16);color:#dff3e6}
/* ------- main (fixed scroller inside glass) ------- */
main{
  display:flex;flex-direction:column;min-height:0;overflow:hidden;
}
.main-scroll{
  flex:1;min-height:0;overflow-y:auto;overflow-x:hidden;padding:22px;scrollbar-gutter:stable;overscroll-behavior:contain;will-change:scroll-position;
}
.cards{display:flex;flex-direction:column;gap:16px;max-width:640px;margin:0 auto;width:100%;padding-top:6px}
.hero{border-color:rgba(94,194,127,.28);box-shadow:0 8px 32px rgba(0,0,0,.32), 0 0 0 1px rgba(94,194,127,.10), inset 0 1px 0 rgba(255,255,255,.06)}
.hero .orb{width:54px;height:54px;border-radius:50%;margin:0 auto 14px;background:radial-gradient(circle at 35% 30%, rgba(94,194,127,.95), rgba(46,110,71,.9));box-shadow:0 0 0 10px rgba(94,194,127,.07), 0 0 24px rgba(94,194,127,.32), inset 0 -5px 12px rgba(0,0,0,.22);animation:breathe 3s ease-in-out infinite}
@keyframes breathe{0%,100%{box-shadow:0 0 0 10px rgba(94,194,127,.07), 0 0 24px rgba(94,194,127,.32)}50%{box-shadow:0 0 0 16px rgba(94,194,127,.03), 0 0 38px rgba(94,194,127,.45)}}
.btn.big{padding:13px 18px;font-size:14.5px}
.card{padding:20px}
.card-h{display:flex;align-items:center;gap:10px;margin-bottom:4px}
.card-t{font-size:15.5px;font-weight:700;letter-spacing:.1px}
.muted{color:var(--muted);font-size:13px;line-height:1.55;margin:6px 0 14px}
.muted.small{font-size:12.5px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px}
@media (max-width: 560px){ .grid3{grid-template-columns:1fr} .grid2{grid-template-columns:1fr} }
.row{display:flex;gap:10px;margin-top:14px;align-items:center;flex-wrap:wrap}
.row .grow{flex:1;min-width:160px}
.sub{padding:18px;margin-bottom:0}
.dhead{display:flex;align-items:center;gap:13px;margin-bottom:18px}
.dh-b{min-width:0}
.dh-t{font-size:18.5px;font-weight:700;letter-spacing:.1px}
.dh-s{color:var(--muted);font-size:13px;margin-top:3px;line-height:1.45}
/* toasts */
#toasts{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;gap:8px;z-index:50;align-items:center;pointer-events:none}
.toast{padding:11px 16px;border-radius:13px;background:rgba(18,24,35,.88);border:1px solid var(--stroke-hi);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);color:var(--text);font-size:13.2px;box-shadow:0 10px 28px rgba(0,0,0,.38);opacity:1;transition:.28s;pointer-events:auto}
.toast.err{border-color:rgba(255,107,107,.45);color:#ffd9d9}
.toast.out{opacity:0;transform:translateY(8px)}
.fade{animation:fade .22s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none)}
/* invisible focus design — when typing, chrome recedes */
body.focus-mode aside{opacity:.55;filter:saturate(.85);transition:.4s}
body.focus-mode .brand, body.focus-mode .segmented{opacity:.7}
body.focus-mode .side-actions{opacity:.6}
.input:focus, .ta:focus, .cselect-trigger:focus{box-shadow:0 0 0 3px var(--accent-glow), 0 2px 12px rgba(0,0,0,.06)}
/* reduce motion for focus */
@media (prefers-reduced-motion: reduce){ .orb{animation:none !important} }
</style>
<script>try{const k="interval-theme";const s=localStorage.getItem(k);const m=window.matchMedia&&matchMedia("(prefers-color-scheme: light)").matches;const t=s||(m?"light":"dark");document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>
</head>
<body>
<div class="app">
  <aside class="glass">
    <div class="brand">
      <img id="brandImg" class="brand-img" alt="Interval">
      <div>
        <div class="brand-title">Interval</div>
        <div class="brand-sub">time, accounted for</div>
      </div>
      <button class="theme-toggle" id="themeBtn" title="Toggle light / dark" aria-label="Toggle theme">
        <svg class="icon-sun" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
        <svg class="icon-moon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" style="display:none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </div>
    <div class="segmented" id="seg">
      <button class="seg active" data-tab="active">Active</button>
      <button class="seg" data-tab="archive">Archive</button>
      <button class="seg" data-tab="export">Export</button>
    </div>
    <div class="list" id="sideList"><div class="list-inner" id="sideListInner"></div></div>
    <div class="side-actions">
      <button class="btn primary full" id="newBtn">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        Start session
      </button>
      <button class="btn ghost full" id="pastBtn">Log a finished session</button>
    </div>
  </aside>
  <main id="main" class="glass"><div class="main-scroll" id="mainScroll"></div></main>
</div>
<datalist id="dlCats"></datalist>
<datalist id="dlTags"></datalist>
<div id="toasts"></div>
<script>
let state={sessions:[]};
let tab="active";
let sel=null;
let nsMode="now";
let deMode="now";
let docAccum={};
let activeSid=null;
let lastKey=0;
let docTick=null;
let exportsCache=[];
let renderQueued=false;
const AVATAR_URI=null;
const DUR_OPTS=["Today","Last 3 days","Last 7 days","Last 12 days","Last 30 days","All time"];
// theme: light beside dark, persisted, respects OS, glass in both — safe for pywebview (no localStorage on about:blank)
(function(){
  const key="interval-theme";
  let saved=null;
  try{ saved=localStorage.getItem(key); }catch(e){}
  let prefersLight=false;
  try{ prefersLight=window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches; }catch(e){}
  const initial=saved || (prefersLight?"light":"dark");
  try{ document.documentElement.setAttribute("data-theme", initial); }catch(e){}
  const updateIcon=()=>{
    try{
      const cur=document.documentElement.getAttribute("data-theme");
      const sun=document.querySelector(".icon-sun"), moon=document.querySelector(".icon-moon");
      if(sun&&moon){ sun.style.display=cur==="dark"?"block":"none"; moon.style.display=cur==="light"?"block":"none"; }
    }catch(e){}
  };
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", updateIcon);
  else updateIcon();
  window.__setTheme=(next)=>{
    try{ document.documentElement.setAttribute("data-theme", next); }catch(e){}
    try{ localStorage.setItem(key, next); }catch(e){}
    updateIcon();
  };
  try{
    const mql=window.matchMedia("(prefers-color-scheme: light)");
    const handler=(e)=>{
      let curSaved=null; try{ curSaved=localStorage.getItem(key); }catch(ex){}
      if(!curSaved){
        try{ document.documentElement.setAttribute("data-theme", e.matches?"light":"dark"); }catch(ex){}
        updateIcon();
      }
    };
    if(mql){
      if(mql.addEventListener) mql.addEventListener("change", handler);
      else if(mql.addListener) mql.addListener(handler);
    }
  }catch(e){}
})();

const $=(s,root=document)=>root.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function nowLocal(){const d=new Date();const p=n=>String(n).padStart(2,"0");return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate())+"T"+p(d.getHours())+":"+p(d.getMinutes());}
function localInput(iso){return iso?iso.slice(0,16):"";}
function fmt(iso){if(!iso)return "—";const d=new Date(iso);return d.toLocaleString(undefined,{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"});}
function fmtT(iso){if(!iso)return "";const d=new Date(iso);return d.toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"});}
function mins(a,b){if(!a||!b)return null;return Math.max(0,Math.round((new Date(b)-new Date(a))/60000));}
function catColor(c){let h=140;const s=String(c||"");if(s){h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;}return `hsl(${h} 68% 62%)`;}
function fmtDay(iso){if(!iso)return "";const d=new Date(iso+"T00:00:00");return d.toLocaleDateString(undefined,{day:"2-digit",month:"short"});}
function docMins(s){return Math.round((s.summary_seconds??s.doc_seconds??0)/60);}
function sessionName(s){
  if(s.kind==="daily-doc-summary")return "Documentation · "+fmtDay(s.summary_of);
  if(!s.category)return "Untitled session";
  if(s.tag)return s.category+": "+s.tag+(s.sub_tag?" + "+s.sub_tag:"");
  return s.category;
}
function toast(msg,type="ok"){const t=document.createElement("div");t.className="toast "+type;t.textContent=msg;document.getElementById("toasts").appendChild(t);setTimeout(()=>t.classList.add("out"),2400);setTimeout(()=>t.remove(),2800);}
const sessions=()=>state.sessions||[];
const byId=id=>sessions().find(s=>s.id===id);

// --- performance: memoized derived data ---
let _catsCache=null,_catsKey="",_tagsCache=null,_tagsKey="";
function getCats(){
  const key=sessions().length+"|"+sessions().map(s=>s.category).join("|");
  if(_catsKey===key) return _catsCache;
  _catsCache=[...new Set(sessions().map(x=>x.category).filter(Boolean))].sort();
  _catsKey=key; return _catsCache;
}
function getTags(){
  const key=sessions().length+"|"+sessions().map(s=>s.tag).join("|");
  if(_tagsKey===key) return _tagsCache;
  _tagsCache=[...new Set(sessions().map(x=>x.tag).filter(Boolean))].sort();
  _tagsKey=key; return _tagsCache;
}

// --- render scheduling (avoid thrash) ---
function scheduleRender(){
  if(renderQueued) return;
  renderQueued=true;
  requestAnimationFrame(()=>{renderQueued=false;render();});
}

function render(){
  document.querySelectorAll("#seg .seg").forEach(b=>b.classList.toggle("active",b.dataset.tab===tab));
  const cats=getCats(), tags=getTags();
  document.getElementById("dlCats").innerHTML=cats.map(c=>`<option value="${esc(c)}">`).join("");
  document.getElementById("dlTags").innerHTML=tags.map(t=>`<option value="${esc(t)}">`).join("");
  if(sel&&!byId(sel))sel=null;
  renderSide();
  renderMain();
}

async function loadExports(){
  try{
    if(!window.pywebview||!pywebview.api.list_exports) return;
    const r=await pywebview.api.list_exports();
    exportsCache = (r&&r.exports)||[];
    if(tab==="export") renderSide();
  }catch(e){}
}

function renderSide(){
  const inner=document.getElementById("sideListInner");
  if(!inner) return;
  if(tab==="export"){
    if(!exportsCache.length){
      inner.innerHTML=`<div class="empty">No exports yet.<br><span style="font-size:12px;color:var(--muted2)">Pick filters and export — your .xlsx files will appear here.</span></div>`;
      return;
    }
    inner.innerHTML = `<div class="side-section">Recent exports — click to open, trash to delete</div>
      <div class="exports-list">` + exportsCache.map(ex=>`
        <div class="export-item" data-path="${esc(ex.path)}" title="${esc(ex.name)}">
          <div class="export-ico">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 14h6"/><path d="M9 18h6"/><path d="M9 10h2"/></svg>
          </div>
          <div style="min-width:0;flex:1">
            <div class="export-name">${esc(ex.name)}</div>
            <div class="export-sub">${esc(ex.mtime_label)} · click to open</div>
          </div>
          <div class="export-size">${esc(ex.size_kb)} KB</div>
          <button class="export-del" data-del="${esc(ex.path)}" title="Delete export" aria-label="Delete">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>
          </button>
        </div>
      `).join("") + `</div>`;
    return;
  }
  const isActive=tab==="active";
  // already sorted desc in state; for active show earliest running first, archive newest first
  let items=sessions().filter(s=>isActive?!s.end:s.end);
  if(isActive) items=items.slice().sort((a,b)=>a.start.localeCompare(b.start));
  else items=items.slice().sort((a,b)=>b.start.localeCompare(a.start));
  if(!items.length){
    inner.innerHTML=`<div class="empty">${isActive?"No active sessions.":"Nothing archived yet."}</div>`;
    return;
  }
  // build HTML string (fast) — keep glass blur off items for perf (only container has blur)
  inner.innerHTML=items.map(s=>{
    const title=sessionName(s);
    const sub=s.kind==="daily-doc-summary"
      ?("end-of-day summary · "+docMins(s)+" min")
      :(!s.end?("since "+fmtT(s.start)):(fmt(s.start)+" → "+fmtT(s.end)));
    const meta=s.kind==="daily-doc-summary" ? `<span class="si-meta">auto</span>` : (!s.end?`<span class="live"></span>`:"");
    return `<div class="si ${sel===s.id?"sel":""}" data-id="${s.id}">
      <span class="dot" style="background:${catColor(s.category)}"></span>
      <div class="si-b">
        <div class="si-t">${esc(title)}</div>
        <div class="si-s">${meta}${esc(sub)}</div>
      </div>
    </div>`;
  }).join("");
}

// delegated click for side list (perf: one listener)
document.getElementById("sideList").addEventListener("click", async (e)=>{
  const delBtn=e.target.closest(".export-del");
  if(delBtn){
    e.stopPropagation();
    const p=delBtn.dataset.del;
    if(!confirm("Delete this export file permanently?\\n\\n"+p.split(/[\\/]/).pop())) return;
    try{
      const r=await pywebview.api.delete_export(p);
      if(r&&r.error) return toast(r.error,"err");
      toast("Export deleted");
      exportsCache=exportsCache.filter(x=>x.path!==p);
      renderSide();
    }catch(err){ toast(String(err),"err"); }
    return;
  }
  const exItem=e.target.closest(".export-item");
  if(exItem){
    const p=exItem.dataset.path;
    try{
      const r=await pywebview.api.open_export(p);
      if(r&&r.error) toast(r.error,"err");
      else toast("Opening "+p.split(/[\\/]/).pop());
    }catch(err){ toast(String(err),"err"); }
    return;
  }
  const si=e.target.closest(".si");
  if(si&&si.dataset.id){ sel=si.dataset.id; scheduleRender(); }
});

function renderMain(){
  const sc=document.getElementById("mainScroll");
  if(tab==="export"){activeSid=null;sc.innerHTML=exportViewHtml();bindExport();loadExports();return;}
  const s=sel?byId(sel):null;
  if(!s){activeSid=null;sc.innerHTML=newViewHtml();bindNew();return;}
  sc.innerHTML=detailHtml(s);bindDetail(s);watchDoc(s);
}

function newViewHtml(){
  return `<div class="cards">
    <div class="card glass fade hero">
      <div class="orb"></div>
      <div class="card-h"><span class="dot" style="background:var(--accent)"></span><div class="card-t">Start a session</div></div>
      <p class="muted">Logs a start time. Begin right now, or tell it when the session actually started.</p>
      <div class="chips" id="nsChips" style="margin-bottom:12px">
        <button class="chip ${nsMode==="now"?"active":""}" data-v="now">Right now</button>
        <button class="chip ${nsMode==="at"?"active":""}" data-v="at">At time</button>
      </div>
      <input type="datetime-local" id="nsAt" class="input" value="${nowLocal()}" ${nsMode==="at"?"":"hidden"}>
      <p class="muted small" style="margin:16px 0 8px">Name it now — optional. You can add or change it later.</p>
      <div class="grid3">
        <label>Category<div class="ac-wrap"><input list="dlCats" id="nsCat" class="input" placeholder="e.g. Research" autocomplete="off"><div class="ac-menu" id="ac-nsCat"></div></div></label>
        <label>Tag<div class="ac-wrap"><input list="dlTags" id="nsTag" class="input" placeholder="e.g. Paper text" autocomplete="off"><div class="ac-menu" id="ac-nsTag"></div></div></label>
        <label>Sub-tag<input id="nsSub" class="input" placeholder="optional"></label>
      </div>
      <label>Describe (what you did)<textarea id="nsDesc" class="input ta" rows="2" placeholder="What did you work on?"></textarea></label>
      <div class="row"><button class="btn primary big full" id="nsGo">Start session</button></div>
    </div>
    <div class="card glass fade">
      <div class="card-h"><span class="dot" style="background:var(--info)"></span><div class="card-t">Log a finished session</div></div>
      <p class="muted">Backfill a session that already ended — give it a start and an end time.</p>
      <div class="grid2">
        <label>Started<input type="datetime-local" id="psStart" class="input" value="${nowLocal()}"></label>
        <label>Ended<input type="datetime-local" id="psEnd" class="input" value="${nowLocal()}"></label>
      </div>
      <div class="row"><button class="btn primary" id="psGo">Create finished session</button></div>
    </div>
  </div>`;
}

function exportViewHtml(){
  const pool=sessions().filter(s=>s.end&&!s.kind);
  const cats=[...new Set(pool.map(s=>s.category).filter(Boolean))].sort();
  const tags=[...new Set(pool.map(s=>s.tag).filter(Boolean))].sort();
  const cOpts=["All categories",...cats], tOpts=["All tags",...tags];
  // custom select markup (dark glass, no white dropdown)
  const mkSelect=(id, opts, val)=>`
    <div class="cselect" data-id="${id}" data-value="${esc(val)}">
      <button type="button" class="cselect-trigger" aria-haspopup="listbox">
        <span>${esc(val)}</span>
        <svg class="cselect-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      <div class="cselect-menu" role="listbox">
        ${opts.map(o=>`<div class="copt ${o===val?"active":""}" data-v="${esc(o)}"><span>${esc(o)}</span>${o===val?'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 13l4 4L19 7"/></svg>':''}</div>`).join("")}
      </div>
    </div>`;
  return `<div class="cards">
    <div class="card glass fade">
      <div class="card-h"><span class="dot" style="background:var(--accent)"></span><div class="card-t">Export to Excel</div></div>
      <p class="muted">Filter finished sessions by category, tag and date range. Exports now include 4 sheets: <b>Sessions</b> (with Doc min), <b>By Category</b> + <b>By Tag</b> (session + documentation per tag) and <b>Documentation daily</b> (per-day breakdown). Documentation time is counted per its original category/tag, so you can see <b>documentation</b> contributions inside the tag sheets — not as a separate category row. When a single category is selected, the Category column is dropped.</p>
      <div class="grid3">
        <label>Category${mkSelect("exCat", cOpts, "All categories")}</label>
        <label>Tag${mkSelect("exTag", tOpts, "All tags")}</label>
        <label>Range${mkSelect("exDur", DUR_OPTS, "Last 12 days")}</label>
      </div>
      <label style="margin-top:6px">Export name (optional)<input id="exName" class="input" placeholder="Leave empty for auto: category_tag_YYYYMMDD_YYYYMMDD"></label>
      <p class="muted small" id="exPreview" style="margin:6px 0 0;opacity:.9"></p>
      <p class="muted" id="exCount"></p>
      <div class="row">
        <button class="btn primary" id="exGo">Export to Excel</button>
        <button class="btn ghost small" id="exRefresh">Refresh list</button>
      </div>
      <p class="muted small" style="margin-top:10px">Recent exports are listed in the sidebar — click to open, trash to delete. Auto name is <code>category_tag_YYYYMMDD_YYYYMMDD.xlsx</code> (dates without hour: start &amp; end of the chosen range).</p>
    </div>
  </div>`;
}

function bindCustomSelects(root, onChange){
  root.querySelectorAll(".cselect").forEach(cs=>{
    const trig=cs.querySelector(".cselect-trigger");
    const menu=cs.querySelector(".cselect-menu");
    trig.addEventListener("click", (e)=>{
      e.stopPropagation();
      const open=cs.classList.contains("open");
      document.querySelectorAll(".cselect.open").forEach(o=>{ if(o!==cs) o.classList.remove("open"); });
      cs.classList.toggle("open", !open);
    });
    menu.querySelectorAll(".copt").forEach(opt=>{
      opt.addEventListener("click", ()=>{
        const v=opt.dataset.v;
        cs.dataset.value=v;
        trig.querySelector("span").textContent=v;
        menu.querySelectorAll(".copt").forEach(o=>{
          const is=o.dataset.v===v;
          o.classList.toggle("active", is);
          const chk=o.querySelector("svg");
          if(chk) chk.style.display=is?"block":"none";
          if(is && !chk){
            o.insertAdjacentHTML("beforeend", '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 13l4 4L19 7"/></svg>');
          } else if(!is && chk){
            // keep svg but hide via active class already
          }
        });
        // ensure checkmark exists for active
        menu.querySelectorAll(".copt").forEach(o=>{
          const has=o.querySelector("svg");
          if(o.classList.contains("active") && !has){
            o.insertAdjacentHTML("beforeend", '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 13l4 4L19 7"/></svg>');
          }
          if(!o.classList.contains("active") && has){
            has.remove();
          }
        });
        cs.classList.remove("open");
        if(onChange) onChange();
      });
    });
  });
  // close on outside click
  document.addEventListener("click", ()=> document.querySelectorAll(".cselect.open").forEach(c=>c.classList.remove("open")), {once:false});
}
function getCSelectValue(id){ const el=document.querySelector(`.cselect[data-id="${id}"]`); return el?el.dataset.value:""; }

function bindExport(){
  const sanitize=s=>{
    s=String(s||"").trim();
    if(!s || s==="All categories" || s==="All tags") return "all";
    s=s.replace(/[\\/*?:"<>|]/g,"-").replace(/\s+/g,"_").replace(/_+/g,"_").replace(/^[_-]+|[_-]+$/g,"");
    return s.slice(0,48)||"all";
  };
  const autoName=(cat,tag,dur)=>{
    const catS=sanitize(cat), tagS=sanitize(tag);
    const today=new Date(); const end=today.toISOString().slice(0,10).replace(/-/g,"");
    const modeMap={"Today":0,"Last 3 days":3,"Last 7 days":7,"Last 12 days":12,"Last 30 days":30,"All time":Infinity};
    let start;
    if(dur==="All time"){
      const pool=sessions().filter(s=>s.end&&!s.kind);
      const tagged=pool.filter(s=> (cat==="All categories"||s.category===cat) && (tag==="All tags"||s.tag===tag));
      // filtered by duration as well? for preview, mimic backend: All time => earliest of filtered rows
      const rows=tagged; // before duration cutoff, but for All time cutoff is -Infinity, so all
      if(rows.length){
        const mins=rows.map(r=> new Date(r.start)).sort((a,b)=>a-b)[0];
        start=mins.toISOString().slice(0,10).replace(/-/g,"");
      } else start=end;
    } else if(dur==="Today"){
      start=end;
    } else {
      const n=modeMap[dur]||0;
      const d=new Date(today.getTime()-n*86400000);
      start=d.toISOString().slice(0,10).replace(/-/g,"");
    }
    return `${catS}_${tagS}_${start}_${end}.xlsx`;
  };
  const refresh=()=>{
    const cat=getCSelectValue("exCat")||"All categories", tag=getCSelectValue("exTag")||"All tags", dur=getCSelectValue("exDur")||"Last 12 days";
    const now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
    const days={["Today"]:0,["Last 3 days"]:3,["Last 7 days"]:7,["Last 12 days"]:12,["Last 30 days"]:30,["All time"]:Infinity};
    const cutoff=dur==="Today"?today:new Date(now.getTime()-days[dur]*86400000);
    const n=sessions().filter(s=>{
      if(!s.end||s.kind) return false;
      if(cat!=="All categories"&&s.category!==cat) return false;
      if(tag!=="All tags"&&s.tag!==tag) return false;
      return new Date(s.start)>=cutoff;
    }).length;
    const el=document.getElementById("exCount");
    if(el) el.textContent=n?`${n} session(s) will be exported.  ·  4 sheets: Sessions + By Category + By Tag + Documentation daily.`:"No sessions match this filter.";
    const preview=document.getElementById("exPreview");
    const exNameEl=document.getElementById("exName");
    const custom=(exNameEl ? exNameEl.value : "") .trim();
    const auto=autoName(cat,tag,dur);
    if(preview){
      if(custom) preview.textContent=`Will save as: ${sanitize(custom).replace(/\.xlsx$/i,"")}.xlsx  (auto would be ${auto})`;
      else preview.textContent=`Auto name: ${auto}`;
    }
  };
  bindCustomSelects(document.getElementById("mainScroll"), refresh);
  refresh();
  const exNameEl2=document.getElementById("exName"); if(exNameEl2) exNameEl2.addEventListener("input", refresh);
  const exRefreshEl=document.getElementById("exRefresh"); if(exRefreshEl) exRefreshEl.addEventListener("click", loadExports);
  document.getElementById("exGo").addEventListener("click",async()=>{
    const cat=getCSelectValue("exCat")||"All categories", tag=getCSelectValue("exTag")||"All tags", dur=getCSelectValue("exDur")||"Last 12 days";
    const exNameEl3=document.getElementById("exName");
    const custom=(exNameEl3 ? exNameEl3.value : "").trim();
    const r=await pywebview.api.export_excel(cat,tag,dur, custom||null);
    if(r.error) return toast(r.error,"err");
    const name=String(r.path).split(/[\\/]/).pop();
    toast(`Exported ${r.count} session(s) — ${name} (4 sheets)`);
    loadExports();
    // auto-open the freshly exported file
    try{ await pywebview.api.open_export(r.path); }catch(e){}
  });
}

function bindAutocomplete(inputId, menuId, sourceFn){
  const inp=document.getElementById(inputId);
  const menu=document.getElementById(menuId);
  if(!inp||!menu) return;
  function renderMenu(){
    const q=inp.value.trim().toLowerCase();
    const src=sourceFn().filter(v=>!q||v.toLowerCase().includes(q)).slice(0,8);
    if(!src.length){ menu.innerHTML=`<div class="ac-empty">No matches</div>`; menu.classList.add("open"); return; }
    menu.innerHTML=src.map(v=>`<div class="ac-opt" data-v="${esc(v)}">${esc(v)}</div>`).join("");
    menu.classList.add("open");
    menu.querySelectorAll(".ac-opt").forEach(o=>o.addEventListener("click",()=>{
      inp.value=o.dataset.v;
      menu.classList.remove("open");
      inp.focus();
    }));
  }
  inp.addEventListener("focus", renderMenu);
  inp.addEventListener("input", renderMenu);
  inp.addEventListener("blur", ()=> setTimeout(()=>menu.classList.remove("open"),140));
}

function detailHtml(s){
  const running=!s.end;
  const dur=running?null:mins(s.start,s.end);
  const endBlock=running?`
    <div class="card sub glass">
      <p class="muted small" style="margin-bottom:10px">End this session now, or set when it actually finished.</p>
      <div class="chips" id="deChips" style="margin-bottom:12px">
        <button class="chip ${deMode==="now"?"active":""}" data-v="now">Right now</button>
        <button class="chip ${deMode==="at"?"active":""}" data-v="at">At time</button>
      </div>
      <div class="row">
        <input type="datetime-local" id="deAt" class="input grow" value="${nowLocal()}" ${deMode==="at"?"":"hidden"}>
        <button class="btn warn" id="deGo">End session</button>
      </div>
    </div>`:`
    <div class="card sub glass">
      <div class="grid2" style="margin-bottom:0">
        <label>Started<input type="datetime-local" id="edStart" class="input" value="${localInput(s.start)}"></label>
        <label>Ended<input type="datetime-local" id="edEnd" class="input" value="${localInput(s.end)}"></label>
      </div>
    </div>`;
  const headSub=s.kind==="daily-doc-summary"
    ?'Automatic end-of-day documentation summary · '+docMins(s)+' min of documentation across the day'
    :running?'<span class="live"></span> Running since '+fmt(s.start):'Finished '+fmt(s.start)+" → "+fmt(s.end)+(dur!=null?"  ·  "+dur+" min":"");
  return `<div class="dhead">
      <span class="dot big" style="background:${catColor(s.category)}"></span>
      <div class="dh-b">
        <div class="dh-t">${esc(sessionName(s))}</div>
        <div class="dh-s">${headSub}</div>
      </div>
    </div>
    ${endBlock}
    <div class="card sub glass" style="margin-top:14px">
      <div class="grid3">
        <label>Category<div class="ac-wrap"><input list="dlCats" id="edCat" class="input" value="${esc(s.category)}" autocomplete="off"><div class="ac-menu" id="ac-edCat"></div></div></label>
        <label>Tag<div class="ac-wrap"><input list="dlTags" id="edTag" class="input" value="${esc(s.tag)}" autocomplete="off"><div class="ac-menu" id="ac-edTag"></div></div></label>
        <label>Sub-tag<input list="dlTags" id="edSub" class="input" value="${esc(s.sub_tag)}"></label>
      </div>
      <label style="margin-bottom:12px">Describe (what you did)<textarea id="edDesc" class="input ta" rows="4">${esc(s.describe)}</textarea></label>
      <label>Notes<textarea id="edNotes" class="input ta" rows="2">${esc(s.notes)}</textarea></label>
      <div class="row">
        <button class="btn primary" id="edSave">${running?"Save details":"Save changes"}</button>
        ${running?"":`<button class="btn ghost" id="edReopen">Reopen</button>`}
        <button class="btn danger" id="edDel">Delete</button>
      </div>
    </div>`;
}

function bindNew(){
  $("#nsChips").querySelectorAll(".chip").forEach(c=>c.addEventListener("click",()=>{
    nsMode=c.dataset.v;
    $("#nsChips").querySelectorAll(".chip").forEach(x=>x.classList.toggle("active",x===c));
    $("#nsAt").hidden=nsMode!=="at";
  }));
  bindAutocomplete("nsCat","ac-nsCat",getCats);
  bindAutocomplete("nsTag","ac-nsTag",getTags);
  $("#nsGo").addEventListener("click",async()=>{
    const payload=nsMode==="now"?{type:"now"}:{type:"at",value:$("#nsAt").value};
    const data={category:$("#nsCat").value,tag:$("#nsTag").value,sub_tag:$("#nsSub").value,describe:$("#nsDesc").value};
    const r=await pywebview.api.start_session(payload,data);
    if(r.error) return toast(r.error,"err");
    state=r;sel=null;scheduleRender();toast("Session started.");
  });
  $("#psGo").addEventListener("click",async()=>{
    const r=await pywebview.api.log_past_session({start:$("#psStart").value,end:$("#psEnd").value});
    if(r.error) return toast(r.error,"err");
    state=r;sel=null;scheduleRender();toast("Finished session logged.");
  });
}

function bindDetail(s){
  bindAutocomplete("edCat","ac-edCat",getCats);
  bindAutocomplete("edTag","ac-edTag",getTags);
  if(s.end){
    $("#edSave").addEventListener("click",saveDetail);
    $("#edReopen").addEventListener("click",async()=>{
      const r=await pywebview.api.reopen_session(s.id);
      if(r.error) toast(r.error,"err");else{state=r;sel=s.id;scheduleRender();toast("Session reopened — it is active again.");}
    });
    $("#edDel").addEventListener("click",del);
  }else{
    $("#deChips").querySelectorAll(".chip").forEach(c=>c.addEventListener("click",()=>{
      deMode=c.dataset.v;
      $("#deChips").querySelectorAll(".chip").forEach(x=>x.classList.toggle("active",x===c));
      $("#deAt").hidden=deMode!=="at";
    }));
    $("#deGo").addEventListener("click",async()=>{
      const payload=deMode==="now"?{type:"now"}:{type:"at",value:$("#deAt").value};
      const r=await pywebview.api.end_session(s.id,payload);
      if(r.error) toast(r.error,"err");else{state=r;sel=s.id;tab="archive";scheduleRender();toast("Session ended. Fill the details to finish.");}
    });
    $("#edSave").addEventListener("click",saveDetail);
    $("#edDel").addEventListener("click",del);
  }
}

async function saveDetail(){
  const s=byId(sel);if(!s) return;
  const fields={category:$("#edCat").value,tag:$("#edTag").value,sub_tag:$("#edSub").value,describe:$("#edDesc").value,notes:$("#edNotes").value,doc_seconds:Math.round(docAccum[sel]||0)};
  if(s.end){fields.start=$("#edStart").value;fields.end=$("#edEnd").value;}
  const r=await pywebview.api.update_session(s.id,fields);
  if(r.error) toast(r.error,"err");else{state=r;scheduleRender();toast("Changes saved.");}
}

async function del(){
  if(!confirm("Delete this session permanently?")) return;
  const r=await pywebview.api.delete_session(sel);
  if(r.error) toast(r.error,"err");else{delete docAccum[sel];state=r;sel=null;scheduleRender();toast("Session deleted.");}
}

function watchDoc(s){
  activeSid=s.id;
  if(!docTick){
    docTick=setInterval(()=>{
      const id=activeSid;if(!id) return;
      const cur=byId(id);if(!cur) return;
      if(cur.kind==="daily-doc-summary") return;
      if(!document.hasFocus()) return;
      // throttle: only count if page visible
      if(document.visibilityState!=="visible") return;
      const ae=document.activeElement;
      const focused=ae&&["edCat","edTag","edSub","edDesc","edNotes"].indexOf(ae.id)>=0;
      if(focused||(Date.now()-lastKey)<45000) docAccum[id]=(docAccum[id]||0)+1;
    },1000);
  }
  document.querySelectorAll("#edCat,#edTag,#edSub,#edDesc,#edNotes").forEach(el=>{
    el.addEventListener("input",()=>{lastKey=Date.now();});
  });
}

document.getElementById("seg").addEventListener("click",e=>{
  const b=e.target.closest(".seg");if(!b) return;
  tab=b.dataset.tab;sel=null;scheduleRender();
  if(tab==="export") loadExports();
});
document.getElementById("newBtn").addEventListener("click",()=>{tab="active";sel=null;scheduleRender();});
document.getElementById("pastBtn").addEventListener("click",()=>{tab="active";sel=null;scheduleRender();document.getElementById("mainScroll").scrollTop=0;});
const themeBtnEl=document.getElementById("themeBtn"); if(themeBtnEl) themeBtnEl.addEventListener("click",()=>{
  const cur=document.documentElement.getAttribute("data-theme");
  const next=cur==="dark"?"light":"dark";
  try{ document.documentElement.setAttribute("data-theme", next); }catch(e){}
  try{ localStorage.setItem("interval-theme", next); }catch(e){}
  const sun=document.querySelector(".icon-sun"), moon=document.querySelector(".icon-moon");
  if(sun&&moon){ sun.style.display=next==="dark"?"block":"none"; moon.style.display=next==="light"?"block":"none"; }
});
// invisible focus: chrome recedes when you're writing
const mainScrollEl=document.getElementById("mainScroll");
mainScrollEl.addEventListener("focusin", e=>{
  if(e.target.matches && e.target.matches("textarea, input")){
    document.body.classList.add("focus-mode");
  }
});
mainScrollEl.addEventListener("focusout", e=>{
  setTimeout(()=>{
    const ae=document.activeElement;
    if(!ae || !mainScrollEl.contains(ae) || !ae.matches("textarea, input")){
      document.body.classList.remove("focus-mode");
    }
  }, 80);
});

async function init(){state=await pywebview.api.get_state();scheduleRender();
  const bi=document.getElementById("brandImg");if(bi&&AVATAR_URI) bi.src=AVATAR_URI;
  loadExports();
}
if(window.pywebview){init();}else{window.addEventListener("pywebviewready",init);}
</script>
</body>
</html>
"""