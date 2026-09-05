"""graph-builder-p2 acceptance: B1-B4 nodes, user-wins, critic, DPO."""
import json

import aigraph
import ai


def _seed(app_dir):
    sessions = [
        {"id": "s1", "start": "2026-08-31T09:00:00", "end": "2026-08-31T10:00:00",
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "Auditing, building phase 1 MVP.",
         "notes": "Researched mockups.\n\nHit a login bug, half fixed.", "doc_seconds": 0},
        {"id": "s2", "start": "2026-09-01T09:00:00", "end": "2026-09-01T09:30:00",
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "Phase 1 QA.",
         "notes": "Finished login fix.", "doc_seconds": 0},
    ]
    (app_dir / "sessions.json").write_text(json.dumps({"sessions": sessions}),
                                           encoding="utf-8")
    return aigraph.assign_tasks()["memberships"]


def _run_all(app_dir, monkeypatch):
    tids = [m["task_id"] for m in _seed(app_dir)]
    monkeypatch.setattr(ai, "MOCK", True)
    cfg = ai.load_config()
    res = aigraph.run_task_graph(cfg)
    assert res["ok"], res
    return tids[0]


def test_b1_timeline_improvisation_flagged(app_dir, monkeypatch):
    tid = _run_all(app_dir, monkeypatch)
    t = aigraph.get_task_template(tid)["template"]
    kinds = [p["payload"] for p in t["timeline"]]
    assert len(kinds) == 2
    improvised = [e for e in t["timeline"] if e.get("ai_improvised")]
    assert len(improvised) == 1 and "Phase 2" in improvised[0]["payload"]["name"]


def test_b2_challenge_done_remains(app_dir, monkeypatch):
    tid = _run_all(app_dir, monkeypatch)
    t = aigraph.get_task_template(tid)["template"]
    ch = t["challenges"][0]["payload"]
    assert ch["status"] == "partially_solved"
    assert ch["done"] == ["investigated"] and ch["remaining"] == ["fix", "verify"]
    assert ch["severity"] in ("low", "medium", "high", "critical")


def test_b3_steps_link_real_parts(app_dir, monkeypatch):
    tid = _run_all(app_dir, monkeypatch)
    t = aigraph.get_task_template(tid)["template"]
    assert len(t["steps"]) == 2
    known = set()
    for s in json.loads((app_dir / "sessions.json").read_text(encoding="utf-8"))["sessions"]:
        known.update(p["part_id"] for p in aigraph.split_parts(s))
    for st in t["steps"]:
        for pid in st["payload"]["part_ids"]:
            assert pid in known, pid
    # challenge back-links populated
    linked = [c for c in t["challenges"]
              if (c["payload"].get("step_refs") or [])]
    assert linked
    # transitive map resolves to sessions
    tl = aigraph.challenge_timelogs({"evidence_refs": t["steps"][0]["evidence_refs"]})
    assert {x["session_id"] for x in tl} <= {"s1", "s2"}


def test_n12_user_edits_win(app_dir, monkeypatch):
    tid = _run_all(app_dir, monkeypatch)
    ch_id = aigraph.get_task_template(tid)["template"]["challenges"][0]["id"]
    r = aigraph.user_edit_entity(tid, "challenges", ch_id, {"status": "solved"})
    assert r["status"] == "user_authoritative"
    # agent revision must NOT overwrite -> proposal instead
    r2 = aigraph.revise_entity(tid, "challenges", ch_id, {"status": "identified"},
                               by="agent", reason="miner rerun")
    assert r2["status"] == "proposed"
    t = aigraph.get_task_template(tid)["template"]
    cur = next(e for e in t["challenges"] if e["id"] == ch_id)
    assert cur["payload"]["status"] == "solved"  # user value intact
    assert len(t["proposals"]) == 1
    # second agent proposal supersedes the pending one (max 1)
    aigraph.revise_entity(tid, "challenges", ch_id, {"status": "identified"},
                          by="agent", reason="again")
    t = aigraph.get_task_template(tid)["template"]
    assert len(t["proposals"]) == 1
    # accept applies as user-confirmed content
    pid = t["proposals"][0]["id"]
    r3 = aigraph.accept_proposal(tid, pid, True)
    assert r3["status"] == "user_authoritative"
    t = aigraph.get_task_template(tid)["template"]
    assert t["proposals"] == []


def test_n11_critic_gate():
    excerpts = ["the login bug comes from token expiry after one hour"]
    good = [{"text": "p1", "confidence": "high",
             "grounding": "the login bug comes from token expiry after one hour"}]
    bad = [{"text": "p2", "confidence": "high", "grounding": "unrelated claim xyz"}]
    vague = [{"text": "p3", "confidence": "medium",
              "grounding": "the login bug comes from token expiry after one hour"}]
    kept, rejected = aigraph.critic_filter(good + bad + vague, excerpts)
    assert [p["text"] for p in kept] == ["p1"]
    assert {p["text"] for p in rejected} == {"p2", "p3"}


def test_b4_propositions_and_dpo(app_dir, monkeypatch):
    tid = _run_all(app_dir, monkeypatch)
    t = aigraph.get_task_template(tid)["template"]
    assert t["propositions"], "expected gated propositions"
    prop_id = t["propositions"][0]["id"]
    # consent gate first
    assert aigraph.export_dpo_rows_v2() == {"ok": False, "error": "consent not given"}
    ai.set_consent(True)
    assert aigraph.toggle_proposition_v2(tid, prop_id, True)["ok"] is True
    res = aigraph.export_dpo_rows_v2()
    assert res["count"] == 1, res
    rows = (app_dir / "dpo_rows.jsonl").read_text(encoding="utf-8").splitlines()
    row = json.loads(rows[0])
    assert row["chosen"] != "NO_PROPOSITION" and row["rejected"] == "NO_PROPOSITION"
    assert row["decision"] == "in"
    assert row["trajectory"], "trajectory required"
    assert any(n.get("node") == prop_id for n in row["trajectory"])
