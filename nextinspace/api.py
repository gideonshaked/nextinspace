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
        pass


def getOtherEvents(num_events=1):
    """Returns list of OtherEvents from API

    Args:
        num_events (int, optional): Number of events to be returned. Defaults to 1.
    """

    response = requests.get("https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit=" + str(num_events))
    data = response.json()

    events = []
    for i in range(num_events):
        mission_name = data["results"][i]["name"]
        location = data["results"][i]["location"]

        date_string = data["results"][i]["date"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        mission_date = get_localzone().localize(mission_date_unaware)

        mission_description = data["results"][i]["description"]
        mission_type = data["results"][i]["type"]["name"]

        events.append(space.OtherEvent(mission_name, location, mission_date, mission_description, mission_type))

    return events
