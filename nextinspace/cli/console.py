"""Central logic and driver code for CLI"""

import sys

import requests

import nextinspace
from nextinspace.cli import parser, viewer


def run():
    args = parser.get_args()

    if args.verbose:
        verbosity = viewer.Verbosity.verbose
    elif args.quiet:
        verbosity = viewer.Verbosity.quiet
    else:
        verbosity = viewer.Verbosity.normal

    include_launcher = verbosity == viewer.Verbosity.verbose

    try:
        if args.events_only:
            items = nextinspace.next_event(args.num_items)
        elif args.launches_only:
            items = nextinspace.next_launch(args.num_items, include_launcher)
        else:
            items = nextinspace.nextinspace(args.num_items, include_launcher)
    except requests.exceptions.RequestException as err:
        sys.exit(f"nextinspace: {err}")

    if args.json:
        viewer.show_json(items)
    else:
        viewer.display(items, verbosity)
