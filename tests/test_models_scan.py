"""provider-scanner acceptance: live parse, caps, pricing, cache, estimator."""
import io
import json
import urllib.request

import ai
import models


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _fake_openrouter(req, timeout=30):
    assert "openrouter.ai" in req.full_url
    return _Resp({"data": [
        {"id": "openai/gpt-4o-mini",
         "architecture": {"modality": "text->text", "input_modalities": ["text"]},
         "pricing": {"prompt": "0.00000015", "completion": "0.0000006",
                     "input_cache_read": "0.000000075"}},
        {"id": "openai/whisper-large",
         "architecture": {"modality": "audio->text", "input_modalities": ["audio"]},
         "pricing": {}},
    ]})


def test_openrouter_scan_parse_and_price(app_dir, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", _fake_openrouter)
    res = models.scan("openrouter")
    assert res["ok"], res
    by_id = {m["id"]: m for m in res["models"]}
    assert by_id["openai/gpt-4o-mini"]["caps"] == ["chat"]
    assert by_id["openai/whisper-large"]["caps"] == ["asr"]
    p = models.price_for("openai/gpt-4o-mini")
    assert p["in"] == 0.15 and p["out"] == 0.6 and p["source"] == "live"
    assert (app_dir / "models_cache.json").exists()


def test_cached_models_source_and_staleness(app_dir, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", _fake_openrouter)
    models.scan("openrouter")
    live = ai.list_models("openrouter", "chat")
    assert live["source"] == "live" and live["stale"] is False
    assert "openai/gpt-4o-mini" in live["models"]
    # google ASR: mechanical no-endpoint rule preserved
    asr = ai.list_models("google", "asr")
    assert asr["models"] == [] and "no English ASR" in asr["note"]
    # unknown provider without cache -> labeled seed path
    seed = ai.list_models("mistral", "chat")
    assert seed["source"] == "seed" and seed["stale"] is True
    assert "scan" in seed["note"]


def test_scan_requires_key_where_needed(app_dir):
    assert models.scan("openai")["ok"] is False
    assert models.scan("google")["ok"] is False
    assert models.scan("nope")["ok"] is False


def test_estimator_and_spend(app_dir, monkeypatch):
    (app_dir / "sessions.json").write_text(json.dumps({"sessions": [
        {"id": "s1", "start": "2026-08-03T09:00:00", "end": "2026-08-03T10:00:00",
         "category": "C", "tag": "t", "describe": "d", "notes": "",
         "doc_seconds": 0}]}), encoding="utf-8")
    est = models.estimate_backfill(1)
    assert est["usd_low"] > 0 and est["usd_high"] >= est["usd_low"]
    assert est["basis"].startswith("norm-based")
    import aigraph
    aigraph.meter_call("coach", "openai", "gpt-4o-mini", "x" * 4000, "y" * 400)
    summary = models.spend_summary()
    assert summary["total_usd_est"] > 0
    assert summary["per_agent"]["coach"]["calls"] == 1
    assert summary["basis"].startswith("usage-based")
