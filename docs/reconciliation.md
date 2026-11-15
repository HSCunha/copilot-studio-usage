# Reconciliation

`src/csu/sink/recon.py` validates each run and makes failures explicit and
testable (never silently logged).

## Checks

`reconcile(engine, sessions, credits, credit_csv_paths, source_session_count)`
returns a list of `Check(name, passed, expected, actual, detail)`:

1. `sessions_normalized_vs_source` - normalized session count == source count.
2. `credit_total_normalized_vs_raw` - normalized (billed+non-billed) == an
   **independent** sum read straight from the raw CSV.
3. `delta_billed_vs_norm` - billed sum in Delta == normalized billed sum.
4. `session_keys_unique` - no duplicate `session_key` in Delta.
5. `credit_keys_unique` - no duplicate `credit_key` in Delta.
6. `grains_separate` - no `credit_key` in session rows and no `session_key` in
   credit rows.
7. `delta_session_count_vs_norm` - Delta session row count == normalized count.

## Outputs

- **Machine-readable:** `Check.as_dict()` for each check.
- **Human-readable:** `summarize(checks)` prints `PASS/FAIL (n/m checks)` plus a
  per-check line.

## Failure behavior

The CLI `e2e` command exits non-zero when any check fails, so reconciliation can
gate a pipeline. Interpret a failure by its name: count mismatches point to
extraction/normalization gaps; `grains_separate` failing indicates a modeling
leak; total mismatches point to parsing/rounding issues.
