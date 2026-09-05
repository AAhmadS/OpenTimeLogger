"""Time parsing/formatting for Interval (backend-hardener split).

Single home for the two local timestamp formats. All datetimes are naive
local (documented assumption); DST-boundary arithmetic may yield 0 for
ambiguous hours — callers clamp via minutes_between.
"""
from datetime import datetime

FMT = "%Y-%m-%dT%H:%M:%S"
FMT_SHORT = "%Y-%m-%dT%H:%M"
FORMATS = (FMT, FMT_SHORT)


def parse_time(v):
    """Parse FMT/FMT_SHORT (or passthrough datetime). None when unparseable."""
    if isinstance(v, datetime):
        return v
    if not isinstance(v, str):
        return None
    for f in FORMATS:
        try:
            return datetime.strptime(v, f)
        except ValueError:
            continue
    return None


def to_iso(dt):
    return dt.strftime(FMT)


def now_iso():
    return datetime.now().strftime(FMT)


def minutes_between(start, end, default=0.0):
    """Session length in minutes, clamped to >= 0. default on bad input."""
    try:
        a, b = parse_time(start), parse_time(end)
        if a is None or b is None:
            return default
        return max(0.0, (b - a).total_seconds() / 60.0)
    except Exception:
        return default
