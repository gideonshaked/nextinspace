"""Pytest fixtures"""

from datetime import datetime

import pytest

import nextinspace


@pytest.fixture
def example_launch_text():
    return open("tests/data/launch.json", "r").read()


@pytest.fixture
def example_launcher_text():
    return open("tests/data/launcher.json", "r").read()


@pytest.fixture
def example_event_text():
    return open("tests/data/event.json", "r").read()


@pytest.fixture
def example_launch_verbose(example_launcher):
    return nextinspace.Launch(
        name="New Shepard | NS-13",
        location="West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        description="This will be the 13th New Shepard mission...",
        date=nextinspace.date_str_to_datetime("2020-09-24T15:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        type_="Suborbital",
        launcher=example_launcher,
    )


@pytest.fixture
def example_launch_normal():
    return nextinspace.Launch(
        name="New Shepard | NS-13",
        location="West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        description="This will be the 13th New Shepard mission...",
        date=nextinspace.date_str_to_datetime("2020-09-24T15:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        type_="Suborbital",
        launcher=None,
    )


@pytest.fixture
def example_event():
    return nextinspace.Event(
        name="2017 NASA Astronaut class graduation ceremony",
        location="NASA's Johnson Space Center, Houston, TX, USA",
        description="NASA will honor the first class of astronaut...",
        date=nextinspace.date_str_to_datetime("2020-01-10T15:30:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        type_="Press Event",
    )


@pytest.fixture
def example_launcher():
    return nextinspace.Launcher(
        name="New Shepard",
        payload_leo=0,
        payload_gto=0,
        liftoff_thrust=490,
        liftoff_mass=75,
        max_stages=1,
        height=15.0,
        successful_launches=12,
        consecutive_successful_launches=12,
        failed_launches=0,
        maiden_flight_date=nextinspace.date_str_to_datetime("2015-04-29", "%Y-%m-%d"),
    )


class DateHolder:
    """Placeholder for Launches or Events with actual date attributes"""

    def __init__(self, size):
        self.date = datetime(size, 1, 1)


@pytest.fixture
def list_1():
    return [DateHolder(size) for size in range(1, 8)]


@pytest.fixture
def list_2():
    return [DateHolder(size * 2) for size in range(1, 8)]


@pytest.fixture
def example_event_dict():
    return {
        "type": "event",
        "name": "2017 NASA Astronaut class graduation ceremony",
        "location": "NASA's Johnson Space Center, Houston, TX, USA",
        "date": "2020-01-10T15:30:00Z",
        "description": "NASA will honor the first class of astronaut...",
        "subtype": "Press Event",
    }


@pytest.fixture
def example_launcher_dict():
    return {
        "name": "New Shepard",
        "payload_leo": 0,
        "payload_gto": 0,
        "liftoff_thrust": 490,
        "liftoff_mass": 75,
        "max_stages": 1,
        "height": 15.0,
        "successful_launches": 12,
        "consecutive_successful_launches": 12,
        "failed_launches": 0,
        "maiden_flight_date": "2015-04-29",
    }


@pytest.fixture
def example_launch_normal_dict():
    return {
        "type": "launch",
        "name": "New Shepard | NS-13",
        "location": "West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        "date": "2020-09-24T15:00:00Z",
        "description": "This will be the 13th New Shepard mission...",
        "subtype": "Suborbital",
        "launcher": None,
    }


@pytest.fixture
def example_launch_verbose_dict():
    return {
        "type": "launch",
        "name": "New Shepard | NS-13",
        "location": "West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        "date": "2020-09-24T15:00:00Z",
        "description": "This will be the 13th New Shepard mission...",
        "subtype": "Suborbital",
        "launcher": {
            "name": "New Shepard",
            "payload_leo": 0,
            "payload_gto": 0,
            "liftoff_thrust": 490,
            "liftoff_mass": 75,
            "max_stages": 1,
            "height": 15.0,
            "successful_launches": 12,
            "consecutive_successful_launches": 12,
            "failed_launches": 0,
            "maiden_flight_date": "2015-04-29",
        },
    }
