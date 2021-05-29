# Nextinspace

<p align="center">
<a href="https://github.com/not-stirred/nextinspace/actions?query=workflow%3ATest"><img alt="Test" src="https://github.com/not-stirred/nextinspace/workflows/Test/badge.svg"></a>
<a href='https://nextinspace.readthedocs.io/en/stable/?badge=stable'><img src='https://readthedocs.org/projects/nextinspace/badge/?version=stable' alt='Documentation Status' /></a>
<a href="https://codecov.io/gh/not-stirred/nextinspace">
<img src="https://codecov.io/gh/not-stirred/nextinspace/branch/master/graph/badge.svg?token=OCYIVWG21F"/></a>
<a href="https://pypi.org/project/nextinspace"><img alt="PyPI" src="https://img.shields.io/pypi/v/nextinspace?color=lgreen&label=PyPI%20Package"></a>
<a href="https://github.com/not-stirred/nextinspace/releases/latest"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/not-stirred/nextinspace?label=Github%20Release"></a>
<a href="https://pepy.tech/project/nextinspace"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/nextinspace?period=total&units=none&left_color=grey&right_color=green&left_text=Downloads"></a>
<a href="https://img.shields.io/pypi/pyversions/nextinspace"><img alt="Pyversions" src="https://img.shields.io/pypi/pyversions/nextinspace"></a>
<a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>
</p>

> *“Never miss a launch.”*

## Overview

A command-line tool for seeing the latest in space. Nextinspace also supports use as a Python library, so you can integrate it into your application. You can also get data printed to the terminal in JSON, which can be piped into another program.

<p align="center">
<a href="#features">Features</a> • <a href="#installation-and-documentation">Installation and Documentation</a> • <a href="#using-the-nextinspace-public-api">Using the Nextinspace Public API</a> • <a href="#using-nextinspace-in-shell-scripting">Using Nextinspace in Shell Scripting</a> • <a href="#cli-reference">CLI Reference</a> • <a href="#credits">Credits</a>
</p>

## Features

