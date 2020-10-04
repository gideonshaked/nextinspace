"""Retrieve data from the LL2 API"""

import requests
from datetime import datetime, date
from tzlocal import get_localzone
from nextinspace import space


def get_launches(num_launches):
    """Return list of Launches from API

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
        location = result["pad"]["name"] + ", " + result["pad"]["location"]["name"]

        date_string = result["net"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        # Sometimes the API does not have any values for the mission
        try:
            mission_description = result["mission"]["description"]
            mission_type = result["mission"]["type"]
        except:
            mission_description = None
            mission_type = None

        rocket_url = result["rocket"]["configuration"]["url"]
        rocket = get_rocket(rocket_url)

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

    maiden_flight_date_string = data["maiden_flight"]
    maiden_flight_date_unaware = datetime.strptime(maiden_flight_date_string, "%Y-%m-%d")
    maiden_flight_date = get_localzone().localize(maiden_flight_date_unaware)

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

        date_string = result["date"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        mission_description = result["description"]
        mission_type = result["type"]["name"]

        events.append(space.Event(mission_name, location, mission_date, mission_description, mission_type))

    return events


def get_all(num_items):
    """Return list of items from API

       Unfortunately, because the LL2 API does not offer any way of getting N
       upcoming spaceflight items, the below process is necessary. This function
       is horribly inefficient because it must do two API requests instead of one when
       it will only use half of the information it receives. 🙁

    Args:
        num_items (int): Number of items to be returned.
    """

    # Get events and launches from API
    events = get_events(num_items)
    launches = get_launches(num_items)

    # Set values needed for sorting
    l_events = len(events)
    l_launches = len(launches)

    max_length = l_events + l_launches
    if num_items < max_length:
        l_all_items = num_items
    else:
        l_all_items = max_length

    all_items = [None] * max_length
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
            k = k + 1
            if k >= num_items:
                return all_items
            i = i + 1
        else:
            all_items[k] = launches[j]
            k = k + 1
            if k >= num_items:
                return all_items
            j = j + 1

    # Store remaining elements
    # of first array
    while i < l_events:
        all_items[k] = events[i]
        k = k + 1
        if k >= num_items:
            return all_items
        i = i + 1

    # Store remaining elements
    # of second array
    while j < l_launches:
        all_items[k] = launches[j]
        k = k + 1
        if k >= num_items:
            return all_items
        j = j + 1

    return all_items