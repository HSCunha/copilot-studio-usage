# Architecture

## System context

The collector turns Copilot Studio agent usage into queryable Databricks Delta
tables. It is a backend component; any web/front end is peripheral and limited to
status and configuration.

Two independent **lanes** feed two different **grains**:

- **Lane A - Engagement usage (Dataverse, app-only).** Reads `bot`,
  `msdyn_botsession`, and `conversationtranscript` with a service principal and
  normalizes to per-session facts.
- **Lane B - Credit usage (PPAC CSV).** Ingests `MCSMessages` consumption CSV
  exports that are landed into storage, normalized to per-agent x feature x window
  credit facts.

The grains answer different questions ("how is the agent used?" vs. "what did it
cost?") and are **never force-joined** (see ADR 0002).

## Module flow

```
            Lane A (app-only)                         Lane B (file drop)
 Dataverse ------------------.                 PPAC CSV --------------.
 bot / msdyn_botsession /    |                 MCSMessages exports    |
 conversationtranscript      v                                        v
         sources/dataverse_client.py                     sources/credits_csv.py
                 |                                                |
     sources/agents.py  sources/sessions.py                      |
     (dim_agent)        (fact_agent_session)                      |
                 \__________________  ____________________________/
                                    \/
                          hashing (deterministic keys + row_hash)
                                    |
                           sink/delta_writer.py
                 LocalEngine (tests) | DeltaRsEngine (ADLS, delta-rs)
                                    |
                 dim_agent | fact_agent_session | fact_agent_credit_consumption | ingestion_run
                                    |
                          Databricks / Unity Catalog (external tables)
```

`sink/recon.py` validates each run; `state/watermarks.py` and `state/runlog.py`
provide incremental watermarks and an audit record.

## Boundaries

- **Parser boundary:** all transcript JSON parsing is confined to `sessions.py`
  (ADR 0005). Schema drift is a one-file change protected by golden fixtures.
- **Storage/auth boundary:** credential/storage options are built in `config.py`
  (`storage_options`) and never embedded in business logic.
- **Engine boundary:** the physical Delta write is behind an engine interface, so
  the merge *decision* is testable without any cloud dependency.

## Key decisions (see `adr/`)

1. Official Dataverse Python client behind a `DataverseReader` Protocol.
2. Two usage grains kept separate.
3. PPAC CSV as the credit source (no unattended per-agent API).
4. User-level credit API disabled in the production path.
5. Transcript parser boundary + golden tests.
6. delta-rs idempotent MERGE on business key + `row_hash`.
7. Optional, client-supplied Power Automate landing.

## Non-goals

- Full agent/model/tool inventory, runtime telemetry/observability, IaC/CI/CD,
  and unrelated Copilot products are explicitly out of scope.
