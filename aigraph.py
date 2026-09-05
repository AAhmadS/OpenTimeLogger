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
    # D2 end-of-day (locked 23:30): the designated nightly job — fires even
    # inside quiet hours (23:00-07:00); D3 debounce still queues for 07:00.
    today = datetime.now().strftime("%Y-%m-%d")
    now_hm = datetime.now().strftime("%H:%M")
    if now_hm >= "23:30" and st.get("last_eod") != today and not st.get("eod_running"):
        due.append("eod")
    _save_scheduler_state(st)
    import threading
    for job in due:
        if job == "eod":
            t = threading.Thread(target=_run_eod, daemon=True)
        else:
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


def _run_eod():
    import ai
    from datetime import date as _date
    st = _scheduler_state()
    if st.get("eod_running"):
        return
    st["eod_running"] = True
    _save_scheduler_state(st)
    log_run({"kind": "run_start", "trigger": "D2-end-of-day", "job": "eod"})
    try:
        cfg = ai.load_config()
        cs = detect_changes()
        ids = set(cs["added"]) | set(cs["edited"])
        run_session_analyzer_v2(cfg, session_ids=ids or None)
        assign_tasks()
        maintain_patterns()
        r19 = check_confounders()
        weekly_due = True
        try:
            last = st.get("last_weekly_coach", "")
            weekly_due = (not last) or (
                (_date.today() - _date(*map(int, last.split("-")))).days >= 7)
        except Exception:
            weekly_due = True
        narrator = None
        if weekly_due:
            r = run_coach_refresh(cfg)
            narrator = r.get("narrator")
            st["last_weekly_coach"] = _date.today().isoformat()
        commit_snapshot(detect_changes()["hashes"])
        st["last_eod"] = _date.today().isoformat()
        log_run({"kind": "run_done", "trigger": "D2-end-of-day", "job": "eod",
                 "findings": r19, "weekly_narrator": bool(narrator)})
    except Exception as e:
        log_run({"kind": "run_error", "trigger": "D2-end-of-day", "job": "eod",
                 "error": str(e)})
    finally:
        st["eod_running"] = False
        _save_scheduler_state(st)


def graph_status():
    """UI-facing status: scheduler state + store counts + last runs."""
    st = _scheduler_state()
    reports = _read_json("session_reports.json", {})
    tasks = _read_json("tasks.json", {})
    templates = tasks.get("templates", {}) if isinstance(tasks, dict) else {}
    return {"ok": True, "scheduler": st,
            "reports": len(reports.get("reports", [])) if isinstance(reports, dict) else 0,
            "memberships": len(tasks.get("memberships", [])) if isinstance(tasks, dict) else 0,
            "templates": len(templates),
            "recent_runs": read_runs(10)}


# =====================================================================
# Phase 2 — task graph (graph-builder-p2): N6/N7/N8/N12/N10/N11/N13
# =====================================================================

def _templates_store():
    store = _read_json("tasks.json", {})
    if not isinstance(store, dict):
        store = {}
    store.setdefault("templates", {})
    store.setdefault("revisions", [])
    return store


def _save_templates_store(store):
    store["updated_at"] = _now()
    _write_json("tasks.json", store)


def _get_template(task_id):
    return _templates_store().get("templates", {}).get(task_id)


def get_task_template(task_id):
    t = _get_template(task_id)
    if not t:
        return {"ok": False, "error": "Task not found"}
    return {"ok": True, "template": t}


# ---------------- N12 — Refiner / Revision Engine ----------------

def _envelope(ent_type, eid, payload, by="agent", evidence_refs=None):
    return {"id": eid, "type": ent_type, "version": 1, "supersedes": [],
            "superseded_by": None, "status": "active",
            "created_by": by, "ai_improvised": False,
            "user_feedback": {"checked_in": None, "edited_at": None, "edited_fields": []},
            "evidence_refs": evidence_refs or [],
            "payload": payload, "updated_at": _now()}


def _ledger(store, task_id, entity, from_v, to_v, by, reason):
    store.setdefault("revisions", []).append(
        {"ts": _now(), "task_id": task_id, "entity": entity,
         "from_v": from_v, "to_v": to_v, "by": by, "reason": reason})


def revise_entity(task_id, section, eid, payload, by="agent",
                  evidence_refs=None, improvised=False, reason=""):
    """Patch-or-revise one entity inside a task template (N12).

    - user_authoritative entities: agent output goes to `proposed` (max 1
      pending), never active. User output applies directly.
    - structural agent change: version bump + supersede chain + ledger.
    Returns {ok, status, version}.
    """
    store = _templates_store()
    t = store["templates"].get(task_id)
    if not t:
        return {"ok": False, "error": "Task not found"}
    entities = t.setdefault(section, [])
    cur = next((e for e in entities if e.get("id") == eid), None)
    if cur and cur.get("status") == "user_authoritative" and by == "agent":
        prop = dict(cur)
        prop["payload"] = payload
        prop["proposed_for"] = eid
        prop["status"] = "proposed"
        prop["updated_at"] = _now()
        if improvised:
            prop["ai_improvised"] = True
        # max 1 pending proposal per entity
        t.setdefault("proposals", [])
        t["proposals"] = [p for p in t["proposals"]
                          if p.get("proposed_for") != eid]
        prop["id"] = "%s@proposed" % eid
        t["proposals"].append(prop)
        _ledger(store, task_id, eid, cur.get("version"), cur.get("version"),
                "agent", "proposed (user-owned): %s" % reason)
        _save_templates_store(store)
        return {"ok": True, "status": "proposed", "version": cur.get("version")}
    if cur is None:
        ent = _envelope(section, eid, payload, by, evidence_refs)
        if improvised:
            ent["ai_improvised"] = True
        entities.append(ent)
        _ledger(store, task_id, eid, 0, 1, by, reason or "created")
    else:
        old_v = cur.get("version", 1)
        cur["supersedes"] = (cur.get("supersedes") or []) + [old_v]
        cur["version"] = old_v + 1
        cur["payload"] = payload
        if evidence_refs is not None:
            cur["evidence_refs"] = evidence_refs
        if improvised:
            cur["ai_improvised"] = True
        if by == "user":
            cur["status"] = "user_authoritative"
            cur["user_feedback"]["edited_at"] = _now()
        cur["updated_at"] = _now()
        _ledger(store, task_id, eid, old_v, cur["version"], by, reason or "revised")
    _save_templates_store(store)
    ent = next(e for e in entities if e.get("id") == eid)
    return {"ok": True, "status": ent["status"], "version": ent["version"]}


