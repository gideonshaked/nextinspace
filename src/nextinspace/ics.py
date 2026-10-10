"""iCalendar (RFC 5545) export, so launches can be imported into any calendar app."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from nextinspace.models import Event, Item, Launch
from nextinspace.timefmt import describe, has_clock


def _escape(text: str) -> str:
    text = text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
    return text.replace("\r\n", "\\n").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Fold to 75 octets per RFC 5545 3.1, never splitting a UTF-8 sequence."""
    out: list[str] = []
    current = ""
    for ch in line:
        limit = 75 if not out else 74  # continuation lines start with a space
        if len((current + ch).encode()) > limit:
            out.append(current)
            current = ""
        current += ch
    out.append(current)
    return "\r\n ".join(out)


def _utc(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


# Coarser precisions would put the item on an arbitrary day of its week or month.
DAY_OR_FINER = {None, "SEC", "MIN", "HR", "AM", "PM", "DAY"}


def exportable(items: Sequence[Item]) -> list[Item]:
    return [i for i in items if i.net is not None and i.precision in DAY_OR_FINER]


def calendar(items: Sequence[Item], now: datetime) -> str:
    """An iCalendar file of the exportable items. RFC 5545 needs at least one."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//nextinspace//nextinspace//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Next in space",
    ]
    for item in exportable(items):
        assert item.net is not None
        lines += ["BEGIN:VEVENT", f"UID:{item.kind}-{item.id}@nextinspace", f"DTSTAMP:{_utc(now)}"]
        if has_clock(item.precision):
            start = item.window_start if isinstance(item, Launch) and item.window_start else item.net
            end = item.window_end if isinstance(item, Launch) and item.window_end else item.net
            if end - start < timedelta(minutes=15):
                end = start + timedelta(minutes=15)
            lines += [f"DTSTART:{_utc(start)}", f"DTEND:{_utc(end)}"]
        else:
            day = item.net.astimezone(UTC).date()
            lines += [f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}"]

        summary = f"🚀 {item.name}" if isinstance(item, Launch) else f"🛰 {item.name}"
        lines.append(f"SUMMARY:{_escape(summary)}")
        if item.location:
            lines.append(f"LOCATION:{_escape(item.location)}")
        if isinstance(item, Launch) and item.pad and item.pad.latitude is not None and item.pad.longitude is not None:
            lines.append(f"GEO:{item.pad.latitude};{item.pad.longitude}")
        lines.append(f"DESCRIPTION:{_escape(_description(item))}")
        if item.webcasts:
            lines.append(f"URL:{item.webcasts[0].url}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"


def _description(item: Item) -> str:
    parts = [f"NET {describe(item.net, item.precision, UTC)}"]
    if isinstance(item, Launch):
        parts.insert(0, f"Status: {item.status.name}")
        if item.provider:
            parts.append(f"Provider: {item.provider.name}")
    elif isinstance(item, Event) and item.type:
        parts.insert(0, item.type)
    if item.description:
        parts.append("")
        parts.append(item.description.strip())
    return "\n".join(parts)
