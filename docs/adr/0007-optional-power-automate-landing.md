# ADR 0007: Optional, client-supplied Power Automate landing

## Status
Accepted.

## Context
PPAC credit CSVs must reach the storage location the collector reads. Automation
is desirable but must not become a hard runtime dependency.

## Decision
Recommend a client-owned Power Automate flow (governed SharePoint drop-zone ->
validate/rename -> ADLS Gen2) as the preferred landing mechanism, but make it
**optional**. The collector ingests any valid `MCSMessages` CSV placed in the
landing location by any approved mechanism. Browser/UI scraping is out of scope.

## Consequences
- The Python project has no dependency on Power Automate.
- Clients can choose their own secure landing mechanism.
- The flow spec is documented for teams that want it.
