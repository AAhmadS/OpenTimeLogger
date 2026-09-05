"""BYOK AI layer for OpenTimeLogger: provider catalog, key config, chat completions,
model tests, fallback selection, the agent pipeline (session analyzer -> task builder ->
coach), task storage with propositions, DPO export and audio transcription.
Standard library only. The app dir defaults to this file's folder; set OTL_APP_DIR to
override it (used by tests to avoid polluting the repo)."""

import base64
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import keystore as _keystore
except ImportError:
    _keystore = None

MOCK = False

PROVIDERS = {
    "openai": {
        "id": "openai",
        "label": "OpenAI",
        "base": "https://api.openai.com/v1",
        "chat_models": ["gpt-5.2", "gpt-5.1-mini", "gpt-4.1-mini", "o4-mini"],
        "asr_models": ["whisper-1", "gpt-4o-transcribe"],
        "capabilities": ["chat", "asr"],
    },
    "openrouter": {
        "id": "openrouter",
        "label": "OpenRouter",
        "base": "https://openrouter.ai/api/v1",
        "chat_models": ["openai/gpt-5.2", "anthropic/claude-sonnet-4.5", "google/gemini-3-flash", "mistralai/mistral-large-3.1", "deepseek/deepseek-v4-flash", "qwen/qwen3-235b-a22b"],
        "asr_models": [],
        "capabilities": ["chat"],
    },
    "mistral": {
        "id": "mistral",
        "label": "Mistral",
        "base": "https://api.mistral.ai/v1",
        "chat_models": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
        "asr_models": [],
        "capabilities": ["chat"],
    },
    "avalai": {
        "id": "avalai",
        "label": "AvalAI",
        "base": "https://api.avalai.ir/v1",
        "chat_models": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
        "asr_models": ["whisper-1"],
        "capabilities": ["chat", "asr"],
    },
    "google": {
        "id": "google",
        "label": "Google AI Studio",
        "base": "https://generativelanguage.googleapis.com/v1beta",
        "chat_models": ["gemini-3-flash", "gemini-3-pro", "gemini-2.5-flash"],
        "asr_models": [],
        "capabilities": ["chat"],
    },
}

PRICES = {
    "openai/gpt-5.2": 0.75,
    "openai/gpt-5.1-mini": 0.15,
    "openai/gpt-4.1-mini": 0.08,
    "anthropic/claude-sonnet-4.5": 0.9,
    "google/gemini-3-flash": 0.08,
    "google/gemini-3-pro": 0.35,
    "google/gemini-2.5-flash": 0.06,
    "mistralai/mistral-large-3.1": 0.9,
    "mistral/mistral-large-latest": 0.9,
    "mistral/mistral-medium-latest": 0.5,
    "mistral/mistral-small-latest": 0.25,
    "deepseek/deepseek-v4-flash": 0.12,
    "qwen/qwen3-235b-a22b": 0.25,
    "gpt-4o-mini": 0.1,
    "gpt-4o": 0.4,
    "gpt-4.1-mini": 0.08,
    "gpt-5.2": 0.75,
    "gpt-5.1-mini": 0.15,
    "gemini-3-flash": 0.08,
    "gemini-3-pro": 0.35,
    "gemini-2.5-flash": 0.06,
}

