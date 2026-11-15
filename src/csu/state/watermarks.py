"""Per-environment incremental watermark persisted as a small JSON file."""
from __future__ import annotations
import json
import os
from typing import Optional


class WatermarkStore:
    def __init__(self, path: str):
        self.path = path
        self._data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)

    def get(self, environment_id: str, table: str) -> Optional[str]:
        return self._data.get(environment_id, {}).get(table)

    def set(self, environment_id: str, table: str, value: str) -> None:
        self._data.setdefault(environment_id, {})[table] = value
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, sort_keys=True)
