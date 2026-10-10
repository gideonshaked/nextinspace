from datetime import timedelta

import pytest

from nextinspace import __version__
from nextinspace.client import Filters, LL2Error, sort_key
from nextinspace.models import Event, Launch, parse_event, parse_launch

LAUNCHES = "/2.3.0/launches/upcoming/"
EVENTS = "/2.3.0/events/upcoming/"
PREVIOUS = "/2.3.0/launches/previous/"


def test_ttl_hit_skips_http(server, make_client):
    client = make_client()
    first = client.upcoming_launches(10)
    second = client.upcoming_launches(10)
    assert first == second
    assert len(server.requests) == 1
    assert make_client().upcoming_launches(10) == first
    assert len(server.requests) == 1
    assert client.notes == []


def test_different_params_are_cached_separately(server, make_client):
    client = make_client()
    client.upcoming_launches(10)
    client.upcoming_launches(5)
    assert len(server.requests) == 2


def test_refresh_bypasses_cache(server, make_client):
    make_client().upcoming_launches(10)
    make_client(refresh=True).upcoming_launches(10)
    assert len(server.requests) == 2


def test_expired_ttl_refetches(server, make_client):
    make_client().upcoming_launches(10)
    make_client(ttl=0).upcoming_launches(10)
    assert len(server.requests) == 2


def test_rate_limit_falls_back_to_cache(server, make_client):
    fresh = make_client().upcoming_launches(10)
    server.status = 429
    server.text = '{"detail": "Request was throttled. Expected available in 1800 seconds."}'
    client = make_client(ttl=0)
    assert client.upcoming_launches(10) == fresh
    assert len(server.requests) == 2
    (note,) = client.notes
    assert "rate limit" in note
    assert "30 min" in note
    assert "cached" in note


def test_rate_limit_without_cache_raises(server, make_client):
    server.status = 429
    with pytest.raises(LL2Error, match="NEXTINSPACE_API_KEY"):
        make_client().upcoming_launches(10)


def test_transport_error_falls_back_to_cache(server, make_client):
    fresh = make_client().upcoming_launches(10)
    server.offline = True
    client = make_client(refresh=True)
    assert client.upcoming_launches(10) == fresh
    (note,) = client.notes
    assert "could not reach" in note
    assert "ConnectError" in note


def test_transport_error_without_cache_raises(server, make_client):
    server.offline = True
    with pytest.raises(LL2Error, match="could not reach"):
        make_client().upcoming_launches(10)


def test_server_error_falls_back_to_cache(server, make_client):
    fresh = make_client().upcoming_launches(10)
    server.status = 503
    client = make_client(ttl=0)
    assert client.upcoming_launches(10) == fresh
    assert "HTTP 503" in client.notes[0]


def test_not_found_raises(make_client):
    with pytest.raises(LL2Error, match="nothing found"):
        make_client().launch("does-not-exist")


def test_headers(server, make_client):
    make_client(api_key="secret").upcoming_launches(1)
    make_client(refresh=True).upcoming_launches(1)
    keyed, anonymous = server.requests
    assert keyed.headers["Authorization"] == "Token secret"
    assert "Authorization" not in anonymous.headers
    for request in server.requests:
        assert request.headers["User-Agent"].startswith(f"nextinspace/{__version__} ")


def test_upcoming_merges_chronologically(server, load, make_client):
    launches = [parse_launch(r) for r in load("launches_upcoming.json")["results"]]
    events = [parse_event(r) for r in load("events_upcoming.json")["results"]]
    # The merge relies on LL2 returning each page already in order.
    assert launches == sorted(launches, key=sort_key)
    assert events == sorted(events, key=sort_key)

    items = make_client().upcoming(5)
    assert items == sorted(launches + events, key=sort_key)[:5]
    assert len(items) == 5
    assert any(isinstance(i, Event) for i in items)
    assert any(isinstance(i, Launch) for i in items)
    assert len(server.requests) == 2

    params = server.params(LAUNCHES)
    assert params == server.params(EVENTS)
    assert params == {"limit": "5", "mode": "normal", "hide_recent_previous": "true"}


