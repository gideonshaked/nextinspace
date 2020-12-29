import pytest

from nextinspace.cli import viewer


def test_dict_event(example_event, example_event_dict):
    assert viewer.dict_event(example_event) == example_event_dict


@pytest.mark.parametrize(
    "launcher, dict_",
    [
        (
            pytest.lazy_fixture("example_launcher"),
            pytest.lazy_fixture("example_launcher_dict"),
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
            pytest.lazy_fixture("example_launch_verbose"),
            pytest.lazy_fixture("example_launch_verbose_dict"),
        ),
        (
            pytest.lazy_fixture("example_launch_normal"),
            pytest.lazy_fixture("example_launch_normal_dict"),
        ),
    ],
)
def test_dict_launch(launch, dict_):
    assert viewer.dict_launch(launch) == dict_


@pytest.mark.parametrize(
    "item, dict_",
    [
        (
            pytest.lazy_fixture("example_launch_normal"),
            pytest.lazy_fixture("example_launch_normal_dict"),
        ),
        (
            pytest.lazy_fixture("example_event"),
            pytest.lazy_fixture("example_event_dict"),
        ),
    ],
)
def test_dict_item(item, dict_):
    assert viewer.dict_item(item) == dict_
