"""Command-line interface."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import UTC, datetime, timedelta, tzinfo
from enum import StrEnum
from typing import Annotated, Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import typer
from rich.align import Align
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typer.core import TyperGroup

from nextinspace import __version__, ics, render
from nextinspace.client import PROD_URL, Client, Filters, LL2Error
from nextinspace.models import Item, Launch, to_dict
from nextinspace.timefmt import describe, parse_duration, relative


class DefaultToNext(TyperGroup):
    """Run ``next`` when no subcommand is given, so ``nextinspace 5 -l`` works."""

    def parse_args(self, ctx: Any, args: list[str]) -> list[str]:
        passthrough = {
            "--help",
            "-h",
            "--version",
            "--install-completion",
            "--show-completion",
        }
        if not args or (args[0] not in self.commands and args[0] not in passthrough):
            args = ["next", *args]
        return super().parse_args(ctx, args)


app = typer.Typer(
    cls=DefaultToNext,
    help="Never miss a launch. Upcoming rocket launches and spaceflight events from Launch Library 2.",
    epilog="Run without a command to list what's next. Data: The Space Devs, thespacedevs.com.",
    no_args_is_help=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)

out = Console(highlight=False)
err = Console(stderr=True, highlight=False)


class Format(StrEnum):
    table = "table"
    cards = "cards"
    json = "json"
    ics = "ics"


# ---- Shared options ----


def _zone(value: str | None) -> tzinfo | None:
    if value is None:
        return None
    try:
        return ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError):
        raise typer.BadParameter(f"unknown time zone {value!r}; use an IANA name like Europe/London") from None


def _duration(value: str | None) -> timedelta | None:
    if value is None:
        return None
    try:
        return parse_duration(value)
    except ValueError as e:
        raise typer.BadParameter(str(e)) from None


Count = Annotated[
    int,
    typer.Argument(min=1, max=100, help="How many items to show.", show_default=True),
]
Search = Annotated[
    str | None,
    typer.Option(
        "--search",
        "-s",
        help="Free-text search over names, rockets, providers and sites.",
    ),
]
Provider = Annotated[
    str | None,
    typer.Option(
        "--provider",
        "-p",
        help="Exact launch provider name, e.g. SpaceX or 'Rocket Lab'.",
    ),
]
Crewed = Annotated[bool, typer.Option("--crewed", help="Only launches carrying people.")]
Within = Annotated[
    str | None,
    typer.Option("--within", "-w", help="Only items within a time span: 90m, 36h, 7d, 2w."),
]
Tz = Annotated[
    str | None,
    typer.Option(
        "--tz",
        envvar="NEXTINSPACE_TZ",
        help="IANA time zone for display (default: system local).",
    ),
]
Refresh = Annotated[
    bool,
    typer.Option("--refresh", "-r", help="Ignore cached responses and ask the API again."),
]


def make_client(refresh: bool) -> Client:
    return Client(
        base_url=os.environ.get("NEXTINSPACE_API_URL") or PROD_URL,
        api_key=os.environ.get("NEXTINSPACE_API_KEY"),
        refresh=refresh,
    )


def flush_notes(client: Client) -> None:
    for note in dict.fromkeys(client.notes):
        err.print(Text(f"note: {note}", style="yellow"))
    client.notes.clear()


def fail(message: str) -> typer.Exit:
    err.print(Text(f"nextinspace: {message}", style="bold red"))
    return typer.Exit(1)


def emit_json(data: Any) -> None:
    sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def remember(client: Client, items: list[Item]) -> None:
    client.cache.save_listing([{"kind": i.kind, "id": i.id} for i in items])


def describe_filters(filters: Filters) -> str:
    parts = []
    if filters.search:
        parts.append(f"matching “{filters.search}”")
    if filters.provider:
        parts.append(f"by {filters.provider}")
    if filters.crewed:
        parts.append("crewed")
    if filters.within:
        parts.append("in the chosen window")
    return (" · " + ", ".join(parts)) if parts else ""


# ---- Commands ----


@app.callback()
def root(
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the version and exit.", is_eager=True),
    ] = False,
) -> None:
    if version:
        out.print(f"nextinspace {__version__}")
        raise typer.Exit()


@app.command("next")
def next_(
    count: Count = 5,
    launches: Annotated[bool, typer.Option("--launches", "-l", help="Only launches.")] = False,
    events: Annotated[
        bool,
        typer.Option("--events", "-e", help="Only events: dockings, spacewalks..."),
    ] = False,
    search: Search = None,
    provider: Provider = None,
    crewed: Crewed = False,
    within: Within = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show full cards with descriptions.")] = False,
    fmt: Annotated[Format, typer.Option("--format", "-f", help="Output format.")] = Format.table,
    as_json: Annotated[bool, typer.Option("--json", help="Shorthand for --format json.")] = False,
    tz: Tz = None,
    refresh: Refresh = False,
) -> None:
    """What's next: upcoming launches and events, soonest first."""
    if launches and events:
        raise typer.BadParameter("--launches and --events are mutually exclusive")
    filters = Filters(search=search, provider=provider, crewed=crewed, within=_duration(within))
    if events and filters.launch_only:
        raise typer.BadParameter("--provider and --crewed only apply to launches")
    fmt = Format.json if as_json else Format.cards if verbose and fmt == Format.table else fmt
    zone = _zone(tz)

    with make_client(refresh) as client:
        try:
            items = client.upcoming(count, launches=not events, events=not launches, filters=filters)
        except LL2Error as e:
            raise fail(str(e)) from None
        flush_notes(client)

        now = datetime.now(UTC)
        if fmt == Format.json:
            emit_json([to_dict(i) for i in items])
            return
        if fmt == Format.ics:
            sys.stdout.write(ics.calendar(items, now))
            return
        if not items:
            err.print("Nothing found." + (" Try fewer filters." if describe_filters(filters) else ""))
            return
        remember(client, items)

    noun = "launches" if launches else "events" if events else "in space"
    title = f"Next {noun}" + describe_filters(filters)
    if fmt == Format.cards:
        out.print(Text(title, style=f"bold {render.ACCENT}"))
        out.print(render.cards(items, now, zone))
    else:
        out.print(render.listing(items, now, zone, title=title, width=out.width))
        out.print(
            Text(
                "nextinspace show <#> for details · nextinspace watch for a live countdown",
                style="dim",
            )
        )