- **Get the next *n* items:** Nextinspace by default prints the closest upcoming item, but you can request as many items as the [LL2 API](https://thespacedevs.com/llapi)
will provide.

- **Filter by type:** Nextinspace allows you to filter upcoming-related by type. You can choose to only see `launches`, only see `events`, or both.

- **Toggle the verbosity:** Nextinspace offers quiet, normal, and verbose modes. With `--quiet`, you can get a quick overview of upcoming items.
With `--verbose`, you can see all of the important details such as description and launcher.

- **JSON output:** Nextinspace provides a `--json` flag for output in JSON format. This can be parsed with tools like [`jq`](https://github.com/stedolan/jq).

- **Pretty printing:** Nextinspace prints upcoming items in formatted panels and with colored text.

<p align="center">
  <img height=550 src="https://raw.githubusercontent.com/not-stirred/nextinspace/master/img/demo.svg" />
</p>

## Installation and Documentation

Nextinspace can be installed using `pip`:

```bash
pip install nextinspace
```

It can also be installed directly from Github:

```bash
pip install git+https://github.com/not-stirred/nextinspace
```

Or you can use your favorite package manager:

```bash
# Arch Linux
yay -S nextinspace

# Nix
nix-env -iA nixpkgs.nextinspace
```

Documentation can be found at [Read the Docs](https://nextinspace.readthedocs.io).

## Using the Nextinspace Public API

Nextinspace defines a [public API](https://nextinspace.readthedocs.io/en/stable/nextinspace.html) of functions and classes that you can use in your code.

```python
>>> import nextinspace
```

### Example 1: Get the next upcoming space-related thing

```python
>>> next_in_space = nextinspace.nextinspace(1)
>>> next_in_space
(nextinspace.Event('Starship SN9 Pressure Test', 'Boca Chica, Texas', datetime.datetime(2020, 12, 28, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')), 'SpaceX has conducted a pressure test on Starship SN9.', 'Ambient Pressure Test'),)
>>> print(next_in_space[0].date)
2020-12-28 21:00:00-05:00
```

### Example 2: Get the next two upcoming events

```python
>>> next_2_events = nextinspace.next_event(2)
>>> next_2_events
(nextinspace.Event('Starship SN9 Pressure Test', 'Boca Chica, Texas', datetime.datetime(2020, 12, 28, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')), 'SpaceX has conducted a pressure test on Starship SN9.', 'Ambient Pressure Test'), nextinspace.Event('Starship SN9 Cryoproof Test', 'Boca Chica, Texas', datetime.datetime(2020, 12, 29, 18, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')), 'SpaceX will likely conduct a cryoproof test on Starship SN9. This is the first cryo test performed on the vehicle.', 'Cryoproof Test'))
>>> next_2_events[1].name
'Starship SN9 Cryoproof Test'
```

### Example 3: Get the next upcoming launch

```python
>>> next_space_launch = nextinspace.next_launch(1)
>>> next_space_launch
(nextinspace.Launch('Soyuz STA/Fregat | CSO-2', 'Soyuz Launch Complex, Kourou, French Guiana', datetime.datetime(2020, 12, 29, 11, 42, 7, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')), 'The CSO-2 (Composante Spatiale Optique-2) satellite is the second of three new-generation high-resolution optical imaging satellites for the French military, replacing the Helios 2 spy satellite series.', 'Government/Top Secret', None),)
>>> print(next_space_launch[0].launcher)
None
```

### Example 4: Get the next two upcoming launches and their launchers

```python
>>> next_2_launches = nextinspace.next_launch(2, include_launcher=True)
>>> next_2_launches
(nextinspace.Launch('Soyuz STA/Fregat | CSO-2', 'Soyuz Launch Complex, Kourou, French Guiana', datetime.datetime(2020, 12, 29, 11, 42, 7, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')), 'The CSO-2 (Composante Spatiale Optique-2) satellite is the second of three new-generation high-resolution optical imaging satellites for the French military, replacing the Helios 2 spy satellite series.', 'Government/Top Secret', nextinspace.Launcher('Soyuz STA/Fregat', 7020, 2810, None, 312, 3, 46.3, 8, 8, 0, datetime.datetime(2011, 12, 16, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')))), nextinspace.Launch('Falcon 9 Block 5 | Türksat 5A', 'Space Launch Complex 40, Cape Canaveral, FL, USA', datetime.datetime(2021, 1, 4, 20, 27, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=68400), 'EST')), 'Türksat 5A is the first of two Turkish next generation communications satellites, which will be operated by Türksat for commercial and military purposes.', 'Communications', nextinspace.Launcher('Falcon 9 Block 5', 22800, 8300, 7607, 549, 2, 70.0, 47, 47, 0, datetime.datetime(2018, 5, 10, 20, 0, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=72000), 'EDT')))))
>>> next_2_launches[0].launcher.failed_launches
0
```

## Using Nextinspace in Shell Scripting

Nextinspace is capable of outputting structured JSON data that can be parsed by the likes of [`jq`](https://github.com/stedolan/jq). As such, you can do something like this:

```bash
❯ next_3_in_space=$(nextinspace 3 --verbose --json)
❯ echo $next_3_in_space | jq "."
[
  {
    "type": "launch",
    "name": "Soyuz STA/Fregat | CSO-2",
    "location": "Soyuz Launch Complex, Kourou, French Guiana",
    "date": "2020-12-29T16:42:07Z",
    "description": "The CSO-2 (Composante Spatiale Optique-2) satellite is the second of three new-generation high-resolution optical imaging satellites for the French military, replacing the Helios 2 spy satellite series.",
    "subtype": "Government/Top Secret",
    "launcher": {
      "name": "Soyuz STA/Fregat",
      "payload_leo": 7020,
      "payload_gto": 2810,
      "liftoff_thrust": null,
      "liftoff_mass": 312,
      "max_stages": 3,
      "height": 46.3,
      "successful_launches": 8,
      "consecutive_successful_launches": 8,
      "failed_launches": 0,
      "maiden_flight_date": "2011-12-17"
    }
  },
  {
    "type": "event",
    "name": "Starship SN9 Cryoproof Test",
    "location": "Boca Chica, Texas",
    "date": "2020-12-29T23:00:00Z",
    "description": "SpaceX will likely conduct a cryoproof test on Starship SN9. This is the first cryo test performed on the vehicle.",
    "subtype": "Cryoproof Test"
  },
  {
    "type": "event",
    "name": "SLS Green Run Hot Fire",
    "location": "Stennis Space Center, Mississippi",
    "date": "2020-12-31T00:00:00Z",
    "description": "The core stage of the Space Launch System will undergo the final 'Green Run' test, where the core stage will be fired for 8 minutes, demonstrating performance similar to an actual launch.",
    "subtype": "Static Fire"
  }
]
❯ echo $next_3_in_space | jq ".[].name"
"Soyuz STA/Fregat | CSO-2"
"Starship SN9 Cryoproof Test"
"SLS Green Run Hot Fire"
```

The structure of the JSON outputted by nextinspace is basically demonstrated in the example above.
The structure and values of the data reflect the relationships between the `Launch`, `Event`, and `Launcher` classes, with a few notable exceptions:

- **The `type_` attribute:** The `type_` attribute of Nextinspace `Event` and `Launch` objects is stored in the `subtype` key. The `type` key actually holds the class of the Nextinspace object represented in the JSON object (either `launch` or `event`).
- **The `date` key:** Internally, Nextinspace stores dates and times in local time, but for JSON output Nextinspace converts date and time values to UTC. Also, Nextinspace outputs date and time values in [ISO 8601 format](https://www.iso.org/iso-8601-date-and-time-format.html).

## CLI Reference

```
❯ nextinspace --help
usage: nextinspace [-h] [-e | -l] [-v | -q] [--json] [--version] [number of items]

Never miss a launch.

positional arguments:
  number of items      The number of items to display.

optional arguments:
  -h, --help           show this help message and exit
  -e, --events-only    Only show events. These are typically not covered by standard launches. These events could be spacecraft landings, engine tests, or spacewalks.
  -l, --launches-only  Only display orbital and suborbital launches. Generally these will be all orbital launches and suborbital launches which aim to reach “space” or the Karman line.
  -v, --verbose        Display additional details about launches.
  -q, --quiet          Only display name, location, date, and type.
  --json               Output data in JSON format. Note that '--quiet' has no effect when this flag is set.
  --version            show program's version number and exit
```

## Credits

This project would not have been possible without the [Launch Library 2 API](https://thespacedevs.com/llapi). Please consider [sponsoring them on Patreon](https://www.patreon.com/TheSpaceDevs).
