# type: ignore

import copy
from datetime import MINYEAR, datetime, timedelta, timezone

import pytest
from pytest_lazy_fixtures import lf

import nextinspace
from nextinspace import BASE_URL


@pytest.mark.parametrize(
    "example",
    [
        lf("example_event"),
        lf("example_launcher"),
        lf("example_launch_verbose"),
    ],
)
def test_eq(example):
    assert example == copy.copy(example)


@pytest.mark.parametrize(
    "target_length_merged_list, expected_result",
    [
        (5, [1, 2, 2, 3, 4]),
        (14, [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 10, 12, 14]),
        (21, [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 10, 12, 14]),
    ],
)
def test_merge_sorted_sequences(list_1, list_2, target_length_merged_list, expected_result):
    result = nextinspace.merge_sorted_sequences(list_1, list_2, target_length_merged_list)
    result_only_nums = [holder.date.year for holder in result]

    assert result_only_nums == expected_result


@pytest.mark.parametrize(
    "pad, pad_loc, result",
    [
        ("Pad", "Location", "Pad, Location"),
        (None, "Location", "Location"),
        (None, None, None),
        ("Pad", None, "Pad"),
    ],
)
def test_build_location_string(pad, pad_loc, result):
    assert nextinspace.build_location_string(pad, pad_loc) == result


@pytest.mark.parametrize(
    "datetime_str, result",
    [
        (None, datetime(MINYEAR, 1, 1)),
        (
            "2020-09-24T15:00:00Z",
            # Don't run this test if you are not on Eastern time!
            datetime(2020, 9, 24, 11, 0, tzinfo=timezone(timedelta(days=-1, seconds=72000), "EDT")),
        ),
    ],
)
def test_date_str_to_datetime(datetime_str, result):
    FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
    print(nextinspace.date_str_to_datetime(datetime_str, FORMAT_STRING))
    assert nextinspace.date_str_to_datetime(datetime_str, FORMAT_STRING) == result


@pytest.mark.parametrize(
    "launch, include_launcher",
    [
        (lf("example_launch_verbose"), True),
        (lf("example_launch_normal"), False),
    ],
)
def test_next_launch(requests_mock, example_launch_text, launch, include_launcher, example_launcher_text):
    # Mock API
    now = datetime.utcnow()
    requests_mock.get(
        f"{BASE_URL}/launch?limit=1&net__gte=" + now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        text=example_launch_text,
    )
    # Make sure the request from the nested get_launcher call is intercepted
    requests_mock.get("https://ll.thespacedevs.com/2.0.0/config/launcher/137/", text=example_launcher_text)

    # Get result of function
    result_launch = nextinspace.next_launch(1, include_launcher)[0]

    assert result_launch == launch


def test_get_launcher(requests_mock, example_launcher_text, example_launcher):
    # Mock API
    launcher_url = "https://ll.thespacedevs.com/2.0.0/config/launcher/137/"
    requests_mock.get(launcher_url, text=example_launcher_text)

    # Get result of function
    launcher = nextinspace.get_launcher(launcher_url)

    assert launcher == example_launcher


def test_next_event(requests_mock, example_event_text, example_event):
    # Mock API
    requests_mock.get(f"{BASE_URL}/event/upcoming?limit=1", text=example_event_text)

    # Get result of function
    event = nextinspace.next_event(1)[0]

    assert event == example_event


def test_nextinspace(
    requests_mock, example_launch_text, example_event_text, example_launcher_text, example_event, example_launch_normal
):
    # Mock API (Launch)
    now = datetime.utcnow()
    requests_mock.get(
        f"{BASE_URL}/launch?limit=2&net__gte=" + now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        text=example_launch_text,
    )
    # Make sure the request from the nested get_launcher call is intercepted
    requests_mock.get(f"{BASE_URL}/config/launcher/137/", text=example_launcher_text)

    # Mock API (Event)
    requests_mock.get(f"{BASE_URL}/event/upcoming?limit=2", text=example_event_text)

    next = nextinspace.nextinspace(2)

    assert next == (example_event, example_launch_normal)
