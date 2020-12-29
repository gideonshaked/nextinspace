"""Viewer for terminal output

This code is (excluding the json output) isinherited from v1 and needs to be
refactored. Properly methodizing this code would be putting lipstick on a pig,
so to refactor properly would be to use a library like Rich. Eventually...
"""

import json
import textwrap as t
from datetime import MINYEAR, datetime, timezone
from enum import Enum

from colorama import Fore, Style, deinit, init

import nextinspace

MAX_LINE_LENGTH = 88
CHART_WIDTH = 59
DATE_FMAT_STR = "%a %B %d, %Y %I:%M %p %Z"


class Verbosity(Enum):
    quiet = 1
    normal = 2
    verbose = 3


# ---- Top-level display functions ----


def display(items, verbosity):
    if len(items) == 0:
        return

    show_top()

    init()  # For compatibility with Windows terminals
    display_item(items[0], verbosity)
    for item in items[1:]:
        show_divider()
        display_item(item, verbosity)
    deinit()  # For compatibility with Windows terminals

    show_bottom()


def display_item(item, verbosity):
    if type(item) is nextinspace.Event:
        display_event(item, verbosity)
    else:
        display_launch(item, verbosity)


def show_top():
    print("┌" + "─" * MAX_LINE_LENGTH + "┐")


def show_divider():
    print("├" + "─" * MAX_LINE_LENGTH + "┤")


def show_bottom():
    print("└" + "─" * MAX_LINE_LENGTH + "┘")


# ---- Launch and Event display functions ----


def display_event(event, verbosity):
    show_name(event.name)
    show_location(event.location)
    show_filler()
    show_date(event.date)
    show_type(nextinspace.Event, event.type_)

    # If verbosity is not set to quiet, show description
    if verbosity != Verbosity.quiet:
        show_filler()
        show_description(event.description)


def display_launch(launch, verbosity):
    show_name(launch.name)
    show_location(launch.location)
    show_filler()
    show_date(launch.date)
    show_type(nextinspace.Launch, launch.type_)

    # If verbosity is not set to quiet, print mission description
    if verbosity != Verbosity.quiet:
        # If verbosity is set to verbose, print rocket information
        if verbosity == Verbosity.verbose:
            show_filler()
            display_launcher(launch.launcher)

        show_filler()
        show_description(launch.description)


# ---- Launch and Event display helper functions ----


def show_name(name):
    if name is not None:
        mission_name_lines = t.wrap(name, width=MAX_LINE_LENGTH)
        for line in mission_name_lines:
            print("│" + Style.BRIGHT + Fore.CYAN + line.ljust(MAX_LINE_LENGTH, " ") + Style.RESET_ALL + "│")
    else:
        print("│" + Style.BRIGHT + Fore.CYAN + "Name Unavailable".ljust(MAX_LINE_LENGTH, " ") + Style.RESET_ALL + "│")


def show_location(location):
    if location is not None:
        location_lines = t.wrap(location, width=MAX_LINE_LENGTH)
        for line in location_lines:
            print("│" + Fore.CYAN + line.ljust(MAX_LINE_LENGTH, " ") + Fore.RESET + "│")
    else:
        print("│" + Fore.CYAN + "Location Unavailable".ljust(MAX_LINE_LENGTH, " ") + Fore.RESET + "│")


def show_date(date):
    if date != datetime(MINYEAR, 1, 1):
        print("│" + Fore.GREEN + ("    " + date.strftime(DATE_FMAT_STR)).ljust(MAX_LINE_LENGTH, " ") + Fore.RESET + "│")
    else:
        print("│" + Fore.GREEN + "    Date Unavailable".ljust(MAX_LINE_LENGTH, " ") + Fore.RESET + "│")


def show_type(obj, type_):
    if type_ is not None:
        print("│" + ("    " + type(obj).__name__ + " Type: " + type_).ljust(MAX_LINE_LENGTH, " ") + "│")
    else:
        print("│" + "    Launch Type Unavailable".ljust(MAX_LINE_LENGTH, " ") + "│")


