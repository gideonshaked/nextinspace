"""The functions used to retrieve data from the LL2 API"""

import requests
from datetime import datetime
from tzlocal import get_localzone
from nextinspace import space


def get_launches(num_launches=1):
    """Return list of Launches from API

    Args:
        num_launches (int, optional): Number of Launches to be returned. Defaults to 1.
    """

    now = datetime.now()
    response = requests.get(
        f"https://ll.thespacedevs.com/2.0.0/launch/?limit={num_launches}&net__gte={now.strftime('%Y-%m-%d')}"
    )
    data = response.json()

    launches = []
    for i in range(num_launches):
        current = data["results"][i]

        mission_name = current["mission"]["name"]
        location = current["pad"]["name"] + ", " + current["pad"]["location"]["name"]

        date_string = current["net"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        mission_description = current["mission"]["description"]
        mission_type = current["mission"]["type"]

        rocket_url = current["rocket"]["configuration"]["url"]
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


def get_events(num_events=1):
    """Return list of Events from API

    Args:
        num_events (int, optional): Number of Events to be returned. Defaults to 1.
    """

    response = requests.get(f"https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit={num_events}")
    data = response.json()

    events = []
    for i in range(num_events):
        current = data["results"][i]

        mission_name = current["name"]
        location = current["location"]

        date_string = current["date"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        mission_description = current["description"]
        mission_type = current["type"]["name"]

        events.append(space.Event(mission_name, location, mission_date, mission_description, mission_type))

    return events
