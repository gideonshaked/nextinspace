# nextinspace

<p align="center">
<a href="https://github.com/gideonshaked/nextinspace/actions/workflows/test.yml"><img alt="Test" src="https://github.com/gideonshaked/nextinspace/actions/workflows/test.yml/badge.svg"></a>
<a href="https://pypi.org/project/nextinspace"><img alt="PyPI" src="https://img.shields.io/pypi/v/nextinspace?color=lgreen&label=PyPI"></a>
<a href="https://pepy.tech/project/nextinspace"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/nextinspace?period=total&units=none&left_color=grey&right_color=green&left_text=Downloads"></a>
<a href="https://pypi.org/project/nextinspace"><img alt="Python versions" src="https://img.shields.io/pypi/pyversions/nextinspace"></a>
<a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>
</p>

> *"Never miss a launch."*

nextinspace shows upcoming rocket launches and spaceflight events in your terminal.
It lists what's next with live countdowns, digs into any launch down to the booster and crew, runs a full-screen countdown clock, exports to your calendar, and has an interactive browser.
Data comes from [The Space Devs](https://thespacedevs.com)' Launch Library 2.

<p align="center"><img src="https://raw.githubusercontent.com/gideonshaked/nextinspace/master/img/next.svg" width="820"></p>

## Install

```bash
uv tool install nextinspace     # or: pipx install nextinspace
```

nextinspace needs Python 3.11 or newer.

## Use

### What's next

```bash
nextinspace                      # the next 5 launches and events
nextinspace 12                   # the next 12
nextinspace -l                   # launches only
nextinspace -e                   # events only: dockings, spacewalks, landings, flybys
nextinspace -w 48h               # everything in the next two days
nextinspace -s starship          # free-text search over names, rockets, providers and sites
nextinspace -p SpaceX --crewed   # crewed SpaceX launches
nextinspace -v                   # full cards with mission descriptions
```

Each listing is numbered, and `nextinspace show 3` opens the third item of the last listing you printed.

Countdowns follow how well a date is known.
A launch scheduled to the second ticks down to the second.
A launch known only to the month shows "October 2026" and no countdown at all.

### Everything about one launch

```bash
nextinspace show                 # the next launch
nextinspace show 2               # item 2 of the last listing
nextinspace show artemis         # the first launch or event matching "artemis"
```

The detail view covers the mission, orbit and customers, and the rocket's size, thrust, payload capacity and flight record.
It also shows the booster and where it will land, the spacecraft and crew, the pad with a map link, and the webcasts.

<p align="center"><img src="https://raw.githubusercontent.com/gideonshaked/nextinspace/master/img/show.svg" width="700"></p>

### Live countdown

```bash
nextinspace watch                # full-screen clock for the next launch
nextinspace watch "crew-14"      # or for any launch you name
```

The clock moves on to the next launch by itself once the current one has flown.

<p align="center"><img src="https://raw.githubusercontent.com/gideonshaked/nextinspace/master/img/watch.svg" width="700"></p>

### Interactive browser

```bash
nextinspace browse
```

Arrow keys move through the list and Enter loads full details.
The other keys are listed below.

- `/` searches.
- `a`, `l`, `e` and `p` switch between everything, launches, events and past launches.
- `w` opens the webcast and `m` opens the pad on a map.
- `r` refreshes and `q` quits.

<p align="center"><img src="https://raw.githubusercontent.com/gideonshaked/nextinspace/master/img/browse.svg" width="820"></p>

### Past launches

```bash
nextinspace past 10              # the last 10 launches and how they went
nextinspace past -p "Rocket Lab" -w 30d
```

### Calendar and scripting

```bash
nextinspace 50 -l -f ics > launches.ics     # import into any calendar app
nextinspace 5 --json | jq '.[].name'
nextinspace show --json | jq '.rocket'
```

The calendar export skips items known only to the month or coarser, since they would land on an arbitrary day.

## Rate limits and configuration

Launch Library 2 allows 15 requests per hour without an API key.
nextinspace caches every response for ten minutes, and a typical listing costs two requests.
When the limit is reached or the network is down, nextinspace shows the newest cached data and says how old it is.

These environment variables change its behaviour:

- `NEXTINSPACE_API_KEY` is an LL2 API key, which lifts the rate limit. The Space Devs give keys to [Patreon supporters](https://www.patreon.com/TheSpaceDevs).
- `NEXTINSPACE_TZ` is an IANA time zone for display, such as `Europe/London`. The `--tz` option sets the same thing for one command.
- `NEXTINSPACE_API_URL` points at another LL2 server, such as the development server `https://lldev.thespacedevs.com/2.3.0`, which has no rate limit but serves stale data.

Pass `--refresh` to skip the cache for one command.

## Use from Python

```python
from nextinspace import Client, Filters

with Client() as client:
    for item in client.upcoming(5, filters=Filters(search="falcon")):
        print(item.net, item.name)

    launch = client.launch("<LL2 launch id>")
    print(launch.rocket.full_name, [c.name for s in launch.spacecraft for c in s.crew])
```

`Client.upcoming`, `upcoming_launches`, `upcoming_events` and `previous_launches` return `Launch` and `Event` dataclasses, and `nextinspace.to_dict` turns either into JSON-ready data.

## Development

```bash
uv sync
uv run pytest
uv run ruff check && uv run mypy
```

The tests run against recorded Launch Library 2 responses in `tests/data` and never touch the network.

## Credits

All data comes from [Launch Library 2](https://thespacedevs.com/llapi) by The Space Devs.
nextinspace is not affiliated with them.