def user_edit_entity(task_id, section, eid, fields):
    """User edit path: applies directly and marks user_authoritative."""
    store = _templates_store()
    t = store["templates"].get(task_id)
    if not t:
        return {"ok": False, "error": "Task not found"}
    cur = next((e for e in (t.get(section) or []) if e.get("id") == eid), None)
    if not cur:
        return {"ok": False, "error": "Entity not found"}
    payload = dict(cur.get("payload") or {})
    payload.update(fields or {})
    cur["user_feedback"]["edited_fields"] = sorted(
        set(cur["user_feedback"].get("edited_fields") or []) | set((fields or {}).keys()))
    # bypass the agent-propose branch by writing as user
    _save_templates_store(store)
    return revise_entity(task_id, section, eid, payload, by="user",
                         reason="user edit")


def accept_proposal(task_id, proposal_id, accept):
    """Resolve a pending AI proposal: accept applies it (new version),
    reject drops it. Exactly one outcome; proposals never auto-apply."""
    store = _templates_store()
    t = store["templates"].get(task_id)
    if not t:
        return {"ok": False, "error": "Task not found"}
    prop = next((p for p in (t.get("proposals") or []) if p.get("id") == proposal_id), None)
    if not prop:
        return {"ok": False, "error": "Proposal not found"}
    t["proposals"] = [p for p in t["proposals"] if p.get("id") != proposal_id]
    if not accept:
        _ledger(store, task_id, prop.get("proposed_for"),
                prop.get("version"), prop.get("version"), "user", "proposal rejected")
        _save_templates_store(store)
        return {"ok": True, "status": "rejected"}
    _save_templates_store(store)  # persist removal before revise reloads
    # find which section holds the entity
    for section in ("timeline", "challenges", "steps", "propositions"):
        if any(e.get("id") == prop.get("proposed_for") for e in (t.get(section) or [])):
            # temporarily lift user ownership so the accepted text lands,
            # then re-mark: accepted proposal becomes user-confirmed content
            res = revise_entity(task_id, section, prop["proposed_for"],
                                prop.get("payload"), by="user",
                                evidence_refs=prop.get("evidence_refs"),
                                reason="proposal accepted")
            return res
    return {"ok": False, "error": "Entity not found"}


def _ensure_template(task_id, membership):
    store = _templates_store()
    t = store["templates"].get(task_id)
    if not t:
        t = {"id": task_id, "name": membership.get("name", "Untitled"),
             "session_ids": membership.get("session_ids", []),
             "timeline": [], "challenges": [], "steps": [],
             "propositions": [], "proposals": [], "critiques": []}
        store["templates"][task_id] = t
        _ledger(store, task_id, task_id, 0, 1, "system", "template created")
        _save_templates_store(store)
    return t


# ---------------- N6 — Timeline Architect ----------------

N6_PROMPT = (
    "You build a task timeline from work-session logs. Return only JSON: "
    "{\"phases\": [{\"name\": string, \"kind\": \"user_derived|ai_improvised\", "
    "\"evidence\": string (which log lines ground this phase), \"states\": "
    "[string]}]}. Map the user's own phase cues first (kind user_derived). "
    "You MAY improvise further phases ONLY when grounded in the logs "
    "(kind ai_improvised); never invent ungrounded phases.")

N6_SCHEMA = ("name", "kind", "evidence", "states")


def run_timeline_architect(cfg, task_ids=None):
    """Build/revise per-task timelines (B1)."""
    import ai
    store = _templates_store()
    memberships = store.get("memberships", [])
    if task_ids is not None:
        memberships = [m for m in memberships if m.get("task_id") in set(task_ids)]
    reports = {r.get("session_id"): r for r in
               _read_json("session_reports.json", {}).get("reports", [])}
    out = {}
    for m in memberships:
        tid = m["task_id"]
        _ensure_template(tid, m)
        body = "\n\n".join(
            ai._session_text(s) for s in _sessions_all()
            if s.get("id") in set(m.get("session_ids", [])))[:6000]
        if ai.MOCK or cfg.get("mock"):
            data = {"phases": [
                {"name": m.get("name", "Task") + ": Phase 1", "kind": "user_derived",
                 "evidence": "mock", "states": ["start", "done"]},
                {"name": m.get("name", "Task") + ": Phase 2 (improved)",
                 "kind": "ai_improvised", "evidence": "mock notes",
                 "states": ["start", "done"]}]}
            ok, text = True, json.dumps(data)
        else:
            text, ok = ai._agent_chat(cfg, "task-builder",
                                      N6_PROMPT + "\n\nTask: %s\n\nSessions:\n%s"
                                      % (m.get("name"), body), {})
        if not ok:
            out[tid] = {"ok": False, "error": "no working model"}
            continue
        data = ai._extract_json(text)
        phases = (data.get("phases") if isinstance(data, dict) else None) or []
        if not phases or any(any(k not in p for k in N6_SCHEMA) for p in phases):
            out[tid] = {"ok": False, "error": "invalid timeline JSON"}
            continue
        for i, p in enumerate(phases):
            eid = "phase-%d" % (i + 1)
            refs = [{"session_id": sid, "part_id": "*", "span": "all", "excerpt_hash": ""}
                    for sid in m.get("session_ids", [])]
            revise_entity(tid, "timeline", eid,
                          {"name": p["name"], "states": p.get("states", []),
                           "evidence": p.get("evidence", "")},
                          by="agent", evidence_refs=refs,
                          improvised=(p.get("kind") == "ai_improvised"),
                          reason="timeline architect")
            index_upsert("timeline:%s:%s" % (tid, eid), refs)
        out[tid] = {"ok": True, "phases": len(phases)}
    return {"ok": all(v.get("ok") for v in out.values()), "tasks": out}


