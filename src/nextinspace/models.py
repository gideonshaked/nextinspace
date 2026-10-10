"""Launch Library 2 records parsed into immutable dataclasses.

LL2 documents almost nothing about which fields may be null, so every lookup into
a payload tolerates a missing or null value. This module is the only place that
happens: everything downstream works with the typed records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Literal


@dataclass(frozen=True)
class Status:
    abbrev: str
    name: str
    description: str | None


@dataclass(frozen=True)
class Webcast:
    title: str | None
    url: str
    publisher: str | None
    type: str | None
    live: bool


@dataclass(frozen=True)
class Agency:
    name: str
    abbrev: str | None


@dataclass(frozen=True)
class Rocket:
    name: str
    full_name: str
    family: str | None
    # The fields below are only populated by detailed responses.
    description: str | None = None
    length_m: float | None = None
    diameter_m: float | None = None
    launch_mass_t: float | None = None
    thrust_kn: float | None = None
    leo_capacity_kg: float | None = None
    gto_capacity_kg: float | None = None
    reusable: bool | None = None
    maiden_flight: date | None = None
    successful_launches: int | None = None
    failed_launches: int | None = None
    consecutive_successes: int | None = None
    wiki_url: str | None = None


@dataclass(frozen=True)
class Booster:
    serial: str | None
    flight_number: int | None
    reused: bool | None
    landing_attempt: bool | None
    landing_success: bool | None
    landing_location: str | None
    landing_description: str | None


@dataclass(frozen=True)
class CrewMember:
    name: str
    role: str | None
    agency: str | None


@dataclass(frozen=True)
class Spacecraft:
    name: str
    serial: str | None
    destination: str | None
    crew: tuple[CrewMember, ...]


@dataclass(frozen=True)
class Pad:
    name: str
    location: str | None
    country_code: str | None
    latitude: float | None
    longitude: float | None
    map_url: str | None


@dataclass(frozen=True)
class Mission:
    name: str
    type: str | None
    description: str | None
    orbit: str | None
    orbit_abbrev: str | None
    agencies: tuple[str, ...]


@dataclass(frozen=True)
class Launch:
    id: str
    slug: str | None
    name: str
    status: Status
    net: datetime | None
    precision: str | None
    window_start: datetime | None
    window_end: datetime | None
    provider: Agency | None
    rocket: Rocket | None
    mission: Mission | None
    pad: Pad | None
    probability: int | None
    weather_concerns: str | None
    failreason: str | None
    webcast_live: bool
    image_url: str | None
    last_updated: datetime | None
    provider_launches_this_year: int | None
    orbital_launches_this_year: int | None
    # The fields below are only populated by detailed responses.
    webcasts: tuple[Webcast, ...] = ()
    info_urls: tuple[str, ...] = ()
    boosters: tuple[Booster, ...] = ()
    spacecraft: tuple[Spacecraft, ...] = ()
    kind: Literal["launch"] = "launch"

    @property
    def location(self) -> str | None:
        if self.pad is None:
            return None
        return ", ".join(p for p in (self.pad.name, self.pad.location) if p)

    @property
    def description(self) -> str | None:
        return self.mission.description if self.mission else None


@dataclass(frozen=True)
class Event:
    id: str
    slug: str | None
    name: str
    type: str | None
    net: datetime | None
    precision: str | None
    location: str | None
    description: str | None
    webcast_live: bool
    image_url: str | None
    last_updated: datetime | None
    webcasts: tuple[Webcast, ...] = ()
    info_urls: tuple[str, ...] = ()
    kind: Literal["event"] = "event"


Item = Launch | Event


def to_dict(item: Item) -> dict[str, Any]:
    """JSON-ready dict of an item, with datetimes as ISO 8601 strings in UTC."""
    return _jsonable(asdict(item))  # type: ignore[no-any-return]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, date):
        return value.isoformat()
    return value


# ---- Parsing ----


def _get(d: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(key)
    return d


def _datetime(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s) if s else None


def _date(s: str | None) -> date | None:
    return date.fromisoformat(s) if s else None


def _webcasts(urls: list[dict[str, Any]] | None) -> tuple[Webcast, ...]:
    # LL2's "priority" only orders streams within a launch and usually puts a fan
    # re-stream first. The type id ranks them: 1 official, 2 official re-stream,
    # 3 unofficial, 4 unofficial re-stream, higher ids are recaps and other video.
    ordered = sorted(
        (v for v in urls or [] if v.get("url")),
        key=lambda v: (_get(v, "type", "id") or 99, v.get("priority") or 0),
    )
    return tuple(
        Webcast(
            title=v.get("title"),
            url=v["url"],
            publisher=v.get("publisher"),
            type=_get(v, "type", "name"),
            live=bool(v.get("live")),
        )
        for v in ordered
    )


def _info_urls(urls: list[dict[str, Any]] | None) -> tuple[str, ...]:
    return tuple(u["url"] for u in urls or [] if u.get("url"))


def _rocket(config: dict[str, Any] | None) -> Rocket | None:
    if not config:
        return None
    families = config.get("families") or []
    return Rocket(
        name=config["name"],
        full_name=config.get("full_name") or config["name"],
        family=families[0]["name"] if families else None,
        description=config.get("description") or None,
        length_m=config.get("length"),
        diameter_m=config.get("diameter"),
        launch_mass_t=config.get("launch_mass"),
        thrust_kn=config.get("to_thrust"),
        leo_capacity_kg=config.get("leo_capacity"),
        gto_capacity_kg=config.get("gto_capacity"),
        reusable=config.get("reusable"),
        maiden_flight=_date(config.get("maiden_flight")),
        successful_launches=config.get("successful_launches"),
        failed_launches=config.get("failed_launches"),
        consecutive_successes=config.get("consecutive_successful_launches"),
        wiki_url=config.get("wiki_url") or None,
    )


def _booster(stage: dict[str, Any]) -> Booster:
    landing = stage.get("landing") or {}
    location = landing.get("landing_location") or {}
    serial = _get(stage, "launcher", "serial_number")
    return Booster(
        serial=None if _get(stage, "launcher", "is_placeholder") else serial,
        flight_number=stage.get("launcher_flight_number"),
        reused=stage.get("reused"),
        landing_attempt=landing.get("attempt"),
        landing_success=landing.get("success"),
        landing_location=location.get("abbrev") or location.get("name"),
        landing_description=landing.get("description") or None,
    )


def _spacecraft(stage: dict[str, Any]) -> Spacecraft:
    craft = stage.get("spacecraft") or {}
    crew = tuple(
        CrewMember(
            name=c["astronaut"]["name"],
            role=_get(c, "role", "role"),
            agency=_get(c, "astronaut", "agency", "abbrev") or _get(c, "astronaut", "agency", "name"),
        )
        for c in stage.get("launch_crew") or []
        if _get(c, "astronaut", "name")
    )
    return Spacecraft(
        name=_get(craft, "spacecraft_config", "name") or craft.get("name") or "Spacecraft",
        serial=None if craft.get("is_placeholder") else craft.get("serial_number"),
        destination=stage.get("destination"),
        crew=crew,
    )


def parse_launch(r: dict[str, Any]) -> Launch:
    lsp = r.get("launch_service_provider")
    mission = r.get("mission")
    pad = r.get("pad")
    rocket = r.get("rocket") or {}
    return Launch(
        id=r["id"],
        slug=r.get("slug"),
        name=r["name"],
        status=Status(
            abbrev=_get(r, "status", "abbrev") or "TBD",
            name=_get(r, "status", "name") or "To Be Determined",
            description=_get(r, "status", "description"),
        ),
        net=_datetime(r.get("net")),
        precision=_get(r, "net_precision", "abbrev"),
        window_start=_datetime(r.get("window_start")),
        window_end=_datetime(r.get("window_end")),
        provider=Agency(name=lsp["name"], abbrev=lsp.get("abbrev")) if lsp else None,
        rocket=_rocket(rocket.get("configuration")),
        mission=(
            Mission(
                name=mission["name"],
                type=mission.get("type"),
                description=mission.get("description") or None,
                orbit=_get(mission, "orbit", "name"),
                orbit_abbrev=_get(mission, "orbit", "abbrev"),
                agencies=tuple(a["name"] for a in mission.get("agencies") or []),
            )
            if mission
            else None
        ),
        pad=(
            Pad(
                name=pad["name"],
                location=_get(pad, "location", "name"),
                country_code=_get(pad, "country", "alpha_2_code") or _get(pad, "location", "country", "alpha_2_code"),
                latitude=pad.get("latitude"),
                longitude=pad.get("longitude"),
                map_url=pad.get("map_url"),
            )
            if pad
            else None
        ),
        probability=r.get("probability"),
        weather_concerns=r.get("weather_concerns") or None,
        failreason=r.get("failreason") or None,
        webcast_live=bool(r.get("webcast_live")),
        image_url=_get(r, "image", "image_url"),
        last_updated=_datetime(r.get("last_updated")),
        provider_launches_this_year=r.get("agency_launch_attempt_count_year"),
        orbital_launches_this_year=r.get("orbital_launch_attempt_count_year"),
        webcasts=_webcasts(r.get("vid_urls")),
        info_urls=_info_urls(r.get("info_urls")),
        boosters=tuple(_booster(s) for s in rocket.get("launcher_stage") or []),
        spacecraft=tuple(_spacecraft(s) for s in rocket.get("spacecraft_stage") or []),
    )


def parse_event(r: dict[str, Any]) -> Event:
    return Event(
        id=str(r["id"]),
        slug=r.get("slug"),
        name=r["name"],
        type=_get(r, "type", "name"),
        net=_datetime(r.get("date")),
        precision=_get(r, "date_precision", "abbrev"),
        location=r.get("location") or None,
        description=r.get("description") or None,
        webcast_live=bool(r.get("webcast_live")),
        image_url=_get(r, "image", "image_url"),
        last_updated=_datetime(r.get("last_updated")),
        webcasts=_webcasts(r.get("vid_urls")),
        info_urls=_info_urls(r.get("info_urls")),
    )
