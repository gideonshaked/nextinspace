"""Never miss a launch: upcoming spaceflight launches and events from Launch Library 2."""

from importlib.metadata import version

# Defined before the imports below because the client reads it for its User-Agent.
__version__ = version("nextinspace")

from nextinspace.client import Client, Filters, LL2Error
from nextinspace.models import Event, Item, Launch, to_dict

__all__ = ["Client", "Event", "Filters", "Item", "LL2Error", "Launch", "__version__", "to_dict"]
