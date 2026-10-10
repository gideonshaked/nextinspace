import io
from dataclasses import replace
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from rich.console import Console

from nextinspace import render
from nextinspace.models import parse_event, parse_launch

NOW = datetime(2026, 10, 10, 12, tzinfo=UTC)
UTC_ZONE = ZoneInfo("UTC")
NEW_YORK = ZoneInfo("America/New_York")


def export(renderable, width=120):
    console = Console(width=width, record=True, color_system=None, file=io.StringIO())
    console.print(renderable)
    return console.export_text()


@pytest.fixture
def launches(load):
    return [parse_launch(r) for r in load("launches_upcoming.json")["results"]]


@pytest.fixture
def events(load):
    return [parse_event(r) for r in load("events_upcoming.json")["results"]]


@pytest.fixture
def crewed(detailed_launch):
    return parse_launch(detailed_launch)


def test_listing(launches, events):
    starlink, dragon = launches[:2]
    monthly = replace(dragon, id="m", net=datetime(2026, 10, 1, tzinfo=UTC), precision="M")
    text = export(render.listing([starlink, events[0], monthly], NOW, NEW_YORK, title="Next in space", width=120))
    assert "Next in space" in text
    assert "T-11:00:00" in text
    assert "Sat Oct 10, 2026 19:00 EDT" in text
    assert "T-5d 03:00:00" in text
    assert "SpaceX CRS-35 Dragon Docking" in text
    assert "Starlink Group 15-25" in text
    assert "Falcon 9 Block 5 · SpaceX" in text
    assert "Vandenberg SFB, CA, USA" in text
    (row,) = [line for line in text.splitlines() if "October 2026" in line]
    assert row.split()[:3] == ["3", "October", "2026"]


@pytest.mark.parametrize("fn", ["listing", "outcomes"])
def test_location_column_needs_width(launches, fn):
    def table(width):
        if fn == "listing":
            return render.listing(launches[:3], NOW, UTC_ZONE, title="t", width=width)
        return render.outcomes(launches[:3], UTC_ZONE, title="t", width=width)

    assert "Location" in export(table(120))
    assert "Location" in export(table(110))
    narrow = export(table(109), width=109)
    assert "Location" not in narrow
    assert "Vandenberg" not in narrow


def test_square_brackets_render_literally(launches, events):
    launch = replace(launches[0], name="Falcon 9 Block 5 | Starlink [Group 6]")
    event = replace(events[0], name="Docking [bold]test[/bold]")
    for renderable in (
        render.listing([launch, event], NOW, UTC_ZONE, title="t", width=120),
        render.cards([launch, event], NOW, UTC_ZONE),
    ):
        text = export(renderable)
        assert "Starlink [Group 6]" in text
        assert "Docking [bold]test[/bold]" in text
    assert "Starlink [Group 6]" in export(render.detail(launch, NOW, UTC_ZONE))
    assert "Docking [bold]test[/bold]" in export(render.detail(event, NOW, UTC_ZONE))


def test_outcomes(load):
    previous = [parse_launch(r) for r in load("launches_previous.json")["results"]]
    failed = replace(previous[1], failreason="Second stage anomaly")
    text = export(render.outcomes([previous[0], failed], UTC_ZONE, title="Recent launches", width=120))
    assert "Recent launches" in text
    assert "Fri Oct 9, 2026 ~19:25 UTC" in text
    assert "NeonSat-2 to 6" in text
    assert "Second stage anomaly" in text
    assert "Naro Space Center, South Korea" in text


def test_cards(launches, events):
    text = export(render.cards([launches[0], events[1]], NOW, UTC_ZONE))
    assert "1. Starlink Group 15-25" in text
    assert "2. BepiColombo Mercury Orbit Insertion" in text
    assert "T-11:00:00" in text
    assert "November 2026" in text
    assert "Space Launch Complex 4E, Vandenberg SFB, CA, USA" in text


def test_crewed_launch_detail(crewed):
    text = export(render.detail(crewed, NOW, UTC_ZONE))
    assert "Crew-14" in text
    assert "March 2027" in text
    assert "Countdown" not in text
    for name in ("Kayla Barron", "Arutyun Kiviryan", "Christina Birch", "Makoto Suwa"):
        assert name in text
    assert "Spacecraft Commander" in text
    assert "JAXA" in text
    assert "LZ-40" in text
    assert "International Space Station" in text
    assert "May 11, 2018" in text
    assert "Low Earth Orbit (LEO)" in text
    assert "Space Launch Complex 40" in text


def test_clock_launch_detail(launches):
    text = export(render.detail(launches[0], NOW, NEW_YORK))
    assert "T-11:00:00" in text
    assert "Sat Oct 10, 2026 19:00 EDT" in text
    assert "Sat Oct 10, 2026 23:00 UTC" in text


def test_event_detail(events):
    text = export(render.detail(events[0], NOW, UTC_ZONE))
    assert "SpaceX CRS-35 Dragon Docking" in text
    assert "T-5d 03:00:00" in text
    assert "Docking" in text
    assert "International Space Station" in text


def test_big_countdown(launches, events):
    text = render.big_countdown(launches[0], NOW)
    rows = text.plain.split("\n")
    assert len(rows) == 5
    assert len({len(r) for r in rows}) == 1
    assert render.big_countdown(events[1], NOW).plain == "NET November 2026"
    assert render.big_countdown(replace(events[1], net=None), NOW).plain == "NET Date unknown"


@pytest.mark.parametrize("text", ["T-2d 04:13:22", "T+00:00:05", "0123456789"])
def test_big_has_five_even_rows(text):
    rows = render.big(text, "bold").plain.split("\n")
    assert len(rows) == 5
    assert len({len(r) for r in rows}) == 1
    assert len(export(render.big(text, "bold")).rstrip("\n").split("\n")) == 5


def test_ordinal():
    expected = ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd", "101st", "111th", "112th", "123rd"]
    assert [render.ordinal(int(s[:-2])) for s in expected] == expected
