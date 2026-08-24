UI_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session Logger</title>
<style>
:root{
  --bg1:#0d131d; --bg2:#18212e;
  --glass:rgba(255,255,255,.065);
  --glass-hi:rgba(255,255,255,.11);
  --stroke:rgba(255,255,255,.16);
  --stroke-hi:rgba(255,255,255,.28);
  --text:#eef2f7; --muted:#98a4b5;
  --accent:#5ec27f; --accent-dim:#3d8a5c;
  --info:#67b3ff; --warn:#ffb36b; --danger:#ff6b6b;
  --radius:20px;
}
*{box-sizing:border-box}
[hidden]{display:none !important}
html,body{height:100%;margin:0}
body{
  font-family:"Segoe UI Variable","Segoe UI",system-ui,-apple-system,sans-serif;
  color:var(--text);
  background:
    radial-gradient(1100px 750px at 88% -12%, rgba(94,194,127,.30), transparent 62%),
    radial-gradient(950px 700px at -12% 108%, rgba(103,179,255,.24), transparent 60%),
    radial-gradient(720px 520px at 46% 60%, rgba(255,179,107,.10), transparent 60%),
    linear-gradient(160deg,var(--bg1),var(--bg2));
  overflow:hidden;
  -webkit-font-smoothing:antialiased;
}
.glass{
  background:var(--glass);
  backdrop-filter:blur(24px) saturate(150%);
  -webkit-backdrop-filter:blur(24px) saturate(150%);
  border:1px solid var(--stroke);
  border-radius:var(--radius);
  box-shadow:0 10px 36px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.08);
}
.app{display:grid;grid-template-columns:286px 1fr;gap:16px;height:100vh;padding:16px}

/* ------- side menu ------- */
aside{display:flex;flex-direction:column;overflow:hidden}
.brand{display:flex;align-items:center;gap:10px;padding:16px 16px 10px}
.brand-img{width:32px;height:32px;border-radius:50%;flex:none;object-fit:cover;border:1px solid rgba(255,255,255,.25);background:radial-gradient(circle at 35% 30%, rgba(94,194,127,.95), rgba(61,138,92,.95));box-shadow:0 4px 14px rgba(0,0,0,.4)}
.brand svg{flex:none}
.brand span{font-weight:650;letter-spacing:.2px}
.segmented{display:flex;gap:4px;margin:8px 14px 4px;padding:4px;background:rgba(255,255,255,.05);border:1px solid var(--stroke);border-radius:14px}
.seg{flex:1;padding:8px 0;border:0;border-radius:11px;background:transparent;color:var(--muted);font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;transition:.18s}
.seg:hover{color:var(--text)}
.seg.active{background:rgba(255,255,255,.14);color:var(--text);box-shadow:0 2px 10px rgba(0,0,0,.25), inset 0 1px 0 rgba(255,255,255,.12)}
.list{flex:1;overflow-y:auto;padding:8px;margin:4px 8px 8px}
.list::-webkit-scrollbar{width:8px}
.list::-webkit-scrollbar-thumb{background:rgba(255,255,255,.14);border-radius:8px}
.si{display:flex;align-items:center;gap:10px;padding:11px 12px;border-radius:14px;cursor:pointer;border:1px solid transparent;transition:.16s}
.si:hover{background:rgba(255,255,255,.06)}
.si.sel{background:var(--glass-hi);border-color:var(--stroke-hi);box-shadow:0 4px 16px rgba(0,0,0,.28)}
.dot{flex:none;width:10px;height:10px;border-radius:50%;box-shadow:0 0 0 4px rgba(255,255,255,.05)}
.dot.big{width:14px;height:14px;box-shadow:0 0 0 6px rgba(255,255,255,.05)}
.si-b{min-width:0;flex:1}
.si-t{font-size:13.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.si-s{font-size:12px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.live{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--accent);margin-right:6px;vertical-align:1px;animation:pulse 1.6s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(94,194,127,.5)}50%{opacity:.55;box-shadow:0 0 0 5px rgba(94,194,127,0)}}
.empty{color:var(--muted);font-size:13px;text-align:center;padding:26px 10px}
.side-actions{padding:8px 14px 14px;display:flex;flex-direction:column;gap:8px}

