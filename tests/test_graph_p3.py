"""graph-builder-p3 acceptance: patterns, confounder math, division, coach."""
import json

import aigraph
import ai


def _seed(app_dir):
    # 12 sessions: Coding dominates mornings, Mgmt afternoons; one 3h gap.
    sessions = []
    days = ["2026-08-%02d" % d for d in range(3, 15)]
    i = 0
    for d in days:
        sessions.append({"id": "c%d" % i, "start": "%sT09:00:00" % d,
                         "end": "%sT10:00:00" % d, "category": "Coding",
                         "tag": "app", "sub_tag": "", "describe": "Built feature %d." % i,
                         "notes": "Implemented the parser module.", "doc_seconds": 0})
        i += 1
        sessions.append({"id": "m%d" % i, "start": "%sT15:00:00" % d,
                         "end": "%sT15:30:00" % d, "category": "Mgmt",
                         "tag": "meet", "sub_tag": "", "describe": "Sync meeting notes.",
                         "notes": "Discussed the parser module timeline.", "doc_seconds": 0})
        i += 1
    (app_dir / "sessions.json").write_text(json.dumps({"sessions": sessions}),
                                           encoding="utf-8")


def test_n14_patterns_use_own_excerpts(app_dir):
    _seed(app_dir)
    res = aigraph.maintain_patterns()
    assert res["shapes"] >= 2, res
    shapes = json.loads((app_dir / "patterns.json").read_text(encoding="utf-8"))
    for sh in shapes.values():
        assert sh["examples"], sh["shape_id"]
        assert sh["recurrence_count"] >= 1


def test_n19_computed_findings(app_dir):
    _seed(app_dir)
    res = aigraph.check_confounders()
    assert res["claims"] >= 2, res  # hour + weekday have n>=5
    store = json.loads((app_dir / "findings.json").read_text(encoding="utf-8"))
    by_id = {f["id"]: f for f in store["findings"]}
    assert by_id["f-hour"]["verdict"] == "claim"
    assert by_id["f-hour"]["n"] >= 5
    assert "weekday" in by_id["f-hour"]["confounders_checked"] + \
        by_id["f-hour"]["residual_confounders"]
    # tiny corpus -> insufficient_data, never a claim
    (app_dir / "sessions.json").write_text(json.dumps({"sessions": [
        {"id": "x1", "start": "2026-08-03T09:00:00", "end": "2026-08-03T10:00:00",
         "category": "Coding", "tag": "t", "describe": "d", "notes": "",
         "doc_seconds": 0}]}), encoding="utf-8")
    aigraph.check_confounders()
    store = json.loads((app_dir / "findings.json").read_text(encoding="utf-8"))
    assert all(f["verdict"] == "insufficient_data" for f in store["findings"])


def test_n17_division_numbers(app_dir):
    _seed(app_dir)
    div = aigraph.divide_time()
    coding = next(s for s in div["shares"] if s["name"] == "Coding")
    assert coding["share"] > 0.6  # 60min vs 30min daily
    assert div["edge"]["n"] == 24
    assert div["edge"]["p90_min"] == 60.0
    assert div["trend"], "expected weekly trend rows"


def test_n15_points_cite_real_shapes(app_dir, monkeypatch):
    _seed(app_dir)
    aigraph.maintain_patterns()
    monkeypatch.setattr(ai, "MOCK", True)
    pts = aigraph.run_style_critic(ai.load_config())["points"]
    assert pts, "expected style points from recurring shapes"
    shapes = json.loads((app_dir / "patterns.json").read_text(encoding="utf-8"))
    for p in pts:
        assert p["example_from_log"] in shapes[p["pattern_shape_id"]]["examples"]


def test_n20_claims_verbatim_or_appended(app_dir, monkeypatch):
    _seed(app_dir)
    monkeypatch.setattr(ai, "MOCK", True)
    aigraph.maintain_patterns()
    aigraph.check_confounders()
    r = aigraph.render_coach(ai.load_config())
    assert r["claims"] >= 2 and r["appended_raw"] == 0, r
    coach = aigraph.get_coach()["coach"]
    store = json.loads((app_dir / "findings.json").read_text(encoding="utf-8"))
    for f in store["findings"]:
        if f.get("verdict") == "claim":
            claim_line = "%s [n=%s" % (f["claim"], f["n"])
            assert claim_line in coach["body"], claim_line
    # ideal-time ask present until set
    assert "Ideal hours" in coach["body"]


def test_coach_refresh_pipeline(app_dir, monkeypatch):
    _seed(app_dir)
    monkeypatch.setattr(ai, "MOCK", True)
    res = aigraph.run_coach_refresh(ai.load_config())
    assert res["ok"] and res["findings"]["claims"] >= 2, res
    assert aigraph.get_coach()["coach"] is not None
