"""On-disk JSON cache for API responses and the last listing shown."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


class Cache:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, key: str) -> Path:
        return self.root / "responses" / f"{hashlib.sha256(key.encode()).hexdigest()[:32]}.json"

    def get(self, key: str) -> tuple[float, Any] | None:
        """Return ``(age_seconds, data)`` for a cached response, however old it is."""
        try:
            entry = json.loads(self._path(key).read_text())
        except (OSError, ValueError):
            return None
        return time.time() - entry["fetched_at"], entry["data"]

    def put(self, key: str, data: Any) -> None:
        self._write(self._path(key), {"fetched_at": time.time(), "data": data})

    def load_listing(self) -> list[dict[str, str]]:
        try:
            return json.loads((self.root / "last_listing.json").read_text())  # type: ignore[no-any-return]
        except (OSError, ValueError):
            return []

    def save_listing(self, refs: list[dict[str, str]]) -> None:
        self._write(self.root / "last_listing.json", refs)

    @staticmethod
    def _write(path: Path, payload: Any) -> None:
        # `watch` and `browse` refresh in the background while another invocation may
        # be reading, so writes go through a rename to never expose a partial file.
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        os.replace(tmp, path)