/* ------- buttons / inputs ------- */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:14px;padding:12px 16px;font-family:inherit;font-size:14px;font-weight:600;cursor:pointer;transition:.16s;color:var(--text);background:rgba(255,255,255,.09);box-shadow:inset 0 1px 0 rgba(255,255,255,.10)}
.btn:hover{background:rgba(255,255,255,.15);transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn.primary{background:linear-gradient(180deg,rgba(94,194,127,.85),rgba(61,138,92,.9));box-shadow:0 6px 18px rgba(61,138,92,.35), inset 0 1px 0 rgba(255,255,255,.25)}
.btn.primary:hover{filter:brightness(1.08)}
.btn.warn{background:linear-gradient(180deg,rgba(255,179,107,.75),rgba(214,124,58,.85));box-shadow:0 6px 18px rgba(214,124,58,.3), inset 0 1px 0 rgba(255,255,255,.22)}
.btn.danger{background:rgba(255,107,107,.16);border:1px solid rgba(255,107,107,.4)}
.btn.danger:hover{background:rgba(255,107,107,.28)}
.btn.ghost{background:transparent;border:1px solid var(--stroke)}
.btn.full{width:100%}
.chips{display:flex;gap:6px}
.chip{padding:8px 14px;border:1px solid var(--stroke);border-radius:12px;background:rgba(255,255,255,.04);color:var(--muted);font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;transition:.16s}
.chip:hover{color:var(--text)}
.chip.active{background:rgba(255,255,255,.14);color:var(--text);border-color:var(--stroke-hi)}
.input{width:100%;background:rgba(255,255,255,.055);border:1px solid var(--stroke);border-radius:12px;padding:11px 13px;color:var(--text);font-family:inherit;font-size:14px;outline:none;transition:.15s;color-scheme:dark}
.input:focus{border-color:var(--stroke-hi);box-shadow:0 0 0 3px rgba(94,194,127,.18)}
.ta{resize:vertical;line-height:1.45}
label{display:flex;flex-direction:column;gap:6px;font-size:12px;font-weight:600;color:var(--muted)}
label .input{font-weight:400}

/* ------- main ------- */
main{overflow-y:auto;padding:22px}
main::-webkit-scrollbar{width:8px}
main::-webkit-scrollbar-thumb{background:rgba(255,255,255,.14);border-radius:8px}
.cards{display:flex;flex-direction:column;gap:16px;max-width:640px;margin:0 auto;padding-top:8px}
.card{padding:20px}
.card-h{display:flex;align-items:center;gap:10px;margin-bottom:4px}
.card-t{font-size:16px;font-weight:650}
.muted{color:var(--muted);font-size:13px;line-height:1.5;margin:6px 0 14px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px}
.row{display:flex;gap:10px;margin-top:14px;align-items:center}
.row .grow{flex:1}
.sub{padding:18px;margin-bottom:0}
.dhead{display:flex;align-items:center;gap:14px;margin-bottom:18px}
.dh-b{min-width:0}
.dh-t{font-size:19px;font-weight:650}
.dh-s{color:var(--muted);font-size:13.5px;margin-top:3px}

/* ------- toasts ------- */
#toasts{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;gap:8px;z-index:50;align-items:center}
.toast{padding:11px 18px;border-radius:14px;background:rgba(20,26,36,.72);border:1px solid var(--stroke-hi);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);color:var(--text);font-size:13.5px;box-shadow:0 10px 30px rgba(0,0,0,.4);opacity:1;transition:.3s}
.toast.err{border-color:rgba(255,107,107,.55);color:#ffd9d9}
.toast.out{opacity:0;transform:translateY(8px)}
.fade{animation:fade .22s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
</style>
</head>
<body>
<div class="app">
  <aside class="glass">
    <div class="brand">
      <img id="brandImg" class="brand-img" alt="Session Logger">
      <span>Session Logger</span>
    </div>
    <div class="segmented" id="seg">
      <button class="seg active" data-tab="active">Active</button>
      <button class="seg" data-tab="archive">Archive</button>
    </div>
    <div class="list" id="sideList"></div>
    <div class="side-actions">
      <button class="btn primary full" id="newBtn">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        Start session
      </button>
      <button class="btn ghost full" id="pastBtn">Log a finished session</button>
    </div>
  </aside>
  <main id="main" class="glass"></main>
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
const AVATAR_URI=null;

const $=(s,root=document)=>root.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function nowLocal(){const d=new Date();const p=n=>String(n).padStart(2,"0");return d.getFullYear()+"-"+p(d.getMonth()+1)+"-"+p(d.getDate())+"T"+p(d.getHours())+":"+p(d.getMinutes());}
function localInput(iso){return iso?iso.slice(0,16):"";}
function fmt(iso){if(!iso)return "—";const d=new Date(iso);return d.toLocaleString(undefined,{day:"2-digit",month:"short",hour:"2-digit",minute:"2-digit"});}
function fmtT(iso){if(!iso)return "";const d=new Date(iso);return d.toLocaleTimeString(undefined,{hour:"2-digit",minute:"2-digit"});}
function mins(a,b){if(!a||!b)return null;return Math.max(0,Math.round((new Date(b)-new Date(a))/60000));}
function catColor(c){let h=140;const s=String(c||"");if(s){h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))%360;}return `hsl(${h} 72% 66%)`;}
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

