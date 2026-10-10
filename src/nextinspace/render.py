"""Rich renderables for launches and events.

Every function takes ``now`` and ``tz`` explicitly so output is reproducible. Data from
the API is always wrapped in ``Text`` rather than interpolated into markup, because
names like "Starlink [Group 6]" would otherwise be parsed as style tags.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, tzinfo

from rich import box
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nextinspace.models import Event, Item, Launch, Webcast
from nextinspace.timefmt import countdown, describe, has_clock, relative

STATUS_STYLES = {
    "Go": "bold green",
    "TBC": "yellow",
    "TBD": "dim yellow",
    "Hold": "bold red",
    "In Flight": "bold cyan",
    "Success": "green",
    "Deployed": "green",
    "Failure": "bold red",
    "Partial Failure": "red",
}
EVENT_STYLE = "magenta"
ACCENT = "bright_cyan"
LANDING = {True: ("landed", "green"), False: ("lost", "red"), None: ("landing", "yellow")}


def status_text(item: Item) -> Text:
    if isinstance(item, Event):
        text = Text(item.type or "Event", style=EVENT_STYLE)
    else:
        text = Text(item.status.abbrev, style=STATUS_STYLES.get(item.status.abbrev, ""))
    if item.webcast_live:
        text.append(" ● LIVE", style="bold red")
    return text


def countdown_style(item: Item, now: datetime) -> str:
    if item.net is None or not has_clock(item.precision):
        return "dim"
    seconds = (item.net - now).total_seconds()
    if seconds < 0:
        return "green"
    if seconds < 3600:
        return "bold red"
    if seconds < 86400:
        return "bold yellow"
    return ACCENT


def split_name(item: Item) -> tuple[str, str | None]:
    """LL2 names launches "<rocket> | <mission>"; return the mission and the rocket."""
    if isinstance(item, Launch) and " | " in item.name:
        rocket, mission = item.name.split(" | ", 1)
        return mission, rocket
    return item.name, None


def subtitle(item: Item) -> str:
    if isinstance(item, Event):
        return ""
    parts = [split_name(item)[1] or (item.rocket.full_name if item.rocket else None)]
    if item.provider:
        long = len(item.provider.name) > 24 and item.provider.abbrev
        parts.append(item.provider.abbrev if long else item.provider.name)
    if item.mission and item.mission.orbit_abbrev:
        parts.append(item.mission.orbit_abbrev)
    return " · ".join(p for p in parts if p)


# ---- Listing ----


def site(item: Item) -> str | None:
    """Launch site without the pad, which is too long for a table cell."""
    if isinstance(item, Launch) and item.pad:
        return item.pad.location or item.pad.name
    return item.location


def when(item: Item, now: datetime) -> Text:
    """Countdown cell: blank when the date is too coarse for a relative time to mean anything."""
    if item.net is not None and not has_clock(item.precision) and item.precision not in {"AM", "PM", "DAY"}:
        return Text("")
    return Text(relative(item.net, item.precision, now), style=countdown_style(item, now))


def listing(items: Sequence[Item], now: datetime, tz: tzinfo | None, *, title: str, width: int) -> Table:
    table = Table(
        title=Text(title, style=f"bold {ACCENT}"),
        title_justify="left",
        box=box.SIMPLE_HEAD,
        header_style="dim",
        pad_edge=False,
        expand=False,
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("When", no_wrap=True)
    table.add_column("Date", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Mission", ratio=3, min_width=24)
    show_location = width >= 110
    if show_location:
        table.add_column("Location", ratio=2, style="dim")

    for i, item in enumerate(items, 1):
        name, _ = split_name(item)
        mission = Text(name, style="bold")
        sub = subtitle(item)
        if sub:
            mission.append("\n" + sub, style="dim")
        row: list[RenderableType] = [
            str(i),
            when(item, now),
            describe(item.net, item.precision, tz),
            status_text(item),
            mission,
        ]
        if show_location:
            row.append(Text(site(item) or "", style="dim"))
        table.add_row(*row)
    return table


def outcomes(items: Sequence[Launch], tz: tzinfo | None, *, title: str, width: int) -> Table:
    """Listing of past launches, with failure reasons where the API gives one."""
    table = Table(
        title=Text(title, style=f"bold {ACCENT}"),
        title_justify="left",
        box=box.SIMPLE_HEAD,
        header_style="dim",
        pad_edge=False,
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Date", no_wrap=True)
    table.add_column("Result", no_wrap=True)
    table.add_column("Mission", ratio=3, min_width=24)
    show_location = width >= 110
    if show_location:
        table.add_column("Location", ratio=2, style="dim")
    for i, item in enumerate(items, 1):
        name, _ = split_name(item)
        mission = Text(name, style="bold")
        mission.append("\n" + subtitle(item), style="dim")
        if item.failreason:
            mission.append("\n" + item.failreason, style="red")
        row: list[RenderableType] = [str(i), describe(item.net, item.precision, tz), status_text(item), mission]
        if show_location:
            row.append(Text(site(item) or "", style="dim"))
        table.add_row(*row)
    return table


def cards(items: Sequence[Item], now: datetime, tz: tzinfo | None) -> Group:
    return Group(*(card(item, now, tz, index=i) for i, item in enumerate(items, 1)))


def card(item: Item, now: datetime, tz: tzinfo | None, *, index: int | None = None) -> Panel:
    grid = _kv_grid()
    _row(grid, "When", Text(describe(item.net, item.precision, tz)))
    _row(grid, "Countdown", when(item, now))
    if isinstance(item, Launch):
        _row(grid, "Provider", item.provider.name if item.provider else None)
        _row(grid, "Rocket", item.rocket.full_name if item.rocket else None)
        if item.mission:
            _row(grid, "Mission", " · ".join(p for p in (item.mission.type, item.mission.orbit) if p) or None)
        _row(grid, "Probability", f"{item.probability}% go" if item.probability is not None else None)
    _row(grid, "Location", item.location)
    body: list[RenderableType] = [grid]
    if item.description:
        body.append(Padding(Text(item.description.strip(), style="italic"), (1, 0, 0, 0)))
    name, _ = split_name(item)
    title = Text.assemble((f"{index}. " if index else "", "dim"), (name, "bold"))
    return Panel(
        Group(*body),
        title=title,
        title_align="left",
        subtitle=status_text(item),
        subtitle_align="right",
        border_style=EVENT_STYLE if isinstance(item, Event) else ACCENT,
        padding=(0, 1),
    )


# ---- Detail ----


def detail(item: Item, now: datetime, tz: tzinfo | None) -> Group:
    return launch_detail(item, now, tz) if isinstance(item, Launch) else event_detail(item, now, tz)


def _header(item: Item, now: datetime, tz: tzinfo | None) -> Panel:
    name, rocket = split_name(item)
    head = Text(name, style=f"bold {ACCENT}")
    if rocket:
        head.append(f"  {rocket}", style="bold")
    head.append("\n")
    head.append_text(status_text(item))
    if isinstance(item, Launch) and item.status.description:
        head.append(f"  {item.status.description}", style="dim")

    grid = _kv_grid()
    if item.net and has_clock(item.precision):
        _row(grid, "Countdown", Text(countdown(item.net, now), style=countdown_style(item, now)))
    _row(grid, "NET", describe(item.net, item.precision, tz))
    if item.net and has_clock(item.precision):
        _row(grid, "UTC", Text(describe(item.net, item.precision, UTC), style="dim"))
    if isinstance(item, Launch):
        if item.window_start and item.window_end and item.window_start != item.window_end and has_clock(item.precision):
            minutes = int((item.window_end - item.window_start).total_seconds() // 60)
            span = f"{item.window_start.astimezone(tz):%H:%M} to {item.window_end.astimezone(tz):%H:%M %Z}"
            _row(grid, "Window", f"{span} ({minutes} min)")
        elif item.window_start and item.window_start == item.window_end and has_clock(item.precision):
            _row(grid, "Window", "Instantaneous")
        _row(grid, "Probability", f"{item.probability}% go" if item.probability is not None else None)
        _row(grid, "Weather", item.weather_concerns)
        _row(grid, "Failure", Text(item.failreason, style="red") if item.failreason else None)
    return Panel(Group(head, Text(), grid), box=box.HEAVY, border_style=ACCENT, padding=(0, 1))


def launch_detail(launch: Launch, now: datetime, tz: tzinfo | None) -> Group:
    sections: list[RenderableType] = [_header(launch, now, tz)]

    if launch.mission:
        m = launch.mission
        grid = _kv_grid()
        _row(grid, "Type", m.type)
        _row(grid, "Orbit", f"{m.orbit} ({m.orbit_abbrev})" if m.orbit and m.orbit_abbrev else m.orbit)
        _row(grid, "Customers", ", ".join(m.agencies) or None)
        body: list[RenderableType] = [grid]
        if m.description:
            body.append(Padding(Text(m.description.strip()), (1, 0, 0, 0)))
        sections.append(_section(f"Mission · {m.name}", Group(*body)))

    vehicle: list[RenderableType] = []
    if launch.rocket:
        r = launch.rocket
        grid = _kv_grid()
        _row(grid, "Provider", launch.provider.name if launch.provider else None)
        _row(grid, "Family", r.family)
        _row(grid, "Height", _unit(r.length_m, "m"))
        _row(grid, "Diameter", _unit(r.diameter_m, "m"))
        _row(grid, "Liftoff mass", _unit(r.launch_mass_t, "t"))
        _row(grid, "Liftoff thrust", _unit(r.thrust_kn, "kN"))
        _row(grid, "To LEO", _unit(r.leo_capacity_kg, "kg"))
        _row(grid, "To GTO", _unit(r.gto_capacity_kg, "kg"))
        _row(grid, "Reusable", {True: "yes", False: "no", None: None}[r.reusable])
        if r.maiden_flight:
            _row(grid, "First flight", f"{r.maiden_flight:%B} {r.maiden_flight.day}, {r.maiden_flight.year}")
        _row(grid, "Record", _record(r.successful_launches, r.failed_launches, r.consecutive_successes))
        vehicle.append(grid)
    for b in launch.boosters:
        line = Text("Booster ", style="dim")
        line.append(b.serial or "unassigned", style="bold")
        if b.flight_number:
            line.append(f"  flight {b.flight_number}")
        if b.landing_attempt:
            verb, style = LANDING[b.landing_success]
            line.append(f"  {verb} → {b.landing_location or 'unknown site'}", style=style)
        elif b.landing_attempt is False:
            line.append("  expended", style="dim")
        vehicle.append(line)
    if vehicle:
        vehicle_name = launch.rocket.full_name if launch.rocket else "Unknown"
        sections.append(_section(f"Vehicle · {vehicle_name}", Group(*vehicle)))

    for craft in launch.spacecraft:
        title = craft.name + (f" ({craft.serial})" if craft.serial else "")
        if craft.destination:
            title += f" → {craft.destination}"
        crew = Table(box=None, show_header=bool(craft.crew), header_style="dim", pad_edge=False)
        crew.add_column("Crew")
        crew.add_column("Role")
        crew.add_column("Agency")
        for c in craft.crew:
            crew.add_row(Text(c.name, style="bold"), c.role or "", c.agency or "")
        sections.append(_section(f"Spacecraft · {title}", crew if craft.crew else Text("Uncrewed", style="dim")))

    if launch.pad:
        p = launch.pad
        grid = _kv_grid()
        _row(grid, "Pad", p.name)
        _row(grid, "Site", p.location)
        if p.latitude is not None and p.longitude is not None:
            _row(grid, "Coordinates", f"{p.latitude:.4f}, {p.longitude:.4f}")
        _row(grid, "Map", _link(p.map_url))
        sections.append(_section("Launch site", grid))

    links = _links(launch.webcasts, launch.info_urls, launch.rocket.wiki_url if launch.rocket else None)
    if links:
        sections.append(_section("Watch & read", links))

    trivia = []
    year = launch.net.astimezone(UTC).year if launch.net else None
    if launch.provider and launch.provider_launches_this_year and year:
        trivia.append(f"{launch.provider.name}'s {ordinal(launch.provider_launches_this_year)} launch of {year}")
    if launch.orbital_launches_this_year and year:
        trivia.append(f"{ordinal(launch.orbital_launches_this_year)} orbital launch attempt of {year}")
    if trivia:
        sections.append(Padding(Text(" · ".join(trivia), style="dim italic"), (0, 1)))
    return Group(*sections)


def event_detail(event: Event, now: datetime, tz: tzinfo | None) -> Group:
    sections: list[RenderableType] = [_header(event, now, tz)]
    grid = _kv_grid()
    _row(grid, "Type", event.type)
    _row(grid, "Location", event.location)
    body: list[RenderableType] = [grid]
    if event.description:
        body.append(Padding(Text(event.description.strip()), (1, 0, 0, 0)))
    sections.append(_section("Event", Group(*body)))
    links = _links(event.webcasts, event.info_urls, None)
    if links:
        sections.append(_section("Watch & read", links))
    return Group(*sections)


# ---- Big countdown ----

# A 3x5 block font. Every glyph has exactly five rows of equal width.
_FONT = {
    "0": ["███", "█ █", "█ █", "█ █", "███"],
    "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"],
    "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"],
    "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"],
    "7": ["███", "  █", " █ ", " █ ", " █ "],
    "8": ["███", "█ █", "███", "█ █", "███"],
    "9": ["███", "█ █", "███", "  █", "███"],
    ":": [" ", "▪", " ", "▪", " "],
    "-": ["   ", "   ", "███", "   ", "   "],
    "+": ["   ", " █ ", "███", " █ ", "   "],
    "T": ["███", " █ ", " █ ", " █ ", " █ "],
    "d": ["  █", "  █", "███", "█ █", "███"],
    " ": ["  ", "  ", "  ", "  ", "  "],
}


def big(text: str, style: str) -> Text:
    rows = [" ".join(_FONT[ch][r] for ch in text) for r in range(5)]
    return Text("\n".join(rows), style=style)


def big_countdown(item: Item, now: datetime) -> Text:
    """Large countdown for ``watch``; a plain sentence when the time is not known precisely."""
    if item.net is None or not has_clock(item.precision):
        return Text(f"NET {describe(item.net, item.precision, UTC)}", style="bold dim")
    return big(countdown(item.net, now), countdown_style(item, now))


def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ---- Helpers ----


def _kv_grid() -> Table:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", no_wrap=True)
    grid.add_column()
    return grid


def _row(grid: Table, key: str, value: RenderableType | None) -> None:
    if value:
        grid.add_row(key, Text(value) if isinstance(value, str) else value)


def _section(title: str, body: RenderableType) -> Panel:
    return Panel(body, title=Text(title, style="bold"), title_align="left", border_style="dim", padding=(0, 1))


def _unit(value: float | None, unit: str) -> str | None:
    if value is None:
        return None
    return f"{value:,.0f} {unit}" if value >= 100 else f"{value:g} {unit}"


def _record(ok: int | None, failed: int | None, streak: int | None) -> str | None:
    if ok is None or failed is None or ok + failed == 0:
        return None
    rate = 100 * ok / (ok + failed)
    record = f"{ok} of {ok + failed} successful ({rate:.1f}%)"
    return record + (f", {streak} in a row" if streak else "")


def _link(url: str | None, label: str | None = None) -> Text | None:
    if not url:
        return None
    return Text(label or url, style=f"underline link {url}")


def _links(webcasts: Iterable[Webcast], info_urls: Iterable[str], wiki: str | None) -> Group | None:
    lines: list[RenderableType] = []
    for w in webcasts:
        line = Text("▶ ", style="red")
        if w.live:
            line.append("LIVE ", style="bold red")
        line.append(w.title or w.url, style=f"underline link {w.url}")
        if w.publisher:
            line.append(f"  {w.publisher}", style="dim")
        lines.append(line)
    for url in info_urls:
        lines.append(Text.assemble(("ⓘ ", "dim"), _link(url) or ""))
    if wiki:
        lines.append(Text.assemble(("W ", "dim"), _link(wiki) or ""))
    return Group(*lines) if lines else None
