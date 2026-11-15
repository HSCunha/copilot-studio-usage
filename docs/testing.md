# Testing

## How to run

```bash
pytest -q
```

Tests are offline and require no cloud credentials. `conftest.py` puts `src/` on
the path.

## Taxonomy

| File | Focus |
|------|-------|
| `test_hashing.py` | deterministic keys and `row_hash` change detection |
| `test_sessions.py` | transcript parser boundary: normal, list/dict, missing, malformed (never raises), unknown activity, empty, normalize join |
| `test_agents.py` | `dim_agent` normalization and orchestration heuristic |
| `test_credits_csv.py` | alias + comma-safe parsing, report-type detection, key uniqueness, raw-vs-normalized total |
| `test_delta_writer.py` | MERGE matrix: insert / skip / update-on-hash / missing-key / empty / duplicate; LocalEngine rerun idempotency |
| `test_recon.py` | all-pass and deliberate-failure reconciliation |
| `test_retry.py` | transient retry and non-transient raise |
| `test_e2e.py` | full fixture run + idempotent second run |

## Golden fixtures

Transcript variants live in `tests/fixtures/transcripts/`. Because all transcript
parsing is isolated in `sessions.py` (ADR 0005), handling a new activity shape is
a one-file change plus a new golden fixture and test.

## Adding a test

1. Add a fixture (JSON/CSV) with synthetic data only.
2. Write the parser/normalizer change.
3. Cover normal, missing/optional, malformed, unknown, and duplicate cases.
4. Confirm the e2e reconciliation still passes.
