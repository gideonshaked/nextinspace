import copy
from datetime import datetime

import pytest

import nextinspace
from tests.conftest import *


@pytest.mark.parametrize("example", [example_event, example_rocket, example_launch])
def test_eq(example):
    assert example == copy.copy(example)


class DateHolder:
    """Placeholder for Launches or Events with actual date attributes"""

    def __init__(self, size):
        self.date = datetime(size, 1, 1)


@pytest.mark.parametrize(
    "target_length_merged_list, expected_result",
    [
        (5, [1, 2, 2, 3, 4]),
        (14, [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 10, 12, 14]),
        (21, [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 8, 10, 12, 14]),
    ],
)
def test_merge_sorted_sequences(target_length_merged_list, expected_result):
    list_1 = [DateHolder(size) for size in range(1, 8)]
    list_2 = [DateHolder(size * 2) for size in range(1, 8)]

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
