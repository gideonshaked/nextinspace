from datetime import datetime

import pytest
from tzlocal import get_localzone

from nextinspace import api, space


@pytest.fixture
def example_launch_text():
    return open("tests/data/launch.json", "r").read()


@pytest.fixture
def example_rocket_text():
    return open("tests/data/rocket.json", "r").read()


@pytest.fixture
def example_event_text():
    return open("tests/data/event.json", "r").read()


@pytest.fixture
def example_launch():
    return space.Launch(
        mission_name="New Shepard | NS-13",
        location="West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        mission_description="This will be the 13th New Shepard mission and the 7th consecutive flight for this particular vehicle (a record), demonstrating its operational reusability. \r\n\r\nNew Shepard will fly 12 commercial payloads to space and back on this mission, including the Deorbit, Descent, and Landing Sensor Demonstration with the NASA Space Technology Mission Directorate under the NASA Tipping Point partnership. This is the first payload to fly mounted on the exterior of a New Shepard booster rather than inside the capsule, opening the door to a wide range of future high-altitude sensing, sampling, and exposure payloads.",
        mission_date=get_localzone().localize(datetime(2020, 9, 24, hour=15, minute=0, second=0)),
        mission_type="Suborbital",
        rocket=None,
    )


@pytest.fixture
def example_event():
    return space.Event(
        mission_name="2017 NASA Astronaut class graduation ceremony",
        location="NASA's Johnson Space Center, Houston, TX, USA",
        mission_description="NASA will honor the first class of astronaut candidates to graduate under the Artemis program at 10:30 a.m. EST Friday, Jan. 10, at the Johnson Space Center in Houston. After completing more than two years of basic training, these candidates will become eligible for spaceflight, including assignments to the International Space Station, Artemis missions to the Moon, and ultimately, missions to Mars.",
        mission_date=get_localzone().localize(datetime(2020, 1, 10, hour=15, minute=30, second=0)),
        mission_type="Press Event",
    )


def test_get_launches(requests_mock, example_launch_text, example_launch):
    # Mock API
    now = datetime.now()
    requests_mock.get(
        "https://ll.thespacedevs.com/2.0.0/launch/?limit=1&net__gte=" + now.strftime("%Y-%m-%d"),
        text=example_launch_text,
    )
    # Make sure the request from the nested get_rocket call is intercepted
    rocket_text = open("tests/data/rocket.json", "r").read()
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/config/launcher/137/", text=rocket_text)

    # Get result of method
    launch = api.get_launches(1)[0]

    assert launch.mission_name == example_launch.mission_name
    assert launch.location == example_launch.location
    assert launch.mission_date == example_launch.mission_date
    assert launch.mission_description == example_launch.mission_description
    assert launch.mission_type == example_launch.mission_type


def test_get_rocket(requests_mock, example_rocket_text):
    # Mock API
    rocket_url = "https://ll.thespacedevs.com/2.0.0/config/launcher/137/"
    requests_mock.get(rocket_url, text=example_rocket_text)

    # Test data
    test_name = "New Shepard"
    test_payload_leo = 0
    test_payload_gto = 0
    test_liftoff_thrust = 490
    test_liftoff_mass = 75
    test_max_stages = 1
    test_height = 15.0
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
    assert rocket.height == test_height
    assert rocket.successful_launches == test_successful_launches
    assert rocket.consecutive_successful_launches == test_consecutive_successful_launches
    assert rocket.failed_launches == test_failed_launches
    assert rocket.maiden_flight_date == test_maiden_flight_date


def test_get_events(requests_mock, example_event_text, example_event):
    # Mock API
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/event/upcoming/?limit=1", text=example_event_text)

    # Get result of method
    event = api.get_events(1)[0]

    assert event.mission_name == example_event.mission_name
    assert event.location == example_event.location
    assert event.mission_date == example_event.mission_date
    assert event.mission_description == example_event.mission_description
    assert event.mission_type == example_event.mission_type
