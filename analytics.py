"""Analytics for Interval.

Pure-Python, stdlib-only dashboard aggregations over sessions.json.
All functions are pure; the only module-level state is constants.
"""

import json
from bisect import bisect_left
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "sessions.json"
FMT = "%Y-%m-%dT%H:%M:%S"
FMT_SHORT = "%Y-%m-%dT%H:%M"

ALL_RANGES = ("today", "7d", "30d", "90d", "all")

WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

BUCKET_ORDER = ("Morning(6-12)", "Afternoon(12-18)", "Evening(18-24)", "Night(0-6)")
DURATION_BUCKETS = ("0-15", "15-30", "30-60", "60-120", "120-240", "240+")


def load_sessions():
    """Load sessions.json as a list of session dicts; empty list on any failure."""
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(raw, dict):
        return []
    sessions = raw.get("sessions")
    if not isinstance(sessions, list):
        return []
    return sessions


def _parse_time(value):
    """Parse a local 'YYYY-MM-DDTHH:MM:SS' (or short) timestamp into a datetime."""
    if not isinstance(value, str):
        return None
    for fmt in (FMT, FMT_SHORT):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def _classify(sessions):
    """Split sessions into (work, active): work = ended, non-summary, valid times."""
    work, active = [], []
    for s in sessions:
        if s.get("kind") == "daily-doc-summary":
            continue
        start = _parse_time(s.get("start"))
        if start is None:
            continue
        end = _parse_time(s.get("end"))
        if end is None:
            active.append(s)
        else:
            work.append((s, start, end))
    return work, active


def _range_dates(range_key, sessions):
    """Return inclusive (start_date, end_date) for a range key."""
    today = date.today()
    if range_key == "today":
        return today, today
    if range_key in ("7d", "30d", "90d"):
        n = int(range_key[:-1])
        return today - timedelta(days=n - 1), today
    starts = [d for d in (_parse_time(s.get("start")) for s in sessions) if d is not None]
    start = min((d.date() for d in starts), default=today)
    return start, today


def _minutes(start, end):
    """Session length in minutes, clamped to zero and rounded to 2 decimals."""
    return round(max(0.0, (end - start).total_seconds() / 60.0), 2)


def _doc_minutes(session):
    """doc_seconds converted to minutes for one session."""
    return round(float(session.get("doc_seconds") or 0) / 60.0, 2)


def _bucket_for(hour):
    """Day-part bucket name for an hour of day."""
    if hour < 6:
        return "Night(0-6)"
    if hour < 12:
        return "Morning(6-12)"
    if hour < 18:
        return "Afternoon(12-18)"
    return "Evening(18-24)"


