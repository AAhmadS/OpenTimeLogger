"""Agent-graph Phase 1 substrate (graph-builder-p1, T3 hybrid).

Local, LLM-free nodes: N2 Change Detector, N3 Part Splitter, N9 Evidence
Indexer, N22 Schema Verifier, N23 Run Log (reader), N21 Scheduler (minimal:
D1 backfill trigger + D3 debounce). Plus N5 Task Assigner (rules-first, LLM
assist) and N4 session-extraction in A-schema (explicit+implicit questions).

All stores live in ai.app_dir() (OTL_APP_DIR-overridable). No LLM call is
made here without going through ai.chat (BYOK-gated there).
"""

import hashlib
import json
import time
from datetime import datetime

TRACKED_FIELDS = ("start", "end", "category", "tag", "sub_tag", "describe",
                  "notes", "doc_seconds")
SNAPSHOT_NAME = "last_run_snapshot.json"
DEBOUNCE_SECONDS = 10 * 60
TICK_THROTTLE_SECONDS = 60

# ---- N22 schemas: type -> (required fields, list fields) ----
SCHEMAS = {
    "session_report": (("session_id", "topic", "questions", "steps_taken",
                        "numeric_metrics", "qualitative_results"),
                       ("questions", "steps_taken", "qualitative_results")),
    "task_membership": (("task_id", "session_ids", "confidence"),
                        ("session_ids",)),
    "challenge": (("id", "text", "severity", "status"), ()),
    "step": (("id", "phase_state_id", "goal", "part_ids", "challenge_ids"),
             ("part_ids", "challenge_ids")),
    "proposition": (("id", "step_id", "text", "confidence"), ()),
    "finding": (("id", "claim", "metric", "confounders_checked", "n",
                 "data_window"), ("confounders_checked",)),
    "style_point": (("point_id", "excerpt_ref", "ambiguity",
                     "improved_wording", "benefit"), ()),
}


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _app_dir():
    import ai
    return ai.app_dir()


def _read_json(name, default):
    p = _app_dir() / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _write_json(name, obj):
    p = _app_dir() / name
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


# ---------------- N2 — Change Detector ----------------

def _content_hash(session):
    h = hashlib.sha1()
    for f in TRACKED_FIELDS:
        h.update(("%s=%s;" % (f, session.get(f, ""))).encode("utf-8"))
    return h.hexdigest()[:16]


def _load_sessions():
    import ai
    return ai._load_sessions() if hasattr(ai, "_load_sessions") else []


def detect_changes():
    """Diff sessions.json against the last snapshot.

    Returns ChangeSet {added[], edited[], deleted[], materiality,
    hashes}. Materiality: 'structural' when any tracked field changed
    (or rows added/deleted), 'metadata' when only untracked fields differ.
    Does NOT advance the snapshot — call commit_snapshot() after a run.
    """
    import ai
    sessions = ai._load_sessions_all() if hasattr(ai, "_load_sessions_all") \
        else _sessions_all()
    snap = _read_json(SNAPSHOT_NAME, {})
    cur = {}
    for s in sessions:
        if isinstance(s, dict) and s.get("id"):
            cur[s["id"]] = _content_hash(s)
    added = [sid for sid in cur if sid not in snap]
    deleted = [sid for sid in snap if sid not in cur]
    edited = [sid for sid in cur if sid in snap and snap[sid] != cur[sid]]
    materiality = "structural" if (added or deleted or edited) else "none"
    return {"added": added, "edited": edited, "deleted": deleted,
            "materiality": materiality, "hashes": cur}


def _sessions_all():
    p = _app_dir() / "sessions.json"
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = raw.get("sessions", []) if isinstance(raw, dict) else []
    return [r for r in rows if isinstance(r, dict)]


def commit_snapshot(hashes=None):
    """Advance the snapshot after a successful run."""
    if hashes is None:
        cs = detect_changes()
        hashes = cs["hashes"]
    _write_json(SNAPSHOT_NAME, hashes)
    return {"ok": True, "sessions": len(hashes)}


# ---------------- N3 — Part Splitter ----------------

