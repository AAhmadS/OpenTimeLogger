"""security-auditor acceptance: OS keyring round-trip, no-plaintext config,
migration, validation, secret scrubbing."""
import json
import sys

import pytest

import ai
import keystore

needs_locker = pytest.mark.skipif(
    not keystore.available(), reason="no OS keyring on this platform")


@needs_locker
def test_keystore_round_trip():
    assert keystore.save_key("otl-test-rt", "sk-rt-SECRET")["ok"]
    got = keystore.load_key("otl-test-rt")
    assert got == {"ok": True, "secret": "sk-rt-SECRET"}
    assert keystore.delete_key("otl-test-rt")["ok"]
    assert keystore.load_key("otl-test-rt")["ok"] is False
    assert keystore.delete_key("otl-test-rt")["ok"]  # missing = success


@needs_locker
def test_add_key_stores_ref_only(app_dir):
    res = ai.add_key("openai", "t", "sk-add-SECRET-1")
    assert res.get("ok"), res
    kid = res["key_id"]
    try:
        raw = json.loads((app_dir / "ai_config.json").read_text(encoding="utf-8"))
        entry = raw["keys"][kid]
        assert "key" not in entry, "plaintext secret persisted!"
        assert entry["provider"] == "openai"
        assert keystore.load_key(kid) == {"ok": True, "secret": "sk-add-SECRET-1"}
    finally:
        ai.remove_key(kid)
    assert keystore.load_key(kid)["ok"] is False  # removed from locker too


@needs_locker
def test_migrate_legacy_inline_keys(app_dir):
    cfg = ai.load_config()
    cfg["keys"] = {"legacy1": {"provider": "openai", "label": "old",
                               "key": "sk-legacy-SECRET"}}
    ai.save_config(cfg)  # sanitize must already drop it...
    raw = json.loads((app_dir / "ai_config.json").read_text(encoding="utf-8"))
    assert "key" not in raw["keys"]["legacy1"]
    # ...so simulate a true legacy file, then migrate
    raw["keys"]["legacy1"]["key"] = "sk-legacy-SECRET"
    (app_dir / "ai_config.json").write_text(json.dumps(raw), encoding="utf-8")
    try:
        res = ai.migrate_keys_to_keyring()
        assert res == {"ok": True, "migrated": 1}, res
        raw = json.loads((app_dir / "ai_config.json").read_text(encoding="utf-8"))
        assert "key" not in raw["keys"]["legacy1"]
        assert keystore.load_key("legacy1") == {"ok": True, "secret": "sk-legacy-SECRET"}
    finally:
        keystore.delete_key("legacy1")


def test_save_config_never_persists_secrets(app_dir):
    cfg = ai.load_config()
    cfg["keys"] = {"x": {"provider": "openai", "label": "evil",
                         "key": "sk-should-never-persist"}}
    assert ai.save_config(cfg)["ok"]
    raw = (app_dir / "ai_config.json").read_text(encoding="utf-8")
    assert "sk-should-never-persist" not in raw


def test_set_agent_validation(app_dir):
    assert ai.set_agent("nope", "openai", "", "m")["ok"] is False
    assert ai.set_agent("coach", "nope", "", "m")["ok"] is False
    assert ai.set_agent("coach", "openai", "", "  ")["ok"] is False
    assert ai.set_agent("coach", "openai", "missing-key", "m")["ok"] is False


def test_scrub_redacts_secrets():
    text = ai._scrub_text("401 bad key sk-live-SECRET-99 here", ["sk-live-SECRET-99"])
    assert "sk-live-SECRET-99" not in text and "***" in text
    assert ai._scrub_text("clean error", ["sk-live-SECRET-99"]) == "clean error"


@needs_locker
def test_remove_key_clears_agent_refs(app_dir):
    kid = ai.add_key("openai", "t", "sk-ref-SECRET")["key_id"]
    try:
        assert ai.set_agent("coach", "openai", kid, "gpt-4.1-mini")["ok"]
        assert ai.remove_key(kid)["ok"]
        assert ai.load_config()["agents"]["coach"]["key_id"] == ""
    finally:
        keystore.delete_key(kid)


def test_add_key_refuses_without_locker(app_dir, monkeypatch):
    monkeypatch.setattr(ai, "_keystore", None)
    monkeypatch.setattr(ai, "_keyring_ready", lambda: False)
    res = ai.add_key("openai", "t", "sk-xxx")
    assert res["ok"] is False and "keyring" in res["error"].lower()
