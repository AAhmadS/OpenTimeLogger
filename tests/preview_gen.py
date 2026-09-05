"""Preview harness (qa-harness): render ui.py in a browser with a mock
pywebview bridge backed by REAL backend outputs (MOCK LLM path).

Usage: python tests/preview_gen.py <outdir>
Writes <outdir>/preview.html. Serve it (python -m http.server) and
screenshot; all data is canned, nothing touches the repo.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    os.environ["OTL_APP_DIR"] = outdir
    import ai
    import aigraph
    import analytics
    import session_logger as sl
    from brand import AVATAR_DATA_URI
    from ui import UI_HTML

    ai.MOCK = True
    sessions = [
        {"id": "s1", "start": "2026-09-01T09:00:00", "end": "2026-09-01T11:00:00",
         "category": "Coding", "tag": "app", "sub_tag": "ui", "describe": "Built dashboard.",
         "notes": "Researched charts.\n\nHit a heatmap bug, half fixed.", "doc_seconds": 600},
        {"id": "s2", "start": "2026-09-02T09:30:00", "end": "2026-09-02T10:00:00",
         "category": "Coding", "tag": "app", "sub_tag": "ui", "describe": "Phase 1 QA.",
         "notes": "Finished heatmap fix.", "doc_seconds": 300},
        {"id": "s3", "start": "2026-09-02T15:00:00", "end": "2026-09-02T15:30:00",
         "category": "Mgmt", "tag": "meet", "sub_tag": "", "describe": "Sync.",
         "notes": "Discussed dashboard scope.", "doc_seconds": 0},
        {"id": "s4", "start": "2026-09-04T22:00:00", "end": None,
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "Nightly review.",
         "notes": "", "doc_seconds": 0},
    ]
    with open(os.path.join(outdir, "sessions.json"), "w", encoding="utf-8") as f:
        json.dump({"sessions": sessions}, f)
    # keyring-backed keys can't exist here; seed ref-only entries for render
    cfg = ai.load_config()
    cfg["keys"] = {"k1": {"provider": "openai", "label": "preview"}}
    cfg["agents"] = {"session-analyzer": {"provider": "openai", "key_id": "k1", "model": "gpt-4.1-mini"},
                     "task-builder": {"provider": "openai", "key_id": "k1", "model": "gpt-4.1-mini"},
                     "coach": {"provider": "openai", "key_id": "k1", "model": "gpt-5.2"}}
    ai.save_config(cfg)

    aigraph.run_session_analyzer_v2(cfg)
    aigraph.assign_tasks()
    aigraph.run_task_graph(cfg)
    aigraph.run_coach_refresh(cfg)
    aigraph.meter_call("coach", "openai", "gpt-4.1-mini", "x" * 4000, "y" * 400)
    aigraph.meter_call("session-analyzer", "openai", "gpt-4.1-mini", "x" * 8000, "y" * 800)

    api = sl.Api()
    canned = {
        "get_state": api.get_state(),
        "ai_get_config": api.ai_get_config(),
        "ai_agents": api.ai_agents(),
        "ai_providers": api.ai_providers(),
        "ai_pipeline_status": api.ai_pipeline_status(),
        "ai_get_tasks": api.ai_get_tasks(),
        "ai_get_reports": api.ai_get_reports(),
        "ai_get_insights": api.ai_get_insights(),
        "ai_get_coach": api.ai_get_coach(),
        "ai_spend_summary": api.ai_spend_summary(),
        "ai_estimate_cost": api.ai_estimate_cost(),
        "ai_graph_status": api.ai_graph_status(),
        "ai_asr_allowlist": api.ai_asr_allowlist(),
        "ai_models_cache": api.ai_models_cache(),
        "dashboard_30d": api.dashboard_stats("30d"),
    }
    html = UI_HTML.replace("const AVATAR_URI=null;",
                           'const AVATAR_URI="%s";' % AVATAR_DATA_URI)
    mock = ("<script>window.__CANNED=" + json.dumps(canned, ensure_ascii=False) +
            ";window.pywebview={api:new Proxy({},{get:(t,n)=>{" +
            "if(n==='ai_tick')return async()=>({ok:true});" +
            "if(n==='dashboard_stats')return async()=>window.__CANNED['dashboard_30d'];" +
            "if(n==='ai_list_models'){return async(p,task)=>({" +
            "ok:true,models:task==='asr'?[]:['m1','m2']," +
            "source:'seed',stale:true," +
            "note:task==='asr'?'No verified <4% WER models (see docs/asr-evidence; 2 suspended with reasons)':'Seed list — re-scan for live data'});}" +
            "if(n in window.__CANNED)return async()=>window.__CANNED[n];" +
            "return async()=>({error:'mock-missing:'+n});}})};</script>")
    html = html.replace("<head>", "<head>" + mock, 1)
    with open(os.path.join(outdir, "preview.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("preview written:", os.path.join(outdir, "preview.html"))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.environ.get("TEMP", "/tmp"), "otl-preview"))
