import io
import json
from datetime import UTC, datetime

import pytest
from rich.console import Console
from typer.testing import CliRunner

from nextinspace import __version__, cli
from nextinspace.models import parse_launch

LAUNCHES = "/2.3.0/launches/upcoming/"
EVENTS = "/2.3.0/events/upcoming/"
PREVIOUS = "/2.3.0/launches/previous/"
UUID = "0d779392-1a36-4c1e-b0b8-ec11e3031ee6"


@pytest.fixture
def run(monkeypatch, make_client, frozen):
    monkeypatch.setattr(cli, "make_client", lambda refresh: make_client(refresh=refresh))
    monkeypatch.setattr(cli, "datetime", frozen)
    monkeypatch.setattr(cli, "out", Console(width=160, highlight=False))
    monkeypatch.setenv("NEXTINSPACE_TZ", "UTC")
    runner = CliRunner()
    return lambda *args: runner.invoke(cli.app, list(args))


def test_bare_invocation_lists_next(run, server, load):
    result = run()
    assert result.exit_code == 0, result.output
    assert "Next in space" in result.stdout
    assert "Starlink Group 15-25" in result.stdout
    assert "SpaceX CRS-35 Dragon Docking" in result.stdout
    assert "T-10:22:45" in result.stdout
    assert server.params(LAUNCHES)["limit"] == "5"
    assert server.params(EVENTS)["limit"] == "5"


def test_positional_count_routes_to_next(run, server):
    result = run("3", "-l")
    assert result.exit_code == 0, result.output
    assert "Next launches" in result.stdout
    assert server.paths() == [LAUNCHES]
    assert server.params(LAUNCHES)["limit"] == "3"
    assert "Dragon CRS-2 SpX-35" in result.stdout
    assert "SpaceX CRS-35 Dragon Docking" not in result.stdout


def test_verbose_cards(run):
    result = run("2", "-v")
    assert result.exit_code == 0, result.output
    assert "1. Starlink Group 15-25" in result.stdout
    assert "2. Dragon CRS-2 SpX-35" in result.stdout


def test_json(run):
    result = run("7", "--json")
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert len(data) == 7
    assert data[0]["name"] == "Falcon 9 Block 5 | Starlink Group 15-25"
    assert {d["kind"] for d in data} == {"launch", "event"}


def test_ics(run):
    result = run("-f", "ics")
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith("BEGIN:VCALENDAR")
    assert "BEGIN:VEVENT" in result.stdout


def test_version(run, server):
    result = run("--version")
    assert result.exit_code == 0
    assert result.stdout.strip() == f"nextinspace {__version__}"
    assert server.requests == []


@pytest.mark.parametrize(
    "args",
    [
        ["-l", "-e"],
        ["-e", "--crewed"],
        ["-e", "-p", "SpaceX"],
        ["--tz", "Bad/Zone"],
        ["-w", "7x"],
        ["0"],
        ["past", "--json", "--tz", "Bad/Zone"],
    ],
)
def test_bad_arguments_exit_2(run, server, args):
    result = run(*args)
    assert result.exit_code == 2
    assert server.requests == []


def test_api_error_exits_1(run, server):
    server.status = 429
    result = run()
    assert result.exit_code == 1
    assert "nextinspace:" in result.stderr
    assert "NEXTINSPACE_API_KEY" in result.stderr
    assert result.stdout == ""


def test_stale_data_note_on_stderr(run, server):
    assert run("-l").exit_code == 0
    server.status = 429
    result = run("-l", "--refresh")
    assert result.exit_code == 0
    assert "Starlink Group 15-25" in result.stdout
    assert "note:" in result.stderr
    assert "rate limit" in result.stderr


def test_nothing_found(run, server):
    server.pages[LAUNCHES]["results"] = []
    result = run("-l", "-s", "nothing")
    assert result.exit_code == 0
    assert "Nothing found." in result.stderr


def test_show_number_uses_last_listing(run, server, load):
    assert run().exit_code == 0
    first = load("launches_upcoming.json")["results"][0]["id"]

    result = run("show", "1")
    assert result.exit_code == 0, result.output
    assert server.paths()[-1] == f"/2.3.0/launches/{first}/"
    assert dict(server.requests[-1].url.params) == {"mode": "detailed"}
    assert "Kayla Barron" in result.stdout

    assert run("show", "3").exit_code == 0
    assert server.paths()[-1] == "/2.3.0/events/1525/"

    result = run("show", "9")
    assert result.exit_code == 1
    assert "only had 5 items" in result.stderr


def test_show_uuid(run, server):
    result = run("show", UUID, "--json")
    assert result.exit_code == 0, result.output
    assert server.paths() == [f"/2.3.0/launches/{UUID}/"]
    assert json.loads(result.stdout)["id"] == UUID


def test_show_search_text(run, server, load):
    result = run("show", "sometext")
    assert result.exit_code == 0, result.output
    assert server.params(LAUNCHES)["search"] == "sometext"
    assert server.params(EVENTS)["search"] == "sometext"
    first = load("launches_upcoming.json")["results"][0]["id"]
    assert server.paths()[-1] == f"/2.3.0/launches/{first}/"


def test_past(run, server):
    result = run("past", "10", "--json", "-p", "SpaceX")
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert len(data) == 10
    assert data[0]["status"]["abbrev"] == "Go"
    assert server.params(PREVIOUS) == {"limit": "10", "mode": "normal", "lsp__name": "SpaceX"}

    result = run("past")
    assert result.exit_code == 0, result.output
    assert "Recent launches" in result.stdout
    assert "NeonSat-2 to 6" in result.stdout


def test_watch_view(load, detailed_launch):
    launches = [parse_launch(r) for r in load("launches_upcoming.json")["results"]]
    now = datetime(2026, 10, 10, 12, tzinfo=UTC)
    console = Console(width=100, record=True, color_system=None, file=io.StringIO())

    console.print(cli.watch_view(launches[0], launches, now, UTC))
    text = console.export_text()
    assert text.count("Starlink Group 15-25") == 1
    assert "Space Launch Complex 4E, Vandenberg SFB, CA, USA" in text
    assert "Up next" in text
    assert "Dragon CRS-2 SpX-35" in text
    assert "Sat Oct 10, 2026 23:00 UTC" in text
    assert sum("█" in line for line in text.splitlines()) == 5
    assert "Updates itself" in text

    console.print(cli.watch_view(parse_launch(detailed_launch), launches, now, UTC))
    assert "NET March 2027" in console.export_text()


def test_completion_offers_subcommands(monkeypatch):
    monkeypatch.setenv("_NEXTINSPACE_COMPLETE", "complete_zsh")
    monkeypatch.setenv("_TYPER_COMPLETE_ARGS", "nextinspace sh")
    result = CliRunner().invoke(cli.app, [], prog_name="nextinspace")
    assert "show" in result.output


def test_ics_with_nothing_exportable_fails(run, server, load):
    page = load("launches_upcoming.json")
    server.pages[LAUNCHES] = {**page, "results": [r for r in page["results"] if r["net_precision"]["abbrev"] == "M"]}
    result = run("-l", "-f", "ics")
    assert result.exit_code == 1
    assert "nothing to export" in result.stderr
    assert "BEGIN:VCALENDAR" not in result.stdout