function render(){
  document.querySelectorAll("#seg .seg").forEach(b=>b.classList.toggle("active",b.dataset.tab===tab));
  const cats=[...new Set(sessions().map(x=>x.category).filter(Boolean))];
  const tags=[...new Set(sessions().map(x=>x.tag).filter(Boolean))];
  document.getElementById("dlCats").innerHTML=cats.map(c=>`<option value="${esc(c)}">`).join("");
  document.getElementById("dlTags").innerHTML=tags.map(t=>`<option value="${esc(t)}">`).join("");
  if(sel&&!byId(sel))sel=null;
  renderSide();
  renderMain();
}

function renderSide(){
  const list=document.getElementById("sideList");
  const isActive=tab==="active";
  const items=sessions().filter(s=>isActive?!s.end:s.end);
  items.sort((a,b)=>isActive?a.start.localeCompare(b.start):b.start.localeCompare(a.start));
  list.innerHTML=items.map(s=>{
    const title=sessionName(s);
    const sub=s.kind==="daily-doc-summary"
      ?("end-of-day summary · "+docMins(s)+" min")
      :(!s.end?("since "+fmtT(s.start)):(fmt(s.start)+" → "+fmtT(s.end)));
    return `<div class="si ${sel===s.id?"sel":""}" data-id="${s.id}">
      <span class="dot" style="background:${catColor(s.category)}"></span>
      <div class="si-b">
        <div class="si-t">${esc(title)}</div>
        <div class="si-s">${s.end?'':'<span class="live"></span>'}${esc(sub)}</div>
      </div>
    </div>`;
  }).join("")||`<div class="empty">${isActive?"No active sessions.":"Nothing archived yet."}</div>`;
  list.querySelectorAll(".si").forEach(el=>el.addEventListener("click",()=>{sel=el.dataset.id;render();}));
}

function renderMain(){
  const main=document.getElementById("main");
  const s=sel?byId(sel):null;
  if(!s){activeSid=null;main.innerHTML=newViewHtml();bindNew();return;}
  main.innerHTML=detailHtml(s);bindDetail(s);watchDoc(s);
}

