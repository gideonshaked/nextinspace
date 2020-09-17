"""The functions used to retrieve data from the LL2 API."""

from nextinspace import space
import requests
from datetime import datetime
from tzlocal import get_localzone


def getLaunchEvents(num_events=1):
    pass


def getOtherEvents(num_events=10):
    response = requests.get("https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit=" + str(num_events))
    data = response.json()

    events = []

    for i in range(num_events):
        mission_name = data["results"][i]["name"]
        location = data["results"][i]["location"]

        date_string = data["results"][i]["date"]
        mission_date_unaware = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        tz = get_localzone()
        mission_date = tz.localize(mission_date_unaware)
        print(mission_date_unaware)
        print(mission_date)


getOtherEvents()