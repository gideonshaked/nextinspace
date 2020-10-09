"""Pytest fixtures"""

from datetime import datetime

import pytest
from tzlocal import get_localzone

from nextinspace import space


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
def example_launch(example_rocket):
    return space.Launch(
        mission_name="New Shepard | NS-13",
        location="West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        mission_description="This will be the 13th New Shepard mission and the 7th consecutive flight for this particular vehicle (a record), demonstrating its operational reusability. \r\n\r\nNew Shepard will fly 12 commercial payloads to space and back on this mission, including the Deorbit, Descent, and Landing Sensor Demonstration with the NASA Space Technology Mission Directorate under the NASA Tipping Point partnership. This is the first payload to fly mounted on the exterior of a New Shepard booster rather than inside the capsule, opening the door to a wide range of future high-altitude sensing, sampling, and exposure payloads.",
        mission_date=get_localzone().localize(datetime(2020, 9, 24, hour=15, minute=0, second=0)),
        mission_type="Suborbital",
        rocket=example_rocket,
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


@pytest.fixture
def example_rocket():
    return space.Rocket(
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
        maiden_flight_date=get_localzone().localize(datetime(2015, 4, 29)),
    )
