import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from nextinspace.cache import Cache
from nextinspace.client import Client

DATA = Path(__file__).parent / "data"
NOW = datetime(2026, 10, 10, 12, 37, 15, tzinfo=UTC)


def read(name: str) -> Any:
    return json.loads((DATA / name).read_text())


class FrozenDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW.astimezone(tz)


class FakeLL2:
    """MockTransport handler serving the recorded fixtures and recording every request."""

    def __init__(self) -> None:
        self.pages = {
            "/2.3.0/launches/upcoming/": read("launches_upcoming.json"),
            "/2.3.0/events/upcoming/": read("events_upcoming.json"),
            "/2.3.0/launches/previous/": read("launches_previous.json"),
        }
        self.detail = read("launch_crewed_detailed.json")["results"][0]
        self.requests: list[httpx.Request] = []
        self.status = 200
        self.text = ""
        self.offline = False

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.offline:
            raise httpx.ConnectError("unreachable", request=request)
        if self.status != 200:
            return httpx.Response(self.status, text=self.text)
        path = request.url.path
        if path in self.pages:
            return httpx.Response(200, json=self.pages[path])
        # Any launch UUID gets the crewed detail record under that id.
        if m := re.fullmatch(r"/2\.3\.0/launches/([0-9a-f-]{36})/", path):
            return httpx.Response(200, json={**self.detail, "id": m[1]})
        if m := re.fullmatch(r"/2\.3\.0/events/(\d+)/", path):
            events = self.pages["/2.3.0/events/upcoming/"]["results"]
            found = [e for e in events if str(e["id"]) == m[1]]
            if found:
                return httpx.Response(200, json=found[0])
        return httpx.Response(404, json={"detail": "Not found."})

    def paths(self) -> list[str]:
        return [r.url.path for r in self.requests]

    def params(self, path: str) -> dict[str, str]:
        (request,) = [r for r in self.requests if r.url.path == path]
        return dict(request.url.params)


@pytest.fixture
def load() -> Callable[[str], Any]:
    return read


@pytest.fixture
def detailed_launch() -> dict[str, Any]:
    return read("launch_crewed_detailed.json")["results"][0]


@pytest.fixture
def server() -> FakeLL2:
    return FakeLL2()


@pytest.fixture
def make_client(server, tmp_path):
    clients = []

    def make(**kwargs: Any) -> Client:
        client = Client(cache=Cache(tmp_path), transport=httpx.MockTransport(server), **kwargs)
        clients.append(client)
        return client

    yield make
    for client in clients:
        client.close()


@pytest.fixture
def frozen(monkeypatch):
    monkeypatch.setattr("nextinspace.client.datetime", FrozenDatetime)
    return FrozenDatetime
