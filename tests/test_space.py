from datetime import datetime

import pytest

from nextinspace import space


@pytest.fixture
def example_event():
    return space.Event(
        mission_name="this is a really long name with lots of edge cases that no one would in their right mind would name their mission",
        location="some launch pad",
        mission_date=datetime(1800, 9, 24, hour=15, minute=25, second=40),
        mission_description="I can't think of a descriptio so: This will be the 13th New Shepard mission and the 7th consecutive flight for this particular vehicle (a record), demonstrating its operational reusability. \r\n\r\nNew Shepard will fly 12 commercial payloads to space and back on this mission, including the Deorbit, Descent, and Landing Sensor Demonstration with the NASA Space Technology Mission Directorate under the NASA Tipping Point partnership. This is the first payload to fly mounted on the exterior of a New Shepard booster rather than inside the capsule, opening the door to a wide range of future high-altitude sensing, sampling, and exposure payloads.",
        mission_type="a type",
    )


@pytest.fixture
def example_launch():
    test_rocket = space.Rocket(
        name="Saturn V",
        payload_leo=300000000,
        payload_gto=40000000,
        liftoff_thrust=321,
        max_stages=70,
        height=10000,
        successful_launches=-1,
        failed_launches=-10,
        consecutive_successful_launches=-56,
        liftoff_mass=1,
        maiden_flight_date=datetime(1800, 9, 24, hour=15, minute=25, second=40),
    )
    return space.Launch(
        mission_name="this is a really long name with lots of edge cases that no one would in their right mind would name their mission",
        location="some launch pad",
        mission_date=datetime(1800, 9, 24, hour=15, minute=25, second=40),
        mission_description="I can't think of a description so: This will be the 13th New Shepard mission and the 7th consecutive flight for this particular vehicle (a record), demonstrating its operational reusability. \r\n\r\nNew Shepard will fly 12 commercial payloads to space and back on this mission, including the Deorbit, Descent, and Landing Sensor Demonstration with the NASA Space Technology Mission Directorate under the NASA Tipping Point partnership. This is the first payload to fly mounted on the exterior of a New Shepard booster rather than inside the capsule, opening the door to a wide range of future high-altitude sensing, sampling, and exposure payloads.",
        mission_type="Jeff Who Bald-Head, Aborthtrop Grumman, Scrubx, United Hold Alliance",
        rocket=test_rocket,
    )


@pytest.mark.parametrize(
    "verbosity",
    [
        space.Verbosity.QUIET,
        space.Verbosity.NORMAL,
        space.Verbosity.VERBOSE,
    ],
)
def test_event_display(verbosity, example_event):
    # Because the implementation of the display method will change fairly often and it not stable,
    # it doesn't make any sense to test by capturing stdout and comparing. As such, a visual confirmation
    # of the display method working is sufficient.

    # This test always passes, it can be manually assessed with 'pytest -s'

    print()
    print("Event verbosity: " + str(verbosity))
    example_event.display(verbosity)
    print()


@pytest.mark.parametrize(
    "verbosity",
    [
        space.Verbosity.QUIET,
        space.Verbosity.NORMAL,
        space.Verbosity.VERBOSE,
    ],
)
def test_launch_display(verbosity, example_launch):
    # Because the implementation of the display method will change fairly often and it not stable,
    # it doesn't make any sense to test by capturing stdout and comparing. As such, a visual confirmation
    # of the display method working is sufficient.

    # This test always passes, it can be manually assessed with 'pytest -s'

    print()
    print("Launch verbosity: " + str(verbosity))
    example_launch.display(verbosity)
    print()