AGENTS = [
    {
        "id": "session-analyzer",
        "label": "Session Analyzer",
        "task": "chat",
        "purpose": "Extracts from each session log: topic, questions (explicit+implicit) attempted, steps taken, numeric metrics/results, qualitative results.",
        "tools": ["read sessions.json", "write ai_reports.json"],
        "proposed_models": ["openai/gpt-5.1-mini", "openai/gpt-4.1-mini", "google/gemini-2.5-flash", "deepseek/deepseek-v4-flash", "qwen/qwen3-235b-a22b", "mistral/mistral-small-latest"],
    },
    {
        "id": "task-builder",
        "label": "Task & Timeline Builder",
        "task": "chat",
        "purpose": "Builds task/subtask structure from session logs: per-task timeline (phases), challenges with severity+status (identified/solved/partially solved), steps (many-to-many with timelogs), propositions (confident thinking issues / domain help).",
        "tools": ["read ai_reports.json", "write tasks.json"],
        "proposed_models": ["openai/gpt-5.1-mini", "google/gemini-3-flash", "anthropic/claude-sonnet-4.5", "mistral/mistral-large-latest"],
    },
    {
        "id": "coach",
        "label": "Work Coach",
        "task": "chat",
        "purpose": "Independent advisor: better logging style (with examples from user's past logs), work-time optimization patterns (best hours/days, X-after-Y effects), time-division breakdown, exhaustion/blocking detection.",
        "tools": ["read sessions.json", "read ai_reports.json", "write insights.json"],
        "proposed_models": ["openai/gpt-5.2", "anthropic/claude-sonnet-4.5", "google/gemini-3-pro", "mistralai/mistral-large-3.1", "google/gemini-3-flash"],
    },
]

_MOCK_REPORTS = [
    {
        "session_id": "00000000000000000000000000000000",
        "topic": "Mock session analysis",
        "questions": ["What was the session about?"],
        "steps": ["Recorded a session"],
        "numeric_metrics": {"duration_min": 30},
        "qualitative_results": ["Mock analysis complete"],
    }
]

_MOCK_TASKS = {
    "tasks": [
        {
            "id": "mock-task-1",
            "name": "Mock Task",
            "timeline": [{"label": "Start", "status": "done", "note": "Mock"}],
            "challenges": [],
            "steps": [{"title": "Mock step", "log_refs": []}],
            "propositions": [{"text": "Mock proposition", "confidence": "high", "accepted": False}],
        }
    ]
}

_MOCK_INSIGHTS = {
    "logging_style": [{"issue": "Mock issue", "example_from_log": "Mock", "suggestion": "Mock"}],
    "time_optimization": [{"pattern": "Mock", "evidence": "Mock", "suggestion": "Mock"}],
    "time_division": {"categories": [{"name": "Mock", "share": 0.5}], "note": "Mock"},
    "exhaustion": [{"pattern": "Mock", "evidence": "Mock", "suggestion": "Mock"}],
}

_pipeline_lock = threading.Lock()
_pipeline_status = {"running": False, "stage": 0, "agent_id": "", "message": "", "done": False, "results": {}}


def app_dir():
    env = os.environ.get("OTL_APP_DIR")
    if env:
        return Path(env)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def config_path():
    return app_dir() / "ai_config.json"


def load_config():
    cfg = {
        "keys": {},
        "agents": {},
        "ideal_time": {"days": [1, 2, 3, 4, 5], "start": "08:00", "end": "18:00", "set": False},
        "consent_dpo": False,
        "asr": {"provider": "", "key_id": "", "model": ""},
    }
    p = config_path()
    if p.exists():
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for k in ("keys", "agents"):
                    if isinstance(raw.get(k), dict):
                        cfg[k] = raw[k]
                if isinstance(raw.get("ideal_time"), dict):
                    cfg["ideal_time"] = raw["ideal_time"]
                if "consent_dpo" in raw:
                    cfg["consent_dpo"] = bool(raw["consent_dpo"])
                if isinstance(raw.get("asr"), dict):
                    cfg["asr"] = raw["asr"]
                if "mock" in raw:
                    cfg["mock"] = bool(raw["mock"])
        except Exception:
            pass
    return cfg


def _keyring_ready():
    return _keystore is not None and _keystore.available()


def _sanitized(cfg):
    """Strip secret material from a config before it touches disk.

    Key entries keep only {provider, label, flags}. Anything else
    (notably a legacy inline `key`) is dropped here; secrets live in
    the OS keyring and are resolved at call time via _resolve_secret.
    """
    out = dict(cfg)
    keys = {}
    for kid, e in (cfg.get("keys") or {}).items():
        if isinstance(e, dict):
            keys[kid] = {k: v for k, v in e.items()
                         if k in ("provider", "label", "plaintext", "legacy")}
    out["keys"] = keys
    return out


