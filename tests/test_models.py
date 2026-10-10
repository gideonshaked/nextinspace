import json

import pytest

from nextinspace.models import Event, Launch, parse_event, parse_launch, to_dict

LAUNCH_FILES = ["launches_upcoming.json", "launches_previous.json", "launch_crewed_detailed.json"]


@pytest.mark.parametrize("name", LAUNCH_FILES)
def test_parse_every_launch(load, name):
    results = load(name)["results"]
    launches = [parse_launch(r) for r in results]
    assert len(launches) == len(results)
    assert all(isinstance(launch, Launch) and launch.kind == "launch" for launch in launches)


def test_parse_every_event(load):
    results = load("events_upcoming.json")["results"]
    events = [parse_event(r) for r in results]
    assert len(events) == len(results)
    assert all(isinstance(e, Event) and e.kind == "event" for e in events)


def test_upcoming_launch_fields(load):
    launch = parse_launch(load("launches_upcoming.json")["results"][0])
    assert launch.name == "Falcon 9 Block 5 | Starlink Group 15-25"
    assert launch.status.abbrev == "Go"
    assert launch.precision == "MIN"
    assert launch.net.isoformat() == "2026-10-10T23:00:00+00:00"
    assert launch.provider.name == "SpaceX"
    assert launch.provider.abbrev == "SpX"
    assert launch.rocket.full_name == "Falcon 9 Block 5"
    assert launch.pad.name == "Space Launch Complex 4E"
    assert launch.pad.location == "Vandenberg SFB, CA, USA"
    assert launch.pad.country_code == "US"
    assert launch.location == "Space Launch Complex 4E, Vandenberg SFB, CA, USA"
    assert launch.mission.name == "Starlink Group 15-25"


def test_previous_launch_fields(load):
    launches = [parse_launch(r) for r in load("launches_previous.json")["results"]]
    assert launches[0].precision == "HR"
    assert launches[1].rocket.full_name == "KSLV-2 Nuri"
    assert launches[1].provider.abbrev == "KARI"
    assert {launch.status.abbrev for launch in launches} >= {"Success"}


def test_detailed_launch(detailed_launch):
    launch = parse_launch(detailed_launch)
    assert launch.name == "Falcon 9 Block 5 | Crew-14"
    assert launch.status.abbrev == "TBD"
    assert launch.precision == "M"
    assert launch.rocket.name == "Falcon 9"
    assert launch.rocket.family == "Falcon"
    assert launch.rocket.reusable is True
    assert launch.rocket.maiden_flight.isoformat() == "2018-05-11"
    assert launch.mission.orbit_abbrev == "LEO"
    assert "National Aeronautics and Space Administration" in launch.mission.agencies

    (booster,) = launch.boosters
    assert booster.landing_attempt is True
    assert booster.landing_location == "LZ-40"

    (craft,) = launch.spacecraft
    assert craft.destination == "International Space Station"
    assert [(c.name, c.role, c.agency) for c in craft.crew] == [
        ("Kayla Barron", "Spacecraft Commander", "NASA"),
        ("Arutyun Kiviryan", "Flight Engineer", "RFSA"),
        ("Christina Birch", "Pilot", "NASA"),
        ("Makoto Suwa", "Flight Engineer", "JAXA"),
    ]


def test_event_fields(load):
    events = [parse_event(r) for r in load("events_upcoming.json")["results"]]
    first = events[0]
    assert first.id == "1525"
    assert first.name == "SpaceX CRS-35 Dragon Docking"
    assert first.type == "Docking"
    assert first.location == "International Space Station"
    assert first.precision == "MIN"
    assert first.net.isoformat() == "2026-10-15T15:00:00+00:00"
    assert events[1].precision == "M"
    assert events[2].type == "Flyby"
    assert events[2].precision == "DAY"


@pytest.mark.parametrize("name", [*LAUNCH_FILES, "events_upcoming.json"])
def test_to_dict_is_json_serialisable(load, name):
    parse = parse_event if name.startswith("events") else parse_launch
    for r in load(name)["results"]:
        json.dumps(to_dict(parse(r)))


def test_to_dict_values(load, detailed_launch):
    d = to_dict(parse_launch(load("launches_upcoming.json")["results"][0]))
    assert d["kind"] == "launch"
    assert d["net"] == "2026-10-10T23:00:00+00:00"
    assert d["status"]["abbrev"] == "Go"

    d = to_dict(parse_launch(detailed_launch))
    assert d["rocket"]["maiden_flight"] == "2018-05-11"
    assert d["spacecraft"][0]["crew"][0] == {"name": "Kayla Barron", "role": "Spacecraft Commander", "agency": "NASA"}

    d = to_dict(parse_event(load("events_upcoming.json")["results"][0]))
    assert d["kind"] == "event"
    assert d["net"] == "2026-10-15T15:00:00+00:00"


def test_launch_with_null_fields():
    launch = parse_launch(
        {
            "id": "x",
            "name": "Mystery",
            "status": None,
            "net": None,
            "net_precision": None,
            "pad": None,
            "mission": None,
            "rocket": None,
            "launch_service_provider": None,
            "image": None,
            "vid_urls": None,
        }
    )
    assert launch.status.abbrev == "TBD"
    assert launch.net is None
    assert launch.precision is None
    assert launch.pad is None
    assert launch.location is None
    assert launch.mission is None
    assert launch.description is None
    assert launch.provider is None
    assert launch.rocket is None
    assert launch.image_url is None
    assert launch.webcasts == ()
    json.dumps(to_dict(launch))


def test_launch_with_missing_fields():
    launch = parse_launch({"id": "x", "name": "Bare"})
    assert launch.status.name == "To Be Determined"
    assert (launch.net, launch.pad, launch.mission, launch.rocket, launch.provider) == (None,) * 5


def test_partial_nested_fields():
    launch = parse_launch(
        {
            "id": "x",
            "name": "n",
            "pad": {"name": "LC-1", "location": None},
            "mission": {"name": "m", "orbit": None, "agencies": None},
            "rocket": {"configuration": None, "launcher_stage": None, "spacecraft_stage": None},
        }
    )
    assert launch.location == "LC-1"
    assert launch.pad.country_code is None
    assert launch.mission.orbit is None
    assert launch.mission.agencies == ()
    assert launch.rocket is None
    assert launch.boosters == ()


def test_event_with_null_fields():
    event = parse_event({"id": 7, "name": "e", "type": None, "date": None, "date_precision": None, "location": ""})
    assert event.id == "7"
    assert event.type is None
    assert event.net is None
    assert event.precision is None
    assert event.location is None


def test_webcasts_rank_official_streams_first():
    def stream(priority, type_id, name):
        return {"priority": priority, "url": f"https://x/{name}", "title": name, "type": {"id": type_id, "name": name}}

    launch = parse_launch(
        {
            "id": "x",
            "name": "x",
            "vid_urls": [
                stream(8, 4, "Unofficial Re-stream"),
                stream(9, 3, "Unofficial Webcast"),
                stream(10, 1, "Official Webcast"),
                stream(11, 1, "Official Webcast 2"),
                {"priority": 1, "url": "https://x/untyped"},
            ],
        }
    )
    assert [w.title for w in launch.webcasts] == [
        "Official Webcast",
        "Official Webcast 2",
        "Unofficial Webcast",
        "Unofficial Re-stream",
        None,
    ]
    assert launch.webcasts[0].type == "Official Webcast"
