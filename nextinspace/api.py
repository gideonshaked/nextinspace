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

    # Since we know the size of the list, creating it beforehand is faster
    launches = [None] * num_launches
    for i in range(num_launches):
        current = data["results"][i]

        mission_name = current["name"]
        location = current["pad"]["name"] + ", " + current["pad"]["location"]["name"]

        date_string = current["net"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        # Sometimes the API does not have any values for the mission
        try:
            mission_description = current["mission"]["description"]
            mission_type = current["mission"]["type"]
        except:
            mission_description = None
            mission_type = None

        rocket_url = current["rocket"]["configuration"]["url"]
        rocket = get_rocket(rocket_url)

        launches[i] = space.Launch(mission_name, location, mission_date, mission_description, mission_type, rocket)

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

    # Since we know the size of the list, creating it beforehand is faster
    events = [None] * num_events
    for i in range(num_events):
        current = data["results"][i]

        mission_name = current["name"]
        location = current["location"]

        date_string = current["date"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        mission_description = current["description"]
        mission_type = current["type"]["name"]

        events[i] = space.Event(mission_name, location, mission_date, mission_description, mission_type)

    return events