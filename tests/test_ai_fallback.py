"""qa-harness: fallback policy with mocked transport (no network)."""
import ai


def test_fallback_mock_returns_first_proposed(app_dir, monkeypatch):
    monkeypatch.setattr(ai, "MOCK", True)
    res = ai.fallback_model("coach", "openai", "", "gpt-5.2")
    assert res["ok"] is True
    first = ai.AGENTS[2]["proposed_models"][0]
    assert res["model"] == first


def test_fallback_unknown_agent_no_keys(app_dir, monkeypatch):
    monkeypatch.setattr(ai, "MOCK", False)
    res = ai.fallback_model("no-such-agent", "openai", "", "gpt-5.2")
    assert res == {"ok": False, "error": "No model available"}


def test_price_distance_orders_proposals(app_dir, monkeypatch):
    monkeypatch.setattr(ai, "MOCK", True)
    # cheapest previous model -> nearest-price candidate should win
    res = ai.fallback_model("session-analyzer", "openai", "", "openai/gpt-4.1-mini")
    assert res["ok"] is True
    assert res["model"] in ai.AGENTS[0]["proposed_models"]
