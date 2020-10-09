from datetime import datetime

from nextinspace import api, space


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
    launch = api.get_launches(1, space.Verbosity.VERBOSE)[0]

    assert launch.mission_name == example_launch.mission_name
    assert launch.location == example_launch.location
    assert launch.mission_date == example_launch.mission_date
    assert launch.mission_description == example_launch.mission_description
    assert launch.mission_type == example_launch.mission_type


def test_get_rocket(requests_mock, example_rocket_text, example_rocket):
    # Mock API
    rocket_url = "https://ll.thespacedevs.com/2.0.0/config/launcher/137/"
    requests_mock.get(rocket_url, text=example_rocket_text)

    # Get result of method
    rocket = api.get_rocket(rocket_url)

    assert rocket.name == example_rocket.name
    assert rocket.payload_leo == example_rocket.payload_leo
    assert rocket.payload_gto == example_rocket.payload_gto
    assert rocket.liftoff_thrust == example_rocket.liftoff_thrust
    assert rocket.liftoff_mass == example_rocket.liftoff_mass
    assert rocket.max_stages == example_rocket.max_stages
    assert rocket.height == example_rocket.height
    assert rocket.successful_launches == example_rocket.successful_launches
    assert rocket.consecutive_successful_launches == example_rocket.consecutive_successful_launches
    assert rocket.failed_launches == example_rocket.failed_launches
    assert rocket.maiden_flight_date == example_rocket.maiden_flight_date


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