# ---------------- N7 — Challenge Miner ----------------

N7_PROMPT = (
    "You mine challenges from work-session logs for one task. Return only "
    "JSON: {\"challenges\": [{\"text\": string, "
    "\"severity\": \"low|medium|high|critical\", "
    "\"status\": \"identified|solved|partially_solved\", "
    "\"done\": [strings: what is finished], "
    "\"remaining\": [strings: what is left — REQUIRED when partially_solved], "
    "\"evidence\": string}]}.")

SEVERITIES = ("low", "medium", "high", "critical")
STATUSES = ("identified", "solved", "partially_solved")


def run_challenge_miner(cfg, task_ids=None):
    """Extract challenges with severity + status + done/remains (B2)."""
    import ai
    store = _templates_store()
    memberships = store.get("memberships", [])
    if task_ids is not None:
        memberships = [m for m in memberships if m.get("task_id") in set(task_ids)]
    out = {}
    for m in memberships:
        tid = m["task_id"]
        _ensure_template(tid, m)
        body = "\n\n".join(
            ai._session_text(s) for s in _sessions_all()
            if s.get("id") in set(m.get("session_ids", [])))[:6000]
        if ai.MOCK or cfg.get("mock"):
            data = {"challenges": [
                {"text": "Mock challenge for %s" % m.get("name"),
                 "severity": "medium", "status": "partially_solved",
                 "done": ["investigated"], "remaining": ["fix", "verify"],
                 "evidence": "mock"}]}
            ok, text = True, json.dumps(data)
        else:
            text, ok = ai._agent_chat(cfg, "task-builder",
                                      N7_PROMPT + "\n\nTask: %s\n\nSessions:\n%s"
                                      % (m.get("name"), body), {})
        if not ok:
            out[tid] = {"ok": False, "error": "no working model"}
            continue
        data = ai._extract_json(text)
        chs = (data.get("challenges") if isinstance(data, dict) else None) or []
        valid = [c for c in chs
                 if isinstance(c, dict) and c.get("text")
                 and c.get("severity") in SEVERITIES
                 and c.get("status") in STATUSES
                 and (c.get("status") != "partially_solved" or c.get("remaining"))]
        if not valid:
            out[tid] = {"ok": False, "error": "invalid challenges JSON"}
            continue
        for i, c in enumerate(valid):
            eid = "challenge-%d" % (i + 1)
            refs = [{"session_id": sid, "part_id": "*", "span": "all", "excerpt_hash": ""}
                    for sid in m.get("session_ids", [])]
            v = verify("challenge", {"id": eid, "text": c["text"],
                                     "severity": c["severity"], "status": c["status"]})
            if not v.get("ok"):
                continue
            revise_entity(tid, "challenges", eid,
                          {"text": c["text"], "severity": c["severity"],
                           "status": c["status"], "done": c.get("done", []),
                           "remaining": c.get("remaining", []),
                           "evidence": c.get("evidence", ""), "step_refs": []},
                          by="agent", evidence_refs=refs, reason="challenge miner")
            index_upsert("challenge:%s:%s" % (tid, eid), refs)
        out[tid] = {"ok": True, "challenges": len(valid)}
    return {"ok": all(v.get("ok") for v in out.values()), "tasks": out}


# ---------------- N8 — Step Linker ----------------

N8_PROMPT = (
    "You decompose task phases into steps linked to timelog parts (many-to-many: "
    "one step may use parts from several sessions; one part may serve several "
    "steps). Return only JSON: {\"steps\": [{\"goal\": string, "
    "\"phase\": string (phase name it belongs to), "
    "\"part_ids\": [string], \"challenge_ids\": [string]}]}. "
    "Use ONLY the given part_ids and challenge_ids verbatim.")

N8_SCHEMA = ("goal", "phase", "part_ids", "challenge_ids")


