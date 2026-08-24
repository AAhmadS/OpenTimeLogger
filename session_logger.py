import json
import sys
import threading
import uuid
from datetime import datetime, date
from pathlib import Path

try:
    import webview
except ImportError:
    webview = None

from ui import UI_HTML
from brand import AVATAR_DATA_URI

UI_HTML = UI_HTML.replace("const AVATAR_URI=null;",
                          'const AVATAR_URI="%s";' % AVATAR_DATA_URI)

APP_NAME = "Session Logger"

def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR = app_dir()
DATA_FILE = BASE_DIR / "sessions.json"

FMT = "%Y-%m-%dT%H:%M:%S"
FMT_SHORT = "%Y-%m-%dT%H:%M"


def parse_time(v):
    if isinstance(v, datetime):
        return v
    if not isinstance(v, str):
        return None
    for f in (FMT, FMT_SHORT):
        try:
            return datetime.strptime(v, f)
        except ValueError:
            continue
    return None


def to_iso(dt):
    return dt.strftime(FMT)


def now_iso():
    return datetime.now().strftime(FMT)


def new_session(start_iso):
    return {"id": uuid.uuid4().hex, "start": start_iso, "end": None,
            "category": "", "tag": "", "sub_tag": "", "describe": "", "notes": "",
            "doc_seconds": 0}


