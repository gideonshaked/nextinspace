# nextinspace

## Layout

The package lives in `src/nextinspace/`.
`models.py` parses LL2 payloads into frozen dataclasses and is the only module allowed to tolerate missing or null fields.
`client.py` talks to the API, `cache.py` stores responses on disk, and `timefmt.py` formats dates at their known precision.
`render.py` builds Rich renderables, `cli.py` holds the Typer commands, `ics.py` writes iCalendar and `tui.py` is the Textual browser.

## Decisions and why

### 4.0 rewrite

Version 4.0.0 replaced the 3.x code wholesale.
3.x used LL2 2.1.0, made one extra request per launch to fetch its launcher, and printed through a hand-written colorama viewer whose own docstring asked for Rich.
The 3.x library functions `nextinspace()`, `next_launch()` and `next_event()` were dropped without shims, and `Client` replaced them.
Sphinx docs and Read the Docs were dropped because the README covers a CLI of this size.
Poetry and bump2version gave way to uv and hatchling, and black and isort to ruff.
Python 3.10 support was dropped because it reached end of life in October 2026.

### Launch Library 2 behaviour

- Anonymous access allows 15 requests per hour. Every design choice that touches the network follows from this.
- Cloudflare in front of LL2 answers 403 to the default Python `urllib` User-Agent, so the client always sends its own.
- `/launches/upcoming/` and `/events/upcoming/` include items that flew in the last day unless `hide_recent_previous=true` is sent. 3.x showed flown launches as upcoming because of this.
- `mode=normal` list responses carry pad, mission, provider and rocket name but no webcasts, boosters, crew or rocket statistics. `mode=detailed` has them, so `show`, `watch` and the TUI's Enter fetch the detailed record of one item.
- Filters that work were confirmed against the dev server: `search`, `lsp__name` (exact match), `is_crewed`, `net__lte`, `net__gte`, `date__lte`, `hide_recent_previous`. Lookups such as `lsp__name__icontains` and `lsp__abbrev` are silently ignored and return everything, so they are not used.
- API keys go in `Authorization: Token <key>`.
- `net_precision` ranges from SEC to DEC. A month-precision launch is stored as midnight UTC on some day of the month, so only SEC, MIN and HR get clock times and countdowns, and coarser dates are formatted in UTC to stop a time-zone shift moving them into the previous month.

### Caching

Responses are cached for ten minutes in the platformdirs cache directory, keyed on URL and query.
On a 429, a network error or a 5xx, the client serves the newest cached copy of any age and records a note, which the CLI prints to stderr.
Time bounds such as `net__lte` are floored to ten minutes so repeated commands produce the same query and hit the cache.
`watch` re-resolves every minute but costs two requests per cache window, one for the list and one for the detail.
The TUI fetches detail only on Enter for the same reason.

### CLI shape

`DefaultToNext` in `cli.py` routes anything that is not a subcommand to `next`, so `nextinspace 5 -l` works like the 3.x interface.
`--version` uses an eager option callback because Click checks for a missing subcommand before the group callback runs.
Typer 0.27 vendors Click as `typer._click` and no longer installs `click`, so `cli.py` does not import it.
`show <n>` indexes the last listing printed by `next` or `past`, which is saved to `last_listing.json` in the cache directory.

### Tests

Fixtures in `tests/data` were recorded from `lldev.thespacedevs.com`, the unthrottled development server, so tests never spend the production quota.
The dev server's data is stale, which is why some "previous" launches in the fixtures still have status Go.
Tests pin "now" and pass explicit time zones.

### README images

`img/*.svg` are Rich `save_svg` exports of the renderers fed with the fixtures, not recordings of live output.
