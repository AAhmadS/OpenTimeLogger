"""Paths, JSON store, and shared backend helpers (backend-hardener split).

- app_dir(): OTL_APP_DIR env (tests/preview) > frozen exe dir > source dir.
  This unifies session_logger/ai/analytics, which previously resolved
  differently (session_logger ignored OTL_APP_DIR entirely).
- Store: thread-safe sessions.json load/save with legacy migration.
- resolve_inside(): single path-traversal guard for export file ops.
- get_logger(): stdlib rotating file log (logs/app.log).
"""
import json
import logging
import os
import sys
import threading
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path

from timelib import now_iso

SESSION_FIELDS = ("category", "tag", "sub_tag", "describe", "notes")
SUMMARY_FIELDS = ("kind", "summary_of", "auto_describe", "summary_seconds")


def app_dir():
    env = os.environ.get("OTL_APP_DIR")
    if env:
        return Path(env)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def data_file():
    return app_dir() / "sessions.json"


def exports_dir():
    return app_dir() / "exports"


def new_session(start_iso):
    return {"id": uuid.uuid4().hex, "start": start_iso, "end": None,
            "category": "", "tag": "", "sub_tag": "", "describe": "", "notes": "",
            "doc_seconds": 0}


def resolve_inside(base_dir, user_path):
    """Resolve user_path and ensure it stays inside base_dir.

    Returns the resolved Path. Raises ValueError on traversal/odd input.
    """
    if not user_path or not isinstance(user_path, str):
        raise ValueError("Invalid path")
    try:
        base = Path(base_dir).resolve()
        p = Path(user_path).resolve()
    except Exception:
        raise ValueError("Invalid path")
    if p != base and base not in p.parents:
        raise ValueError("Access denied")
    return p


_log = None


def get_logger(name="interval"):
    """Process-wide rotating file logger. Never raises."""
    global _log
    if _log is not None:
        return _log.getChild(name) if name != "interval" else _log
    try:
        logger = logging.getLogger("interval")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            fh = RotatingFileHandler(str(_log_path()),
                                     maxBytes=512 * 1024, backupCount=2, encoding="utf-8")
            fh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
            logger.addHandler(fh)
        _log = logger
    except Exception:
        _log = logging.getLogger("interval-null")
    return _log.getChild(name) if name != "interval" else _log


def _log_path():
    d = app_dir() / "logs"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    return d / "app.log"


class Store:
    def __init__(self, data_file_path=None):
        self._lock = threading.Lock()
        self._file = Path(data_file_path) if data_file_path else data_file()
        self.sessions = self._load()

    @staticmethod
    def _hydrate(r):
        s = new_session(r.get("start", ""))
        s["id"] = r.get("id", uuid.uuid4().hex)
        s["end"] = r.get("end")
        for k in SESSION_FIELDS:
            s[k] = r.get(k, "")
        s["doc_seconds"] = r.get("doc_seconds", 0)
        for k in SUMMARY_FIELDS:
            if k in r:
                s[k] = r[k]
        return s

    def _load(self):
        log = get_logger("store")
        raw = {}
        if self._file.exists():
            try:
                raw = json.loads(self._file.read_text(encoding="utf-8"))
            except (OSError, ValueError) as e:
                log.warning("sessions.json unreadable, starting empty: %s", e)
                raw = {}
        out = []
        if "active" in raw:
            # legacy format: migrate the in-flight session WITH all fields
            # (previous code kept only start — silent data loss).
            act = raw.get("active")
            if isinstance(act, dict) and act.get("start"):
                migrated = self._hydrate(act)
                migrated["id"] = act.get("id", migrated["id"])
                out.append(migrated)
            for r in raw.get("sessions", []):
                out.append(self._hydrate(r))
        else:
            for r in raw.get("sessions", []):
                out.append(self._hydrate(r))
        out.sort(key=lambda x: x.get("start", ""), reverse=True)
        return out

    def _save(self):
        with self._lock:
            tmp = self._file.with_suffix(".json.tmp")
            tmp.write_text(json.dumps({"sessions": self.sessions},
                                      ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._file)

    def find(self, sid):
        for s in self.sessions:
            if s["id"] == sid:
                return s
        return None
