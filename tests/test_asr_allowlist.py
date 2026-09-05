"""asr-librarian acceptance: evidenced gate, fail-closed selection."""
import csv
import json
import shutil

import ai


def _ship_allowlist(app_dir):
    src = ai.Path(ai.__file__).resolve().parent / "asr_allowlist.json"
    dst = app_dir / "asr_allowlist.json"
    shutil.copyfile(src, dst)
    return dst


def test_evidence_csv_shape():
    p = ai.Path(ai.__file__).resolve().parent / "docs" / "asr-evidence" / \
        "leaderboard-2026-09-05.csv"
    rows = list(csv.DictReader(p.read_text(encoding="utf-8").splitlines()))
    assert len(rows) == 56, len(rows)
    by_model = {r["model"]: float(r["wer_percent"]) for r in rows}
    assert by_model["Whisper Large v2"] == 4.1
    assert by_model["GPT-4o Transcribe"] == 4.0
    assert by_model["Voxtral Small"] == 2.8
    assert by_model["Scribe v2"] == 2.2
    below4 = [m for m, w in by_model.items() if w < 4.0]
    assert len(below4) == 23, len(below4)


def test_gate_fails_closed(app_dir):
    _ship_allowlist(app_dir)
    al = ai.asr_allowlist()
    assert al["ok"] and al["snapshot_date"] == "2026-09-05"
    assert all(e["status"] != "verified" for e in al["entries"])
    # selection surface: nothing selectable
    assert ai.list_models("openai", "asr")["models"] == []
    assert ai.list_models("mistral", "asr")["models"] == []
    assert "evidence" in ai.list_models("openai", "asr")["note"]
    # google mechanical rule preserved
    g = ai.list_models("google", "asr")
    assert g["models"] == [] and "no English ASR" in g["note"]
    # transcribe refuses suspended models without touching the network
    r = ai.transcribe("e30=", "openai", "k", "whisper-1")
    assert r["ok"] is False and "allowlist" in r["error"]
    r = ai.transcribe("e30=", "openai", "k", "gpt-4o-transcribe")
    assert r["ok"] is False and "verified" in r["error"]
