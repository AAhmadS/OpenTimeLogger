"""qa-harness: analytics golden numbers over a fixture corpus."""
import json

import analytics


def _fixture(path):
    sessions = [
        {"id": "a1", "start": "2026-08-31T09:00:00", "end": "2026-08-31T10:00:00",
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "d",
         "notes": "", "doc_seconds": 0},
        {"id": "b1", "start": "2026-08-31T22:00:00", "end": "2026-08-31T23:00:00",
         "category": "Reading", "tag": "pdf", "sub_tag": "", "describe": "d",
         "notes": "", "doc_seconds": 0},
        {"id": "a2", "start": "2026-09-01T14:00:00", "end": "2026-09-01T14:30:00",
         "category": "Coding", "tag": "app", "sub_tag": "x", "describe": "d",
         "notes": "", "doc_seconds": 600},
        # synthetic summary + active session: both excluded from work metrics
        {"id": "s1", "start": "2026-08-31T23:59:59", "end": "2026-08-31T23:59:59",
         "category": "Documentation", "tag": "documentation",
         "kind": "daily-doc-summary", "summary_seconds": 600},
        {"id": "c1", "start": "2026-09-01T15:00:00", "end": None,
         "category": "Coding", "tag": "app", "describe": "d", "doc_seconds": 0},
    ]
    path.write_text(json.dumps({"sessions": sessions}), encoding="utf-8")
    return path


def test_golden_overview_and_daily_nightly(tmp_path, monkeypatch):
    monkeypatch.setattr(analytics, "DATA_FILE", _fixture(tmp_path / "s.json"))
    d = analytics.compute_dashboard("all")
    assert d["overview"]["total_sessions"] == 3
    assert d["overview"]["total_minutes"] == 150.0
    assert d["overview"]["total_doc_minutes"] == 10.0
    assert d["overview"]["active_count"] == 1
    dn = d["daily_nightly"]
    assert (dn["daily_count"], dn["nightly_count"]) == (2, 1)
    assert (dn["daily_minutes"], dn["nightly_minutes"]) == (90.0, 60.0)


def test_golden_categories_and_heatmap(tmp_path, monkeypatch):
    monkeypatch.setattr(analytics, "DATA_FILE", _fixture(tmp_path / "s.json"))
    d = analytics.compute_dashboard("all")
    cats = {c["category"]: c for c in d["categories"]}
    assert cats["Coding"]["minutes"] == 90.0
    assert cats["Coding"]["sessions"] == 2
    assert cats["Reading"]["minutes"] == 60.0
    subs = {s["sub_tag"]: s for s in cats["Coding"]["sub_tags"]}
    assert subs["x"]["minutes"] == 30.0
    hm = d["heatmap"]["minutes"]
    assert hm[0][9] == 60.0 and hm[0][22] == 60.0  # Monday hours