def run_step_linker(cfg, task_ids=None):
    """Build steps with part + challenge links (B3) + local constraint pass."""
    import ai
    store = _templates_store()
    memberships = store.get("memberships", [])
    if task_ids is not None:
        memberships = [m for m in memberships if m.get("task_id") in set(task_ids)]
    out = {}
    for m in memberships:
        tid = m["task_id"]
        t = _ensure_template(tid, m)
        parts = []
        for s in _sessions_all():
            if s.get("id") in set(m.get("session_ids", [])):
                parts.extend(split_parts(s))
        known_parts = {p["part_id"]: p for p in parts}
        ch_ids = [c["id"] for c in t.get("challenges", [])]
        ctx = "\n".join("part %s [%s]: %s" % (p["part_id"], p["kind"], p["text"][:200])
                        for p in parts)[:5000]
        if ai.MOCK or cfg.get("mock"):
            half = max(1, len(parts) // 2)
            data = {"steps": [
                {"goal": "Mock step 1", "phase": "phase-1",
                 "part_ids": [p["part_id"] for p in parts[:half]] or ["none"],
                 "challenge_ids": ch_ids[:1]},
                {"goal": "Mock step 2", "phase": "phase-2",
                 "part_ids": [p["part_id"] for p in parts[half:]] or ["none"],
                 "challenge_ids": ch_ids[1:2]}]}
            ok, text = True, json.dumps(data)
        else:
            text, ok = ai._agent_chat(
                cfg, "task-builder",
                N8_PROMPT + "\n\nValid part_ids: %s\nValid challenge_ids: %s\n\nParts:\n%s"
                % (sorted(known_parts), ch_ids, ctx), {})
        if not ok:
            out[tid] = {"ok": False, "error": "no working model"}
            continue
        data = ai._extract_json(text)
        steps = (data.get("steps") if isinstance(data, dict) else None) or []
        # local constraint pass: known part_ids only, known challenges only
        clean = []
        for s in steps:
            if not isinstance(s, dict) or not s.get("goal"):
                continue
            pids = [p for p in (s.get("part_ids") or []) if p in known_parts]
            cids = [c for c in (s.get("challenge_ids") or []) if c in ch_ids]
            if not pids:
                continue
            clean.append({"goal": s["goal"], "phase": s.get("phase", ""),
                          "part_ids": pids, "challenge_ids": cids})
        if not clean:
            out[tid] = {"ok": False, "error": "no valid steps"}
            continue
        backlinks = {}  # challenge_id -> [step_ids]
        for i, s in enumerate(clean):
            eid = "step-%d" % (i + 1)
            refs = [{"session_id": known_parts[p]["session_id"], "part_id": p,
                     "span": known_parts[p]["span"],
                     "excerpt_hash": known_parts[p]["excerpt_hash"]}
                    for p in s["part_ids"]]
            v = verify("step", {"id": eid, "phase_state_id": s["phase"] or "phase-1",
                                "goal": s["goal"], "part_ids": s["part_ids"],
                                "challenge_ids": s["challenge_ids"]})
            if not v.get("ok"):
                continue
            revise_entity(tid, "steps", eid,
                          {"goal": s["goal"], "phase": s["phase"],
                           "part_ids": s["part_ids"],
                           "challenge_ids": s["challenge_ids"]},
                          by="agent", evidence_refs=refs, reason="step linker")
            index_upsert("step:%s:%s" % (tid, eid), refs)
            for cid in s["challenge_ids"]:
                backlinks.setdefault(cid, []).append(eid)
        # back-links on a FRESH load (revise_entity saves per call; the
        # in-memory `t` above is stale) — challenge.step_refs += steps
        if backlinks:
            fresh = _templates_store()
            ft = (fresh.get("templates") or {}).get(tid) or {}
            for cid, eids in backlinks.items():
                ch = next((c for c in (ft.get("challenges") or [])
                           if c.get("id") == cid), None)
                if ch:
                    have = set(ch.get("payload", {}).get("step_refs") or [])
                    ch["payload"].setdefault("step_refs", []).extend(
                        [e for e in eids if e not in have])
            _save_templates_store(fresh)
        out[tid] = {"ok": True, "steps": len(clean)}
    return {"ok": all(v.get("ok") for v in out.values()), "tasks": out}


# ---------------- N10/N11 — Proposer + Critic ----------------

N10_PROMPT = (
    "You propose observations for ONE work step, ONLY when confidently grounded "
    "in the excerpts. Kinds: thinking_issue | mind_obscuration | domain_help. "
    "Abstain (empty array) over guessing. Return only JSON: {\"propositions\": "
    "[{\"text\": string, \"kind\": string, \"confidence\": \"high|medium\", "
    "\"grounding\": string (exact excerpt supporting it)}]}.")


def critic_filter(propositions, excerpts):
    """N11 mechanical gate (always on, LLM critic adds judgment in live mode):
    keep propositions whose grounding text actually appears in the excerpts."""
    blob = "\n".join(excerpts)
    kept, rejected = [], []
    for p in propositions:
        g = (p.get("grounding") or "").strip()
        if p.get("confidence") == "high" and g and g[:60] in blob:
            kept.append(p)
        else:
            rejected.append(p)
    return kept, rejected


def run_propositions(cfg, task_ids=None):
    """N10 propose + N11 gate per step (B4)."""
    import ai
    store = _templates_store()
    memberships = store.get("memberships", [])
    if task_ids is not None:
        memberships = [m for m in memberships if m.get("task_id") in set(task_ids)]
    out = {}
    for m in memberships:
        tid = m["task_id"]
        t = _ensure_template(tid, m)
        parts_by_id = {}
        for s in _sessions_all():
            if s.get("id") in set(m.get("session_ids", [])):
                for p in split_parts(s):
                    parts_by_id[p["part_id"]] = p
        n_prop = 0
        for st in (t.get("steps") or []):
            sid = st["id"]
            excerpts = [parts_by_id[p]["text"] for p in
                        (st.get("payload", {}).get("part_ids") or []) if p in parts_by_id]
            if ai.MOCK or cfg.get("mock"):
                g = (excerpts[0][:60] if excerpts else "mock")
                data = {"propositions": [
                    {"text": "Mock proposition for %s" % sid, "kind": "domain_help",
                     "confidence": "high", "grounding": g}]}
                ok, text = True, json.dumps(data)
            else:
                text, ok = ai._agent_chat(
                    cfg, "task-builder",
                    N10_PROMPT + "\n\nStep goal: %s\n\nExcerpts:\n%s"
                    % (st.get("payload", {}).get("goal"), "\n---\n".join(excerpts)[:4000]),
                    {})
            if not ok:
                continue
            data = ai._extract_json(text)
            props = (data.get("propositions") if isinstance(data, dict) else None) or []
            kept, rejected = critic_filter(props, excerpts)
            for p in kept:
                eid = "prop-" + hashlib.sha1(
                    (p.get("text", "") + sid).encode("utf-8")).hexdigest()[:8]
                v = verify("proposition", {"id": eid, "step_id": sid,
                                           "text": p.get("text"),
                                           "confidence": p.get("confidence")})
                if not v.get("ok"):
                    continue
                refs = [{"session_id": parts_by_id[pid]["session_id"], "part_id": pid,
                         "span": parts_by_id[pid]["span"],
                         "excerpt_hash": parts_by_id[pid]["excerpt_hash"]}
                        for pid in (st.get("payload", {}).get("part_ids") or [])
                        if pid in parts_by_id]
                revise_entity(tid, "propositions", eid,
                              {"text": p["text"], "kind": p.get("kind"),
                               "confidence": p.get("confidence"),
                               "grounding": p.get("grounding"),
                               "accepted": None, "step_id": sid},
                              by="agent", evidence_refs=refs,
                              reason="proposition proposer")
                n_prop += 1
            t["critiques"].append({"step": sid, "kept": len(kept),
                                  "rejected": len(rejected), "ts": _now()})
        _save_templates_store(_templates_store())
        out[tid] = {"ok": True, "propositions": n_prop}
    return {"ok": all(v.get("ok") for v in out.values()), "tasks": out}


def toggle_proposition_v2(task_id, prop_id, accepted):
    """Check a proposition IN/OUT (B4). Records decision + frozen context for DPO."""
    store = _templates_store()
    t = store.get("templates", {}).get(task_id)
    if not t:
        return {"ok": False, "error": "Task not found"}
    prop = next((e for e in (t.get("propositions") or []) if e.get("id") == prop_id), None)
    if not prop:
        return {"ok": False, "error": "Proposition not found"}
    prop["payload"]["accepted"] = bool(accepted)
    prop["payload"]["decided_at"] = _now()
    _ledger(store, task_id, prop_id, prop.get("version"), prop.get("version"),
            "user", "proposition %s" % ("IN" if accepted else "OUT"))
    _save_templates_store(store)
    return {"ok": True}


# ---------------- N13 — DPO Row Builder ----------------

def export_dpo_rows_v2():
    """Consent-gated DPO export with FULL flow trajectory (locked decision).

    Each row: context (task/phase/step/proposition/critique/excerpts),
    chosen/rejected pair, trajectory[node, input_ref, output_ref, version],
    frozen at decision time. Append-only file; never mutated.
    """
    import ai
    cfg = ai.load_config()
    if not cfg.get("consent_dpo"):
        return {"ok": False, "error": "consent not given"}
    store = _templates_store()
    rows = []
    for tid, t in (store.get("templates") or {}).items():
        revs = [r for r in (store.get("revisions") or []) if r.get("task_id") == tid]
        for prop in (t.get("propositions") or []):
            p = prop.get("payload") or {}
            if p.get("accepted") is None:
                continue
            traj = [{"node": r.get("entity"), "by": r.get("by"),
                     "from_v": r.get("from_v"), "to_v": r.get("to_v"),
                     "ts": r.get("ts"), "reason": r.get("reason")} for r in revs]
            step = next((s for s in (t.get("steps") or [])
                         if s.get("id") == p.get("step_id")), {})
            rows.append({
                "context": {
                    "task_id": tid, "task_name": t.get("name"),
                    "step_id": p.get("step_id"),
                    "step_goal": (step.get("payload") or {}).get("goal"),
                    "proposition": p.get("text"),
                    "kind": p.get("kind"), "confidence": p.get("confidence"),
                    "grounding": p.get("grounding"),
                    "evidence_refs": prop.get("evidence_refs", []),
                    "critiques": t.get("critiques", [])},
                "chosen": p["text"] if p["accepted"] else "NO_PROPOSITION",
                "rejected": "NO_PROPOSITION" if p["accepted"] else p["text"],
                "trajectory": traj,
                "decision": "in" if p["accepted"] else "out",
                "decided_at": p.get("decided_at")})
    path = _app_dir() / "dpo_rows.jsonl"
    try:
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except OSError as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(rows), "path": str(path)}


    ok = all(r.get("ok") for r in (r6, r7, r8, r10))
    return {"ok": ok, "timeline": r6, "challenges": r7, "steps": r8,
            "propositions": r10}


