"""Live provider catalog (provider-scanner). HTTP-first model discovery,
capability tagging, 4-dimensional pricing, cost estimation + spend summary.

Sources per provider (locked Appendix B.3): OpenAI `/v1/models` (key),
OpenRouter `/api/v1/models` (keyless, includes pricing), Mistral
`/v1/models` (key), Google `v1beta/models` (key, supportedGenerationMethods),
AvalAI OpenAI-compatible `/v1/models` (key). Playwright docs-page backups
are specified in docs/provider-scan.md for when endpoints fail.

Cache: models_cache.json {providers: {pid: {models[], fetched_at, source,
stale}}}. Stale/missing cache -> curated seed, visibly marked.
Pricing unit: USD per 1M tokens {in, out, cache_read, cache_write}.
Seed figures are best-known public prices tagged source 'seed' — the
scanner overwrites them with live data whenever an endpoint provides it.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

CACHE_TTL_SECONDS = 7 * 24 * 3600

DOCS_URLS = {
    "openai": "https://platform.openai.com/docs/models",
    "openrouter": "https://openrouter.ai/models",
    "mistral": "https://docs.mistral.ai/getting-started/models/",
    "google": "https://ai.google.dev/gemini-api/docs/models",
    "avalai": "https://avalai.ir/models",
}

# Seed catalog: curated fallback, honestly labeled. Overwritten by scans.
SEED = {
    "openai": ["gpt-5.2", "gpt-5.1-mini", "gpt-4.1-mini", "o4-mini"],
    "openrouter": ["openai/gpt-5.2", "anthropic/claude-sonnet-4.5",
                   "google/gemini-3-flash", "mistralai/mistral-large-3.1",
                   "deepseek/deepseek-v4-flash", "qwen/qwen3-235b-a22b"],
    "mistral": ["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest"],
    "avalai": ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
    "google": ["gemini-3-flash", "gemini-3-pro", "gemini-2.5-flash"],
}
SEED_ASR = {
    "openai": ["whisper-1", "gpt-4o-transcribe"],
    "avalai": ["whisper-1"],
}

# Seed 4D prices (USD/1M). Source 'seed' = best-known public figures,
# verify before quoting; scanner overwrites with live data when available.
SEED_PRICES = {
    "gpt-4o-mini": {"in": 0.15, "out": 0.60, "cache_read": 0.075, "cache_write": None},
    "gpt-4o": {"in": 2.50, "out": 10.00, "cache_read": 1.25, "cache_write": None},
    "gpt-4.1-mini": {"in": 0.40, "out": 1.60, "cache_read": 0.10, "cache_write": None},
    "gpt-5.2": {"in": 1.75, "out": 14.00, "cache_read": 0.175, "cache_write": None},
    "gpt-5.1-mini": {"in": 0.40, "out": 3.20, "cache_read": 0.04, "cache_write": None},
    "o4-mini": {"in": 1.10, "out": 4.40, "cache_read": 0.275, "cache_write": None},
    "mistral-large-latest": {"in": 2.00, "out": 6.00, "cache_read": None, "cache_write": None},
    "mistral-medium-latest": {"in": 0.40, "out": 2.00, "cache_read": None, "cache_write": None},
    "mistral-small-latest": {"in": 0.10, "out": 0.30, "cache_read": None, "cache_write": None},
    "gemini-3-flash": {"in": 0.50, "out": 3.00, "cache_read": 0.05, "cache_write": None},
    "gemini-3-pro": {"in": 2.00, "out": 12.00, "cache_read": 0.20, "cache_write": None},
    "gemini-2.5-flash": {"in": 0.30, "out": 2.50, "cache_read": 0.03, "cache_write": None},
}


def _app_dir():
    import ai
    return ai.app_dir()


def _cache_path():
    return _app_dir() / "models_cache.json"


def read_cache():
    p = _cache_path()
    if not p.exists():
        return {"providers": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"providers": {}}
    except (OSError, ValueError):
        return {"providers": {}}


def _write_cache(data):
    p = _cache_path()
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def _get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _caps_for(model_id, asr_hint=False):
    mid = model_id.lower()
    if any(k in mid for k in ("whisper", "transcribe", "stt", "asr", "nova", "parakeet")):
        return ["asr"]
    if asr_hint:
        return ["asr"]
    return ["chat"]


def _bare(model_id):
    return model_id.split("/")[-1] if "/" in model_id else model_id


def _price_from_openrouter(pricing):
    """OpenRouter pricing strings are USD/unit-token; scale to USD/1M."""
    if not isinstance(pricing, dict):
        return None
    try:
        def f(key):
            v = pricing.get(key)
            return float(v) * 1_000_000 if v is not None else None
        return {"in": f("prompt"), "out": f("completion"),
                "cache_read": f("input_cache_read") or f("discount"),
                "cache_write": f("input_cache_write")}
    except (TypeError, ValueError):
        return None


def scan(provider, key=None):
    """Live-scan one provider. Returns {ok, models[{id, caps, pricing,
    source}], source} and updates the cache on success."""
    import ai
    meta = ai.PROVIDERS.get(provider)
    if not meta:
        return {"ok": False, "error": "Unknown provider: %s" % provider}
    base = meta["base"]
    models = []
    try:
        if provider == "openrouter":
            data = _get(base + "/models")
            for m in data.get("data", []):
                mid = m.get("id", "")
                arch = (m.get("architecture") or {})
                modality = "%s %s" % (arch.get("modality", ""), arch.get("input_modalities", ""))
                caps = ["asr"] if "audio" in modality and "text" not in modality else ["chat"]
                if any(k in mid.lower() for k in ("whisper", "transcribe")):
                    caps = ["asr"]
                price = _price_from_openrouter(m.get("pricing")) or \
                    SEED_PRICES.get(_bare(mid))
                models.append({"id": mid, "caps": caps, "pricing": price,
                               "source": "live-openrouter" if price and price != SEED_PRICES.get(_bare(mid)) else "seed"})
        elif provider == "google":
            if not key:
                return {"ok": False, "error": "API key required for Google model list"}
            data = _get(base + "/models?key=" + urllib.parse.quote(key))
            for m in data.get("models", []):
                name = m.get("name", "").replace("models/", "")
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" not in methods:
                    continue  # mechanically documents the no-ASR rule
                models.append({"id": name, "caps": ["chat"],
                               "pricing": SEED_PRICES.get(_bare(name)), "source": "live-google"})
        else:
            # OpenAI-compatible: openai, mistral, avalai
            if not key:
                return {"ok": False, "error": "API key required for %s model list" % provider}
            data = _get(base + "/models", {"Authorization": "Bearer " + key})
            for m in data.get("data", []):
                mid = m.get("id", "")
                caps = _caps_for(mid)
                models.append({"id": mid, "caps": caps,
                               "pricing": SEED_PRICES.get(_bare(mid)), "source": "live-" + provider})
        if not models:
            return {"ok": False, "error": "provider returned no usable models"}
        cache = read_cache()
        cache.setdefault("providers", {})[provider] = {
            "models": models, "fetched_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "source": "live", "docs": DOCS_URLS.get(provider, "")}
        _write_cache(cache)
        return {"ok": True, "models": models, "source": "live"}
    except Exception as e:
        return {"ok": False, "error": "scan failed: %s" % e}


def cached_models(provider, task="chat"):
    """Models for a provider: live cache when fresh, else labeled seed."""
    cache = read_cache()
    entry = (cache.get("providers") or {}).get(provider)
    fresh = False
    if entry:
        try:
            fetched = entry.get("fetched_at", "2000-01-01T00:00:00")
            fmt = "%Y-%m-%dT%H:%M:%S" if len(fetched) > 16 else "%Y-%m-%dT%H:%M"
            age = (datetime.now() - datetime.strptime(fetched, fmt)).total_seconds()
            fresh = age < CACHE_TTL_SECONDS
        except ValueError:
            fresh = False
    if entry and fresh:
        models = [m["id"] for m in entry.get("models", [])
                  if task in (m.get("caps") or []) or task == "chat" and "chat" in (m.get("caps") or [])]
        return {"ok": True, "models": models, "source": "live",
                "fetched_at": entry.get("fetched_at"), "stale": False,
                "note": ""}
    import ai
    meta = ai.PROVIDERS.get(provider, {})
    if task == "asr":
        seed = list(meta.get("asr_models", []) or SEED_ASR.get(provider, []))
        if provider == "google":
            return {"ok": True, "models": [], "source": "seed", "stale": True,
                    "note": "Google AI Studio has no English ASR endpoint"}
        note = "Seed list — run a live scan for current availability" if seed \
            else "No ASR models for this provider"
        return {"ok": True, "models": seed, "source": "seed", "stale": True, "note": note}
    seed = list(meta.get("chat_models", []) or SEED.get(provider, []))
    return {"ok": True, "models": seed, "source": "seed", "stale": True,
            "note": "Seed list — run a live scan for current availability"}


def price_for(model_id):
    """4D price lookup: live cache first, seed second, None when unknown."""
    bare = _bare(model_id)
    cache = read_cache()
    for entry in (cache.get("providers") or {}).values():
        for m in (entry.get("models") or []):
            if m.get("id") == model_id or _bare(m.get("id", "")) == bare:
                if m.get("pricing"):
                    return dict(m["pricing"], source="live")
    if bare in SEED_PRICES:
        return dict(SEED_PRICES[bare], source="seed")
    if model_id in SEED_PRICES:
        return dict(SEED_PRICES[model_id], source="seed")
    return None


def _configured_model_price(cfg, agent_id):
    a = (cfg.get("agents") or {}).get(agent_id) or {}
    model = a.get("custom_model") or a.get("model")
    if not model:
        return None, None
    return model, price_for(model)


def estimate_backfill(n_sessions):
    """Norm-based D1 cost projection (locked spend decision).

    Basis: ~1200 input tokens/session for extraction, shared task-builder
    context ~6000 + 400/task, coach ~9000 per weekly refresh. Output ~25%
    of input. Uses each agent's configured model price when known, else the
    cheapest seed price (low) / most expensive (high) as bounds.
    All figures labeled estimated.
    """
    import ai
    cfg = ai.load_config()
    known = []
    for aid in ("session-analyzer", "task-builder", "coach"):
        model, price = _configured_model_price(cfg, aid)
        if price and price.get("in") is not None:
            known.append(price["in"])
    ins = [p for p in [SEED_PRICES[m]["in"] for m in SEED_PRICES if SEED_PRICES[m]["in"] is not None]]
    lo_in, hi_in = (min(known), max(known)) if known else (min(ins), max(ins))
    lo_out, hi_out = lo_in * 3, hi_in * 3
    tasks = max(1, n_sessions // 8)
    tok_in = n_sessions * 1200 + tasks * 400 + 6000 + 9000
    tok_out = int(tok_in * 0.25)
    return {"ok": True, "basis": "norm-based estimate",
            "input_tokens_est": tok_in, "output_tokens_est": tok_out,
            "usd_low": round(tok_in / 1e6 * lo_in + tok_out / 1e6 * lo_out, 4),
            "usd_high": round(tok_in / 1e6 * hi_in + tok_out / 1e6 * hi_out, 4),
            "sessions": n_sessions}


def spend_summary():
    """Usage-based spend from Run Log metering (locked: per-agent + total,
    inferred automatically). Token counts are estimates (len//4)."""
    import aigraph
    per_agent, unknown = {}, 0
    for r in aigraph.read_runs(10000):
        if r.get("kind") != "llm_call":
            continue
        price = price_for(r.get("model", "")) or {}
        pin, pout = price.get("in"), price.get("out")
        if pin is None or pout is None:
            unknown += 1
            continue
        cost = r.get("prompt_est", 0) / 1e6 * pin + r.get("completion_est", 0) / 1e6 * pout
        a = per_agent.setdefault(r.get("agent_id", "?"), {"calls": 0, "usd_est": 0.0})
        a["calls"] += 1
        a["usd_est"] = round(a["usd_est"] + cost, 6)
    total = round(sum(a["usd_est"] for a in per_agent.values()), 6)
    return {"ok": True, "basis": "usage-based estimate from metered calls",
            "per_agent": per_agent, "total_usd_est": total,
            "unpriced_calls": unknown}
