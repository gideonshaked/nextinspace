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
`tzdata` is a Windows-only dependency because Windows ships no IANA time-zone database, so `zoneinfo` and `--tz` fail there without it.

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
`--within` is applied client-side rather than through `net__lte`, `net__gte` or `date__lte`, because a bound that moves with the clock gives every call a new cache key and leaves nothing to fall back on when rate-limited.
Listings arrive sorted by date, so filtering the first `limit` results locally matches what the server would return.
`show` with no target asks for five launches, not one, so it shares a cache entry with `next` and `watch`.
`watch` reloads every minute but costs two requests per cache window, the list and the detail by id.
A named `watch` target is resolved once, because a search costs an extra two requests and a listing number would follow whatever listing another terminal prints next.
The TUI fetches detail only on Enter for the same reason.

### Webcasts

LL2's `priority` on a webcast only orders streams and usually puts a fan re-stream first.
`models.py` sorts by the webcast type id instead (1 official, 2 official re-stream, 3 unofficial, 4 unofficial re-stream), so `webcasts[0]` is the provider's own stream when there is one.

### Output on Windows

Windows writes redirected stdout in its ANSI code page with strict errors, and translates LF to CRLF.
`main()` reconfigures stdout and stderr to UTF-8 for Rich output, and JSON and iCalendar go out as UTF-8 bytes through `emit()` so the CRLF line endings iCalendar requires are not doubled.

### Textual workers

Cancelling a thread worker only flags it, and the thread still finishes and calls back.
`Browser.load` stamps each request with a generation number and `show_items` drops results from older generations.
`detail_loaded` shows a fetched detail only if its row is still the current one.
A refresh goes through `Client.fresh()`, a shallow copy with `refresh` set, so overlapping workers never share a mutable refresh flag.

### CLI shape

`DefaultToNext` in `cli.py` routes anything that is not a subcommand to `next`, so `nextinspace 5 -l` works like the 3.x interface.
It leaves arguments alone when `ctx.resilient_parsing` is set, which is how shell completion parses, or completion would never offer subcommand names.
`--version` uses an eager option callback because Click checks for a missing subcommand before the group callback runs.
Typer 0.27 vendors Click as `typer._click` and no longer installs `click`, so `cli.py` does not import it.
`show <n>` indexes the last listing printed by `next` or `past`, which is saved to `last_listing.json` in the cache directory.

### Tests

Fixtures in `tests/data` were recorded from `lldev.thespacedevs.com`, the unthrottled development server, so tests never spend the production quota.
The dev server's data is stale, which is why some "previous" launches in the fixtures still have status Go.
Tests pin "now" and pass explicit time zones.

### README images

`img/*.svg` are Rich `save_svg` exports of the renderers fed with the fixtures, not recordings of live output.
