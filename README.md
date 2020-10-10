# Nextinspace
<p align="center">
<a href="https://github.com/The-Kid-Gid/nextinspace/workflows/Test/badge.svg"><img alt="Test" src="https://github.com/The-Kid-Gid/nextinspace/workflows/Test/badge.svg"></a>
<a href="https://www.gnu.org/licenses/gpl-3.0"><img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>
<a href="https://badge.fury.io/py/nextinspace"><img alt="PyPi Version" src="https://badge.fury.io/py/nextinspace.svg"></a>
<a href="https://img.shields.io/pypi/pyversions/nextinspace"><img alt="Pyversions" src="https://badge.fury.io/py/nextinspace.svg"></a>
<a href="https://pycqa.github.io/isort/"><img alt="Imports: isort" src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336"></a>
<a href="https://github.com/pre-commit/pre-commit"><img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

> ”Never miss a launch.”

Nextinspace is a command-line tool for seeing the latest in space! Nextinspace will print upcoming space-related events to your terminal. You can filter by type, toggle the verbosity level, and view the next *n* events, all from the CLI.


<p align="center">
  <img src="https://raw.githubusercontent.com/The-Kid-Gid/nextinspace/master/img/demo.svg" />
</p>


---

## Installation

```bash
pip install nextinspace
```

If you want to install it manually, use:

```bash
git clone https://github.com/The-Kid-Gid/nextinspace
cd nextinspace
pip install .
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