@app.command()
def past(
    count: Count = 5,
    search: Search = None,
    provider: Provider = None,
    crewed: Crewed = False,
    within: Within = None,
    as_json: Annotated[bool, typer.Option("--json", help="Output JSON.")] = False,
    tz: Tz = None,
    refresh: Refresh = False,
) -> None:
    """Recent launches and how they went."""
    filters = Filters(search=search, provider=provider, crewed=crewed, within=_duration(within))
    with make_client(refresh) as client:
        try:
            items = client.previous_launches(count, filters)
        except LL2Error as e:
            raise fail(str(e)) from None
        flush_notes(client)
        if as_json:
            emit_json([to_dict(i) for i in items])
            return
        if not items:
            err.print("Nothing found.")
            return
        remember(client, list(items))
    title = "Recent launches" + describe_filters(filters)
    out.print(render.outcomes(items, _zone(tz), title=title, width=out.width))


def resolve(client: Client, target: str | None) -> Item:
    """Turn a listing number, LL2 id or search text into an item."""
    if target is None:
        launches = client.upcoming_launches(1)
        if not launches:
            raise LL2Error("no upcoming launches")
        return client.detail(launches[0])
    if target.isdigit():
        refs = client.cache.load_listing()
        n = int(target)
        if 1 <= n <= len(refs):
            ref = refs[n - 1]
            return client.launch(ref["id"]) if ref["kind"] == "launch" else client.event(ref["id"])
        if refs:
            raise LL2Error(f"the last listing only had {len(refs)} items")
        upcoming = client.upcoming(n)
        if len(upcoming) < n:
            raise LL2Error(f"only {len(upcoming)} upcoming items")
        return client.detail(upcoming[n - 1])
    if len(target) == 36 and target.count("-") == 4:
        return client.launch(target)
    filters = Filters(search=target)
    found = client.upcoming(1, filters=filters) or client.previous_launches(1, filters)
    if not found:
        raise LL2Error(f"nothing matches {target!r}")
    return client.detail(found[0])