# =====================================================================
# Phase 3 — coach suite (graph-builder-p3): N14-N20 + D2 end-of-day
# =====================================================================

def _ended_sessions():
    from datetime import timedelta  # noqa: F401 (kept local for clarity)
    return [s for s in _sessions_all()
            if s.get("end") and s.get("kind") != "daily-doc-summary"
            and _parse_dt(s.get("start")) and _parse_dt(s.get("end"))]


def _sess_minutes(s):
    try:
        return max(0.0, (_parse_dt(s["end"]) - _parse_dt(s["start"])).total_seconds() / 60.0)
    except Exception:
        return 0.0


# ---------------- N14 — Pattern DB Maintainer ----------------

def _shape_of(text):
    import re
    t = (text or "").lower()
    words = re.findall(r"[a-z]+", t)
    has_nums = bool(re.search(r"\d", t))
    has_q = "?" in t
    bucket = "s" if len(words) < 15 else ("m" if len(words) < 50 else "l")
    return (bucket, has_nums, has_q)


def _jaccard(a, b):
    sa, sb = set(a.split()), set(b.split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def maintain_patterns():
    """Cluster log excerpts by structural shape (local, no LLM).

    patterns.json: [{shape_id, name, examples[] (own excerpts),
    ambiguity_note, improved_wording, recurrence_count, last_seen}].
    improved_wording is a local template in P3; N15 refines per point.
    """
    import re
    shapes = _read_json("patterns.json", {})
    if not isinstance(shapes, dict):
        shapes = {}
    for s in _ended_sessions():
        for field in ("describe", "notes"):
            text = (s.get(field) or "").strip()
            if len(text) < 12:
                continue
            key = "%s|%s" % (s.get("category") or "?", _shape_of(text))
            norm = re.sub(r"\d+", "#", text.lower())
            match = None
            for sid, sh in shapes.items():
                if sh.get("key") == key and _jaccard(norm, sh.get("norm", "")) >= 0.4:
                    match = sid
                    break
            if match is None:
                import hashlib as _hl
                sid = "shape-" + _hl.sha1(key.encode()).hexdigest()[:8]
                shapes[sid] = {"shape_id": sid, "key": key, "norm": norm,
                               "name": "Recurring %s log in %s" % (
                                   field, s.get("category") or "work"),
                               "examples": [], "ambiguity_note": "",
                               "improved_wording": "", "recurrence_count": 0,
                               "last_seen": None}
                match = sid
            sh = shapes[match]
            if text not in sh["examples"]:
                sh["examples"] = (sh["examples"] + [text[:500]])[:3]
            sh["recurrence_count"] += 1
            sh["last_seen"] = (s.get("start") or "")[:10]
    for sh in shapes.values():
        if not sh.get("ambiguity_note"):
            sh["ambiguity_note"] = (
                "Entries with this shape state activity but not outcome: "
                "add what was attempted, what resulted, and any open question.")
            sh["improved_wording"] = (
                "Topic: … | Attempted: … | Result (numbers where possible): … | Open: …")
    _write_json("patterns.json", shapes)
    return {"ok": True, "shapes": len(shapes)}


# ---------------- N16/N18 — Hypothesis enumerators (local) ----------------

def enumerate_hypotheses():
    """Testable hypotheses ONLY (N16/N18) — claims come from N19.

    Kinds: best_hour, best_weekday, task_on_weekday, after_effect, gap_norm.
    Each carries candidate_confounders for N19 to actually check.
    """
    sessions = _ended_sessions()
    hyps = [{"id": "h-hour", "kind": "best_hour",
             "claim_template": "Most focused work happens around hour H",
             "variables": ["start_hour"], "candidate_confounders": ["weekday", "category"]},
            {"id": "h-weekday", "kind": "best_weekday",
             "claim_template": "Weekday D yields the most focused minutes",
             "variables": ["weekday"], "candidate_confounders": ["category", "hour"]},
            {"id": "h-gap", "kind": "gap_norm",
             "claim_template": "Unusually long gaps precede rushed sessions",
             "variables": ["inter_gap"], "candidate_confounders": ["weekday", "hour"]}]
    cats = sorted({s.get("category") or "?" for s in sessions})
    for c in cats[:6]:
        hyps.append({"id": "h-cat-%s" % c[:12], "kind": "task_on_weekday",
                     "claim_template": "Category %s performs best on weekday D" % c,
                     "variables": ["category", "weekday"], "category": c,
                     "candidate_confounders": ["hour", "other_tasks"]})
    for a in cats[:4]:
        for b in cats[:4]:
            if a != b:
                hyps.append({"id": "h-after-%s-%s" % (a[:8], b[:8]), "kind": "after_effect",
                             "claim_template": "%s after %s changes %s sessions" % (b, a, b),
                             "variables": ["sequence"], "cat_after": a, "cat_then": b,
                             "candidate_confounders": ["weekday", "hour"]})
    return hyps


# ---------------- N19 — Confounder Checker (LOCAL, LLM-free) ----------------

MIN_N = 5
LUNCH = (12, 14)


def _mean(xs):
    import statistics
    return statistics.mean(xs) if xs else 0.0


def check_confounders():
    """Compute every hypothesis from real data with confounder checks.

    Findings ONLY. Small samples (n<MIN_N) -> insufficient_data, never a
    claim. This is the sole node allowed to emit 'we checked X' text.
    """
    import statistics
    sessions = _ended_sessions()
    for s in sessions:
        s["_min"] = _sess_minutes(s)
        s["_dt"] = _parse_dt(s["start"])
    window = "%s..%s" % (min((s["start"] for s in sessions), default="?")[:10],
                         max((s["start"] for s in sessions), default="?")[:10])
    findings = []

    def add(fid, claim, metric, effect, base, checked, residual, n):
        if n < MIN_N:
            findings.append({"id": fid, "claim": claim, "metric": metric,
                             "effect_size": None, "base_rate": base,
                             "confounders_checked": [], "residual_confounders": checked + residual,
                             "data_window": window, "n": n, "verdict": "insufficient_data"})
        else:
            findings.append({"id": fid, "claim": claim, "metric": metric,
                             "effect_size": round(effect, 3), "base_rate": round(base, 2),
                             "confounders_checked": checked, "residual_confounders": residual,
                             "data_window": window, "n": n, "verdict": "claim"})

    # H-hour / H-weekday: best bucket vs overall mean, confounder = other axis
    by_hour, by_wd = {}, {}
    for s in sessions:
        by_hour.setdefault(s["_dt"].hour, []).append(s["_min"])
        by_wd.setdefault(s["_dt"].weekday(), []).append(s["_min"])
    overall = _mean([s["_min"] for s in sessions])
    if by_hour:
        h = max(by_hour, key=lambda k: _mean(by_hour[k]))
        # confounder check: does the lead survive within each weekday?
        survives = sum(1 for wd in by_wd
                       if [x for x in sessions if x["_dt"].weekday() == wd and x["_dt"].hour == h])
        add("f-hour", "Most focused work happens around %02d:00" % h,
            "mean minutes", _mean(by_hour[h]) - overall, overall,
            ["weekday"] if survives >= MIN_N else [], ["weekday", "category"],
            len(by_hour[h]))
    if by_wd:
        wd = max(by_wd, key=lambda k: _mean(by_wd[k]))
        names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        add("f-weekday", "%s yields the most focused minutes" % names[wd],
            "mean minutes", _mean(by_wd[wd]) - overall, overall,
            ["category"] if len(by_wd[wd]) >= MIN_N else [], ["category", "hour"],
            len(by_wd[wd]))

    # H-cat: category X on weekday D vs X elsewhere (confounder: hour, lunch)
    for h in enumerate_hypotheses():
        if h["kind"] != "task_on_weekday":
            continue
        c = h["category"]
        xs = [s for s in sessions if (s.get("category") or "?") == c]
        if not xs:
            continue
        per_wd = {}
        for s in xs:
            per_wd.setdefault(s["_dt"].weekday(), []).append(s["_min"])
        best = max(per_wd, key=lambda k: _mean(per_wd[k]))
        rest = [s["_min"] for s in xs if s["_dt"].weekday() != best]
        names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        # lunch check: exclude 12-14, does the lead survive?
        no_lunch = [s["_min"] for s in xs if s["_dt"].weekday() == best
                    and not (LUNCH[0] <= s["_dt"].hour < LUNCH[1])]
        checked = ["hour"] if len(no_lunch) >= MIN_N and _mean(no_lunch) > _mean(rest) else []
        add("f-cat-%s" % c[:12], "%s performs best on %s" % (c, names[best]),
            "mean minutes", _mean(per_wd[best]) - _mean(rest), _mean(rest),
            checked, ["hour", "other_tasks", "lunch_routine"], len(per_wd[best]))

    # H-after: X-after-Y sequences vs Y-baseline within same weekday
    ordered = sorted(sessions, key=lambda s: s["_dt"])
    for h in enumerate_hypotheses():
        if h["kind"] != "after_effect":
            continue
        a, b = h["cat_after"], h["cat_then"]
        seq, base = [], []
        for prev, cur in zip(ordered, ordered[1:]):
            gap = (cur["_dt"] - _parse_dt(prev["end"])).total_seconds() / 60.0 \
                if prev.get("end") else None
            if gap is None or gap < 0 or gap > 8 * 60:
                continue
            if (prev.get("category") or "?") == a and (cur.get("category") or "?") == b:
                seq.append((cur, gap))
            elif (cur.get("category") or "?") == b:
                base.append(cur["_min"])
        if not seq:
            continue
        seq_min = [c["_min"] for c, _ in seq]
        # same-weekday control: compare against baseline on the same weekdays
        wds = {c["_dt"].weekday() for c, _ in seq}
        ctrl = [x for x in base]  # baseline pool (residual: weekday mix noted)
        checked = ["weekday"] if len([c for c, _ in seq]) >= MIN_N else []
        add("f-after-%s-%s" % (a[:8], b[:8]),
            "%s after %s averages %.0f min vs %.0f baseline" % (
                b, a, _mean(seq_min), _mean(ctrl) if ctrl else 0),
            "mean minutes", _mean(seq_min) - (_mean(ctrl) if ctrl else 0),
            _mean(ctrl) if ctrl else 0, checked,
            ["weekday", "hour", "gap_length"], len(seq_min))

    # H-gap: median inter-session gap; long gaps (>4x median) before sessions
    gaps = []
    for prev, cur in zip(ordered, ordered[1:]):
        if prev.get("end"):
            g = (cur["_dt"] - _parse_dt(prev["end"])).total_seconds() / 60.0
            if 0 <= g <= 24 * 60:
                gaps.append(g)
    if gaps:
        import statistics as _st
        med = _st.median(gaps)
        long_gaps = [g for g in gaps if g > 4 * med] if med > 0 else []
        add("f-gap", "Your normal gap is ~%.0f min; %d long gaps observed" % (med, len(long_gaps)),
            "median gap min", float(med), float(med), ["weekday", "hour"], [],
            len(gaps))

    store = {"findings": findings, "generated_at": _now(), "window": window}
    _write_json("findings.json", store)
    return {"ok": True, "findings": len(findings),
            "claims": sum(1 for f in findings if f.get("verdict") == "claim")}


# ---------------- N17 — Divider (local numbers) ----------------

def _sub_split(describe, notes):
    t = ("%s\n%s" % (describe or "", notes or "")).lower()
    if any(w in t for w in ("pdf", "paper", "arxiv", "book", "article")):
        return "PDFs/papers"
    if any(w in t for w in ("tab", "browser", "chrome", "site", "website", "stackoverflow")):
        return "browser tabs"
    if any(w in t for w in ("video", "youtube", "course", "lecture")):
        return "video"
    if any(w in t for w in ("meeting", "call", "sync", "standup")):
        return "meetings"
    return "other"


def divide_time():
    """C3 numbers, computed locally: shares, sub-splits, trend, edge metrics."""
    sessions = _ended_sessions()
    total = sum(s["_min"] if "_min" in s else _sess_minutes(s) for s in sessions) or 1.0
    for s in sessions:
        s.setdefault("_min", _sess_minutes(s))
    by_cat, sub = {}, {}
    for s in sessions:
        c = s.get("category") or "?"
        by_cat[c] = by_cat.get(c, 0.0) + s["_min"]
        k = (c, _sub_split(s.get("describe"), s.get("notes")))
        sub[k] = sub.get(k, 0.0) + s["_min"]
    shares = [{"name": c, "share": round(m / total, 4), "minutes": round(m, 1)}
              for c, m in sorted(by_cat.items(), key=lambda kv: -kv[1])]
    subs = [{"category": c, "split": sp, "share": round(m / total, 4)}
            for (c, sp), m in sorted(sub.items(), key=lambda kv: -kv[1])]
    # trend: weekly shares, last 8 weeks
    weeks = {}
    for s in sessions:
        d = s["_dt"] if "_dt" in s else _parse_dt(s["start"])
        wk = (d.date() - __import__("datetime").timedelta(days=d.weekday())).isoformat()
        w = weeks.setdefault(wk, {})
        w[s.get("category") or "?"] = w.get(s.get("category") or "?", 0.0) + s["_min"]
    trend = [{"week": wk, "shares": {c: round(m / (sum(v.values()) or 1), 3)
                                    for c, m in v.items()}}
             for wk, v in sorted(weeks.items())[-8:]]
    # edge metrics: p90 length, pre-break endings, fatigue cues
    import statistics as _st
    lens = sorted(s["_min"] for s in sessions)
    p90 = lens[min(len(lens) - 1, int(len(lens) * 0.9))] if lens else 0
    ordered = sorted(sessions, key=lambda s: s["_dt"] if "_dt" in s else _parse_dt(s["start"]))
    pre_break = 0
    for prev, cur in zip(ordered, ordered[1:]):
        if prev.get("end"):
            g = ((cur["_dt"] if "_dt" in cur else _parse_dt(cur["start"]))
                 - _parse_dt(prev["end"])).total_seconds() / 60.0
            if g >= 120:
                pre_break += 1
    fatigue_words = ("rush", "tired", "exhaust", "hasty", "late night", "sloppy")
    fatigue = sum(1 for s in sessions
                  if any(w in ("%s %s" % (s.get("describe") or "", s.get("notes") or "")).lower()
                         for w in fatigue_words))
    return {"shares": shares, "sub_splits": subs, "trend": trend,
            "edge": {"p90_min": round(p90, 1), "pre_break_endings": pre_break,
                     "fatigue_cues": fatigue, "n": len(sessions)}}


# ---------------- N15 — Style Critic ----------------

def run_style_critic(cfg):
    """C1: one point per eligible pattern shape. Excerpt MUST come from the
    user's own pattern DB (no invented quotes — N22-style check inline)."""
    import ai
    shapes = _read_json("patterns.json", {})
    points = []
    for sid, sh in sorted(shapes.items()):
        if not sh.get("examples") or (sh.get("recurrence_count") or 0) < 2:
            continue
        excerpt = sh["examples"][0]
        if ai.MOCK or cfg.get("mock"):
            point = {"issue": "Activity stated without outcome (%s)" % sh.get("name"),
                     "example_from_log": excerpt,
                     "suggestion": "Use: Topic | Attempted | Result (numbers) | Open. " +
                                   sh.get("improved_wording", ""),
                     "benefit": "Future reports can cite results instead of re-reading logs."}
        else:
            text, ok = ai._agent_chat(
                cfg, "coach",
                "Give ONE logging-style point as JSON {issue, suggestion, benefit} "
                "for this recurring log shape. Do NOT quote or invent excerpts.\n"
                "Shape: %s\nExample: %s" % (sh.get("name"), excerpt[:400]), {})
            if not ok:
                continue
            data = ai._extract_json(text)
            if not isinstance(data, dict) or not data.get("suggestion"):
                continue
            point = {"issue": data.get("issue", ""), "example_from_log": excerpt,
                     "suggestion": data.get("suggestion", ""),
                     "benefit": data.get("benefit", "")}
        v = verify("style_point", {"point_id": sid, "excerpt_ref": sid,
                                   "ambiguity": point["issue"],
                                   "improved_wording": point["suggestion"],
                                   "benefit": point["benefit"]})
        if v.get("ok") and point["example_from_log"] in sh["examples"]:
            points.append({"point_id": sid, **point, "pattern_shape_id": sid})
    return {"ok": True, "points": points}


# ---------------- N20 — Coach Narrator ----------------

def render_coach(cfg, division=None, style_points=None):
    """Assemble C1–C5. Finding claim strings render VERBATIM; a local
    post-pass re-appends any claim the prose dropped (fail-safe honesty)."""
    import ai
    findings = _read_json("findings.json", {}).get("findings", [])
    claims = ["%s [n=%s, window %s]" % (f["claim"], f["n"], f.get("data_window", "?"))
              for f in findings if f.get("verdict") == "claim"]
    division = division if division is not None else divide_time()
    style_points = style_points if style_points is not None \
        else run_style_critic(cfg).get("points", [])
    ideal = (cfg.get("ideal_time") or {})
    ask_block = "" if ideal.get("set") else (
        "To sharpen this analysis, tell me your ideal time-of-day, days, and "
        "work hours (Coach tab → ideal hours).")
    if ai.MOCK or cfg.get("mock"):
        body = "## Work-time patterns\n" + "\n".join("- " + c for c in claims)
        body += "\n\n## Time division\n" + "\n".join(
            "- %s: %.1f%%" % (s["name"], s["share"] * 100) for s in division["shares"])
        body += "\n\n## Logging style\n" + "\n".join(
            "- %s (e.g. you wrote: %s…)" % (p["issue"], p["example_from_log"][:80])
            for p in style_points)
        if ask_block:
            body += "\n\n## Ideal hours\n" + ask_block
    else:
        prompt = ("You are a work coach. Write concise markdown with sections "
                  "## Work-time patterns, ## Time division, ## Logging style. "
                  "RULES: quote each CLAIM below character-for-character at least "
                  "once; never alter numbers; never add unchecked claims.\n\n"
                  "CLAIMS:\n" + "\n".join("- " + c for c in claims) +
                  "\n\nDIVISION:\n" + json.dumps(division, ensure_ascii=False)[:2000] +
                  "\n\nSTYLE POINTS:\n" + json.dumps(style_points, ensure_ascii=False)[:3000])
        text, ok = ai._agent_chat(cfg, "coach", prompt, {})
        body = text if ok and text else ""
    # post-pass: every claim must appear verbatim, else append raw
    missing = [c for c in claims if c not in body]
    if missing:
        body += "\n\n## Verified findings (quoted)\n" + "\n".join("- " + c for c in missing)
    if ask_block and "Ideal hours" not in body:
        body += "\n\n## Ideal hours\n" + ask_block
    _write_json("coach.json", {"body": body, "generated_at": _now(),
                               "claims": len(claims), "missing": len(missing)})
    return {"ok": True, "claims": len(claims), "appended_raw": len(missing)}


def run_coach_refresh(cfg):
    """P3 staged run: patterns -> hypotheses/checks -> division -> style ->
    narrator. Returns stage results for the run log."""
    r14 = maintain_patterns()
    hyps = enumerate_hypotheses()
    r19 = check_confounders()
    div = divide_time()
    r15 = run_style_critic(cfg)
    r20 = render_coach(cfg, division=div, style_points=r15.get("points", []))
    log_run({"kind": "run_done", "trigger": "manual", "job": "coach-refresh",
             "patterns": r14, "hypotheses": len(hyps),
             "findings": r19, "style_points": len(r15.get("points", [])),
             "narrator": r20})
    return {"ok": True, "patterns": r14, "hypotheses": len(hyps),
            "findings": r19, "style_points": len(r15.get("points", [])),
            "narrator": r20}


def get_coach():
    c = _read_json("coach.json", None)
    if not c:
        return {"ok": True, "coach": None}
    return {"ok": True, "coach": c}


# ---------------- P2 pipeline convenience ----------------

def run_task_graph(cfg, task_ids=None):
    """N6 -> N7 -> N8 -> N10/N11 staged mini-DAG (N12 governs revisions)."""
    r6 = run_timeline_architect(cfg, task_ids)
    r7 = run_challenge_miner(cfg, task_ids)
    r8 = run_step_linker(cfg, task_ids)
    r10 = run_propositions(cfg, task_ids)
    log_run({"kind": "run_done", "trigger": "manual", "job": "task-graph",
             "timeline": r6, "challenges": r7, "steps": r8,
             "propositions": r10})
    ok = all(r.get("ok") for r in (r6, r7, r8, r10))
    return {"ok": ok, "timeline": r6, "challenges": r7, "steps": r8,
            "propositions": r10}