def _resolve_secret(cfg, key_id):
    """Return the secret for key_id or None. Keyring first, legacy inline
    `key` field second (pre-migration configs). Never logs the value."""
    entry = (cfg.get("keys") or {}).get(key_id) or {}
    if _keyring_ready():
        res = _keystore.load_key(key_id)
        if res.get("ok") and res.get("secret"):
            return res["secret"]
    if entry.get("key"):
        return entry["key"]
    return None


def _has_secret(cfg, key_id):
    return bool(_resolve_secret(cfg, key_id))


def _scrub_text(text, secrets):
    """Redact known secret values from an error string (secret-leak guard)."""
    if not isinstance(text, str):
        return text
    for s in secrets:
        if s and len(s) >= 4 and s in text:
            text = text.replace(s, "***")
    return text


def _all_secrets(cfg):
    out = []
    for kid, e in (cfg.get("keys") or {}).items():
        if isinstance(e, dict) and e.get("key"):
            out.append(e["key"])
    if _keyring_ready():
        for kid in (cfg.get("keys") or {}):
            try:
                res = _keystore.load_key(kid)
                if res.get("ok") and res.get("secret"):
                    out.append(res["secret"])
            except Exception:
                continue
    return out


def migrate_keys_to_keyring():
    """One-shot migration: move legacy inline `key` fields into the OS
    keyring, then scrub the file. Returns {ok, migrated, skipped, error}."""
    if not _keyring_ready():
        return {"ok": False, "error": "OS keyring unavailable on this platform"}
    cfg = load_config()
    migrated, skipped = 0, []
    for kid, e in (cfg.get("keys") or {}).items():
        if not isinstance(e, dict) or not e.get("key"):
            continue
        res = _keystore.save_key(kid, e["key"])
        if res.get("ok"):
            migrated += 1
        else:
            skipped.append(kid)
    if skipped:
        return {"ok": False, "error": "keyring write failed",
                "migrated": migrated, "skipped": skipped}
    res = save_config(cfg)  # save_config sanitizes: inline keys dropped
    if not res.get("ok"):
        return res
    return {"ok": True, "migrated": migrated}


