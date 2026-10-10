"""Client for the Launch Library 2 API (https://thespacedevs.com/llapi).

Anonymous access is limited to 15 requests per hour, so every response is cached on
disk and reused for ``ttl`` seconds. When the API refuses a request (rate limit or no
network), the client falls back to the newest cached copy however old it is and
records a note saying so, rather than failing outright.
"""

from __future__ import annotations

import heapq
import re
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import islice
from typing import Any
from urllib.parse import urlencode

import httpx
import platformdirs

from nextinspace import __version__
from nextinspace.cache import Cache
from nextinspace.models import Event, Item, Launch, parse_event, parse_launch
from nextinspace.timefmt import ago

PROD_URL = "https://ll.thespacedevs.com/2.3.0"
DEV_URL = "https://lldev.thespacedevs.com/2.3.0"
DEFAULT_TTL = 600


class LL2Error(Exception):
    """The API could not answer and no cached copy was available."""


@dataclass(frozen=True)
class Filters:
    search: str | None = None
    provider: str | None = None
    crewed: bool = False
    within: timedelta | None = None

    @property
    def launch_only(self) -> bool:
        """Filters that only make sense for launches, so events are skipped."""
        return self.provider is not None or self.crewed


NO_FILTERS = Filters()


def sort_key(item: Item) -> tuple[bool, datetime]:
    """Chronological order with undated items last."""
    return item.net is None, item.net or datetime.max.replace(tzinfo=UTC)


def _stamp(t: datetime) -> str:
    # Bounds are floored to ten minutes so repeated calls produce identical query
    # strings and therefore hit the cache instead of spending the hourly quota.
    t = t.astimezone(UTC).replace(second=0, microsecond=0)
    return t.replace(minute=t.minute - t.minute % 10).strftime("%Y-%m-%dT%H:%M:%SZ")


class Client:
    def __init__(
        self,
        *,
        base_url: str = PROD_URL,
        api_key: str | None = None,
        cache: Cache | None = None,
        ttl: float = DEFAULT_TTL,
        refresh: bool = False,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {"User-Agent": f"nextinspace/{__version__} (+https://github.com/gideonshaked/nextinspace)"}
        if api_key:
            headers["Authorization"] = f"Token {api_key}"
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=headers,
            timeout=20,
            transport=transport,
            follow_redirects=True,
        )
        self.cache = cache or Cache(platformdirs.user_cache_path("nextinspace"))
        self.ttl = ttl
        self.refresh = refresh
        self.notes: list[str] = []

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ---- Raw access ----

    def get(self, path: str, params: dict[str, Any]) -> Any:
        key = f"{self._http.base_url}{path}?{urlencode(sorted(params.items()))}"
        cached = self.cache.get(key)
        if cached is not None and not self.refresh and cached[0] < self.ttl:
            return cached[1]

        try:
            response = self._http.get(path, params=params)
        except httpx.TransportError as err:
            return self._fallback(
                cached,
                f"could not reach Launch Library 2 ({err.__class__.__name__})",
                "",
            )

        if response.status_code == 429:
            wait = re.search(r"(\d+) seconds", response.text)
            when = f" for another {ago(int(wait.group(1)))}" if wait else ""
            return self._fallback(
                cached,
                f"Launch Library 2 rate limit reached{when}",
                "Anonymous access allows 15 requests per hour. "
                "Set NEXTINSPACE_API_KEY to an LL2 API key to lift the limit.",
            )
        if response.status_code == 404:
            raise LL2Error(f"nothing found at {path}")
        if response.is_error:
            return self._fallback(cached, f"Launch Library 2 returned HTTP {response.status_code}", "")

        data = response.json()
        self.cache.put(key, data)
        return data

    def _fallback(self, cached: tuple[float, Any] | None, reason: str, hint: str) -> Any:
        if cached is None:
            raise LL2Error(f"{reason}. {hint}".strip())
        self.notes.append(f"{reason}; showing data cached {ago(cached[0])} ago.")
        return cached[1]

    # ---- Listings ----

    def upcoming_launches(self, limit: int, filters: Filters = NO_FILTERS) -> list[Launch]:
        params: dict[str, Any] = {
            "limit": limit,
            "mode": "normal",
            "hide_recent_previous": "true",
        }
        params |= self._launch_filters(filters)
        if filters.within:
            params["net__lte"] = _stamp(datetime.now(UTC) + filters.within)
        return [parse_launch(r) for r in self.get("/launches/upcoming/", params)["results"]]

    def upcoming_events(self, limit: int, filters: Filters = NO_FILTERS) -> list[Event]:
        params: dict[str, Any] = {
            "limit": limit,
            "mode": "normal",
            "hide_recent_previous": "true",
        }
        if filters.search:
            params["search"] = filters.search
        if filters.within:
            params["date__lte"] = _stamp(datetime.now(UTC) + filters.within)
        return [parse_event(r) for r in self.get("/events/upcoming/", params)["results"]]

    def previous_launches(self, limit: int, filters: Filters = NO_FILTERS) -> list[Launch]:
        params: dict[str, Any] = {"limit": limit, "mode": "normal"}
        params |= self._launch_filters(filters)
        if filters.within:
            params["net__gte"] = _stamp(datetime.now(UTC) - filters.within)
        return [parse_launch(r) for r in self.get("/launches/previous/", params)["results"]]

    def upcoming(
        self,
        limit: int,
        *,
        launches: bool = True,
        events: bool = True,
        filters: Filters = NO_FILTERS,
    ) -> list[Item]:
        """The next ``limit`` launches and events, merged chronologically.

        LL2 has no combined endpoint, so this asks for ``limit`` of each concurrently
        and merges them.
        """
        jobs: list[Callable[[], Sequence[Item]]] = []
        if launches:
            jobs.append(lambda: self.upcoming_launches(limit, filters))
        if events and not filters.launch_only:
            jobs.append(lambda: self.upcoming_events(limit, filters))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda job: job(), jobs))
        return list(islice(heapq.merge(*results, key=sort_key), limit))

    @staticmethod
    def _launch_filters(filters: Filters) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if filters.search:
            params["search"] = filters.search
        if filters.provider:
            params["lsp__name"] = filters.provider
        if filters.crewed:
            params["is_crewed"] = "true"
        return params

    # ---- Single items ----

    def launch(self, launch_id: str) -> Launch:
        return parse_launch(self.get(f"/launches/{launch_id}/", {"mode": "detailed"}))

    def event(self, event_id: str) -> Event:
        return parse_event(self.get(f"/events/{event_id}/", {"mode": "detailed"}))

    def detail(self, item: Item) -> Item:
        return self.launch(item.id) if isinstance(item, Launch) else self.event(item.id)
