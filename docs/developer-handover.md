# Developer Handover

## What this is
A minimal, validated collector for Copilot Studio agent usage into Databricks
Delta. Phases 1-3 are implemented and tested offline.

## What is implemented
- Two-lane collection (Dataverse engagement + PPAC credit CSV).
- Deterministic normalization and hashing.
- Idempotent Delta writer (`LocalEngine` for tests, `DeltaRsEngine` for ADLS).
- Reconciliation with explicit, testable checks.
- CLI `e2e` and a full offline test suite.
- Complete documentation and ADRs.

## What remains (receiving team)
1. **Live Dataverse read:** confirm the official client import path for the
   pinned version; run a real app-only read in a dev environment.
2. **Live Delta/ADLS write:** install the `delta` extra; run `DeltaRsEngine`
   against ADLS Gen2; register Unity Catalog external tables.
3. **Scheduling (Phase 4/5):** wire the Timer/Blob triggers in `backend/` with
   watermarks and per-environment error isolation.
4. **Optional PPAC landing flow:** implement the client-owned Power Automate flow
   if desired (it is optional and not required by the code).

## Known limitations
- Credit data has no unattended API (CSV landing is the backbone).
- Credits identify the agent by name; sessions by `botid` (keep grains separate).
- The official Dataverse Python client is a young 1.x line - pin it; the
  `DataverseReader` Protocol allows falling back to the Web API reader.
- Source retention is short; Delta is the durable system of record.

## First tasks checklist
- [ ] Create venv, `pip install -e ".[dev]"`, run `pytest -q` (expect all pass).
- [ ] Run `csu e2e` twice; confirm `PASS (7/7)` and idempotent second run.
- [ ] Register the app, add the Application User per environment, grant read.
- [ ] Confirm the official client import path; do a live `bots` read.
- [ ] Stand up ADLS + Unity Catalog; do a live `DeltaRsEngine` write.
- [ ] Decide and (optionally) implement the PPAC landing mechanism.
- [ ] Assign code ownership and a security contact.

## Ownership
Assign a repository owner, a reviewer group, and a security contact. Record them
here and in `SECURITY.md` after handover.
