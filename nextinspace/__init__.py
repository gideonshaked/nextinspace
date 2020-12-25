__version__ = "1.0.6"
__all__ = ["nextinspace, next_launch, next_event, Verbosity"]

from datetime import date as datetime_date  # Get around duplicate date identifier
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Sequence, Tuple

import requests


class Verbosity(Enum):
    """This is an Enum class to represent the verbosity of a requested :class:`Launch`. In the internal `nextinspace` API,
    the verbosity affects whether or not a :class:`Rocket` is created (and more importantly retrieved from the LL2 API) for each
    :class:`Launch`. **A :class:`Verbosity` of `verbose` will create an additional API request for each Launch you request. This will
    take time and count toward your daily request quota before you are rate-limited.**

    .. note::

       In the context of the included CLI the "verbosity" a) has an effect on both :class:`Launches <Launch>` and :class:`Events <Event>`
       and b) can be set to `quiet`, `normal`, or `verbose`. That is separate from this.
    """

    normal = 1
    verbose = 2


class Event:
    """Generic space event."""

    def __init__(self, name, location, date, description, type_):
        self.name: str = name
        self.location: str = location
        self.date: datetime = date
        self.description: str = description
        self.type_: str = type_

    def __eq__(self, other: object) -> bool:
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class Launch(Event):
    """Launch event"""

    def __init__(self, name, location, date, description, type_, rocket):
        super().__init__(name, location, date, description, type_)
        self.rocket: Rocket = rocket


class Rocket:
    """Holds rocket information for instances of the :class:`Launch` class"""

    def __init__(
        self,
        name,
        payload_leo,
        payload_gto,
        liftoff_thrust,
        liftoff_mass,
        max_stages,
        height,
        successful_launches,
        consecutive_successful_launches,
        failed_launches,
        maiden_flight_date,
    ):

        self.name: str = name
        self.payload_leo: float = payload_leo
        self.payload_gto: float = payload_gto
        self.liftoff_thrust: float = liftoff_thrust
        self.liftoff_mass: float = liftoff_mass
        self.max_stages: int = max_stages
        self.height: float = height
        self.successful_launches: int = successful_launches
        self.consecutive_successful_launches: int = consecutive_successful_launches
        self.failed_launches: int = failed_launches
        self.maiden_flight_date: datetime = maiden_flight_date

    def __eq__(self, other: object) -> bool:
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


def nextinspace(num_items: int, verbosity: Verbosity = Verbosity.normal) -> Tuple:
    """This gets the next (specified number) of items from the LL2 API.

    :param num_items: Number of items to get from the API
    :type num_items: int
    :param verbosity: The :class:`Verbosity` of the requested :class:`Launches <Launch>`, defaults to Verbosity.normal
    :type verbosity: Verbosity, optional
    :return: Upcoming :class:`Launches <Launch>` and :class:`Events <Event>`. Note that the length of this tuple will be <= `num_items`.
    :rtype: Tuple
    :raises requests.exceptions.RequestException: If there is a problem connecting to the API. Also does a `raise_for_status()` call \
        so HTTPErrors are possible as well.

    .. warning::

       Because the LL2 API does not offer any way of getting *n* upcoming spaceflight items, this function must query the API twice,
       once for the next *n* :class:`Events <Event>`, and once for the next *n* :class:`Launches <Launch>`, and merge the queries
       into a sorted form. **As such, this function may be slower than anticipated.** 🙁

    .. note::

       Because the filter by time function of the LL2 API is currently broken, **upcoming means beyond and including today**.
    """
    events = next_event(num_items)
    launches = next_launch(num_items, verbosity)
    return tuple(merge_sorted_sequences(events, launches, num_items))


def merge_sorted_sequences(seq_1: Sequence, seq_2: Sequence, target_length_merged_list: int) -> List:
    l_seq_1 = len(seq_1)
    l_seq_2 = len(seq_2)

    # The lengths of two lists added is the max possible length of any combination
    max_possible_length = l_seq_1 + l_seq_2

    # The actual length should IDEALLY be as close to the target length as possible, so:
    #
    # If target length <= max possible length --> we can just set merged length to target length
    #
    # If target length > max possible length --> the actual length is set to the max possible length
    # (which is as close to the target as is possible)
    merged_list_length = min(target_length_merged_list, max_possible_length)

    merged_list = [None] * merged_list_length
    i: int = 0
    j: int = 0
    k: int = 0

    # Traverse both lists simultaneously
    while i < l_seq_1 and j < l_seq_2:

        # Check if current element of first array is smaller than current element of second array.
        # If yes, store first array element and increment first array index. Otherwise do same with second array
        if seq_1[i].date < seq_2[j].date:
            merged_list[k] = seq_1[i]
            k += 1
            if k == merged_list_length:
                return merged_list
            i += 1
        else:
            merged_list[k] = seq_2[j]
            k += 1
            if k == merged_list_length:
                return merged_list
            j += 1

    # Store remaining elements of first list
    while i < l_seq_1:
        merged_list[k] = seq_1[i]
        k += 1
        if k == merged_list_length:
            return merged_list
        i += 1

    # Store remaining elements of second list
    while j < l_seq_2:
        merged_list[k] = seq_2[j]
        k += 1
        if k == merged_list_length:
            return merged_list
        j += 1

    return merged_list