TargetArg = Annotated[
    str | None,
    typer.Argument(
        help="A number from the last listing, an LL2 launch id, or search text. Defaults to the next launch.",
        show_default=False,
    ),
]


@app.command()
def show(
    target: TargetArg = None,
    as_json: Annotated[bool, typer.Option("--json", help="Output JSON.")] = False,
    tz: Tz = None,
    refresh: Refresh = False,
) -> None:
    """Everything about one launch or event: mission, rocket, booster, crew, pad and webcasts."""
    zone = _zone(tz)
    with make_client(refresh) as client:
        try:
            item = resolve(client, target)
        except LL2Error as e:
            raise fail(str(e)) from None
        flush_notes(client)
    if as_json:
        emit_json(to_dict(item))
        return
    out.print(render.detail(item, datetime.now(UTC), zone))


def watch_view(item: Item, upcoming: list[Launch], now: datetime, tz: tzinfo | None) -> Group:
    name, _ = render.split_name(item)
    head = Text(name, style=f"bold {render.ACCENT}", justify="center")
    sub = render.subtitle(item)
    if sub:
        head.append("\n" + sub, style="dim")
    if item.location:
        head.append("\n" + item.location, style="dim")

    facts = Text(justify="center")
    facts.append_text(render.status_text(item))
    facts.append("   " + describe(item.net, item.precision, tz))
    if isinstance(item, Launch) and item.probability is not None:
        facts.append(f"   {item.probability}% go", style="dim")
    if isinstance(item, Launch) and item.weather_concerns:
        facts.append(f"\nWeather: {item.weather_concerns}", style="yellow")
    if item.webcasts:
        w = item.webcasts[0]
        facts.append("\n▶ ", style="red")
        facts.append(w.title or w.url, style=f"underline link {w.url}")

    hero = Panel(
        Group(head, Text(), Align.center(render.big_countdown(item, now)), Text(), facts),
        border_style=render.countdown_style(item, now),
        padding=(1, 2),
    )

    later = Table(box=None, show_header=False, pad_edge=False, expand=False)
    later.add_column(justify="right", no_wrap=True)
    later.add_column()
    later.add_column(style="dim")
    for launch in [u for u in upcoming if u.id != item.id][:4]:
        mission, _ = render.split_name(launch)
        later.add_row(
            Text(
                relative(launch.net, launch.precision, now),
                style=render.countdown_style(launch, now),
            ),
            Text(mission, style="bold"),
            render.subtitle(launch),
        )
    footer = Text("Updates itself · Ctrl+C to exit", style="dim", justify="center")
    return Group(
        hero,
        Panel(later, title="Up next", title_align="left", border_style="dim"),
        footer,
    )


@app.command()
def watch(
    target: TargetArg = None,
    tz: Tz = None,
    refresh: Refresh = False,
) -> None:
    """Full-screen live countdown to the next launch (or any launch you name)."""
    zone = _zone(tz)
    client = make_client(refresh)
    item: Item | None = None
    upcoming: list[Launch] = []
    loaded_at = 0.0
    try:
        with Live(console=out, screen=True, auto_refresh=False, transient=True) as live:
            while True:
                # The client's cache keeps this to one real request per TTL; reloading
                # every minute only picks up the next launch once this one is gone.
                if time.monotonic() - loaded_at > 60:
                    try:
                        upcoming = client.upcoming_launches(5)
                        if target is None and not upcoming:
                            raise LL2Error("no upcoming launches")
                        item = resolve(client, target) if target else client.detail(upcoming[0])
                        loaded_at = time.monotonic()
                        client.refresh = False
                    except LL2Error as e:
                        if item is None:
                            raise
                        client.notes.append(str(e))
                        loaded_at = time.monotonic()
                assert item is not None
                live.update(watch_view(item, upcoming, datetime.now(UTC), zone), refresh=True)
                time.sleep(1 - time.time() % 1)
    except KeyboardInterrupt:
        pass
    except LL2Error as e:
        raise fail(str(e)) from None
    finally:
        client.close()
        flush_notes(client)


@app.command()
def browse(tz: Tz = None, refresh: Refresh = False) -> None:
    """Interactive full-screen browser: search, filter, read details and open webcasts."""
    from nextinspace.tui import Browser

    Browser(make_client(refresh), _zone(tz)).run()


def main() -> None:
    app()
