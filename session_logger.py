import os
import subprocess
import sys
from datetime import datetime, date

try:
    import webview
except ImportError:
    webview = None

try:
    import openpyxl  # noqa: F401 (export_xlsx imports it lazily too)
except ImportError:
    openpyxl = None

try:
    import analytics as _analytics
except ImportError:
    _analytics = None

try:
    import ai as _ai
except ImportError:
    _ai = None

try:
    import aigraph as _graph
except ImportError:
    _graph = None

from timelib import FMT, parse_time, to_iso, now_iso
from store import Store, new_session, data_file, exports_dir, resolve_inside, get_logger
from export_xlsx import filter_sessions, build_workbook, export_name, _collision_free

from ui import UI_HTML
from brand import AVATAR_DATA_URI

UI_HTML = UI_HTML.replace("const AVATAR_URI=null;",
                          'const AVATAR_URI="%s";' % AVATAR_DATA_URI)

APP_NAME = "Interval"

log = get_logger("api")


class Api:
    def __init__(self):
        self.store = Store()
        self._last_rollover_day = None
        self._last_doc_total = None
        self._maybe_rollover()
        self._win = None

    def _ok(self):
        self._maybe_rollover()
        # store.sessions is kept sorted desc on every mutation, so no sort needed here
        # (previous version sorted on every call => O(n log n) on each tab visit)
        return {"sessions": self.store.sessions[:]}

    # ---------- window controls (frameless titlebar) ----------
    def win_minimize(self):
        if self._win:
            self._win.minimize()
        return {"ok": True}

    def win_maximize(self):
        if self._win:
            try:
                self._win.maximize()
            except Exception:
                try:
                    self._win.toggle_fullscreen()
                except Exception:
                    pass
        return {"ok": True}

    def win_close(self):
        if self._win:
            self._win.destroy()
        return {"ok": True}

    def win_resize(self, width, height):
        if self._win and width and height:
            try:
                self._win.resize(int(width), int(height))
            except Exception:
                pass
        return {"ok": True}

    # ---------- analytics ----------
    def dashboard_stats(self, range_key="30d"):
        if _analytics is None:
            return {"error": "analytics module missing"}
        try:
            return _analytics.compute_dashboard(range_key)
        except Exception as e:
            return {"error": str(e)}

    # ---------- AI bridge (BYOK) ----------
    def ai_status(self):
        return {"available": _ai is not None}

    def ai_get_config(self):
        return _ai.load_config() if _ai else {"error": "ai module missing"}

    def ai_save_config(self, cfg):
        return _ai.save_config(cfg) if _ai else {"error": "ai module missing"}

    def ai_add_key(self, provider, label, key):
        return _ai.add_key(provider, label, key) if _ai else {"error": "ai module missing"}

    def ai_remove_key(self, key_id):
        return _ai.remove_key(key_id) if _ai else {"error": "ai module missing"}

    def ai_migrate_keys(self):
        return _ai.migrate_keys_to_keyring() if _ai else {"error": "ai module missing"}

    def ai_tick(self):
        return _graph.tick() if _graph else {"error": "graph module missing"}

    def ai_graph_status(self):
        return _graph.graph_status() if _graph else {"error": "graph module missing"}

    def ai_task_template(self, task_id):
        return _graph.get_task_template(task_id) if _graph else {"error": "graph module missing"}

    def ai_run_task_graph(self):
        if not _graph or not _ai:
            return {"error": "graph module missing"}
        return _graph.run_task_graph(_ai.load_config())

    def ai_user_edit(self, task_id, section, eid, fields):
        return _graph.user_edit_entity(task_id, section, eid, fields) if _graph else {"error": "graph module missing"}

    def ai_accept_proposal(self, task_id, proposal_id, accept):
        return _graph.accept_proposal(task_id, proposal_id, accept) if _graph else {"error": "graph module missing"}

    def ai_toggle_proposition_v2(self, task_id, prop_id, accepted):
        return _graph.toggle_proposition_v2(task_id, prop_id, accepted) if _graph else {"error": "graph module missing"}

    def ai_export_dpo2(self):
        return _graph.export_dpo_rows_v2() if _graph else {"error": "graph module missing"}

    def ai_coach_refresh(self):
        if not _graph or not _ai:
            return {"error": "graph module missing"}
        return _graph.run_coach_refresh(_ai.load_config())

    def ai_get_coach(self):
        return _graph.get_coach() if _graph else {"error": "graph module missing"}

    def ai_get_ideal_time(self):
        if not _ai:
            return {"error": "ai module missing"}
        return {"ok": True, "ideal_time": _ai.load_config().get("ideal_time")}

    def ai_set_agent(self, agent_id, provider, key_id, model):
        return _ai.set_agent(agent_id, provider, key_id, model) if _ai else {"error": "ai module missing"}

    def ai_test_model(self, provider, key_id, model):
        return _ai.test_model(provider, key_id, model, "chat") if _ai else {"error": "ai module missing"}

    def ai_list_models(self, provider, task="chat"):
        return _ai.list_models(provider, task) if _ai else {"error": "ai module missing"}

    def ai_refresh_models(self, provider, key_id=""):
        return _ai.refresh_models(provider, key_id) if _ai else {"error": "ai module missing"}

    def ai_models_cache(self, provider=""):
        return _ai.models_cache(provider) if _ai else {"error": "ai module missing"}

    def ai_estimate_cost(self):
        return _ai.estimate_cost() if _ai else {"error": "ai module missing"}

    def ai_spend_summary(self):
        return _ai.spend_summary() if _ai else {"error": "ai module missing"}

    def ai_start_pipeline(self):
        return _ai.start_pipeline() if _ai else {"error": "ai module missing"}

    def ai_pipeline_status(self):
        return _ai.get_pipeline_status() if _ai else {"error": "ai module missing"}

    def ai_get_reports(self):
        return _ai.get_reports() if _ai else {"error": "ai module missing"}

    def ai_get_tasks(self):
        return _ai.get_tasks() if _ai else {"error": "ai module missing"}

    def ai_save_tasks(self, tasks):
        return _ai.save_tasks(tasks) if _ai else {"error": "ai module missing"}

    def ai_toggle_proposition(self, task_id, prop_id, accepted):
        return _ai.toggle_proposition(task_id, prop_id, accepted) if _ai else {"error": "ai module missing"}

    def ai_get_insights(self):
        return _ai.get_insights() if _ai else {"error": "ai module missing"}

    def ai_run_coach(self):
        return _ai.run_coach(_ai.load_config()) if _ai else {"error": "ai module missing"}

    def ai_set_consent(self, value):
        return _ai.set_consent(bool(value)) if _ai else {"error": "ai module missing"}

    def ai_export_dpo(self):
        return _ai.export_dpo_rows() if _ai else {"error": "ai module missing"}

    def ai_set_ideal_time(self, days, start, end):
        return _ai.set_ideal_time(days, start, end) if _ai else {"error": "ai module missing"}

    def ai_fallback(self, agent_id):
        if not _ai:
            return {"error": "ai module missing"}
        cfg = _ai.load_config()
        a = (cfg.get("agents") or {}).get(agent_id) or {}
        return _ai.fallback_model(agent_id, a.get("provider"), a.get("key_id"), a.get("model"))

    def ai_agents(self):
        return _ai.agents_catalog() if _ai else {"error": "ai module missing"}

    def ai_providers(self):
        return _ai.providers_catalog() if _ai else {"error": "ai module missing"}

    # ---------- ASR recording (Python-side mic capture) ----------
    def asr_begin(self):
        try:
            import sounddevice as sd
        except ImportError:
            return {"error": "sounddevice not installed"}
        if getattr(self, "_asr", None):
            return {"error": "already recording"}
        import audio_capture as _ac
        self._asr = _ac.Recorder()
        return self._asr.begin()

    def asr_stop(self, provider, key_id, model):
        rec = getattr(self, "_asr", None)
        if not rec:
            return {"error": "not recording"}
        self._asr = None
        audio = rec.stop()
        if not audio:
            return {"error": "no audio captured"}
        return _ai.transcribe(audio, provider, key_id, model) if _ai else {"error": "ai module missing"}

    def asr_state(self):
        rec = getattr(self, "_asr", None)
        if not rec:
            return {"recording": False, "seconds": 0}
        return {"recording": True, "seconds": rec.seconds()}

    def asr_transcribe(self, audio_b64, provider, key_id, model):
        return _ai.transcribe(audio_b64, provider, key_id, model) if _ai else {"error": "ai module missing"}

    def ai_asr_allowlist(self):
        return _ai.asr_allowlist() if _ai else {"error": "ai module missing"}

    def _maybe_rollover(self):
        """Log an end-of-day 'documentation' summary for every completed day
        that had documentation time, summing it up per category."""
        today = date.today()
        # performance throttle: skip heavy scan if day hasn't changed and total doc unchanged
        doc_total = sum(int(s.get("doc_seconds") or 0) for s in self.store.sessions if s.get("kind") != "daily-doc-summary")
        if self._last_rollover_day == today and self._last_doc_total == doc_total:
            return
        changed = False
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
                     for c, v in sorted(per_cat.items(), key=lambda x: -x[1]) if round(v/60) > 0]
            if not lines:
                lines = ["%s: %d min" % (c, round(v / 60)) for c, v in sorted(per_cat.items(), key=lambda x: -x[1])]
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
        self._last_rollover_day = today
        self._last_doc_total = doc_total

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

    def list_exports(self):
        out_dir = exports_dir()
        if not out_dir.exists():
            return {"exports": []}
        # include both legacy sessions_*.xlsx and new category_tag_date_date.xlsx
        files = sorted(out_dir.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
        exports = []
        for p in files[:80]:
            if p.name.startswith("~$"):
                continue
            try:
                st = p.stat()
                exports.append({
                    "name": p.name,
                    "path": str(p.resolve()),
                    "mtime": datetime.fromtimestamp(st.st_mtime).strftime(FMT),
                    "mtime_label": datetime.fromtimestamp(st.st_mtime).strftime("%d %b · %H:%M"),
                    "size_kb": round(st.st_size / 1024, 1)
                })
            except Exception:
                continue
        return {"exports": exports}

    def delete_export(self, path):
        try:
            p = resolve_inside(exports_dir(), path)
        except ValueError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": "File not found"}
        if p.suffix.lower() != ".xlsx":
            return {"error": "Not an export file"}
        try:
            p.unlink()
            return {"ok": True}
        except Exception as e:
            log.warning("delete_export failed: %s", e)
            return {"error": str(e)}

    def open_export(self, path):
        try:
            p = resolve_inside(exports_dir(), path)
        except ValueError as e:
            return {"error": str(e)}
        if not p.exists():
            return {"error": "File not found"}
        if p.suffix.lower() != ".xlsx":
            return {"error": "Not an export file"}
        try:
            if sys.platform == "win32":
                os.startfile(str(p))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
            return {"ok": True, "path": str(p)}
        except Exception as e:
            return {"error": str(e)}

    def start_session(self, when, data=None):
        iso, err = self._resolve_when(when)
        if err:
            return {"error": err}
        s = new_session(iso)
        data = data or {}
        for k in ("category", "tag", "sub_tag", "describe", "notes"):
            s[k] = str(data.get(k, "")).strip()
        self.store.sessions.append(s)
        # keep sorted desc for fast _ok later (insert at correct position instead of resort)
        self.store.sessions.sort(key=lambda x: x.get("start", ""), reverse=True)
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
        self.store.sessions.sort(key=lambda x: x.get("start", ""), reverse=True)
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
        self.store.sessions.sort(key=lambda x: x.get("start", ""), reverse=True)
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

    def export_excel(self, category, tag, duration_label, custom_name=None):
        if openpyxl is None:
            return {"error": "openpyxl is not installed. Run: python -m pip install openpyxl"}
        rows = [s for s in self.store.sessions
                if s.get("end") and s.get("kind") != "daily-doc-summary"]
        rows = filter_sessions(rows, category, tag, duration_label)
        if not rows:
            return {"error": "No sessions match this filter."}
        keep_cat = category == "All categories"
        wb = build_workbook(rows, keep_cat)
        out_dir = exports_dir()
        out_dir.mkdir(exist_ok=True)
        base = export_name(category, tag, duration_label, rows, custom_name)
        path = _collision_free(out_dir, base)
        try:
            wb.save(path)
        except Exception as e:
            log.warning("export save failed: %s", e)
            return {"error": str(e)}
        return {"path": str(path), "count": len(rows),
                "category_col": keep_cat, "name": path.name}


def main():
    if webview is None:
        print("pywebview is not installed. Run: python -m pip install pywebview")
        return
    api = Api()
    if _ai is not None:
        try:
            _ai.migrate_keys_to_keyring()  # best-effort: legacy inline -> locker
        except Exception:
            pass
    webview.settings["DRAG_REGION_SELECTOR"] = ".titlebar"
    webview.settings["DRAG_REGION_DIRECT_TARGET_ONLY"] = True
    window = webview.create_window(APP_NAME, html=UI_HTML, js_api=api,
                                   width=1180, height=780, min_size=(940, 640),
                                   frameless=True, easy_drag=False,
                                   background_color="#0a0f16")
    api._win = window
    window.events.closed += api.store._save
    webview.start()


if __name__ == "__main__":
    main()