def test_upcoming_kinds(server, make_client):
    client = make_client()
    assert all(isinstance(i, Launch) for i in client.upcoming(10, events=False))
    assert all(isinstance(i, Event) for i in client.upcoming(10, launches=False))
    assert server.paths() == [LAUNCHES, EVENTS]


@pytest.mark.parametrize(
    ("filters", "expected"),
    [(Filters(provider="SpaceX"), {"lsp__name": "SpaceX"}), (Filters(crewed=True), {"is_crewed": "true"})],
)
def test_launch_only_filters_skip_events(server, make_client, filters, expected):
    items = make_client().upcoming(5, filters=filters)
    assert all(isinstance(i, Launch) for i in items)
    assert server.paths() == [LAUNCHES]
    assert server.params(LAUNCHES).items() >= expected.items()


def test_search_applies_to_launches_and_events(server, make_client):
    make_client().upcoming(5, filters=Filters(search="dragon"))
    assert server.params(LAUNCHES)["search"] == "dragon"
    assert server.params(EVENTS)["search"] == "dragon"


def test_within_filters_locally(server, make_client, frozen):
    items = make_client().upcoming(5, filters=Filters(within=timedelta(days=2)))
    # Only the Starlink launch on Oct 10 23:00 falls before Oct 12 12:37:15.
    assert [i.name for i in items] == ["Falcon 9 Block 5 | Starlink Group 15-25"]
    for path in (LAUNCHES, EVENTS):
        assert not {"net__lte", "date__lte"} & server.params(path).keys()


def test_within_keeps_cache_key_stable(server, make_client, frozen):
    client = make_client()
    client.upcoming(5)
    client.upcoming(5, filters=Filters(within=timedelta(hours=1)))
    assert len(server.requests) == 2


def test_previous_launches(server, make_client, frozen):
    launches = make_client().previous_launches(10, Filters(within=timedelta(hours=36), provider="SpaceX"))
    # Of the ten fixture launches only the Oct 9 19:25 one is after Oct 9 00:37:15.
    assert [launch.net.isoformat() for launch in launches] == ["2026-10-09T19:25:00+00:00"]
    assert server.params(PREVIOUS) == {"limit": "10", "mode": "normal", "lsp__name": "SpaceX"}


def test_launch_detail(server, make_client):
    launch_id = server.detail["id"]
    launch = make_client().launch(launch_id)
    (request,) = server.requests
    assert request.url.path == f"/2.3.0/launches/{launch_id}/"
    assert dict(request.url.params) == {"mode": "detailed"}
    assert launch.id == launch_id
    assert [c.name for c in launch.spacecraft[0].crew][:1] == ["Kayla Barron"]


def test_detail_dispatches_on_kind(server, make_client):
    client = make_client()
    launch = parse_launch({"id": server.detail["id"], "name": "stub"})
    assert client.detail(launch).name == "Falcon 9 Block 5 | Crew-14"
    event = parse_event({"id": 1525, "name": "stub"})
    assert client.detail(event).name == "SpaceX CRS-35 Dragon Docking"
    assert server.paths()[-1] == "/2.3.0/events/1525/"
    assert dict(server.requests[-1].url.params) == {"mode": "detailed"}


def test_sort_key_puts_undated_last(load):
    dated = [parse_launch(r) for r in load("launches_upcoming.json")["results"][:3]]
    event = parse_event(load("events_upcoming.json")["results"][0])
    undated_launch = parse_launch({"id": "x", "name": "x"})
    undated_event = parse_event({"id": 1, "name": "y"})
    items = sorted([undated_launch, dated[2], undated_event, event, dated[0], dated[1]], key=sort_key)
    assert items[:4] == [dated[0], dated[1], event, dated[2]]
    assert {id(i) for i in items[4:]} == {id(undated_launch), id(undated_event)}
