from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from nextinspace.ics import calendar
from nextinspace.models import parse_event, parse_launch

NOW = datetime(2026, 10, 10, 12, tzinfo=UTC)


def unfold(text):
    return text.replace("\r\n ", "")


def vevents(text):
    """Each VEVENT as a dict of property (with parameters) to value."""
    events, current = [], None
    for line in unfold(text).split("\r\n"):
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT":
            events.append(current)
            current = None
        elif current is not None:
            name, value = line.split(":", 1)
            current[name] = value
    return events


@pytest.fixture
def launches(load):
    return [parse_launch(r) for r in load("launches_upcoming.json")["results"]]


@pytest.fixture
def events(load):
    return [parse_event(r) for r in load("events_upcoming.json")["results"]]


def test_structure_and_line_endings(launches, events):
    text = calendar(launches + events, NOW)
    assert text.startswith("BEGIN:VCALENDAR\r\nVERSION:2.0\r\n")
    assert text.endswith("END:VCALENDAR\r\n")
    assert "\n" not in text.replace("\r\n", "")
    assert text.count("BEGIN:VEVENT") == text.count("END:VEVENT") > 0


def test_lines_fit_in_75_octets(launches, events, crewed_text):
    long_event = replace(events[0], name="Ünïcödé 🚀 " * 20, description="Comma, semicolon; newline\nand more. " * 10)
    for text in (calendar([*launches, *events, long_event], NOW), crewed_text):
        lines = text.split("\r\n")
        assert all(len(line.encode()) <= 75 for line in lines)
        assert any(line.startswith(" ") for line in lines)


@pytest.fixture
def crewed_text(detailed_launch):
    launch = parse_launch(detailed_launch)
    return calendar([replace(launch, precision="SEC")], NOW)


def test_escaping_survives_folding(events):
    name = "Ünïcödé 🚀 docking, with; punctuation " * 4
    description = "First line, with comma; and semicolon\nSecond line \\ backslash"
    event = replace(events[0], name=name, description=description, location="Pad 39A, KSC; FL")
    (vevent,) = vevents(calendar([event], NOW))
    assert vevent["SUMMARY"] == "🛰 " + name.replace(",", "\\,").replace(";", "\\;")
    assert vevent["LOCATION"] == "Pad 39A\\, KSC\\; FL"
    assert vevent["DESCRIPTION"].endswith(
        "\\n\\nFirst line\\, with comma\\; and semicolon\\nSecond line \\\\ backslash"
    )
    assert "\n" not in vevent["DESCRIPTION"]


def test_coarse_precision_skipped(events, detailed_launch):
    month, year = events[1], events[4]
    assert (month.precision, year.precision) == ("M", "Y")
    crewed = parse_launch(detailed_launch)
    quarter = replace(events[0], precision="Q1")
    undated = replace(events[0], net=None, precision=None)
    text = calendar([month, year, crewed, quarter, undated], NOW)
    assert "BEGIN:VEVENT" not in text


def test_day_precision_is_all_day(events):
    day = events[2]
    assert day.precision == "DAY"
    (vevent,) = vevents(calendar([day], NOW))
    assert vevent["DTSTART;VALUE=DATE"] == "20261224"
    assert vevent["DTEND;VALUE=DATE"] == "20261225"
    assert "DTSTART" not in vevent


def test_clock_times_are_utc_with_minimum_duration(launches, events):
    launch = replace(launches[0], window_start=launches[0].net - timedelta(minutes=30), window_end=None)
    instant = replace(launches[0], window_start=launches[0].net, window_end=launches[0].net)
    windowed = replace(
        launches[0], window_start=launches[0].net, window_end=launches[0].net + timedelta(hours=2, minutes=5)
    )
    vlaunch, vinstant, vwindowed, vevent = vevents(calendar([launch, instant, windowed, events[0]], NOW))
    assert vinstant["DTSTART"] == "20261010T230000Z"
    assert vinstant["DTEND"] == "20261010T231500Z"
    assert vwindowed["DTEND"] == "20261011T010500Z"
    assert vevent["DTSTART"] == "20261015T150000Z"
    assert vevent["DTEND"] == "20261015T151500Z"
    assert (vlaunch["DTSTART"], vlaunch["DTEND"]) == ("20261010T223000Z", "20261010T230000Z")
    assert vinstant["DTSTAMP"] == "20261010T120000Z"
    assert vinstant["GEO"] == "34.632;-120.611"
    assert vinstant["SUMMARY"] == "🚀 Falcon 9 Block 5 | Starlink Group 15-25"


def test_uid_stable_per_item(launches, events):
    first = [v["UID"] for v in vevents(calendar(launches[:3] + events[:1], NOW))]
    again = [v["UID"] for v in vevents(calendar(launches[:3] + events[:1], NOW + timedelta(days=1)))]
    assert first == again
    assert len(set(first)) == 4
    assert first[0] == f"launch-{launches[0].id}@nextinspace"
    assert first[3] == "event-1525@nextinspace"
