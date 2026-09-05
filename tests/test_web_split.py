"""ui-architect acceptance: web/ split loader integrity.

The parts are the source of truth; the loader must serve them raw
(no Python escape processing). Five historical escape sites are pinned
to their CORRECT (browser-true) file forms — the old giant-string build
silently mangled two of them (sanitize + path-split regexes dropped the
backslash), which this split fixes.
"""
import ui


def test_loader_serves_parts_raw():
    from pathlib import Path
    web = Path(ui.__file__).resolve().parent / "web"
    for name in ("shell_top.html", "styles.css", "head.js", "body.html",
                 "app.js", "shell_tail.html"):
        assert (web / name).is_file(), name
        assert (web / name).read_text(encoding="utf-8")
    assert "UI_HTML = " not in (web / "shell_top.html").read_text(encoding="utf-8")


def test_escape_sites_browser_true():
    js = (ui._web_dir() / "app.js").read_text(encoding="utf-8")
    # Raw files are served byte-for-byte: JS string escapes are SINGLE
    # backslash (newline), while regex literals needing a real backslash
    # stay DOUBLE. (The old giant-string build Python-decoded these, which
    # is exactly the hazard class this split kills.)
    assert r's.replace(/[\\/*?:"<>|]/g,"-")' in js  # regex: match backslash
    assert r'.split(/[\\/]/).pop()' in js  # regex: match backslash
    BS = chr(92)  # one backslash, zero escape ambiguity
    assert "s.replace(/[" + BS * 2 + "/*" in js  # regex: match backslash
    assert ".split(/[" + BS * 2 + "/]/)" in js  # regex: match backslash
    assert 'split("' + BS + 'n")' in js  # JS newline escape
    assert 'ta.value+"' + BS + 'n"' in js  # JS newline escape
    assert "permanently?" + BS + "n" + BS + "n" in js  # 2x newline escape
    assert BS * 2 + "n" not in js  # no double-escaped newlines anywhere


def test_composed_document_structure():
    html = ui.UI_HTML
    assert html.startswith("<!doctype html>")
    assert html.count("<style>") == 1 and html.count("</style>") == 1
    assert html.count("</script>") == 2
    assert html.rstrip().endswith("</html>")
    assert "const AVATAR_URI=null;" in html  # session_logger injects here
    assert len(html) > 100000


def test_no_bom_or_python_artifacts():
    raw = (ui._web_dir() / "shell_top.html").read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert b'"""' not in raw
