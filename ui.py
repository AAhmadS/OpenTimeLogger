"""Interval UI shell (ui-architect split).

UI_HTML is composed at import from web/ parts (single source of truth):
  shell_top.html, styles.css, head.js, body.html, app.js, shell_tail.html

Source checkout: web/ lives next to this file. Frozen builds ship web/ as
PyInstaller datas, resolved via sys._MEIPASS (see OpenTimeLogger.spec).

No Python escape processing touches the assets — bytes on disk are
byte-for-byte what the browser gets. This eliminates the old hazard where
JS "\\n" silently became real newlines inside the giant Python string
(which once blanked the whole app at runtime).
"""
import sys
from pathlib import Path


def _web_dir():
    base = getattr(sys, "_MEIPASS", None)
    if base:
        p = Path(base) / "web"
        if p.is_dir():
            return p
    here = Path(__file__).resolve().parent / "web"
    if here.is_dir():
        return here
    raise RuntimeError("UI assets missing: web/ directory not found")


def _read(name):
    return (_web_dir() / name).read_text(encoding="utf-8")


def _compose():
    top = _read("shell_top.html")
    css = _read("styles.css")
    head_js = _read("head.js").rstrip("\n")
    body = _read("body.html")
    app_js = _read("app.js")
    tail = _read("shell_tail.html")
    return (top + "<style>\n" + css + "</style>\n"
            + "<script>" + head_js + "</script>\n"
            + "</head>\n" + body
            + "<script>\n" + app_js + "</script>\n" + tail)


UI_HTML = _compose()
