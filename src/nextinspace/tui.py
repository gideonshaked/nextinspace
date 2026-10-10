"""Interactive browser built on Textual.

Moving the cursor shows a card built from the listing data already in hand. Full
details cost an API request each, so they are fetched only when a row is opened
with Enter; after that they come from the cache.
"""

from __future__ import annotations

import webbrowser
from datetime import UTC, datetime, tzinfo
from typing import ClassVar

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import DataTable, Footer, Header, Input, Static

from nextinspace import render
from nextinspace.client import Client, Filters, LL2Error
from nextinspace.models import Item, Launch
from nextinspace.timefmt import describe, has_clock

MODES = {"all": "Next in space", "launches": "Next launches", "events": "Next events", "past": "Recent launches"}
LIMIT = 30


def key(item: Item) -> str:
    return f"{item.kind}:{item.id}"


class Browser(App[None]):
    TITLE = "nextinspace"
    CSS = """
    #search { display: none; margin: 0 1; }
    #search.visible { display: block; }
    #body { height: 1fr; }
    #list { width: 3fr; min-width: 60; }
    #detail-scroll { width: 2fr; min-width: 50; border-left: tall $primary-background; padding: 0 1; }
    #status { height: 1; padding: 0 1; color: $text-muted; }
    """
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("slash", "search", "Search"),
        Binding("a", "mode('all')", "All"),
        Binding("l", "mode('launches')", "Launches"),
        Binding("e", "mode('events')", "Events"),
        Binding("p", "mode('past')", "Past"),
        Binding("w", "open_webcast", "Webcast"),
        Binding("m", "open_map", "Map"),
        Binding("r", "reload", "Refresh"),
        Binding("escape", "clear_search", "Clear search", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, client: Client, tz: tzinfo | None) -> None:
        super().__init__()
        self.client = client
        self.tz = tz
        self.mode = "all"
        self.search: str | None = None
        self.items: list[Item] = []
        self.details: dict[str, Item] = {}
        self.current: Item | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Search names, rockets, providers, sites (Enter to search, Esc to clear)", id="search")
        with Horizontal(id="body"):
            yield DataTable(id="list", cursor_type="row", zebra_stripes=True)
            with VerticalScroll(id="detail-scroll"):
                yield Static(id="detail")
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_column("When", key="when", width=15)
        table.add_column("Status", key="status")
        table.add_column("Mission", key="mission")
        table.focus()
        self.load()
        self.set_interval(1, self.tick)

    # ---- Data ----

    @work(thread=True, exclusive=True, group="list")
    def load(self, refresh: bool = False) -> None:
        self.call_from_thread(self.set_status, "Loading...")
        filters = Filters(search=self.search)
        self.client.refresh = refresh
        try:
            if self.mode == "past":
                items: list[Item] = list(self.client.previous_launches(LIMIT, filters))
            else:
                items = self.client.upcoming(
                    LIMIT, launches=self.mode != "events", events=self.mode != "launches", filters=filters
                )
        except LL2Error as e:
            self.call_from_thread(self.set_status, str(e), "red")
            return
        finally:
            self.client.refresh = False
        self.call_from_thread(self.show_items, items)

    @work(thread=True, exclusive=True, group="detail")
    def load_detail(self, item: Item) -> None:
        self.call_from_thread(self.set_status, f"Fetching details for {item.name}...")
        try:
            full = self.client.detail(item)
        except LL2Error as e:
            self.call_from_thread(self.set_status, str(e), "red")
            return
        self.details[key(item)] = full
        self.call_from_thread(self.show_detail, full)
        self.call_from_thread(self.set_status, full.name)

    # ---- View ----

    def set_status(self, message: str, style: str = "") -> None:
        status = Text(message, style=style)
        for note in dict.fromkeys(self.client.notes):
            status.append(f"  {note}", style="yellow")
        self.client.notes.clear()
        self.query_one("#status", Static).update(status)

    def show_items(self, items: list[Item]) -> None:
        self.items = items
        self.sub_title = MODES[self.mode] + (f" matching “{self.search}”" if self.search else "")
        table = self.query_one(DataTable)
        table.clear()
        now = datetime.now(UTC)
        for item in items:
            name, _ = render.split_name(item)
            mission = Text(name, style="bold")
            sub = render.subtitle(item)
            if sub:
                mission.append(f"  {sub}", style="dim")
            table.add_row(self.when(item, now), render.status_text(item), mission, key=key(item))
        self.set_status(f"{len(items)} items · Enter for full details · / to search")
        if items:
            table.move_cursor(row=0)
            self.show_detail(items[0])
        else:
            self.query_one("#detail", Static).update(Text("Nothing found.", style="dim"))

    def when(self, item: Item, now: datetime) -> Text:
        cell = Text("") if self.mode == "past" else render.when(item, now)
        return cell if cell.plain else Text(describe(item.net, item.precision, self.tz), style="dim")

    def show_detail(self, item: Item) -> None:
        item = self.details.get(key(item), item)
        self.current = item
        now = datetime.now(UTC)
        full = key(item) in self.details
        view = render.detail(item, now, self.tz) if full else render.card(item, now, self.tz)
        self.query_one("#detail", Static).update(view)

    def tick(self) -> None:
        if self.mode == "past" or not self.items:
            return
        table = self.query_one(DataTable)
        now = datetime.now(UTC)
        for item in self.items:
            if item.net and has_clock(item.precision):
                table.update_cell(key(item), "when", self.when(item, now))
        if self.current and self.current.net and has_clock(self.current.precision):
            self.show_detail(self.current)

    # ---- Events ----

    @on(DataTable.RowHighlighted)
    def highlighted(self, event: DataTable.RowHighlighted) -> None:
        item = self._item(event.row_key.value)
        if item and (self.current is None or self.current.id != item.id):
            self.show_detail(item)

    @on(DataTable.RowSelected)
    def selected(self, event: DataTable.RowSelected) -> None:
        item = self._item(event.row_key.value)
        if item:
            self.load_detail(item)

    @on(Input.Submitted, "#search")
    def searched(self, event: Input.Submitted) -> None:
        self.search = event.value.strip() or None
        self.query_one(DataTable).focus()
        self.load()

    def _item(self, row: str | None) -> Item | None:
        return next((i for i in self.items if key(i) == row), None)

    # ---- Actions ----

    def action_search(self) -> None:
        box = self.query_one("#search", Input)
        box.add_class("visible")
        box.focus()

    def action_clear_search(self) -> None:
        box = self.query_one("#search", Input)
        box.value = ""
        box.remove_class("visible")
        self.query_one(DataTable).focus()
        if self.search:
            self.search = None
            self.load()

    def action_mode(self, mode: str) -> None:
        if mode != self.mode:
            self.mode = mode
            self.load()

    def action_reload(self) -> None:
        self.details.clear()
        self.load(refresh=True)

    def action_open_webcast(self) -> None:
        if self.current is None:
            return
        if not self.current.webcasts:
            self.set_status("No webcast known yet. Press Enter to fetch full details first.")
            return
        webbrowser.open(self.current.webcasts[0].url)

    def action_open_map(self) -> None:
        if isinstance(self.current, Launch) and self.current.pad and self.current.pad.map_url:
            webbrowser.open(self.current.pad.map_url)
