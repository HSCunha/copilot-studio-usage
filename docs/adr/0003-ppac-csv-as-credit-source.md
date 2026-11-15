# ADR 0003: PPAC MCSMessages CSV as the credit source

## Status
Accepted.

## Context
There is no reliable unattended API for per-agent Copilot credits. The robust
source is the Power Platform admin-center consumption export (`MCSMessages`).

## Decision
Ingest the `MCSMessages` CSV exports (environment / agent / user) that are landed
into storage. Parsing is alias-tolerant and comma-safe; report type is detected
from the filename. Per-agent/per-user reports are window totals.

## Consequences
- Credit ingestion depends on a file landing, not an API.
- Snapshot each window into Delta so history survives short retention.
- The landing mechanism is optional/client-supplied (ADR 0007).
