# Delta Writer

`src/csu/sink/delta_writer.py` performs an **idempotent upsert** into Delta.

## Design

- **Decision is pure Python.** `plan_upsert(existing, new_rows, key_field)`
  classifies rows into inserts / updates / skips, collapses duplicate keys
  (last-wins), and raises on a missing key. This is fully unit-tested offline.
- **Physical write is an engine.**
  - `LocalEngine(base_path)` - stores each table as newline-delimited JSON
    (`<table>.jsonl`); used for offline tests and the local e2e.
  - `DeltaRsEngine(base_uri, storage_options)` - production path using delta-rs
    (`deltalake`). Creates the table on first write, then runs a MERGE.
- `DeltaWriter(engine)` is a thin facade accepting dataclass records or dicts
  (`to_rows` normalizes them).

## MERGE semantics (idempotency)

For a target keyed on the business key:

```
MERGE source INTO target ON source.<key> = target.<key>
  WHEN MATCHED AND source.row_hash <> target.row_hash THEN UPDATE *
  WHEN NOT MATCHED THEN INSERT *
```

Because a matched row is updated **only** when `row_hash` differs, re-running an
identical batch is a no-op. The `DeltaRsEngine` expresses exactly this with
`when_matched_update_all(predicate="s.row_hash != t.row_hash")` and
`when_not_matched_insert_all()`.

## Metrics

Every upsert returns `{inserted, updated, skipped, duplicates_collapsed,
source_rows}`. These are surfaced by the CLI and asserted by tests.

## Safety guards

- Empty batch -> no-op.
- Missing key -> `ValueError` (fail fast).
- Duplicate source keys -> collapsed deterministically (counted).
- Session and credit facts are written to **separate** tables.

## Storage / auth configuration

`Config.storage_options()` builds delta-rs options for the selected identity
mode (`managed_identity`, `service_principal`, `azure_cli`). Secret values are
read from the environment at runtime (`AZURE_CLIENT_SECRET`, `IDENTITY_ENDPOINT`).
**No account keys are ever placed in code or returned.**

## Bronze (optional)

`DeltaWriter.append_bronze(table, rows)` appends raw payloads with load metadata
for replay/audit. Keep bronze append-only; the primary Phase 3 deliverable is the
reliable silver MERGE.
