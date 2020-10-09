import pytest

from nextinspace import space


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
