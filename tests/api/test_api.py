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