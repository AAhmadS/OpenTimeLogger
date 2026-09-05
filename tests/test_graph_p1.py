"""graph-builder-p1 acceptance: N2/N3/N5/N9/N22/N23 + tick/D1/D3."""
import json

import aigraph
import ai


def _seed(app_dir):
    sessions = [
        {"id": "s1", "start": "2026-08-31T09:00:00", "end": "2026-08-31T10:00:00",
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "Built X.",
         "notes": "First did A.\n\nThen did B.", "doc_seconds": 0},
        {"id": "s2", "start": "2026-09-01T09:00:00", "end": "2026-09-01T09:30:00",
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "Built Y.",
         "notes": "", "doc_seconds": 0},
        {"id": "s3", "start": "2026-09-10T09:00:00", "end": "2026-09-10T09:10:00",
         "category": "Mgmt", "tag": "meet", "sub_tag": "", "describe": "Sync.",
         "notes": "", "doc_seconds": 0},
    ]
    (app_dir / "sessions.json").write_text(json.dumps({"sessions": sessions}),
                                           encoding="utf-8")
    return sessions


def test_n2_detect_and_commit(app_dir):
    _seed(app_dir)
    cs = aigraph.detect_changes()
    assert cs["materiality"] == "structural" and set(cs["added"]) == {"s1", "s2", "s3"}
    aigraph.commit_snapshot(cs["hashes"])
    cs2 = aigraph.detect_changes()
    assert cs2["materiality"] == "none"


def test_n2_edit_detection(app_dir):
    _seed(app_dir)
    aigraph.commit_snapshot(aigraph.detect_changes()["hashes"])
    raw = json.loads((app_dir / "sessions.json").read_text(encoding="utf-8"))
    raw["sessions"][0]["notes"] = "changed"
    (app_dir / "sessions.json").write_text(json.dumps(raw), encoding="utf-8")
    cs = aigraph.detect_changes()
    assert cs["edited"] == ["s1"] and cs["materiality"] == "structural"


def test_n3_parts_stable_ids(app_dir):
    sessions = _seed(app_dir)
    parts = aigraph.split_parts(sessions[0])
    assert [p["kind"] for p in parts] == ["describe", "notes", "notes"]
    assert abs(sum(p["duration_min"] for p in parts) - 60.0) < 0.01
    assert aigraph.split_parts(sessions[0])[0]["part_id"] == parts[0]["part_id"]


def test_n5_assign_groups(app_dir):
    _seed(app_dir)
    res = aigraph.assign_tasks()
    assert res["ok"] and res["tasks"] == 2
    by_name = {m["name"]: m for m in res["memberships"]}
    assert set(by_name["Coding: app"]["session_ids"]) == {"s1", "s2"}
    assert by_name["Coding: app"]["confidence"] == "rule"


def test_n9_index_and_n22_verify(app_dir):
    _seed(app_dir)
    s = json.loads((app_dir / "sessions.json").read_text(encoding="utf-8"))["sessions"][0]
    parts = aigraph.split_parts(s)
    aigraph.index_upsert("report:s1", [{"session_id": "s1", "part_id": p["part_id"],
                                        "span": p["span"], "excerpt_hash": p["excerpt_hash"]}
                                       for p in parts])
    assert len(aigraph.index_get("report:s1")) == 3
    good = {"session_id": "s1", "topic": "t", "questions": ["q"],
            "steps_taken": ["s"], "numeric_metrics": {},
            "qualitative_results": ["r"]}
    assert aigraph.verify("session_report", good)["ok"] is True
    bad = dict(good, topic="")
    assert aigraph.verify("session_report", bad)["ok"] is False
    assert aigraph.verify("nope", {})["ok"] is False


def test_n4_v2_mock_shape(app_dir, monkeypatch):
    _seed(app_dir)
    monkeypatch.setattr(ai, "MOCK", True)
    res = aigraph.run_session_analyzer_v2(ai.load_config())
    assert res["done"] == 3, res
    store = json.loads((app_dir / "session_reports.json").read_text(encoding="utf-8"))
    rep = store["reports"][0]
    for k in aigraph.A_SCHEMA:
        assert k in rep, k


def test_n21_tick_backfill_once(app_dir, monkeypatch):
    _seed(app_dir)
    monkeypatch.setattr(ai, "MOCK", True)
    monkeypatch.setattr(aigraph, "TICK_THROTTLE_SECONDS", 0)
    cfg = ai.load_config()
    cfg["keys"] = {"k1": {"provider": "openai", "label": "t"}}
    ai.save_config(cfg)
    out = aigraph.tick(force=True)
    assert "backfill" in out["started"], out
    for _ in range(100):  # wait for daemon thread (mock = fast)
        import time
        st = aigraph.graph_status()["scheduler"]
        if st.get("backfill_done"):
            break
        time.sleep(0.1)
    assert aigraph.graph_status()["reports"] == 3
    out2 = aigraph.tick(force=True)
    assert "backfill" not in out2["started"]  # exactly once


def test_metering_sink(app_dir):
    aigraph.meter_call("coach", "openai", "m", "prompt text here", "completion")
    runs = aigraph.read_runs(5)
    assert runs and runs[-1]["kind"] == "llm_call"
    assert runs[-1]["prompt_est"] == len("prompt text here") // 4
