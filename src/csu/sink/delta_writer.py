"""Idempotent Delta writer (ADR 0006).

The MERGE *decision* (insert / update / skip) is pure Python (``plan_upsert``)
so it is fully testable offline and yields explicit metrics. The physical write
is delegated to a swappable engine:

  * ``LocalEngine``  - JSONL store for offline tests / local e2e (no cloud).
  * ``DeltaRsEngine`` - delta-rs (``deltalake``) MERGE to ADLS Gen2 for prod.

Two grains are written to separate tables and never force-joined.
"""
from __future__ import annotations
import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List


def to_rows(records: List[Any]) -> List[Dict[str, Any]]:
    out = []
    for r in records:
        out.append(asdict(r) if is_dataclass(r) else dict(r))
    return out


def plan_upsert(existing: Dict[str, Dict], new_rows: List[Dict], key_field: str) -> Dict[str, Any]:
    """Classify new rows against existing keyed rows. Raises on a missing key."""
    deduped: Dict[str, Dict] = {}
    duplicates = 0
    for r in new_rows:
        k = r.get(key_field)
        if k is None or k == "":
            raise ValueError(f"row missing required key field '{key_field}': {r}")
        if k in deduped:
            duplicates += 1
        deduped[k] = r  # last-wins

    inserts, updates, skips = [], [], []
    for k, r in deduped.items():
        if k not in existing:
            inserts.append(r)
        elif existing[k].get("row_hash") != r.get("row_hash"):
            updates.append(r)
        else:
            skips.append(r)
    return {"inserts": inserts, "updates": updates, "skips": skips,
            "duplicates_collapsed": duplicates}


class LocalEngine:
    """Offline engine storing each table as newline-delimited JSON."""

    def __init__(self, base_path: str):
        self.base = base_path

    def _path(self, table: str) -> str:
        return os.path.join(self.base, table + ".jsonl")

    def read(self, table: str) -> List[Dict]:
        path = self._path(table)
        rows: List[Dict] = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        rows.append(json.loads(line))
        return rows

    def overwrite(self, table: str, rows: List[Dict]) -> None:
        os.makedirs(self.base, exist_ok=True)
        with open(self._path(table), "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, sort_keys=True) + "\n")

    def upsert(self, table: str, rows: List[Dict], key_field: str) -> Dict[str, Any]:
        existing = {r[key_field]: r for r in self.read(table)}
        plan = plan_upsert(existing, rows, key_field)
        for r in plan["inserts"] + plan["updates"]:
            existing[r[key_field]] = r
        self.overwrite(table, list(existing.values()))
        return {"inserted": len(plan["inserts"]), "updated": len(plan["updates"]),
                "skipped": len(plan["skips"]),
                "duplicates_collapsed": plan["duplicates_collapsed"],
                "source_rows": len(rows)}


class DeltaRsEngine:
    """Production engine using delta-rs (``deltalake``). Imported lazily.

    Creates the table on first write, then performs an idempotent MERGE keyed on
    the business key, updating only when ``row_hash`` differs.
    """

    def __init__(self, base_uri: str, storage_options: Dict[str, str] | None = None):
        self.base_uri = base_uri.rstrip("/")
        self.storage_options = storage_options or {}

    def _uri(self, table: str) -> str:
        return f"{self.base_uri}/{table}"

    def upsert(self, table: str, rows: List[Dict], key_field: str) -> Dict[str, Any]:  # pragma: no cover
        if not rows:
            return {"inserted": 0, "updated": 0, "skipped": 0,
                    "duplicates_collapsed": 0, "source_rows": 0}
        # collapse duplicate keys deterministically before writing
        deduped: Dict[str, Dict] = {}
        duplicates = 0
        for r in rows:
            k = r.get(key_field)
            if k is None or k == "":
                raise ValueError(f"row missing required key field '{key_field}'")
            if k in deduped:
                duplicates += 1
            deduped[k] = r
        payload = list(deduped.values())

        import pyarrow as pa  # noqa: F401
        from deltalake import DeltaTable, write_deltalake
        from deltalake.exceptions import TableNotFoundError

        uri = self._uri(table)
        try:
            dt = DeltaTable(uri, storage_options=self.storage_options)
            exists = True
        except TableNotFoundError:
            exists = False

        if not exists:
            write_deltalake(uri, _arrow(payload), storage_options=self.storage_options, mode="overwrite")
            return {"inserted": len(payload), "updated": 0, "skipped": 0,
                    "duplicates_collapsed": duplicates, "source_rows": len(rows)}

        (dt.merge(source=_arrow(payload), predicate=f"s.{key_field} = t.{key_field}",
                  source_alias="s", target_alias="t")
           .when_matched_update_all(predicate="s.row_hash != t.row_hash")
           .when_not_matched_insert_all()
           .execute())
        return {"inserted": -1, "updated": -1, "skipped": -1,
                "duplicates_collapsed": duplicates, "source_rows": len(rows)}


def _arrow(rows: List[Dict]):  # pragma: no cover - only used by DeltaRsEngine
    import pyarrow as pa
    return pa.Table.from_pylist(rows)


class DeltaWriter:
    """Facade over an engine; accepts dataclass records or dicts."""

    def __init__(self, engine):
        self.engine = engine

    def upsert(self, table: str, records: List[Any], key_field: str) -> Dict[str, Any]:
        return self.engine.upsert(table, to_rows(records), key_field)

    def append_bronze(self, table: str, rows: List[Dict]) -> int:
        """Append-only bronze write (raw payloads). Supported by LocalEngine."""
        existing = self.engine.read(table) if hasattr(self.engine, "read") else []
        self.engine.overwrite(table, existing + rows)
        return len(rows)