def compute_dashboard(range_key):
    """Compute every dashboard metric for a range; returns a JSON-safe dict."""
    if range_key not in ALL_RANGES:
        range_key = "all"
    sessions = load_sessions()
    work, active = _classify(sessions)
    start_date, end_date = _range_dates(range_key, sessions)
    day_count = (end_date - start_date).days + 1

    rows = []
    for s, start, end in work:
        if not (start_date <= start.date() <= end_date):
            continue
        rows.append({
            "session": s,
            "start": start,
            "end": end,
            "date": start.date(),
            "weekday": start.weekday(),
            "hour": start.hour,
            "minutes": _minutes(start, end),
            "doc_minutes": _doc_minutes(s),
            "category": str(s.get("category") or "Uncategorized"),
            "sub_tag": s.get("sub_tag") or "",
        })

    total_sessions = len(rows)
    total_minutes = round(sum(r["minutes"] for r in rows), 2)
    total_doc_minutes = round(sum(r["doc_minutes"] for r in rows), 2)
    avg_session_min = round(total_minutes / total_sessions, 2) if total_sessions else 0.0
    doc_ratio = round(total_doc_minutes / total_minutes, 4) if total_minutes else 0.0
    today = date.today()
    today_rows = [r for r in rows if r["date"] == today]
    overview = {
        "total_sessions": total_sessions,
        "total_minutes": total_minutes,
        "total_doc_minutes": total_doc_minutes,
        "avg_session_min": avg_session_min,
        "doc_ratio": doc_ratio,
        "active_count": len(active),
        "sessions_today": len(today_rows),
        "minutes_today": round(sum(r["minutes"] for r in today_rows), 2),
    }

    daily_count = nightly_count = 0
    daily_minutes = nightly_minutes = 0.0
    bucket_stats = {b: {"count": 0, "minutes": 0.0} for b in BUCKET_ORDER}
    for r in rows:
        if r["hour"] >= 18 or r["hour"] < 6:
            nightly_count += 1
            nightly_minutes += r["minutes"]
        else:
            daily_count += 1
            daily_minutes += r["minutes"]
        b = _bucket_for(r["hour"])
        bucket_stats[b]["count"] += 1
        bucket_stats[b]["minutes"] += r["minutes"]
    daily_nightly = {
        "daily_count": daily_count,
        "nightly_count": nightly_count,
        "daily_minutes": round(daily_minutes, 2),
        "nightly_minutes": round(nightly_minutes, 2),
        "by_bucket": [{"bucket": b, "count": bucket_stats[b]["count"],
                       "minutes": round(bucket_stats[b]["minutes"], 2)}
                      for b in BUCKET_ORDER],
    }

    per_day = {
        (start_date + timedelta(days=i)).isoformat():
            {"minutes": 0.0, "sessions": 0, "doc_minutes": 0.0}
        for i in range(day_count)
    }
    per_week = defaultdict(lambda: {"minutes": 0.0, "sessions": 0, "doc_minutes": 0.0})
    per_month = defaultdict(lambda: {"minutes": 0.0, "sessions": 0, "doc_minutes": 0.0})
    for r in rows:
        k = r["date"].isoformat()
        per_day[k]["minutes"] += r["minutes"]
        per_day[k]["sessions"] += 1
        per_day[k]["doc_minutes"] += r["doc_minutes"]
        ws = r["date"] - timedelta(days=r["weekday"])
        wk = per_week[ws]
        wk["minutes"] += r["minutes"]
        wk["sessions"] += 1
        wk["doc_minutes"] += r["doc_minutes"]
        mk = per_month[r["date"].strftime("%Y-%m")]
        mk["minutes"] += r["minutes"]
        mk["sessions"] += 1
        mk["doc_minutes"] += r["doc_minutes"]
    trends = {
        "daily": [{"date": k, "minutes": round(v["minutes"], 2), "sessions": v["sessions"],
                   "doc_minutes": round(v["doc_minutes"], 2)} for k, v in per_day.items()],
        "weekly": [{"week_start": ws.isoformat(), "minutes": round(v["minutes"], 2),
                    "sessions": v["sessions"], "doc_minutes": round(v["doc_minutes"], 2)}
                   for ws, v in sorted(per_week.items())],
        "monthly": [{"month": m, "minutes": round(v["minutes"], 2), "sessions": v["sessions"],
                     "doc_minutes": round(v["doc_minutes"], 2)} for m, v in sorted(per_month.items())],
    }

    cat_stats = {}
    for r in rows:
        c = cat_stats.setdefault(r["category"],
                                 {"minutes": 0.0, "sessions": 0, "doc_minutes": 0.0, "sub": {}})
        c["minutes"] += r["minutes"]
        c["sessions"] += 1
        c["doc_minutes"] += r["doc_minutes"]
        st = c["sub"].setdefault(r["sub_tag"], {"minutes": 0.0, "sessions": 0, "doc_minutes": 0.0})
        st["minutes"] += r["minutes"]
        st["sessions"] += 1
        st["doc_minutes"] += r["doc_minutes"]

    def _cat_entry(cat):
        c = cat_stats[cat]
        sub = sorted(c["sub"].items(), key=lambda kv: (-kv[1]["minutes"], kv[0]))
        return {
            "category": cat,
            "minutes": round(c["minutes"], 2),
            "sessions": c["sessions"],
            "doc_minutes": round(c["doc_minutes"], 2),
            "doc_ratio": round(c["doc_minutes"] / c["minutes"], 4) if c["minutes"] else 0.0,
            "share": round(c["minutes"] / total_minutes, 4) if total_minutes else 0.0,
            "sub_tags": [{"sub_tag": k, "minutes": round(v["minutes"], 2),
                          "sessions": v["sessions"], "doc_minutes": round(v["doc_minutes"], 2)}
                         for k, v in sub],
        }

    ordered_cats = sorted(cat_stats, key=lambda c: (-cat_stats[c]["minutes"], c))
    categories = [_cat_entry(c) for c in ordered_cats]

    cat_day = defaultdict(lambda: defaultdict(float))
    for r in rows:
        cat_day[r["category"]][r["date"].isoformat()] += r["minutes"]
    category_trends = {}
    for cat in ordered_cats:
        if cat_stats[cat]["minutes"] <= 0:
            continue
        day_map = cat_day.get(cat, {})
        category_trends[cat] = [{"period_key": k, "minutes": round(day_map.get(k, 0.0), 2)}
                                for k in per_day]

    doc_ratio_trend = {
        "weekly": [{"week_start": ws.isoformat(), "work_minutes": round(v["minutes"], 2),
                    "doc_minutes": round(v["doc_minutes"], 2),
                    "ratio": (round(v["doc_minutes"] / v["minutes"], 4) if v["minutes"] else None)}
                   for ws, v in sorted(per_week.items())],
        "monthly": [{"month": m, "work_minutes": round(v["minutes"], 2),
                     "doc_minutes": round(v["doc_minutes"], 2),
                     "ratio": (round(v["doc_minutes"] / v["minutes"], 4) if v["minutes"] else None)}
                    for m, v in sorted(per_month.items())],
    }

    hm_min = [[0.0] * 24 for _ in range(7)]
    hm_cnt = [[0] * 24 for _ in range(7)]
    cat_hm = {}
    cell_cats = defaultdict(lambda: defaultdict(float))
    for r in rows:
        hm_min[r["weekday"]][r["hour"]] += r["minutes"]
        hm_cnt[r["weekday"]][r["hour"]] += 1
        cell_cats[(r["weekday"], r["hour"])][r["category"]] += r["minutes"]
        ch = cat_hm.setdefault(r["category"], [[0.0] * 24 for _ in range(7)])
        ch[r["weekday"]][r["hour"]] += r["minutes"]
    hm_min = [[round(v, 2) for v in row] for row in hm_min]
    best_by_hour = []
    for w in range(7):
        if any(hm_min[w]):
            best_by_hour.append(max(range(24), key=lambda h: hm_min[w][h]))
        else:
            best_by_hour.append(None)
    top_cells = []
    for (w, h), cats in cell_cats.items():
        top = min(cats.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        top_cells.append((round(max(cats.values()), 2), "%d_%d" % (w, h), top))
    top_cells.sort(key=lambda t: (-t[0], t[1]))
    top_category_by_cell = {key: cat for _, key, cat in top_cells[:50]}
    heatmap = {
        "minutes": hm_min,
        "sessions": hm_cnt,
        "best_by_hour": best_by_hour,
        "top_category_by_cell": top_category_by_cell,
    }

    top6 = ordered_cats[:6]
    category_heatmap = {
        c: {"minutes": [[round(x, 2) for x in row]
                        for row in cat_hm.get(c, [[0.0] * 24 for _ in range(7)])]}
        for c in top6
    }

    bounds = [15, 30, 60, 120, 240]
    counts = [0] * 6
    for r in rows:
        counts[bisect_left(bounds, r["minutes"])] += 1
    duration_dist = [{"bucket": label, "count": counts[i]}
                     for i, label in enumerate(DURATION_BUCKETS)]

    weekday_totals = [0.0] * 7
    weekday_occurrences = [0] * 7
    hour_totals = [0.0] * 24
    for i in range(day_count):
        weekday_occurrences[(start_date + timedelta(days=i)).weekday()] += 1
    for r in rows:
        weekday_totals[r["weekday"]] += r["minutes"]
        hour_totals[r["hour"]] += r["minutes"]
    per_weekday = [round(weekday_totals[i] / weekday_occurrences[i], 2)
                   if weekday_occurrences[i] else 0.0 for i in range(7)]
    per_hour = [round(hour_totals[h] / day_count, 2) for h in range(24)]
    peak_w = max(range(7), key=lambda i: per_weekday[i]) if any(per_weekday) else None
    peak_h = max(range(24), key=lambda h: per_hour[h]) if any(per_hour) else None
    weekly_pattern = {
        "per_weekday": per_weekday,
        "per_hour": per_hour,
        "peak_weekday": WEEKDAY_NAMES[peak_w] if peak_w is not None else None,
        "peak_hour": peak_h,
    }

    return {
        "range": range_key,
        "overview": overview,
        "daily_nightly": daily_nightly,
        "trends": trends,
        "categories": categories,
        "category_trends": category_trends,
        "doc_ratio_trend": doc_ratio_trend,
        "heatmap": heatmap,
        "category_heatmap": category_heatmap,
        "duration_dist": duration_dist,
        "weekly_pattern": weekly_pattern,
    }
