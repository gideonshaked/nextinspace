"""Precision-aware formatting of launch times.

LL2 reports a ``net`` (No Earlier Than) timestamp together with how precise it is,
from the second up to the decade. A launch "in October" is stored as midnight UTC on
some day of October, so showing it as a clock time or ticking down to it would invent
precision that does not exist.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, tzinfo

# Precisions precise enough for a ticking countdown and a wall-clock time.
CLOCK = {None, "SEC", "MIN", "HR"}

_QUARTER_HALF = {"Q1", "Q2", "Q3", "Q4", "H1", "H2"}


def has_clock(precision: str | None) -> bool:
    return precision in CLOCK


def describe(net: datetime | None, precision: str | None, tz: tzinfo | None) -> str:
    """Human description of when something happens, at the precision LL2 knows it."""
    if net is None:
        return "Date unknown"
    if has_clock(precision):
        local = net.astimezone(tz)
        prefix = "~" if precision == "HR" else ""
        return f"{local:%a %b} {local.day}, {local.year} {prefix}{local:%H:%M %Z}".rstrip()
    # Coarser precisions are calendar dates in UTC. Converting them to local time can
    # push "Oct 31 00:00 UTC" back into October 30th or "Nov 1" back into October.
    d = net.astimezone(UTC)
    match precision:
        case "AM" | "PM":
            return f"{d:%a %b} {d.day}, {d.year} ({'morning' if precision == 'AM' else 'afternoon'})"
        case "DAY":
            return f"{d:%a %b} {d.day}, {d.year}"
        case "WK":
            return f"Week of {d:%b} {d.day}, {d.year}"
        case "M":
            return f"{d:%B %Y}"
        case p if p in _QUARTER_HALF:
            return f"{p} {d.year}"
        case "FY":
            return f"FY {d.year}"
        case "DEC":
            return f"{d.year // 10 * 10}s"
        case _:
            return f"{d.year}"


def countdown(net: datetime, now: datetime) -> str:
    """Mission-clock style ``T-`` / ``T+`` string, e.g. ``T-2d 04:13:22``."""
    delta = net - now
    sign = "-" if delta >= timedelta(0) else "+"
    total = abs(int(delta.total_seconds()))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    clock = f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"T{sign}{days}d {clock}" if days else f"T{sign}{clock}"


def relative(net: datetime | None, precision: str | None, now: datetime) -> str:
    """Short relative time: an exact countdown when the precision allows, a rough one otherwise."""
    if net is None:
        return "TBD"
    if has_clock(precision):
        return ("~" if precision == "HR" else "") + countdown(net, now)
    if precision in {"AM", "PM", "DAY"}:
        days = (net.astimezone(UTC).date() - now.astimezone(UTC).date()).days
        if days == 0:
            return "today"
        if days == 1:
            return "tomorrow"
        if days == -1:
            return "yesterday"
        return f"in {days} days" if days > 0 else f"{-days} days ago"
    return describe(net, precision, UTC)


def ago(seconds: float) -> str:
    """``42s``, ``7 min``, ``3 h``, ``2 days``."""
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        return f"{int(seconds // 60)} min"
    if seconds < 86400:
        return f"{int(seconds // 3600)} h"
    days = int(seconds // 86400)
    return "1 day" if days == 1 else f"{days} days"


def parse_duration(text: str) -> timedelta:
    """Parse ``90m``, ``36h``, ``7d`` or ``2w``."""
    units = {"m": "minutes", "h": "hours", "d": "days", "w": "weeks"}
    text = text.strip().lower()
    if len(text) < 2 or text[-1] not in units or not text[:-1].isdigit():
        raise ValueError(f"expected a duration like 90m, 36h, 7d or 2w, got {text!r}")
    return timedelta(**{units[text[-1]]: int(text[:-1])})
