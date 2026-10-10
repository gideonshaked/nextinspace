from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from nextinspace.timefmt import (
    ago,
    countdown,
    describe,
    has_clock,
    parse_duration,
    relative,
)

NEW_YORK = ZoneInfo("America/New_York")
LOS_ANGELES = ZoneInfo("America/Los_Angeles")
TOKYO = ZoneInfo("Asia/Tokyo")

NET = datetime(2026, 10, 10, 23, 0, tzinfo=UTC)
MIDNIGHT = datetime(2026, 10, 31, tzinfo=UTC)


@pytest.mark.parametrize(
    ("precision", "tz", "expected"),
    [
        ("SEC", UTC, "Sat Oct 10, 2026 23:00 UTC"),
        ("MIN", NEW_YORK, "Sat Oct 10, 2026 19:00 EDT"),
        ("MIN", TOKYO, "Sun Oct 11, 2026 08:00 JST"),
        (None, UTC, "Sat Oct 10, 2026 23:00 UTC"),
        ("HR", NEW_YORK, "Sat Oct 10, 2026 ~19:00 EDT"),
    ],
)
def test_describe_clock(precision, tz, expected):
    assert describe(NET, precision, tz) == expected


@pytest.mark.parametrize(
    ("precision", "expected"),
    [
        ("AM", "Sat Oct 31, 2026 (morning)"),
        ("PM", "Sat Oct 31, 2026 (afternoon)"),
        ("DAY", "Sat Oct 31, 2026"),
        ("WK", "Week of Oct 31, 2026"),
        ("M", "October 2026"),
        ("Q1", "Q1 2026"),
        ("Q4", "Q4 2026"),
        ("H1", "H1 2026"),
        ("H2", "H2 2026"),
        ("Y", "2026"),
        ("FY", "FY 2026"),
        ("DEC", "2020s"),
    ],
)
def test_describe_coarse_ignores_local_zone(precision, expected):
    # Midnight UTC is the previous evening in Los Angeles; coarse precisions must not slip a day.
    assert describe(MIDNIGHT, precision, LOS_ANGELES) == expected
    assert describe(MIDNIGHT, precision, UTC) == expected


def test_describe_month_at_start_of_month_in_us_zone():
    net = datetime(2026, 11, 1, tzinfo=UTC)
    assert describe(net, "M", NEW_YORK) == "November 2026"
    assert describe(net, "M", LOS_ANGELES) == "November 2026"


def test_describe_unknown_date():
    assert describe(None, "MIN", UTC) == "Date unknown"
    assert describe(None, "M", UTC) == "Date unknown"


def test_has_clock():
    assert all(has_clock(p) for p in (None, "SEC", "MIN", "HR"))
    assert not any(has_clock(p) for p in ("AM", "DAY", "M", "Y"))


def test_countdown():
    assert countdown(NET, NET - timedelta(hours=1, minutes=2, seconds=3)) == "T-01:02:03"
    assert countdown(NET, NET - timedelta(days=2, hours=4, minutes=13, seconds=22)) == "T-2d 04:13:22"
    assert countdown(NET, NET + timedelta(seconds=90)) == "T+00:01:30"
    assert countdown(NET, NET + timedelta(days=3, seconds=5)) == "T+3d 00:00:05"
    assert countdown(NET, NET) == "T-00:00:00"


def test_relative_clock():
    now = NET - timedelta(hours=5)
    assert relative(NET, "MIN", now) == "T-05:00:00"
    assert relative(NET, "SEC", now) == "T-05:00:00"
    assert relative(NET, None, now) == "T-05:00:00"
    assert relative(NET, "HR", now) == "~T-05:00:00"


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (datetime(2026, 10, 31, 18, tzinfo=UTC), "today"),
        (datetime(2026, 10, 30, 1, tzinfo=UTC), "tomorrow"),
        (datetime(2026, 10, 27, 23, 59, tzinfo=UTC), "in 4 days"),
        (datetime(2026, 11, 3, tzinfo=UTC), "3 days ago"),
    ],
)
def test_relative_day(now, expected):
    assert relative(MIDNIGHT, "DAY", now) == expected
    assert relative(MIDNIGHT, "PM", now) == expected


def test_relative_day_uses_utc_calendar():
    # 20:00 in New York on Oct 30 is already Oct 31 in UTC.
    now = datetime(2026, 10, 30, 20, tzinfo=NEW_YORK)
    assert relative(MIDNIGHT, "DAY", now) == "today"


def test_relative_coarse():
    now = datetime(2026, 10, 10, tzinfo=UTC)
    assert relative(datetime(2026, 11, 1, tzinfo=UTC), "M", now) == "November 2026"
    assert relative(MIDNIGHT, "Q4", now) == "Q4 2026"
    assert relative(None, "MIN", now) == "TBD"


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "0s"),
        (42.9, "42s"),
        (60, "1 min"),
        (420, "7 min"),
        (3600, "1 h"),
        (3 * 3600 + 59, "3 h"),
        (172800, "2 days"),
    ],
)
def test_ago(seconds, expected):
    assert ago(seconds) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("90m", timedelta(minutes=90)),
        ("36h", timedelta(hours=36)),
        ("7d", timedelta(days=7)),
        ("2w", timedelta(weeks=2)),
        (" 12H ", timedelta(hours=12)),
    ],
)
def test_parse_duration(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize("text", ["", "d", "7", "7x", "-1d", "1.5h", "d7", "7 d", "h12"])
def test_parse_duration_invalid(text):
    with pytest.raises(ValueError, match="expected a duration"):
        parse_duration(text)