function newViewHtml(){
  return `<div class="cards">
    <div class="card glass fade">
      <div class="card-h"><span class="dot" style="background:var(--accent)"></span><div class="card-t">Start a session</div></div>
      <p class="muted">Logs a start time. Begin right now, or tell it when the session actually started.</p>
      <div class="chips" id="nsChips" style="margin-bottom:12px">
        <button class="chip ${nsMode==="now"?"active":""}" data-v="now">Right now</button>
        <button class="chip ${nsMode==="at"?"active":""}" data-v="at">At time</button>
      </div>
      <input type="datetime-local" id="nsAt" class="input" value="${nowLocal()}" ${nsMode==="at"?"":"hidden"}>
      <p class="muted" style="margin:16px 0 8px">Name it now — optional. You can add or change it later.</p>
      <div class="grid3">
        <label>Category<input list="dlCats" id="nsCat" class="input"></label>
        <label>Tag<input list="dlTags" id="nsTag" class="input"></label>
        <label>Sub-tag<input id="nsSub" class="input"></label>
      </div>
      <label>Describe (what you did)<textarea id="nsDesc" class="input ta" rows="2"></textarea></label>
      <div class="row"><button class="btn primary" id="nsGo">Start session</button></div>
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

function detailHtml(s){
  const running=!s.end;
  const dur=running?null:mins(s.start,s.end);
  const endBlock=running?`
    <div class="card sub glass">
      <p class="muted" style="margin-bottom:10px">End this session now, or set when it actually finished.</p>
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
        <label>Category<input list="dlCats" id="edCat" class="input" value="${esc(s.category)}"></label>
        <label>Tag<input list="dlTags" id="edTag" class="input" value="${esc(s.tag)}"></label>
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
  $("#nsGo").addEventListener("click",async()=>{
    const payload=nsMode==="now"?{type:"now"}:{type:"at",value:$("#nsAt").value};
    const data={category:$("#nsCat").value,tag:$("#nsTag").value,sub_tag:$("#nsSub").value,describe:$("#nsDesc").value};
    const r=await pywebview.api.start_session(payload,data);
    if(r.error)return toast(r.error,"err");
    state=r;sel=null;render();toast("Session started.");
  });
  $("#psGo").addEventListener("click",async()=>{
    const r=await pywebview.api.log_past_session({start:$("#psStart").value,end:$("#psEnd").value});
    if(r.error)return toast(r.error,"err");
    state=r;sel=null;render();toast("Finished session logged.");
  });
}

function bindDetail(s){
  if(s.end){
    $("#edSave").addEventListener("click",saveDetail);
    $("#edReopen").addEventListener("click",async()=>{
      const r=await pywebview.api.reopen_session(s.id);
      if(r.error)toast(r.error,"err");else{state=r;sel=s.id;render();toast("Session reopened — it is active again.");}
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
      if(r.error)toast(r.error,"err");else{state=r;sel=s.id;render();toast("Session ended. Fill the details to finish.");}
    });
    $("#edSave").addEventListener("click",saveDetail);
    $("#edDel").addEventListener("click",del);
  }
}

async function saveDetail(){
  const s=byId(sel);if(!s)return;
  const fields={category:$("#edCat").value,tag:$("#edTag").value,sub_tag:$("#edSub").value,describe:$("#edDesc").value,notes:$("#edNotes").value,doc_seconds:Math.round(docAccum[sel]||0)};
  if(s.end){fields.start=$("#edStart").value;fields.end=$("#edEnd").value;}
  const r=await pywebview.api.update_session(s.id,fields);
  if(r.error)toast(r.error,"err");else{state=r;render();toast("Changes saved.");}
}

async function del(){
  if(!confirm("Delete this session permanently?"))return;
  const r=await pywebview.api.delete_session(sel);
  if(r.error)toast(r.error,"err");else{delete docAccum[sel];state=r;sel=null;render();toast("Session deleted.");}
}

function watchDoc(s){
  activeSid=s.id;
  if(!docTick){
    docTick=setInterval(()=>{
      const id=activeSid;if(!id)return;
      const cur=byId(id);if(!cur)return;
      if(cur.kind==="daily-doc-summary")return;
      if(!document.hasFocus())return;
      const ae=document.activeElement;
      const focused=ae&&["edCat","edTag","edSub","edDesc","edNotes"].indexOf(ae.id)>=0;
      if(focused||(Date.now()-lastKey)<45000)docAccum[id]=(docAccum[id]||0)+1;
    },1000);
  }
  document.querySelectorAll("#edCat,#edTag,#edSub,#edDesc,#edNotes").forEach(el=>{
    el.addEventListener("input",()=>{lastKey=Date.now();});
  });
}

document.getElementById("seg").addEventListener("click",e=>{
  const b=e.target.closest(".seg");if(!b)return;
  tab=b.dataset.tab;sel=null;render();
});
document.getElementById("newBtn").addEventListener("click",()=>{sel=null;render();});
document.getElementById("pastBtn").addEventListener("click",()=>{sel=null;render();});

async function init(){state=await pywebview.api.get_state();render();
  const bi=document.getElementById("brandImg");if(bi&&AVATAR_URI)bi.src=AVATAR_URI;
}
if(window.pywebview){init();}else{window.addEventListener("pywebviewready",init);}
</script>
</body>
</html>
"""