class Store:
    def __init__(self):
        self._lock = threading.Lock()
        self.sessions = self._load()

    @staticmethod
    def _hydrate(r):
        s = new_session(r.get("start", ""))
        s["id"] = r.get("id", uuid.uuid4().hex)
        s["end"] = r.get("end")
        for k in ("category", "tag", "sub_tag", "describe", "notes"):
            s[k] = r.get(k, "")
        s["doc_seconds"] = r.get("doc_seconds", 0)
        for k in ("kind", "summary_of", "auto_describe", "summary_seconds"):
            if k in r:
                s[k] = r[k]
        return s

    def _load(self):
        raw = {}
        if DATA_FILE.exists():
            try:
                raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            except Exception:
                raw = {}
        out = []
        if "active" in raw:
            act = raw.get("active")
            if act and act.get("start"):
                out.append(new_session(act["start"]))
            for r in raw.get("sessions", []):
                out.append(self._hydrate(r))
        else:
            for r in raw.get("sessions", []):
                out.append(self._hydrate(r))
        out.sort(key=lambda x: x.get("start", ""), reverse=True)
        return out

    def _save(self):
        with self._lock:
            tmp = DATA_FILE.with_suffix(".json.tmp")
            tmp.write_text(json.dumps({"sessions": self.sessions},
                                      ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(DATA_FILE)

    def find(self, sid):
        for s in self.sessions:
            if s["id"] == sid:
                return s
        return None


class Api:
    def __init__(self):
        self.store = Store()
        self._maybe_rollover()

    def _ok(self):
        self._maybe_rollover()
        return {"sessions": sorted(self.store.sessions,
                                   key=lambda x: x.get("start", ""), reverse=True)}

    def _maybe_rollover(self):
        """Log an end-of-day 'documentation' summary for every completed day
        that had documentation time, summing it up per category."""
        changed = False
        today = date.today()
        days = {}
        for s in self.store.sessions:
            if s.get("kind") == "daily-doc-summary":
                continue
            dt = parse_time(s.get("start"))
            if dt is None:
                continue
            days.setdefault(dt.date(), []).append(s)

        for day, sess in days.items():
            if day >= today:
                continue
            total = sum(int(s.get("doc_seconds") or 0) for s in sess)
            if total <= 0:
                continue
            per_cat = {}
            for s in sess:
                cat = s.get("category") or "Uncategorized"
                per_cat[cat] = per_cat.get(cat, 0) + int(s.get("doc_seconds") or 0)
            lines = ["%s: %d min" % (c, round(v / 60))
                     for c, v in sorted(per_cat.items(), key=lambda x: -x[1])]
            auto_describe = " | ".join(lines) + ("  ·  Total: %d min" % round(total / 60))

            existing = [s for s in self.store.sessions
                        if s.get("kind") == "daily-doc-summary"
                        and s.get("summary_of") == day.isoformat()]
            if existing:
                rec = existing[0]
                if rec.get("auto_describe") != auto_describe or rec.get("summary_seconds") != total:
                    if rec.get("describe", "") == rec.get("auto_describe", ""):
                        rec["describe"] = auto_describe
                    rec["auto_describe"] = auto_describe
                    rec["summary_seconds"] = total
                    changed = True
            else:
                key = "%sT23:59:59" % day.isoformat()
                rec = new_session(key)
                rec["end"] = key
                rec["category"] = "Documentation"
                rec["tag"] = "documentation"
                rec["describe"] = auto_describe
                rec["auto_describe"] = auto_describe
                rec["kind"] = "daily-doc-summary"
                rec["summary_of"] = day.isoformat()
                rec["summary_seconds"] = total
                self.store.sessions.append(rec)
                changed = True
        if changed:
            self.store._save()

    def _resolve_when(self, when):
        if not isinstance(when, dict):
            return None, "Invalid time option."
        t = when.get("type")
        if t == "now":
            return now_iso(), None
        if t == "at":
            dt = parse_time(when.get("value"))
            if dt is None:
                return None, "Please choose a valid time."
            return to_iso(dt), None
        return None, "Invalid time option."

    def _parse(self, v):
        dt = parse_time(v)
        if dt is None:
            return None, "Please choose a valid time."
        return to_iso(dt), None

    # ---------- API ----------
    def get_state(self):
        return self._ok()

    def start_session(self, when, data=None):
        iso, err = self._resolve_when(when)
        if err:
            return {"error": err}
        s = new_session(iso)
        data = data or {}
        for k in ("category", "tag", "sub_tag", "describe", "notes"):
            s[k] = str(data.get(k, "")).strip()
        self.store.sessions.append(s)
        self.store._save()
        return self._ok()

    def log_past_session(self, data):
        data = data or {}
        start_iso, err = self._parse(data.get("start"))
        if err:
            return {"error": err}
        end_iso, err = self._parse(data.get("end"))
        if err:
            return {"error": err}
        if end_iso < start_iso:
            return {"error": "End time must be after the start time."}
        s = new_session(start_iso)
        s["end"] = end_iso
        for k in ("category", "tag", "sub_tag", "describe", "notes"):
            s[k] = str(data.get(k, "")).strip()
        self.store.sessions.append(s)
        self.store._save()
        return self._ok()

    def end_session(self, sid, when):
        s = self.store.find(sid)
        if not s:
            return {"error": "Session not found."}
        if s.get("end"):
            return {"error": "Session already ended."}
        iso, err = self._resolve_when(when)
        if err:
            return {"error": err}
        if iso < s["start"]:
            return {"error": "End time cannot be before the start time."}
        s["end"] = iso
        self.store._save()
        return self._ok()

    def update_session(self, sid, fields):
        s = self.store.find(sid)
        if not s:
            return {"error": "Session not found."}
        fields = fields or {}
        new_start, new_end = s["start"], s.get("end")
        if "start" in fields and fields.get("start"):
            iso, err = self._parse(fields["start"])
            if err:
                return {"error": err}
            new_start = iso
        if "end" in fields:
            if fields.get("end") in (None, ""):
                new_end = None
            else:
                iso, err = self._parse(fields["end"])
                if err:
                    return {"error": err}
                new_end = iso
        if new_end and new_end < new_start:
            return {"error": "End time cannot be before the start time."}

        new_vals = {}
        for k in ("category", "tag", "sub_tag", "describe", "notes"):
            if k in fields:
                new_vals[k] = str(fields.get(k) or "").strip()
        if "doc_seconds" in fields:
            try:
                new_vals["doc_seconds"] = max(0, int(fields.get("doc_seconds") or 0))
            except (TypeError, ValueError):
                pass

        eff = dict(s)
        eff.update(new_vals)
        if s.get("kind") != "daily-doc-summary" and new_end is not None:
            if not (eff["category"] and eff["tag"] and eff["describe"]):
                return {"error": "Category, tag and description are required. Sub-tag and notes are optional."}

        s["start"] = new_start
        s["end"] = new_end
        s.update(new_vals)
        self.store._save()
        return self._ok()

    def reopen_session(self, sid):
        s = self.store.find(sid)
        if not s:
            return {"error": "Session not found."}
        s["end"] = None
        self.store._save()
        return self._ok()

    def delete_session(self, sid):
        s = self.store.find(sid)
        if not s:
            return {"error": "Session not found."}
        self.store.sessions.remove(s)
        self.store._save()
        return self._ok()


def main():
    if webview is None:
        print("pywebview is not installed. Run: python -m pip install pywebview")
        return
    api = Api()
    window = webview.create_window(APP_NAME, html=UI_HTML, js_api=api,
                                   width=1080, height=720, min_size=(880, 580),
                                   background_color="#0d131d")
    window.events.closed += api.store._save
    webview.start()


if __name__ == "__main__":
    main()
