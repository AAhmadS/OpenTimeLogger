"""Benchmark harness (qa-harness + release-engineer).

Measures, never asserts. Writes JSON to docs/benchmarks/<stamp>-<label>.json.

Modes:
  dist-size   sum of dist/ + root *.exe (build artifacts, gitignored)
  import      cold `import session_logger` time (new interpreter each rep)
  api         Api() init + get_state + dashboard_stats latency (headless-safe)
  gui-boot    launch the app from a TEMP COPY of the sources (never the repo,
              so rollover/summary writes can't touch real data); poll for a
              main window; record time-to-window + peak working set; kill the
              exact PID started. Skips gracefully when no desktop is present.

Usage: python scripts/bench.py [dist-size|import|api|gui-boot] [--label X]
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "docs", "benchmarks")


def _py():
    """App interpreter: the one that can import webview (cartography: 3.11).

    Override with OTL_PYTHON. Falls back to sys.executable.
    """
    env = os.environ.get("OTL_PYTHON")
    if env and os.path.exists(env):
        return env
    try:
        import webview  # noqa: F401
        return sys.executable
    except ImportError:
        pass
    cands = [r"C:\Users\USER\AppData\Local\Programs\Python\Python311\python.exe"]
    for c in cands:
        if os.path.exists(c):
            return c
    return sys.executable


def m_dist_size():
    total, files = 0, []
    for name in ("dist",):
        p = os.path.join(ROOT, name)
        for dp, _, fns in os.walk(p):
            for fn in fns:
                fp = os.path.join(dp, fn)
                total += os.path.getsize(fp)
                files.append(os.path.relpath(fp, ROOT))
    for fn in os.listdir(ROOT):
        if fn.lower().endswith(".exe"):
            total += os.path.getsize(os.path.join(ROOT, fn))
            files.append(fn)
    return {"bytes": total, "mb": round(total / 1e6, 1), "entries": len(files), "files": files}


def m_import(reps=3):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        r = subprocess.run([_py(), "-c", "import session_logger"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        ts.append(round((time.perf_counter() - t0) * 1000))
        if r.returncode != 0:
            return {"error": (r.stderr or "")[-500:]}
    return {"ms": ts, "median_ms": sorted(ts)[len(ts) // 2]}


def m_api():
    sys.path.insert(0, ROOT)
    os.environ.setdefault("OTL_APP_DIR", tempfile.mkdtemp(prefix="otl-bench-"))
    import session_logger as sl
    t0 = time.perf_counter()
    api = sl.Api()
    t_init = round((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()
    st = api.get_state()
    t_state = round((time.perf_counter() - t0) * 1000)
    t0 = time.perf_counter()
    d = api.dashboard_stats("30d")
    t_dash = round((time.perf_counter() - t0) * 1000)
    overview = (d.get("overview") or {}) if isinstance(d, dict) else {}
    return {"init_ms": t_init, "get_state_ms": t_state,
            "dashboard_30d_ms": t_dash,
            "sessions": len(st.get("sessions", [])),
            "dashboard_sessions": overview.get("total_sessions")}


def m_gui_boot(timeout_s=45):
    if os.name != "nt":
        return {"skipped": "Windows-only (WebView2)"}
    tmp = tempfile.mkdtemp(prefix="otl-guiboot-")
    for fn in ("session_logger.py", "ui.py", "brand.py", "ai.py", "aigraph.py",
               "analytics.py", "models.py", "keystore.py", "audio_capture.py",
               "timelib.py", "store.py", "export_xlsx.py",
               "asr_allowlist.json", "app.ico"):
        src = os.path.join(ROOT, fn)
        if os.path.exists(src):
            shutil.copy(src, tmp)
    for dn in ("assets",):
        src = os.path.join(ROOT, dn)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(tmp, dn),
                            ignore=shutil.ignore_patterns("logo_seedream5.png"))
    seed = {"sessions": [
        {"id": "b1", "start": "2026-09-01T09:00:00", "end": "2026-09-01T10:00:00",
         "category": "C", "tag": "t", "sub_tag": "", "describe": "d", "notes": "",
         "doc_seconds": 0}]}
    with open(os.path.join(tmp, "sessions.json"), "w", encoding="utf-8") as f:
        json.dump(seed, f)
    import subprocess as sp
    proc = sp.Popen([_py(), "session_logger.py"], cwd=tmp,
                    stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32

        def _visible_windows_of(pid):
            found = []

            @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            def cb(hwnd, _):
                wpid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
                if wpid.value == pid and user32.IsWindowVisible(hwnd):
                    found.append(hwnd)
                return True
            user32.EnumWindows(cb, 0)
            return found

        def _peak_rss(pid):
            try:
                k32 = ctypes.windll.kernel32
                h = k32.OpenProcess(0x1410, False, pid)  # QUERY_INFO|VM_READ
                if not h:
                    return 0
                try:
                    class PMC(ctypes.Structure):
                        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                                    ("PeakWorkingSetSize", ctypes.c_size_t),
                                    ("WorkingSetSize", ctypes.c_size_t),
                                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                                    ("PagefileUsage", ctypes.c_size_t),
                                    ("PeakPagefileUsage", ctypes.c_size_t)]
                    pmc = PMC()
                    pmc.cb = ctypes.sizeof(PMC)
                    psapi = ctypes.windll.psapi
                    psapi.GetProcessMemoryInfo.argtypes = [
                        wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
                    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
                    if psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb):
                        return pmc.PeakWorkingSetSize
                finally:
                    k32.CloseHandle(h)
            except Exception:
                pass
            return 0

        peak, t_window, t0 = 0, None, time.perf_counter()
        while time.perf_counter() - t0 < timeout_s:
            if proc.poll() is not None:
                return {"error": "process exited early, code=%s" % proc.returncode,
                        "peak_rss_mb": round(peak / 1e6, 1)}
            try:
                peak = max(peak, _peak_rss(proc.pid))
            except Exception:
                pass
            if t_window is None and _visible_windows_of(proc.pid):
                t_window = round((time.perf_counter() - t0) * 1000)
                # let WebView2 finish first paint, keep sampling peak
                t_end = time.perf_counter() + 4
                while time.perf_counter() < t_end:
                    try:
                        peak = max(peak, _peak_rss(proc.pid))
                    except Exception:
                        pass
                    if proc.poll() is not None:
                        break
                    time.sleep(0.25)
                break
            time.sleep(0.25)
        if t_window is None:
            return {"error": "no visible window within %ss" % timeout_s,
                    "peak_rss_mb": round(peak / 1e6, 1)}
        return {"time_to_window_ms": t_window, "peak_rss_mb": round(peak / 1e6, 1),
                "note": "visible top-level window owned by app PID (+4s paint settle)"}
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    label = "run"
    if "--label" in sys.argv:
        label = sys.argv[sys.argv.index("--label") + 1]
    fn = {"dist-size": m_dist_size, "import": m_import, "api": m_api,
          "gui-boot": m_gui_boot}[mode]
    res = {"mode": mode, "at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "python": sys.version.split()[0], "result": fn()}
    os.makedirs(OUTDIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(OUTDIR, "%s-%s-%s.json" % (stamp, mode, label))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()
