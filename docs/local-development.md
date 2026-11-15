# Local Development

## Prerequisites
- Python 3.10+
- No cloud credentials are needed for fixture-based runs and tests.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"           # core + pytest
# optional extras:
pip install -e ".[dev,delta]"     # delta-rs writer (deltalake, polars, pyarrow)
pip install -e ".[config]"        # PyYAML for Config.from_yaml
```

If you prefer not to install the package, run with `PYTHONPATH=src`.

## Run the tests

```bash
pytest -q
```

## Fixture-based end-to-end

```bash
csu e2e --fixtures tests/fixtures --out .local/delta
# or
PYTHONPATH=src python -m csu.cli e2e --fixtures tests/fixtures --out .local/delta
```

Expected output: insert metrics for `dim_agent` (2), `fact_agent_session` (2),
`fact_agent_credit_consumption` (4), then `Reconciliation: PASS (7/7 checks)`.
A second identical run skips every row (idempotency).

## Fixtures

- `tests/fixtures/dataverse_e2e.json` - synthetic `bots`, `msdyn_botsessions`,
  `conversationtranscripts`.
- `tests/fixtures/ppac_agent_report.csv` - synthetic `MCSMessages` agent report.
- `tests/fixtures/transcripts/*` - golden transcript variants (normal, unknown
  activity, malformed).

All fixtures use synthetic placeholders only.

## Connectivity check (live)

`csu check` explains how to validate a live Dataverse connection. A real read
requires a configured service principal and the official client; see
`docs/dataverse-source.md`.
