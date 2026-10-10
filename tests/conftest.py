import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

DATA = Path(__file__).parent / "data"


@pytest.fixture
def load() -> Callable[[str], Any]:
    return lambda name: json.loads((DATA / name).read_text())


@pytest.fixture
def detailed_launch(load: Callable[[str], Any]) -> dict[str, Any]:
    return load("launch_crewed_detailed.json")["results"][0]
