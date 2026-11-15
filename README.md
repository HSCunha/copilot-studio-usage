# Copilot Studio Usage Collector

A minimal, production-oriented collector that extracts **Microsoft Copilot Studio
agent usage** and consolidates it into **Databricks Delta** tables.

It deliberately keeps **two usage grains separate**:

| Lane | Grain | Source | Automation |
|------|-------|--------|------------|
| **A - Engagement** | per session / conversation | Dataverse (`bot`, `msdyn_botsession`, `conversationtranscript`) | App-only service principal, fully unattended |
| **B - Credits** | per agent x feature x window | Power Platform admin-center `MCSMessages` CSV exports | File landed into storage (client-supplied mechanism) |

The two lanes are normalized through one deterministic hashing layer and written
to Delta with an idempotent MERGE. The web/front end is intentionally peripheral
(status/configuration only); this repository is the backend collector.

> **Scope guardrails.** No Application Insights, no telemetry/observability SDK,
> no IaC/Bicep, no CI/CD, and no unrelated Copilot products. Runtime telemetry is
> handled by a separate system and is out of scope here.

## Architecture at a glance

```
Dataverse  --app-only-->  sources/dataverse_client.py --> agents.py / sessions.py --,
                                                                                     +--> hashing --> DeltaWriter --> Delta (ADLS) --> Unity Catalog
PPAC CSV   --file drop-->  sources/credits_csv.py ---------------------------------'
```

- `dim_agent` - small dimension used only to label usage facts.
- `fact_agent_session` - engagement grain (keyed by `session_key`).
- `fact_agent_credit_consumption` - credit grain (keyed by `credit_key`).
- `ingestion_run` - audit record per run (idempotency + reconciliation).

See [`docs/architecture.md`](docs/architecture.md) for the full picture.

## Key design decisions

The major decisions are captured as ADRs in [`docs/adr/`](docs/adr/):

1. Function-direct Dataverse reads using the **official Microsoft Dataverse Python
   client** behind a `DataverseReader` abstraction (ADR 0001).
2. Two usage grains kept separate; never force-joined (ADR 0002).
3. PPAC `MCSMessages` CSV exports are the credit source (ADR 0003).
4. The user-level credit API is **disabled** in the production path (ADR 0004).
5. All transcript JSON parsing is isolated in `sessions.py` with golden fixtures (ADR 0005).
6. delta-rs idempotent MERGE keyed on business key + `row_hash` (ADR 0006).
7. PPAC landing via Power Automate is **OPTIONAL / CLIENT-SUPPLIED** (ADR 0007).

## Non-goals

- A full agent / model / tool inventory (only a thin agent dimension is kept).
- Runtime tracing/telemetry (handled by a separate SDK).
- Infrastructure provisioning, deployment pipelines, or hosting setup.

## Repository layout

```
src/csu/            # collector package
  sources/          # dataverse_client, sessions (parser boundary), agents, credits_csv, credits_api (disabled)
  sink/             # delta_writer (LocalEngine + DeltaRsEngine), recon
  state/            # watermarks, runlog
backend/            # Azure Functions host scaffold (context only; not imported by tests)
config/             # sample configuration (placeholders only)
tests/              # unit + golden fixtures + end-to-end
docs/               # full documentation set + ADRs
```

## Prerequisites

- Python **3.10+**
- For production Delta writes: the `delta` extra (`deltalake`, `polars`, `pyarrow`)
- For live Dataverse reads: the official `PowerPlatform-Dataverse-Client` and an
  `azure-identity` credential (service principal added as an Application User)

## Install (local development)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"            # core + pytest
pip install -e ".[dev,delta]"     # add delta-rs for the production writer
```

## Quick start - fixture-based end-to-end (no cloud, no credentials)

```bash
csu e2e --fixtures tests/fixtures --out .local/delta
# or: PYTHONPATH=src python -m csu.cli e2e --fixtures tests/fixtures --out .local/delta
```

Expected: three silver tables plus `ingestion_run` are written to `.local/delta`,
and reconciliation prints `PASS (7/7 checks)`. Re-running the same command is a
**no-op** (every row skipped) - this is the idempotency guarantee.

## Testing

```bash
pytest -q
```

Covers deterministic hashing, the transcript parser boundary (normal / missing /
malformed / unknown-activity), credit CSV parsing, the full MERGE decision matrix,
reconciliation, retries, and the end-to-end run. All offline. See
[`docs/testing.md`](docs/testing.md).

## Delta writer & reconciliation

The MERGE decision (insert / update / skip) is pure Python and fully unit-tested;
the physical write is delegated to a swappable engine (`LocalEngine` for offline
tests, `DeltaRsEngine` for ADLS Gen2). Matched rows update only when `row_hash`
changes. See [`docs/delta-writer.md`](docs/delta-writer.md) and
[`docs/reconciliation.md`](docs/reconciliation.md).

## PPAC credit landing - OPTIONAL / CLIENT-SUPPLIED

There is no unattended API for per-agent credits, so the credit CSV must be
*landed* into the configured storage location. The recommended mechanism is a
client-owned Power Automate flow (governed SharePoint drop-zone -> validate/rename
-> ADLS Gen2). **It is optional and is not a runtime dependency** - the collector
ingests any valid `MCSMessages` CSV placed in the landing location by any approved
mechanism. See [`docs/optional-power-automate-ppac-landing.md`](docs/optional-power-automate-ppac-landing.md).

## Databricks / Unity Catalog handoff

Delta files written to ADLS Gen2 are surfaced in Databricks as Unity Catalog
external tables. Table names, paths, schemas and partitioning guidance are in
[`docs/databricks-handoff.md`](docs/databricks-handoff.md).

## Documentation index

See [`docs/index.md`](docs/index.md) for the complete set, including
configuration, local development, operations, security, troubleshooting, the data
model, source references, and the developer-handover checklist.

## Security & ownership

Secrets are never stored in the repository. Credentials are supplied at runtime
via environment variables / a secret store and consumed through managed identity
or a service principal. See [`SECURITY.md`](SECURITY.md) and
[`docs/security.md`](docs/security.md). Ownership and support channels are to be
assigned by the receiving team (see [`docs/developer-handover.md`](docs/developer-handover.md)).

## License

[MIT](LICENSE).
