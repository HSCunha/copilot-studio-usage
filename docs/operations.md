# Operations

No deployment/IaC content here - operational behavior only.

## Run lifecycle

1. A run starts (scheduled or manual). `state/runlog.py` creates an
   `ingestion_run` record (`run_id`, `started`).
2. Lane A reads Dataverse incrementally (by `createdon` watermark); Lane B
   ingests any new PPAC CSV in the landing location.
3. Records normalize and MERGE into Delta (idempotent).
4. `reconcile(...)` runs; the run is marked `succeeded`/`failed` with row counts.

## Watermarks

`state/watermarks.py` stores a per-environment, per-table watermark (JSON file or
an equivalent store). Lane A filters `createdon gt <watermark>` to pull only new
rows. Credit windows are full-reloaded within their window and upserted on
`credit_key`.

## Replay / reprocessing

- Bronze raw payloads (if enabled) let you re-derive silver without re-pulling.
- Re-running a batch is safe (idempotent MERGE). To reprocess a window, re-ingest
  the CSV or clear the watermark for that environment/table.

## Failure isolation

Process each environment independently so one failing environment does not abort
the whole run; record per-environment status in `ingestion_run`.

## Housekeeping

- Snapshot each run into Delta so history outlives short source retention.
- Periodically `OPTIMIZE`/`VACUUM` Delta tables from Databricks for large tenants
  (operational task on the Databricks side).
- Move processed PPAC CSVs to an archive/processed folder (see the optional flow).

## Operational checks

- Confirm `ingestion_run` has a recent `succeeded` row per environment.
- Confirm reconciliation passed (exit code 0 / `PASS`).
- Alert if a scheduled run is missing or a CSV window did not land.
