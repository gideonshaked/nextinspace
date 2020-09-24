from nextinspace import api
import pytest
from datetime import datetime
from tzlocal import get_localzone


def test_getOtherEvents(requests_mock):
    # Mock API
    other_event_text = open("tests/api/test_other_event.json", "r").read()
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit=1", text=other_event_text)

    # Test data
    test_date_string = "2020-01-10T15:30:00Z"
    test_mission_date_unaware = datetime.strptime(test_date_string, "%Y-%m-%dT%H:%M:%SZ")
    test_mission_date = get_localzone().localize(test_mission_date_unaware)

    test_mission_name = "2017 NASA Astronaut class graduation ceremony"
    test_location = "NASA's Johnson Space Center, Houston, TX, USA"
    test_mission_description = "NASA will honor the first class of astronaut candidates to graduate under the Artemis program at 10:30 a.m. EST Friday, Jan. 10, at the agency’s Johnson Space Center in Houston. After completing more than two years of basic training, these candidates will become eligible for spaceflight, including assignments to the International Space Station, Artemis missions to the Moon, and ultimately, missions to Mars."
    test_mission_type = "Press Event"

    # Get result of method
    event = api.getOtherEvents()[0]

    assert event.mission_name == test_mission_name
    assert event.location == test_location
    assert event.mission_date == test_mission_date
    assert event.mission_description == test_mission_description
    assert event.mission_type == test_mission_type


def test_getLaunchEvents(requests_mock):
    # Mock API
    launch_event_text = open("tests/api/test_launch_event.json", "r").read()
    now = datetime.now()
    requests_mock.get(
        "https://ll.thespacedevs.com/2.0.0/launch/?limit=1&net__gte=" + now.strftime("%Y-%m-%d"),
        text=launch_event_text,
    )

    # Make sure the request from the nested getRocket call is NOT intercepted
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/config/launcher/137/", real_http=True)

    # Test data
    test_date_string = "2020-09-24T15:00:00Z"
    test_mission_date_unaware = datetime.strptime(test_date_string, "%Y-%m-%dT%H:%M:%SZ")
    test_mission_date = get_localzone().localize(test_mission_date_unaware)

    test_mission_name = "NS-13"
    test_location = "West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA"
    test_mission_description = "This will be the 13th New Shepard mission and the 7th consecutive flight for this particular vehicle (a record), demonstrating its operational reusability. \r\n\r\nNew Shepard will fly 12 commercial payloads to space and back on this mission, including the Deorbit, Descent, and Landing Sensor Demonstration with NASA’s Space Technology Mission Directorate under a Tipping Point partnership. This is the first payload to fly mounted on the exterior of a New Shepard booster rather than inside the capsule, opening the door to a wide range of future high-altitude sensing, sampling, and exposure payloads."
    test_mission_type = "Suborbital"

    # Get result of method
    event = api.getLaunchEvents()[0]

    assert event.mission_name == test_mission_name
    assert event.location == test_location
    assert event.mission_date == test_mission_date
    assert event.mission_description == test_mission_description
    assert event.mission_type == test_mission_type


# TODO: add test_getRocket
