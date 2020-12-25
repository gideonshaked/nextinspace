"""Pytest fixtures"""

from datetime import datetime

import pytest
from tzlocal import get_localzone

import nextinspace


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
    return nextinspace.Launch(
        mission_name="New Shepard | NS-13",
        location="West Texas Suborbital Launch Site/ Corn Ranch, Corn Ranch, USA",
        mission_description="This will be the 13th New Shepard mission...",
        mission_date=get_localzone().localize(datetime(2020, 9, 24, hour=15, minute=0, second=0)),
        mission_type="Suborbital",
        rocket=example_rocket,
    )


@pytest.fixture
def example_event():
    return nextinspace.Event(
        mission_name="2017 NASA Astronaut class graduation ceremony",
        location="NASA's Johnson Space Center, Houston, TX, USA",
        mission_description="NASA will honor the first class of astronaut...",
        mission_date=get_localzone().localize(datetime(2020, 1, 10, hour=15, minute=30, second=0)),
        mission_type="Press Event",
    )


@pytest.fixture
def example_rocket():
    return nextinspace.Rocket(
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
