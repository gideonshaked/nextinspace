# Nextinspace
![Test](https://github.com/The-Kid-Gid/nextinspace/workflows/Test/badge.svg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/nextinspace.svg)](https://badge.fury.io/py/nextinspace)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> "Never miss a launch."

Nextinspace is a command-line tool for seeing the latest in space! Nextinspace will print upcoming space-related events to your terminal. You can sort by type, toggle the verbosity level, and specify the next N events, all from the CLI. More features to come!


## Installation
```
pip install nextinspace
```

If you want to install it manually, use:
```
git clone https://github.com/The-Kid-Gid/nextinspace
cd nextinspace
pip install .
```

If you want to contribute to the project, be sure to:
```
pip install -r dev-requirements.txt
```

## Usage
```
usage: nextinspace [-h] [-e | -l] [-v | -q] [--version] [number of items]

Never miss a launch.

positional arguments:
  number of items      The number of items to display.

optional arguments:
  -h, --help           show this help message and exit
  -e, --events-only    Only show events. These are typically not covered by standard launches. These events could be spacecraft landings, engine tests, or spacewalks.
  -l, --launches-only  Only display orbital and suborbital launches. Generally these will be all orbital launches and suborbital launches which aim to reach “space” or the Karman line.
  -v, --verbose        Display additional details about launches.
  -q, --quiet          Only display name, location, date, and type.
  --version            show program's version number and exit
  ```

## Credits

This project would not have been possible without the [Launch Library 2 API](https://thespacedevs.com/llapi). Please consider [sponsoring them on Patreon](https://www.patreon.com/TheSpaceDevs).