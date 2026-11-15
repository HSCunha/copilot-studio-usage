# ADR 0006: delta-rs idempotent MERGE on business key + row_hash

## Status
Accepted.

## Context
We need Spark-free, idempotent writes into Delta on ADLS Gen2, with explicit,
testable merge behavior.

## Decision
Separate the **decision** (`plan_upsert`, pure Python) from the **write** (engine).
`DeltaRsEngine` uses delta-rs `write_deltalake` to create and `DeltaTable.merge`
to upsert, updating a matched row only when `row_hash` differs. `LocalEngine`
mirrors the decision for offline tests.

## Consequences
- Re-runs are no-ops; retries are safe.
- Merge logic is fully unit-tested without cloud access.
- Storage/auth is isolated in `Config.storage_options()` (no account keys).
