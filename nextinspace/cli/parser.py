"""Parse arguments from the CLI"""

import argparse


def get_args():
    parser = argparse.ArgumentParser(prog="nextinspace", description="Never miss a launch.")

    # Number of events wanted by user
    parser.add_argument(
        "num_items",
        default=1,
        metavar="number of items",
        nargs="?",
        type=positive_int,
        help="The number of items to display.",
    )

    # Group of events only and launches only flags.
    # Obviously, only one can be passed.
    filtering_options = parser.add_mutually_exclusive_group()
    filtering_options.add_argument(
        "-e",
        "--events-only",
        action="store_true",
        help="Only show events. These are typically not covered by standard launches. These events could be spacecraft landings, engine tests, or spacewalks.",
    )
    filtering_options.add_argument(
        "-l",
        "--launches-only",
        action="store_true",
        help="Only display orbital and suborbital launches. Generally these will be all orbital launches and suborbital launches which aim to reach “space” or the Karman line.",
    )

    # Verbosity arguments group
    verbosity_options = parser.add_mutually_exclusive_group()
    verbosity_options.add_argument(
        "-v", "--verbose", action="store_true", help="Display additional details about launches."
    )
    verbosity_options.add_argument(
        "-q", "--quiet", action="store_true", help="Only display name, location, date, and type."
    )

    # JSON output
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output data in JSON format. Note that '--quiet' has no effect when this flag is set.",
    )

    # Version argument
    parser.add_argument("--version", action="version", version="%(prog)s v" + __import__("nextinspace").__version__)

    return parser.parse_args()


def positive_int(x):
    i = int(x)
    if i <= 0:
        raise ValueError()
    return i
