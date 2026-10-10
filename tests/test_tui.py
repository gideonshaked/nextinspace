from zoneinfo import ZoneInfo

import pytest
from textual.widgets import DataTable, Input, Static

from nextinspace.tui import Browser


@pytest.fixture
def browser(make_client):
    return Browser(make_client(), ZoneInfo("UTC"))


async def settle(app, pilot):
    # Pause first so a key press has reached its handler and started the worker.
    await pilot.pause()
    await app.workers.wait_for_complete()
    await pilot.pause()


def row_keys(app):
    return [key.value for key in app.query_one(DataTable).rows]


async def test_loads_rows(browser, server):
    async with browser.run_test() as pilot:
        await settle(browser, pilot)
        keys = row_keys(browser)
        assert len(keys) == 20
        assert keys[0].startswith("launch:")
        assert "event:1525" in keys
        assert server.params("/2.3.0/launches/upcoming/")["limit"] == "30"


async def test_launches_mode(browser):
    async with browser.run_test() as pilot:
        await settle(browser, pilot)
        await pilot.press("l")
        await settle(browser, pilot)
        keys = row_keys(browser)
        assert len(keys) == 10
        assert all(k.startswith("launch:") for k in keys)
        assert browser.sub_title == "Next launches"


async def test_enter_fetches_detail(browser, server, load):
    first = load("launches_upcoming.json")["results"][0]["id"]
    async with browser.run_test() as pilot:
        await settle(browser, pilot)
        await pilot.press("enter")
        await settle(browser, pilot)
        assert server.paths()[-1] == f"/2.3.0/launches/{first}/"
        assert f"launch:{first}" in browser.details
        assert browser.current.spacecraft


async def test_search(browser, server):
    async with browser.run_test() as pilot:
        await settle(browser, pilot)
        box = browser.query_one("#search", Input)
        assert not box.has_class("visible")
        await pilot.press("slash")
        assert box.has_class("visible")
        assert browser.focused is box

        await pilot.press(*"dragon", "enter")
        await settle(browser, pilot)
        searched = [r for r in server.requests if r.url.params.get("search") == "dragon"]
        assert {r.url.path for r in searched} == {"/2.3.0/launches/upcoming/", "/2.3.0/events/upcoming/"}
        assert browser.sub_title == "Next in space matching “dragon”"
        assert isinstance(browser.focused, DataTable)


async def test_status_shows_markup_literally(browser):
    async with browser.run_test() as pilot:
        await settle(browser, pilot)
        browser.set_status("Starlink [/] [bold]x")
        await pilot.pause()
        assert "Starlink [/] [bold]x" in str(browser.query_one("#status", Static).render())
