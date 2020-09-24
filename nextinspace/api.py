"""The functions used to retrieve data from the LL2 API."""

from nextinspace import space
import requests
from datetime import datetime
from tzlocal import get_localzone


def getLaunchEvents(num_events=1):
    """Returns list of SpaceEvents from API

    Args:
        num_events (int, optional): Number of launch events to be returned. Defaults to 1.
    """

    now = datetime.now()
    response = requests.get(
        "https://ll.thespacedevs.com/2.0.0/launch/?limit=" + str(num_events) + "&net__gte=" + now.strftime("%Y-%m-%d")
    )
    data = response.json()

    events = []
    for i in range(num_events):
        current = data["results"][i]

        mission_name = current["mission"]["name"]
        location = current["pad"]["name"] + ", " + current["pad"]["location"]["name"]

        date_string = current["net"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        mission_description = current["mission"]["description"]
        mission_type = current["mission"]["type"]

        rocket_url = current["rocket"]["configuration"]["url"]
        rocket = getRocket(rocket_url)

        events.append(
            space.LaunchEvent(mission_name, location, mission_date, mission_description, mission_type, rocket)
        )

    return events


def getRocket(url):
    """Returns Rocket object from API

    Args:
        url (string): The LL2 API URL of the rocket
    """

    response = requests.get(url)
    data = response.json()

    name = data["name"]
    payload_leo = data["leo_capacity"]
    payload_gto = data["gto_capacity"]
    liftoff_thrust = data["to_thrust"]
    liftoff_mass = data["launch_mass"]
    max_stages = data["max_stage"]
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
        successful_launches,
        consecutive_successful_launches,
        failed_launches,
        maiden_flight_date,
    )


def getOtherEvents(num_events=1):
    """Returns list of OtherEvents from API

    Args:
        num_events (int, optional): Number of events to be returned. Defaults to 1.
    """

    response = requests.get("https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit=" + str(num_events))
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

        events.append(space.OtherEvent(mission_name, location, mission_date, mission_description, mission_type))

    return events