def split_parts(session):
    """Split one timelog into first-class parts (deterministic cues only).

    Cues: describe block vs notes paragraphs (blank-line separated).
    Duration is apportioned by text length; spans are logical order indexes
    (sessions carry no intra-session timestamps). part_id is stable for
    identical (session_id, index, text) triples.
    Returns parts[] {part_id, session_id, idx, kind, text, span,
    duration_min, excerpt_hash}.
    """
    sid = session.get("id", "")
    blocks = []
    if (session.get("describe") or "").strip():
        blocks.append(("describe", session["describe"].strip()))
    notes = (session.get("notes") or "").replace("\r\n", "\n")
    for para in notes.split("\n\n"):
        if para.strip():
            blocks.append(("notes", para.strip()))
    if not blocks:
        blocks.append(("empty", ""))
    try:
        total = max(0.0, (_parse_end(session) - _parse_start(session)).total_seconds() / 60.0)
    except Exception:
        total = 0.0
    weights = [max(1, len(t)) for _, t in blocks]
    wsum = sum(weights)
    parts = []
    for i, (kind, text) in enumerate(blocks):
        pid = hashlib.sha1(("%s|%d|%s" % (sid, i, text)).encode("utf-8")).hexdigest()[:12]
        parts.append({
            "part_id": pid, "session_id": sid, "idx": i, "kind": kind,
            "text": text[:2000], "span": "part-%d" % i,
            "duration_min": round(total * weights[i] / wsum, 2) if wsum else 0.0,
            "excerpt_hash": hashlib.sha1(text.encode("utf-8")).hexdigest()[:16],
        })
    return parts


def _parse_start(s):
    return _parse_dt(s.get("start"))


def _parse_end(s):
    return _parse_dt(s.get("end"))


def _parse_dt(v):
    if not isinstance(v, str):
        return None
    for f in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(v, f)
        except ValueError:
            continue
    return None


# ---------------- N9 — Evidence Index ----------------

def index_upsert(entity_key, refs):
    """Upsert provenance refs for an entity. refs: [{session_id, part_id,
    span, excerpt_hash}]."""
    idx = _read_json("evidence_index.json", {})
    idx[entity_key] = refs
    _write_json("evidence_index.json", idx)
    return {"ok": True}


def index_get(entity_key):
    return _read_json("evidence_index.json", {}).get(entity_key, [])


def challenge_timelogs(challenge):
    """Transitive B3 map: challenge -> which parts of which timelogs."""
    out = []
    for ref in challenge.get("evidence_refs", []):
        out.append({"session_id": ref.get("session_id"),
                    "part_id": ref.get("part_id"),
                    "span": ref.get("span")})
    return out


# ---------------- N22 — Schema Verifier ----------------

def verify(obj_type, obj):
    """Validate a node output against its schema + evidence discipline.

    Returns {ok} or {ok: False, errors[]}. Enforces: required fields,
    list-typed fields, and (for types carrying evidence_refs) that refs
    resolve to indexed entries.
    """
    schema = SCHEMAS.get(obj_type)
    if not schema:
        return {"ok": False, "errors": ["unknown type: %s" % obj_type]}
    required, lists = schema
    errors = []
    if not isinstance(obj, dict):
        return {"ok": False, "errors": ["not an object"]}
    for f in required:
        if f not in obj or obj[f] in (None, ""):
            errors.append("missing: %s" % f)
    for f in lists:
        if f in obj and not isinstance(obj[f], list):
            errors.append("not a list: %s" % f)
    if "evidence_refs" in obj:
        idx = _read_json("evidence_index.json", {})
        for r in obj.get("evidence_refs", []):
            key = "%s:%s" % (r.get("session_id"), r.get("part_id"))
            known = any(key == "%s:%s" % (x.get("session_id"), x.get("part_id"))
                        for refs in idx.values() for x in refs)
            if not known:
                errors.append("unresolved evidence ref: %s" % key)
                break
    if errors:
        return {"ok": False, "errors": errors}
    return {"ok": True}


# ---------------- N23 — Run Log (reader + metering sink) ----------------

def log_run(entry):
    """Append a run audit entry (trigger, nodes, calls, outcome)."""
    p = _app_dir() / "run_log.jsonl"
    entry = dict(entry)
    entry.setdefault("ts", _now())
    try:
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return {"ok": True}
    except OSError as e:
        return {"ok": False, "error": str(e)}


def read_runs(limit=50):
    p = _app_dir() / "run_log.jsonl"
    if not p.exists():
        return []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()[-limit:]
        return [json.loads(x) for x in lines if x.strip()]
    except (OSError, ValueError):
        return []


