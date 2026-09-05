"""backend-hardener acceptance: splits, OTL_APP_DIR, migration, guards."""
import json

import pytest

import store
import export_xlsx as ex
import timelib


def test_timelib_parse_roundtrip():
    assert timelib.to_iso(timelib.parse_time("2026-09-01T09:00:00")) == "2026-09-01T09:00:00"
    assert timelib.parse_time("2026-09-01T09:00") is not None
    assert timelib.parse_time("garbage") is None
    assert timelib.parse_time(None) is None
    assert timelib.minutes_between("2026-09-01T09:00:00", "2026-09-01T10:30:00") == 90.0
    assert timelib.minutes_between("2026-09-01T10:00:00", "2026-09-01T09:00:00") == 0.0


def test_store_honors_otl_app_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("OTL_APP_DIR", str(tmp_path))
    assert store.app_dir() == tmp_path
    assert store.data_file() == tmp_path / "sessions.json"
    st = store.Store()
    assert st.sessions == []
    st.sessions.append(store.new_session("2026-09-01T09:00:00"))
    st._save()
    assert (tmp_path / "sessions.json").exists()
    assert len(store.Store().sessions) == 1


def test_legacy_active_migration_preserves_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("OTL_APP_DIR", str(tmp_path))
    legacy = {"active": {"id": "abc", "start": "2026-09-01T09:00:00",
                         "category": "Coding", "tag": "app", "sub_tag": "x",
                         "describe": "did things", "notes": "n",
                         "doc_seconds": 42},
              "sessions": []}
    (tmp_path / "sessions.json").write_text(json.dumps(legacy), encoding="utf-8")
    st = store.Store()
    assert len(st.sessions) == 1
    s = st.sessions[0]
    assert (s["id"], s["category"], s["tag"], s["sub_tag"], s["describe"],
            s["notes"], s["doc_seconds"]) == (
        "abc", "Coding", "app", "x", "did things", "n", 42)


def test_resolve_inside_blocks_traversal(tmp_path):
    base = tmp_path / "exports"
    base.mkdir()
    ok = store.resolve_inside(base, str(base / "a.xlsx"))
    assert ok.name == "a.xlsx"
    with pytest.raises(ValueError):
        store.resolve_inside(base, str(tmp_path / "sessions.json"))
    with pytest.raises(ValueError):
        store.resolve_inside(base, str(base / ".." / "sessions.json"))
    with pytest.raises(ValueError):
        store.resolve_inside(base, "")
    with pytest.raises(ValueError):
        store.resolve_inside(base, None)


def test_export_name_and_collision(tmp_path):
    rows = [{"start": "2026-09-01T09:00:00"}]
    assert ex.export_name("Coding", "app", "all", rows) == \
        ex._auto_export_name("Coding", "app", "all", rows) + ".xlsx"
    assert ex.export_name("C", "t", "all", rows, "My Report!") == "My_Report!.xlsx"
    assert ex.export_name("C", "t", "all", rows, "???") .endswith(".xlsx")
    (tmp_path / "a.xlsx").write_text("x")
    assert ex._collision_free(tmp_path, "a.xlsx").name == "a_1.xlsx"
    assert ex._collision_free(tmp_path, "b.xlsx").name == "b.xlsx"


def test_workbook_parity():
    pytest.importorskip("openpyxl")
    rows = [
        {"start": "2026-09-01T09:00:00", "end": "2026-09-01T10:00:00",
         "category": "Coding", "tag": "app", "sub_tag": "", "describe": "d",
         "notes": "", "doc_seconds": 600},
        {"start": "2026-09-01T11:00:00", "end": "2026-09-01T11:30:00",
         "category": "Mgmt", "tag": "meet", "sub_tag": "", "describe": "d",
         "notes": "", "doc_seconds": 0},
    ]
    wb = ex.build_workbook(rows, True)
    assert wb.sheetnames == ["Sessions", "By Category", "By Tag", "Documentation daily"]
    ws = wb["Sessions"]
    assert [c.value for c in ws[1]][:4] == ["Start", "End", "Duration (min)", "Doc (min)"]
    ws2 = wb["By Category"]
    names = [r[0].value for r in ws2.iter_rows(min_row=2)]
    assert "Coding" in names and "TOTAL" in names
    total = [r for r in ws2.iter_rows(min_row=2) if r[0].value == "TOTAL"][0]
    assert (total[1].value, total[2].value, total[3].value) == (2, 90, 10)
