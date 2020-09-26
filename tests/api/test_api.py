from nextinspace import api
import pytest
from datetime import datetime
from tzlocal import get_localzone


def test_get_events(requests_mock):
    # Mock API
    event_text = open("tests/api/event.json", "r").read()
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit=1", text=event_text)

    # Test data
    test_mission_date_unaware = datetime(2020, 1, 10, hour=15, minute=30, second=0)
    test_mission_date = get_localzone().localize(test_mission_date_unaware)

    test_mission_name = "2017 NASA Astronaut class graduation ceremony"
    test_location = "NASA's Johnson Space Center, Houston, TX, USA"
    test_mission_description = "NASA will honor the first class of astronaut candidates to graduate under the Artemis program at 10:30 a.m. EST Friday, Jan. 10, at the agency’s Johnson Space Center in Houston. After completing more than two years of basic training, these candidates will become eligible for spaceflight, including assignments to the International Space Station, Artemis missions to the Moon, and ultimately, missions to Mars."
    test_mission_type = "Press Event"

    # Get result of method
    event = api.get_events()[0]

    assert event.mission_name == test_mission_name
    assert event.location == test_location
    assert event.mission_date == test_mission_date
    assert event.mission_description == test_mission_description
    assert event.mission_type == test_mission_type


def test_get_launches(requests_mock):
    # Mock API
    launch_text = open("tests/api/launch.json", "r").read()
    now = datetime.now()
    requests_mock.get(
        "https://ll.thespacedevs.com/2.0.0/launch/?limit=1&net__gte=" + now.strftime("%Y-%m-%d"),
        text=launch_text,
    )

    # Make sure the request from the nested getRocket call is NOT intercepted
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/config/launcher/137/", real_http=True)

    # Test data
    test_mission_date_unaware = datetime(2020, 9, 24, hour=15, minute=0, second=0)
    test_mission_date = get_localzone().localize(test_mission_date_unaware)

    test_mission_name = "NS-13"
    test_location = "West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA"
    test_mission_description = "This will be the 13th New Shepard mission and the 7th consecutive flight for this particular vehicle (a record), demonstrating its operational reusability. \r\n\r\nNew Shepard will fly 12 commercial payloads to space and back on this mission, including the Deorbit, Descent, and Landing Sensor Demonstration with NASA’s Space Technology Mission Directorate under a Tipping Point partnership. This is the first payload to fly mounted on the exterior of a New Shepard booster rather than inside the capsule, opening the door to a wide range of future high-altitude sensing, sampling, and exposure payloads."
    test_mission_type = "Suborbital"

    # Get result of method
    event = api.get_launches()[0]

    assert event.mission_name == test_mission_name
    assert event.location == test_location
    assert event.mission_date == test_mission_date
    assert event.mission_description == test_mission_description
    assert event.mission_type == test_mission_type


def test_get_rocket(requests_mock):
    # Mock API
    rocket_url = "https://ll.thespacedevs.com/2.0.0/config/launcher/137/"
    rocket_text = open("tests/api/rocket.json", "r").read()
    requests_mock.get(rocket_url, text=rocket_text)

    # Test data
    test_name = "New Shepard"
    test_payload_leo = 0
    test_payload_gto = 0
    test_liftoff_thrust = 490
    test_liftoff_mass = 75
    test_max_stages = 1
    test_successful_launches = 12
    test_consecutive_successful_launches = 12
    test_failed_launches = 0

    test_maiden_flight_date_unaware = datetime(2015, 4, 29)
    test_maiden_flight_date = get_localzone().localize(test_maiden_flight_date_unaware)

    # Get result of method
    rocket = api.get_rocket(rocket_url)

    assert rocket.name == test_name
    assert rocket.payload_leo == test_payload_leo
    assert rocket.payload_gto == test_payload_gto
    assert rocket.liftoff_thrust == test_liftoff_thrust
    assert rocket.liftoff_mass == test_liftoff_mass
    assert rocket.max_stages == test_max_stages
    assert rocket.successful_launches == test_successful_launches
    assert rocket.consecutive_successful_launches == test_consecutive_successful_launches
    assert rocket.failed_launches == test_failed_launches
    assert rocket.maiden_flight_date == test_maiden_flight_date
