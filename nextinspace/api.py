"""Retrieve data from the LL2 API"""

from datetime import date, datetime

import requests
from tzlocal import get_localzone

from nextinspace import space


def get_launches(num_launches, verbosity):
    """
    Return list of Launches from API. The verbosity is passed
    in to avoid unecessary API calls when rocket is not being displayed.

    Args:
        num_launches (int): Number of Launches to be returned.
    """

    today = date.today()
    response = requests.get(
        f"https://ll.thespacedevs.com/2.0.0/launch/?limit={num_launches}&net__gte={today.strftime('%Y-%m-%d')}"
    )
    data = response.json()

    launches = []
    for result in data["results"]:
        mission_name = result["name"]

        pad = parse_value(result, "pad", "name")
        pad_loc = parse_value(result, "pad", "location", "name")
        # Make sure location is a valid string with valid formatting
        if pad is not None:
            location = pad
            if pad_loc is not None:
                location += ", " + pad_loc
        elif pad_loc is not None:
            location = pad_loc
        else:
            location = None

        mission_date = get_date(result["net"], "%Y-%m-%dT%H:%M:%SZ")
        mission_description = parse_value(result, "mission", "description")
        mission_type = parse_value(result, "mission", "type")
        rocket_url = parse_value(result, "rocket", "configuration", "url")
        rocket = get_rocket(rocket_url) if verbosity == space.Verbosity.VERBOSE else None

        launches.append(space.Launch(mission_name, location, mission_date, mission_description, mission_type, rocket))

    return launches


def get_rocket(url):
    """Return Rocket from API

    Args:
        url (string): The LL2 API URL of the rocket
    """
    response = requests.get(url)
    data = response.json()

    name = data["full_name"]
    payload_leo = data["leo_capacity"]
    payload_gto = data["gto_capacity"]
    liftoff_thrust = data["to_thrust"]
    liftoff_mass = data["launch_mass"]
    max_stages = data["max_stage"]
    height = data["length"]
    successful_launches = data["successful_launches"]
    consecutive_successful_launches = data["consecutive_successful_launches"]
    failed_launches = data["failed_launches"]
    maiden_flight_date = get_date(data["maiden_flight"], "%Y-%m-%d")

    return space.Rocket(
        name,
        payload_leo,
        payload_gto,
        liftoff_thrust,
        liftoff_mass,
        max_stages,
        height,
        successful_launches,
        consecutive_successful_launches,
        failed_launches,
        maiden_flight_date,
    )


def get_events(num_events):
    """Return list of Events from API

    Args:
        num_events (int): Number of Events to be returned.
    """

    response = requests.get(f"https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit={num_events}")
    data = response.json()

    events = []
    for result in data["results"]:
        mission_name = result["name"]
        location = result["location"]
        mission_date = get_date(result["date"], "%Y-%m-%dT%H:%M:%SZ")
        mission_description = result["description"]
        mission_type = parse_value(result, "type", "name")

        events.append(space.Event(mission_name, location, mission_date, mission_description, mission_type))

    return events


def get_all(num_items, verbosity):
    """
    Return list of items from API

    Unfortunately, because the LL2 API does not offer any way of getting N
    upcoming spaceflight items, the below process is necessary. This function
    is horribly inefficient because it must do two API requests instead of one when
    it will only use half of the information it receives. 🙁

    Args:
        num_items (int): Number of items to be returned.
    """

    # Get events and launches from API
    events = get_events(num_items)
    launches = get_launches(num_items, verbosity)

    # Set values needed for sorting
    l_events = len(events)
    l_launches = len(launches)
    max_length = l_events + l_launches
    l_all_items = min(num_items, max_length)

    all_items = [None] * l_all_items
    i = 0
    j = 0
    k = 0

    # Traverse both lists
    while i < l_events and j < l_launches:

        # Check if current element of first array is smaller than current element of second array.
        # If yes, store first array element and increment first array index. Otherwise do same with second array

        # Note that these are compared by date
        if events[i].mission_date < launches[j].mission_date:
            all_items[k] = events[i]
            k += 1
            if k >= num_items:
                return all_items
            i += 1
        else:
            all_items[k] = launches[j]
            k += 1
            if k >= num_items:
                return all_items
            j += 1

    # Store remaining elements
    # of first array
    while i < l_events:
        all_items[k] = events[i]
        k += 1
        if k >= num_items:
            return all_items
        i += 1

    # Store remaining elements
    # of second array
    while j < l_launches:
        all_items[k] = launches[j]
        k += 1
        if k >= num_items:
            return all_items
        j += 1

    return all_items


def parse_value(dict, *keys):
    """
    Try to return the value present in the nested dict at
    the specified keys. If a TypeError is raised
    (because at some point in the path we find None),
    then return None.

    This is necessary because there is no API documentation
    I could find that specified when and how values could be
    left nonexistant. If there was a better way of doing this
    then I would do that.

    Note that this method is only required when accessing a
    nested dict (ex: dict[x][y]).

    Args:
        dict (dict)

    Returns:
        The value at path
    """

    try:
        for key in keys:
            dict = dict[key]
        return dict
    except TypeError:
        return None


def get_date(date_str, fmat_str):
    if date_str is None:
        return None
    return get_localzone().localize(datetime.strptime(date_str, fmat_str))