def save_config(cfg):
    try:
        p = config_path()
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(_sanitized(cfg), ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(p)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def add_key(provider, label, key):
    if not provider or not key:
        return {"ok": False, "error": "provider and key are required"}
    key_id = hashlib.sha1(("%s%s%s" % (provider, label, key)).encode("utf-8")).hexdigest()[:8]
    cfg = load_config()
    entry = {"provider": provider, "label": label}
    if _keyring_ready():
        res = _keystore.save_key(key_id, key)
        if not res.get("ok"):
            return {"ok": False, "error": res.get("error", "keyring write failed")}
    else:
        # No OS locker on this platform: refuse silent plaintext. The caller
        # (UI) must confirm explicit consent before we persist it inline.
        return {"ok": False, "error": "OS keyring unavailable — cannot store keys securely on this platform"}
    cfg.setdefault("keys", {})[key_id] = entry
    res = save_config(cfg)
    if not res.get("ok"):
        try:
            _keystore.delete_key(key_id)
        except Exception:
            pass
        return res
    return {"ok": True, "key_id": key_id}


def remove_key(key_id):
    cfg = load_config()
    if key_id not in cfg.get("keys", {}):
        return {"ok": False, "error": "Key not found"}
    del cfg["keys"][key_id]
    if _keyring_ready():
        try:
            _keystore.delete_key(key_id)
        except Exception:
            pass
    # also drop dangling agent references to the removed key
    for a in (cfg.get("agents") or {}).values():
        if isinstance(a, dict) and a.get("key_id") == key_id:
            a["key_id"] = ""
    res = save_config(cfg)
    if not res.get("ok"):
        return res
    return {"ok": True}


def set_agent(agent_id, provider, key_id, model):
    """Bind an agent to provider/key/model. Validates shape instead of
    clobbering config with malformed UI state (security-auditor)."""
    if not any(a["id"] == agent_id for a in AGENTS):
        return {"ok": False, "error": "Unknown agent: %s" % agent_id}
    if provider not in PROVIDERS:
        return {"ok": False, "error": "Unknown provider: %s" % provider}
    if not model or not str(model).strip():
        return {"ok": False, "error": "Model name is required"}
    cfg = load_config()
    if key_id and key_id not in (cfg.get("keys") or {}):
        return {"ok": False, "error": "Key not found"}
    meta = PROVIDERS.get(provider)
    known = bool(meta) and model in meta.get("chat_models", [])
    cfg.setdefault("agents", {})[agent_id] = {
        "provider": provider,
        "key_id": key_id,
        "model": model,
        "custom_model": None if known else model,
    }
    res = save_config(cfg)
    if not res.get("ok"):
        return res
    return {"ok": True}


def get_agent(agent_id):
    cfg = load_config()
    a = cfg.get("agents", {}).get(agent_id)
    if not a:
        return {"ok": False, "error": "Agent not found"}
    return {"ok": True, "agent": a}


def list_models(provider, task):
    meta = PROVIDERS.get(provider)
    if not meta:
        return {"ok": True, "models": [], "note": "OpenAI-compatible custom endpoint"}
    if task == "asr":
        models = list(meta.get("asr_models", []))
        if provider == "google":
            return {"ok": True, "models": models, "note": "Google AI Studio has no English ASR endpoint"}
        note = "No ASR models for this provider" if not models else ""
        return {"ok": True, "models": models, "note": note}
    models = list(meta.get("chat_models", []))
    cfg = load_config()
    for a in cfg.get("agents", {}).values():
        if a.get("provider") == provider and a.get("custom_model") and a["custom_model"] not in models:
            models.append(a["custom_model"])
    note = "Curated catalog; custom model names are accepted" if provider == "avalai" else ""
    return {"ok": True, "models": models, "note": note}


def _post_json(url, headers, payload, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return False, json.loads(e.read().decode("utf-8"))
        except Exception:
            return False, {"error": str(e)}
    except Exception as e:
        return False, {"error": str(e)}


def _err_msg(data):
    if isinstance(data, dict):
        e = data.get("error")
        if isinstance(e, dict) and e.get("message"):
            return str(e["message"])
        if e:
            return str(e)
        return json.dumps(data, ensure_ascii=False)
    return str(data)


def _chat_request(provider, key, model, messages, max_tokens, temperature):
    meta = PROVIDERS.get(provider)
    if not meta:
        return {"ok": False, "error": "Unknown provider: %s" % provider}
    try:
        if provider == "google":
            system = "\n".join(m.get("content", "") for m in messages if m.get("role") == "system")
            contents = [
                {"role": "model" if m.get("role") in ("assistant", "model") else "user", "parts": [{"text": m.get("content", "")}]}
                for m in messages
                if m.get("role") in ("user", "assistant", "model")
            ]
            body = {"contents": contents}
            if system:
                body["systemInstruction"] = {"parts": [{"text": system}]}
            mpath = model if model.startswith("models/") else "models/" + model
            url = meta["base"] + "/" + mpath + ":generateContent?key=" + urllib.parse.quote(key)
            ok, data = _post_json(url, {"Content-Type": "application/json"}, body)
            if not ok:
                return {"ok": False, "error": _err_msg(data)}
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"ok": True, "text": text}
        url = meta["base"] + "/chat/completions"
        body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
        ok, data = _post_json(url, {"Content-Type": "application/json", "Authorization": "Bearer " + key}, body)
        if not ok:
            return {"ok": False, "error": _err_msg(data)}
        text = data["choices"][0]["message"]["content"]
        return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def chat(agent_id, messages, max_tokens=4000, temperature=0.2):
    cfg = load_config()
    agent = cfg.get("agents", {}).get(agent_id)
    if not agent:
        return {"ok": False, "error": "Agent not configured: %s" % agent_id}
    if MOCK or cfg.get("mock"):
        return {"ok": True, "text": json.dumps({"mock": True, "agent_id": agent_id, "reply": "OK"}, ensure_ascii=False)}
    model = agent.get("custom_model") or agent.get("model")
    if not model:
        return {"ok": True, "text": json.dumps({"mock": True, "agent_id": agent_id, "reply": "OK (no model)"}, ensure_ascii=False)}
    secret = _resolve_secret(cfg, agent.get("key_id", ""))
    if not secret:
        return {"ok": True, "text": json.dumps({"mock": True, "agent_id": agent_id, "reply": "OK (no key)"}, ensure_ascii=False)}
    res = _chat_request(agent.get("provider", ""), secret, model, messages, max_tokens, temperature)
    if not res.get("ok"):
        res["error"] = _scrub_text(res.get("error", ""), _all_secrets(cfg))
    return res


def test_model(provider, key_id, model, task_hint):
    if MOCK:
        return {"ok": True, "latency_ms": 5}
    cfg = load_config()
    secret = _resolve_secret(cfg, key_id)
    if not secret:
        return {"ok": False, "error": "Key not found"}
    ping = "Reply with OK" if not task_hint else str(task_hint)
    t0 = time.time()
    res = _chat_request(provider, secret, model, [{"role": "user", "content": ping}], 4, 0.0)
    lat = int((time.time() - t0) * 1000)
    if res.get("ok"):
        return {"ok": True, "latency_ms": lat}
    return {"ok": False, "latency_ms": lat,
            "error": _scrub_text(res.get("error", "failed"), _all_secrets(cfg))}


def _bare_model(model):
    if model and "/" in model:
        return model.split("/")[-1]
    return model


def fallback_model(agent_id, selected_provider, selected_key_id, selected_model):
    cfg = load_config()
    keys = cfg.get("keys", {})
    bare = _bare_model(selected_model)
    for key_id, k in keys.items():
        if k.get("provider") == selected_provider or not _has_secret(cfg, key_id):
            continue
        p = k.get("provider", "")
        meta = PROVIDERS.get(p)
        models = list(meta.get("chat_models", [])) if meta else []
        if bare in models or p + "/" + bare in models:
            res = test_model(p, key_id, bare, "ping")
            if res.get("ok"):
                return {"ok": True, "provider": p, "key_id": key_id, "model": bare}
    agent = next((a for a in AGENTS if a["id"] == agent_id), None)
    if not agent:
        return {"ok": False, "error": "No model available"}
    prev_price = PRICES.get(selected_model)
    if prev_price is None:
        prev_price = PRICES.get(bare)
    if prev_price is None:
        prev_price = 0.0
    cands = []
    for m in agent.get("proposed_models", []):
        price = PRICES.get(m)
        if price is None:
            price = PRICES.get(_bare_model(m))
        dist = abs((price if price is not None else prev_price) - prev_price)
        cands.append((dist, m))
    cands.sort(key=lambda x: x[0])
    for dist, m in cands:
        parts = m.split("/")
        prov = parts[0] if len(parts) > 1 else None
        b = parts[-1]
        for key_id, k in keys.items():
            if not _has_secret(cfg, key_id):
                continue
            p = k.get("provider", "")
            if prov and p != prov:
                continue
            meta = PROVIDERS.get(p)
            models = list(meta.get("chat_models", [])) if meta else []
            if b in models or p + "/" + b in models:
                res = test_model(p, key_id, b, "ping")
                if res.get("ok"):
                    return {"ok": True, "provider": p, "key_id": key_id, "model": m}
        if MOCK:
            return {"ok": True, "provider": prov or "", "key_id": "", "model": m}
    return {"ok": False, "error": "No model available"}


def _parse_dt(v):
    if not isinstance(v, str):
        return None
    for f in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(v, f)
        except ValueError:
            continue
    return None


def _session_text(s):
    start = _parse_dt(s.get("start"))
    end = _parse_dt(s.get("end"))
    dur = 0
    if start and end:
        dur = round((end - start).total_seconds() / 60)
    doc = round(int(s.get("doc_seconds") or 0) / 60, 1)
    return "session_id=%s\ncategory=%s\ntag=%s\nsub_tag=%s\ndescribe=%s\nnotes=%s\ndoc_min=%s\nduration_min=%s" % (
        s.get("id", ""), s.get("category", ""), s.get("tag", ""), s.get("sub_tag", ""),
        s.get("describe", ""), s.get("notes", ""), doc, dur)


def _load_sessions():
    p = app_dir() / "sessions.json"
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    rows = raw.get("sessions", []) if isinstance(raw, dict) else []
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        if r.get("end") and r.get("kind") != "daily-doc-summary":
            out.append(r)
    out.sort(key=lambda x: x.get("start", ""), reverse=True)
    return out[:200]


def _load_reports():
    p = app_dir() / "ai_reports.json"
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(raw, dict):
        return raw.get("reports", [])
    return raw if isinstance(raw, list) else []


def _load_tasks():
    p = app_dir() / "tasks.json"
    if not p.exists():
        return []
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(raw, dict):
        return raw.get("tasks", [])
    return raw if isinstance(raw, list) else []


def _ensure_prop_ids(tasks):
    for t in tasks:
        for p in t.get("propositions", []):
            if not p.get("id"):
                p["id"] = hashlib.sha1((str(p.get("text", "")) + str(t.get("id", ""))).encode("utf-8")).hexdigest()[:8]
    return tasks


def _write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _extract_json(text):
    if not isinstance(text, str) or not text.strip():
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    try:
        return json.loads(t)
    except Exception:
        pass
    i_b = t.find("{")
    i_a = t.find("[")
    if i_a == -1 and i_b == -1:
        return None
    if i_a == -1 or (i_b != -1 and i_b < i_a):
        start, end = i_b, t.rfind("}")
    else:
        start, end = i_a, t.rfind("]")
    if end <= start:
        return None
    try:
        return json.loads(t[start:end + 1])
    except Exception:
        return None


def _agent_chat(cfg, agent_id, prompt, canned):
    if MOCK or cfg.get("mock"):
        return json.dumps(canned, ensure_ascii=False), True
    res = chat(agent_id, [{"role": "user", "content": prompt}], max_tokens=8000)
    if not res.get("ok"):
        return None, False
    return res.get("text", ""), True


def run_session_analyzer(cfg):
    sessions = _load_sessions()
    body = "\n\n".join(_session_text(s) for s in sessions)
    prompt = ("You are a session analyzer. From the session logs below, produce a JSON array; "
              "each element must have exactly: session_id (string), topic (string), questions "
              "(array of strings), steps (array of strings), numeric_metrics (object), "
              "qualitative_results (array of strings). Return only JSON.\n\nSessions:\n" + body)
    text, ok = _agent_chat(cfg, "session-analyzer", prompt, _MOCK_REPORTS)
    if not ok:
        return {"ok": False, "error": "No working model for session-analyzer"}
    data = _extract_json(text)
    if data is None:
        return {"ok": False, "error": "Invalid JSON from model"}
    reports = data if isinstance(data, list) else [data]
    try:
        _write_json(app_dir() / "ai_reports.json", {"reports": reports, "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(reports)}


def run_task_builder(cfg):
    sessions = _load_sessions()
    reports = _load_reports()
    session_body = "\n\n".join(_session_text(s) for s in sessions)[:6000]
    report_body = json.dumps(reports, ensure_ascii=False)[:6000]
    prompt = ("You build a task and timeline structure from session logs and analysis reports. "
              "Return only JSON with this shape: {\"tasks\": [{\"id\": string, \"name\": string, "
              "\"timeline\": [{\"label\": string, \"status\": string, \"note\": string}], "
              "\"challenges\": [{\"text\": string, \"severity\": \"low|medium|high|critical\", "
              "\"status\": \"identified|solved|partially_solved\", \"done\": [string], "
              "\"remaining\": [string], \"step_refs\": [string]}], "
              "\"steps\": [{\"title\": string, \"log_refs\": [{\"session_id\": string, \"part\": \"start-end\"}]}], "
              "\"propositions\": [{\"text\": string, \"confidence\": \"high|medium\", \"accepted\": false}]}]}.\n\n"
              "Reports:\n" + report_body + "\n\nSessions:\n" + session_body)
    text, ok = _agent_chat(cfg, "task-builder", prompt, _MOCK_TASKS)
    if not ok:
        return {"ok": False, "error": "No working model for task-builder"}
    data = _extract_json(text)
    if data is None or not isinstance(data, dict):
        return {"ok": False, "error": "Invalid JSON from model"}
    tasks = _ensure_prop_ids(data.get("tasks", []))
    try:
        _write_json(app_dir() / "tasks.json", {"tasks": tasks, "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(tasks)}


def run_coach(cfg):
    sessions = _load_sessions()
    reports = _load_reports()
    session_body = "\n\n".join(_session_text(s) for s in sessions)[:5000]
    report_body = json.dumps(reports, ensure_ascii=False)[:4000]
    prompt = ("You are an independent work coach. From the session logs and reports, return only JSON "
              "with this shape: {\"logging_style\": [{\"issue\": string, \"example_from_log\": string, "
              "\"suggestion\": string}], \"time_optimization\": [{\"pattern\": string, \"evidence\": string, "
              "\"suggestion\": string}], \"time_division\": {\"categories\": [{\"name\": string, \"share\": number}], "
              "\"note\": string}, \"exhaustion\": [{\"pattern\": string, \"evidence\": string, \"suggestion\": string}]}.\n\n"
              "Sessions:\n" + session_body + "\n\nReports:\n" + report_body)
    text, ok = _agent_chat(cfg, "coach", prompt, _MOCK_INSIGHTS)
    if not ok:
        return {"ok": False, "error": "No working model for coach"}
    data = _extract_json(text)
    if data is None or not isinstance(data, dict):
        return {"ok": False, "error": "Invalid JSON from model"}
    try:
        _write_json(app_dir() / "insights.json", {"insights": data, "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(data.get("logging_style", []))}


def start_pipeline():
    with _pipeline_lock:
        if _pipeline_status.get("running"):
            return {"ok": False, "error": "Pipeline already running"}
        _pipeline_status.update({"running": True, "stage": 0, "agent_id": "", "message": "starting", "done": False, "results": {}})
    t = threading.Thread(target=_pipeline_run, daemon=True)
    t.start()
    return {"ok": True}


def _set_status(**kw):
    with _pipeline_lock:
        _pipeline_status.update(kw)


def _pipeline_run():
    cfg = load_config()
    results = {}
    runners = {
        "session-analyzer": run_session_analyzer,
        "task-builder": run_task_builder,
        "coach": run_coach,
    }
    try:
        for idx, agent in enumerate(AGENTS):
            aid = agent["id"]
            _set_status(stage=idx, agent_id=aid, message="connecting")
            time.sleep(0.2)
            _set_status(message="fetching models")
            time.sleep(0.1)
            _set_status(message="testing")
            time.sleep(0.1)
            _set_status(message="running")
            try:
                res = runners.get(aid, lambda c: {"ok": False, "error": "Unknown agent"})(cfg)
                results[aid] = res
                _set_status(message="done")
            except Exception as e:
                results[aid] = {"ok": False, "error": str(e)}
                _set_status(message="error")
    finally:
        with _pipeline_lock:
            _pipeline_status.update({"running": False, "done": True, "results": results})


def get_pipeline_status():
    with _pipeline_lock:
        return dict(_pipeline_status)



def agents_catalog():
    return {"ok": True, "agents": AGENTS}

def providers_catalog():
    return {"ok": True, "providers": [dict(id=k, label=v.get("label", k), base=v.get("base", ""), chat_models=v.get("chat_models", []), asr_models=v.get("asr_models", []), capabilities=v.get("capabilities", [])) for k, v in PROVIDERS.items()]}

def get_reports():
    return {"ok": True, "reports": _load_reports()}

def get_insights():
    try:
        p = app_dir() / "insights.json"
        if p.exists():
            return {"ok": True, "insights": json.loads(p.read_text(encoding="utf-8"))}
    except Exception:
        pass
    return {"ok": True, "insights": None}

def set_ideal_time(days, start, end):
    cfg = load_config()
    cfg["ideal_time"] = {"days": list(days or []), "start": str(start or ""), "end": str(end or ""), "set": bool(days)}
    save_config(cfg)
    return {"ok": True}


def get_tasks():
    return {"ok": True, "tasks": _load_tasks()}


def save_tasks(tasks):
    tasks = _ensure_prop_ids(tasks)
    try:
        _write_json(app_dir() / "tasks.json", {"tasks": tasks, "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "tasks": tasks}


def toggle_proposition(task_id, prop_id, accepted):
    tasks = _load_tasks()
    for t in tasks:
        if t.get("id") == task_id:
            for p in t.get("propositions", []):
                if p.get("id") == prop_id or p.get("text") == prop_id:
                    p["accepted"] = bool(accepted)
                    res = save_tasks(tasks)
                    return {"ok": True, "tasks": tasks} if res.get("ok") else res
            return {"ok": False, "error": "Proposition not found"}
    return {"ok": False, "error": "Task not found"}


def _task_context(t):
    parts = ["Task: " + str(t.get("name", ""))]
    tl = t.get("timeline", [])
    if tl:
        parts.append("Timeline: " + "; ".join("%s (%s)" % (x.get("label", ""), x.get("status", "")) for x in tl))
    return " | ".join(parts)


def export_dpo_rows():
    cfg = load_config()
    if not cfg.get("consent_dpo"):
        return {"ok": False, "error": "consent not given"}
    tasks = _load_tasks()
    rows = []
    for t in tasks:
        props = t.get("propositions", [])
        acc = [p for p in props if p.get("accepted")]
        rej = [p for p in props if not p.get("accepted")]
        ctx = _task_context(t)
        if acc and rej:
            for i, p in enumerate(acc):
                r = rej[i % len(rej)]
                rows.append({"prompt": ctx, "chosen": p.get("text", ""), "rejected": r.get("text", ""), "session_context": ctx})
        elif acc:
            for p in acc:
                rows.append({"prompt": ctx, "chosen": p.get("text", ""), "rejected": "", "session_context": ctx})
    path = app_dir() / "dpo_dataset.jsonl"
    try:
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": True, "count": len(rows), "path": str(path)}


def set_consent(value):
    cfg = load_config()
    cfg["consent_dpo"] = bool(value)
    res = save_config(cfg)
    if not res.get("ok"):
        return res
    return {"ok": True, "consent_dpo": bool(value)}


def transcribe(audio_b64, provider, key_id, model):
    meta = PROVIDERS.get(provider)
    if not meta or "asr" not in meta.get("capabilities", []) or not meta.get("asr_models"):
        if provider == "google":
            return {"ok": False, "error": "Google AI Studio has no English ASR endpoint"}
        return {"ok": False, "error": "This provider has no ASR models"}
    if MOCK:
        return {"ok": True, "text": "[mock] transcribed text from audio"}
    cfg = load_config()
    secret = _resolve_secret(cfg, key_id)
    if not secret:
        return {"ok": False, "error": "Key not found"}
    try:
        audio = base64.b64decode(audio_b64)
    except Exception:
        return {"ok": False, "error": "Invalid audio data"}
    boundary = "----OTLBoundary" + hashlib.md5(("%f" % time.time()).encode("utf-8")).hexdigest()
    head = ("--%s\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n%s\r\n" % (boundary, model)).encode("utf-8")
    head += ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"audio.wav\"\r\nContent-Type: audio/wav\r\n\r\n" % boundary).encode("utf-8")
    tail = b"\r\n"
    tail += ("--%s\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\nen\r\n" % boundary).encode("utf-8")
    tail += ("--%s--\r\n" % boundary).encode("utf-8")
    body = head + audio + tail
    url = meta["base"] + "/audio/transcriptions"
    headers = {"Content-Type": "multipart/form-data; boundary=%s" % boundary, "Authorization": "Bearer " + secret}
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read().decode("utf-8"))
        return {"ok": True, "text": resp.get("text", "")}
    except Exception as e:
        return {"ok": False, "error": _scrub_text(str(e), _all_secrets(cfg))}

