__version__ = "2.0.0"
__all__ = ["nextinspace", "next_launch", "next_event"]

import typing
from datetime import MINYEAR
from datetime import date as datetime_date  # Get around duplicate date identifier
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import requests


class Event:
    """Generic space event.

    This constructor is meant for private use. This class is documented solely for its attributes.

    .. note::

       When the LL2 API does not provide a date for the :class:`Event`, the `date` attribute is set to `datetime(datetime.MINYEAR, 1, 1)`.
       This is so the :class:`Event` is sorted to the back of the returned tuple.
    """

    def __init__(
        self,
        name: Optional[str],
        location: Optional[str],
        date: datetime,
        description: Optional[str],
        type_: Optional[str],
    ):
        self.name = name
        self.location = location
        self.date = date
        self.description = description
        self.type_ = type_

    def __eq__(self, other: object) -> bool:
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}({', '.join(repr(attr) for attr in self.__dict__.values())})"


class Launcher:
    """Holds launcher information for instances of the :class:`Launch` class

    This constructor is meant for private use. This class is documented solely for its attributes.

    .. note::

       When the LL2 API does not provide a maiden flight date for the :class:`Launcher`,
       the `maiden_flight_date` attribute is set to `datetime(datetime.MINYEAR, 1, 1)`.
    """

    def __init__(
        self,
        name: Optional[str],
        payload_leo: Optional[float],
        payload_gto: Optional[float],
        liftoff_thrust: Optional[float],
        liftoff_mass: Optional[float],
        max_stages: Optional[int],
        height: Optional[float],
        successful_launches: Optional[int],
        consecutive_successful_launches: Optional[int],
        failed_launches: Optional[int],
        maiden_flight_date: datetime,
    ):

        self.name = name
        self.payload_leo = payload_leo
        self.payload_gto = payload_gto
        self.liftoff_thrust = liftoff_thrust
        self.liftoff_mass = liftoff_mass
        self.max_stages = max_stages
        self.height = height
        self.successful_launches = successful_launches
        self.consecutive_successful_launches = consecutive_successful_launches
        self.failed_launches = failed_launches
        self.maiden_flight_date = maiden_flight_date

    def __eq__(self, other: object) -> bool:
        if type(self) is type(other):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}({', '.join(repr(attr) for attr in self.__dict__.values())})"


class Launch(Event):
    """Launch event

    This constructor is meant for private use. This class is documented solely for its attributes.

    .. note::

       When the LL2 API does not provide a date for the :class:`Launch`, the `date` attribute is set to `datetime(datetime.MINYEAR, 1, 1)`.
       This is so the :class:`Launch` is sorted to the back of the returned tuple.
    """

    def __init__(
        self,
        name: Optional[str],
        location: Optional[str],
        date: datetime,
        description: Optional[str],
        type_: Optional[str],
        launcher: Optional[Launcher],
    ):
        super().__init__(name, location, date, description, type_)
        self.launcher = launcher


def nextinspace(num_items: int, include_launcher: bool = False) -> Tuple[Union[Launch, Event], ...]:
    """This gets the next (specified number) of items from the LL2 API.

    :param num_items: Number of items to get from the API
    :type num_items: int
    :param include_launcher: Whether to include the launcher of the requested :class:`Launches <Launch>`, defaults to False
    :type inlcude_launcher: bool, optional
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
    launches = next_launch(num_items, include_launcher)
    return tuple(merge_sorted_sequences(events, launches, num_items))


@typing.no_type_check
def merge_sorted_sequences(
    seq_1: Sequence[Union[Launch, Event]], seq_2: Sequence[Union[Launch, Event]], target_length_merged_list: int
) -> List[Union[Launch, Event]]:
    """Perform a merge of two sorted sequences. Sequences must be of Events or of Event subclasses with date attributes"""
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

    merged_list: Any = [None] * merged_list_length
    i = 0
    j = 0
    k = 0

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


def next_launch(num_launches: int, include_launcher: bool = False) -> Tuple[Launch, ...]:
    """Same as :func:`nextinspace` but only :class:`Launches <Launch>` requested.

    :param num_launches: Number of :class:`Launches <Launch>` to get from the API
    :type num_launches: int
    :param include_launcher: Whether to include the launcher of the requested :class:`Launches <Launch>`, defaults to False
    :type inlcude_launcher: bool, optional
    :return: Upcoming :class:`Launches <Launch>`. Note that the length of this tuple will be <= `num_launches`.
    :rtype: Tuple
    :raises requests.exceptions.RequestException: If there is a problem connecting to the API. Also does a `raise_for_status()` call \
        so HTTPErrors are possible as well.
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

        launcher_url = get_nested_dict_val(result, "rocket", "configuration", "url")
        launcher = get_launcher(launcher_url) if include_launcher else None

        launches.append(Launch(name, location, date, description, type_, launcher))

    return tuple(launches)


def build_location_string(pad_name: Optional[str], pad_location: Optional[str]) -> Optional[str]:
    if pad_name is not None:
        if pad_location is not None:
            return f"{pad_name}, {pad_location}"
        return pad_name
    elif pad_location is not None:
        return pad_location
    else:
        return None


def next_event(num_events: int) -> Tuple[Event, ...]:
    """Same as :func:`nextinspace` but only :class:`Events <Event>` requested.

    :param num_events: Number of :class:`Events <Event>` to get from the API
    :type num_events: int
    :return: Upcoming :class:`Events <Event>`. Note that the length of this tuple will be <= `num_events`.
    :rtype: Tuple
    :raises requests.exceptions.RequestException: If there is a problem connecting to the API. Also does a `raise_for_status()` call \
        so HTTP errors are possible as well.
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


def get_launcher(url: str) -> Launcher:
    """Get launcher from API

    :param url: LL2 API URL for requested :class:`Launcher`
    :type url: str
    :return: Requested :class:`Launcher`
    :rtype: Launcher
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

    return Launcher(
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


def date_str_to_datetime(datetime_str: Optional[str], fmat_str: str) -> datetime:
    """Convert datetime string in UTC to datetime object in local timezone

    :param datetime_str:
    :type datetime_str: Optional[str]
    :param fmat_str: Format str for `datetime.strptime()`
    :type fmat_str: str
    :return: datetime object in local timezone
    :rtype: datetime
    """
    if datetime_str is None:
        return datetime(MINYEAR, 1, 1)
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
