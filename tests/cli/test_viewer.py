# type: ignore

import pytest
from pytest_lazy_fixtures import lf

from nextinspace.cli import viewer


def test_dict_event(example_event, example_event_dict):
    assert viewer.dict_event(example_event) == example_event_dict


@pytest.mark.parametrize(
    "launcher, dict_",
    [
        (
            lf("example_launcher"),
            lf("example_launcher_dict"),
        ),
        (None, None),
    ],
)
def test_dict_launcher(launcher, dict_):
    assert viewer.dict_launcher(launcher) == dict_


@pytest.mark.parametrize(
    "launch, dict_",
    [
        (
            lf("example_launch_verbose"),
            lf("example_launch_verbose_dict"),
        ),
        (
            lf("example_launch_normal"),
            lf("example_launch_normal_dict"),
        ),
    ],
)
def test_dict_launch(launch, dict_):
    assert viewer.dict_launch(launch) == dict_


@pytest.mark.parametrize(
    "item, dict_",
    [
        (
            lf("example_launch_normal"),
            lf("example_launch_normal_dict"),
        ),
        (
            lf("example_event"),
            lf("example_event_dict"),
        ),
    ],
)
def test_dict_item(item, dict_):
    assert viewer.dict_item(item) == dict_