def show_description(description):
    if description is not None:
        mission_description_lines = t.wrap(
            description, width=MAX_LINE_LENGTH, initial_indent="    ", subsequent_indent="    "
        )
        for line in mission_description_lines:
            print("│" + line.ljust(MAX_LINE_LENGTH, " ") + "│")
    else:
        print("│" + ("    Mission Description Unavailable").ljust(MAX_LINE_LENGTH, " ") + "│")


def show_filler():
    print("│" + " " * MAX_LINE_LENGTH + "│")


# ---- Launcher display functions ----


def display_launcher(launcher):
    print("│" + ("┌" + "─" * CHART_WIDTH + "┐").center(MAX_LINE_LENGTH, " ") + "│")
    if launcher.name is not None:
        print("│" + ("│" + launcher.name.center(CHART_WIDTH) + "│").center(MAX_LINE_LENGTH, " ") + "│")
    else:
        print("│" + ("│" + "Name Unavailable".center(CHART_WIDTH) + "│").center(MAX_LINE_LENGTH, " ") + "│")

    show_chart_divider()
    show_chart_line(
        get_side("Height: ", launcher.height, " m"),
        get_side("Mass to LEO: ", launcher.payload_leo, " kg"),
    )
    show_chart_divider()

    show_chart_line(
        get_side("Max Stages: ", launcher.max_stages),
        get_side("Liftoff Thrust: ", launcher.liftoff_thrust, " kN"),
    )
    show_chart_divider()

    show_chart_line(
        get_side("Mass to GTO: ", launcher.payload_gto, " kg"),
        get_side("Liftoff Mass: ", launcher.liftoff_mass, " Tonnes"),
    )
    show_chart_divider()

    if launcher.maiden_flight_date != datetime(MINYEAR, 1, 1):
        date_str = launcher.maiden_flight_date.strftime("%Y-%m-%d")
    else:
        date_str = "Unavailable"
    show_chart_line(
        get_side("Launch Successes: ", launcher.successful_launches),
        "Maiden Flight: " + date_str,
    )
    show_chart_divider()

    show_chart_line(
        get_side("Consecutive Successes: ", launcher.consecutive_successful_launches),
        get_side("Failed Launches: ", launcher.failed_launches),
    )

    print("│" + ("└" + "─" * CHART_WIDTH + "┘").center(MAX_LINE_LENGTH, " ") + "│")


def show_chart_line(left, right):
    row = left.center(CHART_WIDTH // 2, " ") + "│" + right.center(CHART_WIDTH // 2, " ")
    print("│" + ("│" + row.center(CHART_WIDTH, " ") + "│").center(MAX_LINE_LENGTH, " ") + "│")


def get_side(pre, value, post=""):
    """Get one side of the chart if the value is not None"""

    if value is not None:
        return pre + str(value) + post
    return pre + "Unavailable"


def show_chart_divider():
    print("│" + ("├" + "─" * CHART_WIDTH + "┤").center(MAX_LINE_LENGTH, " ") + "│")


# ---- JSON output ----


def show_json(items_list):
    output_list = [dict_item(item) for item in items_list]
    print(json.dumps(output_list, indent=4))


def dict_item(item):
    if type(item) is nextinspace.Event:
        return dict_event(item)
    return dict_launch(item)


def dict_launch(launch):
    return {
        "type": "launch",
        "name": launch.name,
        "location": launch.location,
        "date": launch.date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": launch.description,
        "subtype": launch.type_,
        "launcher": dict_launcher(launch.launcher),
    }


def dict_launcher(launcher):
    if launcher is not None:
        return {
            "name": launcher.name,
            "payload_leo": launcher.payload_leo,
            "payload_gto": launcher.payload_gto,
            "liftoff_thrust": launcher.liftoff_thrust,
            "liftoff_mass": launcher.liftoff_mass,
            "max_stages": launcher.max_stages,
            "height": launcher.height,
            "successful_launches": launcher.successful_launches,
            "consecutive_successful_launches": launcher.consecutive_successful_launches,
            "failed_launches": launcher.failed_launches,
            "maiden_flight_date": launcher.maiden_flight_date.astimezone(timezone.utc).strftime("%Y-%m-%d"),
        }
    return None


def dict_event(event):
    return {
        "type": "event",
        "name": event.name,
        "location": event.location,
        "date": event.date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": event.description,
        "subtype": event.type_,
    }
