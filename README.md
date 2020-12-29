# Nextinspace
<p align="center">
<a href="https://github.com/The-Kid-Gid/nextinspace/actions?query=workflow%3ATest"><img alt="Test" src="https://github.com/The-Kid-Gid/nextinspace/workflows/Test/badge.svg"></a>
<a href='https://nextinspace.readthedocs.io/en/feat-v2/?badge=feat-v2'><img src='https://readthedocs.org/projects/nextinspace/badge/?version=feat-v2'alt='Documentation Status' /></a>
<a href="https://codecov.io/gh/The-Kid-Gid/nextinspace">
<img src="https://codecov.io/gh/The-Kid-Gid/nextinspace/branch/master/graph/badge.svg?token=OCYIVWG21F"/></a>
<img alt="PyPI" src="https://img.shields.io/pypi/v/nextinspace?color=lgreen&label=PyPI%20Package">
<img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/The-Kid-Gid/nextinspace?label=Github%20Release">
<a href="https://pepy.tech/project/nextinspace"><img alt="Downloads" src="https://static.pepy.tech/personalized-badge/nextinspace?period=total&units=none&left_color=grey&right_color=green&left_text=Downloads"></a>
<a href="https://img.shields.io/pypi/pyversions/nextinspace"><img alt="Pyversions" src="https://img.shields.io/pypi/pyversions/nextinspace"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>
</p>

> “Never miss a launch.”

Nextinspace is a command-line tool for seeing the latest in space! Nextinspace will print upcoming space-related events to your terminal. You can filter by type, toggle the verbosity level, and view the next *n* upcoming events, all from the CLI.

<p align="center">
  <img src="https://raw.githubusercontent.com/The-Kid-Gid/nextinspace/master/img/demo.svg" />
</p>

---

## Installation

To install nextinspace, simply run:
```bash
pip install nextinspace

# directly from Github
pip install git+https://github.com/The-Kid-Gid/nextinspace
```

Or use your favourite package manager:
```bash
# Arch Linux
yay -S nextinspace

# Nix
nix-env -iA nixpkgs.nextinspace
```

## Usage

```
usage: nextinspace [-h] [-e | -l] [-v | -q] [--version] [number of items]

Never miss a launch.

positional arguments:
  number of items      The number of items to display.

optional arguments:
  -h, --help           show this help message and exit
  -e, --events-only    Only show events. These are typically not covered by
                       standard launches. These events could be spacecraft
                       landings, engine tests, or spacewalks.
  -l, --launches-only  Only display orbital and suborbital launches. Generally
                       these will be all orbital launches and suborbital
                       launches which aim to reach “space” or the Karman line.
  -v, --verbose        Display additional details about launches.
  -q, --quiet          Only display name, location, date, and type.
  --version            show program's version number and exit
```

## Credits

This project would not have been possible without the [Launch Library 2 API](https://thespacedevs.com/llapi). Please consider [sponsoring them on Patreon](https://www.patreon.com/TheSpaceDevs).