def meter_call(agent_id, provider, model, prompt_text, completion_text):
    """Token/cost metering sink (estimates labeled estimated: len//4).

    Called from ai.chat / ai.test_model on every provider call. Never
    raises — metering must not break analysis.
    """
    try:
        log_run({"kind": "llm_call", "agent_id": agent_id,
                 "provider": provider, "model": model,
                 "prompt_est": len(prompt_text or "") // 4,
                 "completion_est": len(completion_text or "") // 4})
    except Exception:
        pass


# ---------------- N5 — Task Assigner (rules-first) ----------------

def assign_tasks(session_reports=None):
    """Cluster sessions into tasks. Deterministic anchors first:
    same (category, tag, sub_tag) + temporal proximity (<=72h chain).
    Returns memberships[] {task_id, session_ids[], confidence} and writes
    tasks.json membership section (templates arrive in P2)."""
    sessions = _sessions_all()
    ended = [s for s in sessions
             if s.get("end") and s.get("kind") != "daily-doc-summary"]
    ended.sort(key=lambda s: s.get("start", ""))
    groups, current, cur_key = [], [], None
    for s in ended:
        key = (s.get("category") or "", s.get("tag") or "", s.get("sub_tag") or "")
        gap_ok = True
        if current:
            a, b = _parse_dt(current[-1].get("start")), _parse_dt(s.get("start"))
            gap_ok = bool(a and b and (b - a).total_seconds() <= 72 * 3600)
        if cur_key is None or (key == cur_key and gap_ok):
            current.append(s)
            cur_key = key
        else:
            groups.append((cur_key, current))
            current, cur_key = [s], key
    if current:
        groups.append((cur_key, current))
    memberships = []
    for (cat, tag, sub), rows in groups:
        base = "%s|%s|%s|%s" % (cat, tag, sub, rows[0].get("start", ""))
        tid = "task-" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:8]
        name = ": ".join(x for x in (cat, tag, sub) if x) or "Untitled"
        memberships.append({"task_id": tid, "name": name,
                            "session_ids": [r["id"] for r in rows],
                            "confidence": "rule"})
    store = _read_json("tasks.json", {})
    if not isinstance(store, dict):
        store = {}
    store["memberships"] = memberships
    store["updated_at"] = _now()
    _write_json("tasks.json", store)
    for m in memberships:
        index_upsert("membership:%s" % m["task_id"],
                     [{"session_id": sid, "part_id": "*", "span": "all",
                       "excerpt_hash": ""} for sid in m["session_ids"]])
    return {"ok": True, "tasks": len(memberships), "memberships": memberships}


# ---------------- N4 — Session Extractor (A-schema) ----------------

A_PROMPT = (
    "You are a session analyzer. From ONE work session log, produce JSON with "
    "exactly these keys: session_id (string, echo it), topic (string), "
    "questionsExplicit (array of strings: questions the user explicitly tried "
    "to answer), questionsImplicit (array of {text, confidence 0-1}: inherent "
    "questions the log implies but never states — mark inferred, never invent "
    "facts), stepsTaken (array of strings), numericMetrics (object: durations, "
    "counts, any numbers with units), qualitativeResults (array of strings). "
    "Return only JSON.")

A_SCHEMA = ("session_id", "topic", "questionsExplicit", "questionsImplicit",
            "stepsTaken", "numericMetrics", "qualitativeResults")


def run_session_analyzer_v2(cfg, session_ids=None):
    """Extract A-schema reports into session_reports.json (new store; the
    legacy ai_reports.json path is untouched)."""
    import ai
    sessions = [s for s in _sessions_all()
                if s.get("end") and s.get("kind") != "daily-doc-summary"]
    if session_ids is not None:
        sessions = [s for s in sessions if s.get("id") in set(session_ids)]
    store = _read_json("session_reports.json", {})
    reports = store.get("reports", []) if isinstance(store, dict) else []
    by_id = {r.get("session_id"): r for r in reports if isinstance(r, dict)}
    done, errors = 0, []
    for s in sessions:
        body = ai._session_text(s)
        text, ok = ai._agent_chat(cfg, "session-analyzer",
                                  A_PROMPT + "\n\nSession:\n" + body,
                                  [{"session_id": s.get("id"), "topic": "Mock",
                                    "questionsExplicit": [], "questionsImplicit": [],
                                    "stepsTaken": [], "numericMetrics": {},
                                    "qualitativeResults": []}][0:1])
        if not ok:
            errors.append(s.get("id"))
            continue
        data = ai._extract_json(text)
        if isinstance(data, list):
            data = data[0] if data else None
        if not isinstance(data, dict) or any(k not in data for k in A_SCHEMA):
            errors.append(s.get("id"))
            continue
        data["session_id"] = s.get("id")
        v = verify("session_report", {
            "session_id": data["session_id"], "topic": data.get("topic"),
            "questions": (data.get("questionsExplicit") or []) + [
                q.get("text") if isinstance(q, dict) else q
                for q in (data.get("questionsImplicit") or [])],
            "steps_taken": data.get("stepsTaken"),
            "numeric_metrics": data.get("numericMetrics"),
            "qualitative_results": data.get("qualitativeResults")})
        if not v.get("ok"):
            errors.append(s.get("id"))
            continue
        by_id[s.get("id")] = data
        parts = split_parts(s)
        index_upsert("report:%s" % s.get("id"),
                     [{"session_id": s.get("id"), "part_id": p["part_id"],
                       "span": p["span"], "excerpt_hash": p["excerpt_hash"]}
                      for p in parts])
        done += 1
    _write_json("session_reports.json",
                {"reports": list(by_id.values()), "generated_at": _now()})
    return {"ok": not errors, "done": done, "errors": errors}


# ---------------- N21 — Scheduler (minimal: D1 + D3) ----------------

_state = {"last_tick": 0.0}


def _scheduler_state():
    return _read_json("scheduler.json", {})


def _save_scheduler_state(st):
    _write_json("scheduler.json", st)


def tick(force=False):
    """Cheap periodic check (throttled): starts D1 backfill once when keys
    are provisioned, queues D3 refinement debounced. Spawns daemon threads;
    never blocks the caller. Returns {due[], started[]}."""
    now = time.time()
    if not force and now - _state["last_tick"] < TICK_THROTTLE_SECONDS:
        return {"ok": True, "throttled": True, "due": [], "started": []}
    _state["last_tick"] = now
    import ai
    st = _scheduler_state()
    due, started = [], []
    cfg = ai.load_config()
    has_keys = bool(cfg.get("keys"))
    # D1: keys provisioned + never backfilled -> full-history backfill due
    if has_keys and not st.get("backfill_done") and not st.get("backfill_running"):
        due.append("backfill")
    # D3: structural changes pending longer than debounce
    try:
        cs = detect_changes()
    except Exception:
        cs = {"materiality": "none", "added": [], "edited": [], "deleted": []}
    if cs["materiality"] == "structural":
        pending_since = st.get("changes_pending_since") or now
        st["changes_pending_since"] = pending_since
        if now - pending_since >= DEBOUNCE_SECONDS:
            due.append("refine")
    else:
        st.pop("changes_pending_since", None)
    _save_scheduler_state(st)
    import threading
    for job in due:
        t = threading.Thread(target=_run_job, args=(job,), daemon=True)
        t.start()
        started.append(job)
    return {"ok": True, "throttled": False, "due": due, "started": started}


def _run_job(job):
    import ai
    st = _scheduler_state()
    if job == "backfill":
        if st.get("backfill_running"):
            return
        st["backfill_running"] = True
        _save_scheduler_state(st)
        log_run({"kind": "run_start", "trigger": "D1-keys-provisioned",
                 "job": "backfill"})
        try:
            cfg = ai.load_config()
            r1 = run_session_analyzer_v2(cfg)
            r2 = assign_tasks()
            try:
                cs = detect_changes()
                commit_snapshot(cs["hashes"])
            except Exception:
                pass
            log_run({"kind": "run_done", "trigger": "D1-keys-provisioned",
                     "job": "backfill", "analyzer": r1, "assigner": r2})
            st["backfill_done"] = True
        except Exception as e:
            log_run({"kind": "run_error", "trigger": "D1-keys-provisioned",
                     "job": "backfill", "error": str(e)})
        finally:
            st["backfill_running"] = False
            _save_scheduler_state(st)
    elif job == "refine":
        st.pop("changes_pending_since", None)
        _save_scheduler_state(st)
        log_run({"kind": "run_start", "trigger": "D3-session-change",
                 "job": "refine"})
        try:
            cfg = ai.load_config()
            cs = detect_changes()
            ids = set(cs["added"]) | set(cs["edited"])
            r1 = run_session_analyzer_v2(cfg, session_ids=ids or None)
            r2 = assign_tasks()
            commit_snapshot(detect_changes()["hashes"])
            log_run({"kind": "run_done", "trigger": "D3-session-change",
                     "job": "refine", "analyzer": r1, "assigner": r2})
        except Exception as e:
            log_run({"kind": "run_error", "trigger": "D3-session-change",
                     "job": "refine", "error": str(e)})


def graph_status():
    """UI-facing status: scheduler state + store counts + last runs."""
    st = _scheduler_state()
    reports = _read_json("session_reports.json", {})
    tasks = _read_json("tasks.json", {})
    return {"ok": True, "scheduler": st,
            "reports": len(reports.get("reports", [])) if isinstance(reports, dict) else 0,
            "memberships": len(tasks.get("memberships", [])) if isinstance(tasks, dict) else 0,
            "recent_runs": read_runs(10)}