def next_launch(num_launches: int, verbosity: Verbosity = Verbosity.normal) -> Tuple:
    """Same as :func:`nextinspace` but only :class:`Launches <Launch>` requested.

    :param num_launches: Number of :class:`Launches <Launch>` to get from the API
    :type num_launches: int
    :param verbosity: The :class:`Verbosity` of the requested :class:`Launches <Launch>`, defaults to Verbosity.normal
    :type verbosity: Verbosity, optional
    :return: Upcoming :class:`Launches <Launch>`. Note that the length of this tuple will be <= `num_launches`.
    :rtype: Tuple
    :raises requests.exceptions.RequestException:
    """
    today_str = datetime_date.today().strftime("%Y-%m-%d")
    data = api_get_request("https://ll.thespacedevs.com/2.0.0/launch", {"limit": num_launches, "net__gte": today_str})

    launches = []
    for result in data["results"]:
        name = result["name"]

        pad_name = get_nested_dict_val(result, "pad", "name")
        pad_location = get_nested_dict_val(result, "pad", "location", "name")
        location = build_location_string(pad_name, pad_location)

        date = date_str_to_datetime(result["net"], "%Y-%m-%dT%H:%M:%SZ")
        description = get_nested_dict_val(result, "mission", "description")
        type_ = get_nested_dict_val(result, "mission", "type")

        rocket_url = get_nested_dict_val(result, "rocket", "configuration", "url")
        rocket = get_rocket(rocket_url) if verbosity == Verbosity.verbose else None

        launches.append(Launch(name, location, date, description, type_, rocket))

    return tuple(launches)


def build_location_string(pad_name: str, pad_location: str) -> str:
    if pad_name is not None:
        if pad_location is not None:
            return f"{pad_name}, {pad_location}"
        return pad_name
    elif pad_location is not None:
        return pad_location
    else:
        return None


def next_event(num_events: int) -> Tuple:
    """Same as :func:`nextinspace` but only :class:`Events <Event>` requested.

    :param num_events: Number of :class:`Events <Event>` to get from the API
    :type num_events: int
    :return: Upcoming :class:`Events <Event>`. Note that the length of this tuple will be <= `num_events`.
    :rtype: Tuple
    :raises requests.exceptions.RequestException:
    """
    data = api_get_request("https://ll.thespacedevs.com/2.0.0/event/upcoming", {"limit": num_events})

    events = []
    for result in data["results"]:
        name = result["name"]
        location = result["location"]
        date = date_str_to_datetime(result["date"], "%Y-%m-%dT%H:%M:%SZ")
        description = result["description"]
        type_ = get_nested_dict_val(result, "type", "name")

        events.append(Event(name, location, date, description, type_))

    return tuple(events)


def get_nested_dict_val(dict_: Dict, *keys: str) -> Any:
    """Get the value present in the nested dict at the specified keys. If a TypeError is raised
    (because at some point in the path we find None), then return None. This is necessary because there is
    no API documentation I could find that specified when and how values could be left nonexistent.
    Note that this method is only required when accessing a nested dict (ex: dict[x][y]).

    :param dictionary: The dictionary to search in
    :type dictionary: Dict
    :return: Whatever value is at the last nested key
    :rtype: Any
    """
    try:
        for key in keys:
            dict_ = dict_[key]
        return dict_
    except TypeError:
        return None


def get_rocket(url: str) -> Rocket:
    """Get rocket from API

    :param url: LL2 API URL for requested :class:`Rocket`
    :type url: str
    :return: Requested :class:`Rocket`
    :rtype: Rocket
    """
    data = api_get_request(url)

    name = data["full_name"]
    payload_leo = data["leo_capacity"]
    payload_gto = data["gto_capacity"]
    liftoff_thrust = data["to_thrust"]
    liftoff_mass = data["launch_mass"]
    max_stages = data["max_stage"]
    height = data["length"]
    successful_launches = data["successful_launches"]
    consecutive_successful_launches = data["consecutive_successful_launches"]
    failed_launches = data["failed_launches"]
    maiden_flight_date = date_str_to_datetime(data["maiden_flight"], "%Y-%m-%d")

    return Rocket(
        name,
        payload_leo,
        payload_gto,
        liftoff_thrust,
        liftoff_mass,
        max_stages,
        height,
        successful_launches,
        consecutive_successful_launches,
        failed_launches,
        maiden_flight_date,
    )


def date_str_to_datetime(datetime_str: str, fmat_str: str) -> datetime:
    """Convert datetime string in UTC to datetime object in local timezone

    :param datetime_str:
    :type datetime_str: str
    :param fmat_str: Format str for `datetime.strptime()`
    :type fmat_str: str
    :return: datetime object in local timezone
    :rtype: datetime
    """
    if datetime_str is None:
        return None
    datetime_utc = datetime.strptime(datetime_str, fmat_str).replace(tzinfo=timezone.utc)
    return datetime_utc.astimezone()


def api_get_request(endpoint: str, payload: Dict = {}) -> Any:
    """Make get request to LL2 API

    :param endpoint: API endpoint address
    :type endpoint: str
    :param payload: Query string for API as defined by Requests, defaults to {}
    :type payload: Dict, optional
    :return: Either JSON data from the API or raise an exception if the API is unreachable
    :rtype: Any
    :raises requests.exceptions.RequestException:
    """
    response = requests.get(endpoint, params=payload)
    response.raise_for_status()
    return response.json()
