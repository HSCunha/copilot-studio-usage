# Documentation Index

Start here. The documents below describe the Copilot Studio Usage Collector in
full - architecture, data model, sources, the Delta writer, operations, and the
developer-handover checklist.

## Core
- [architecture.md](architecture.md) - system context, two lanes / two grains, module flow, boundaries, non-goals.
- [data-model.md](data-model.md) - bronze/silver tables, grains, keys, row hashes, retention implications.
- [configuration.md](configuration.md) - configuration fields, environment variables, identity modes, secret handling.

## Sources
- [dataverse-source.md](dataverse-source.md) - official Python client, app-only auth, tables, paging/incremental, permissions, limitations.
- [ppac-credit-source.md](ppac-credit-source.md) - `MCSMessages` report types, field mapping, grain, retention/window semantics.
- [optional-power-automate-ppac-landing.md](optional-power-automate-ppac-landing.md) - OPTIONAL / CLIENT-SUPPLIED landing flow.

## Sink
- [delta-writer.md](delta-writer.md) - engines, MERGE semantics, idempotency, duplicate handling, storage/auth, bronze append.
- [reconciliation.md](reconciliation.md) - checks, failure behavior, machine- and human-readable outputs.
- [databricks-handoff.md](databricks-handoff.md) - Delta paths, Unity Catalog external tables, SQL examples, partitioning.

## Build & run
- [local-development.md](local-development.md) - setup, install, fixtures, CLI, tests, local e2e.
- [testing.md](testing.md) - test taxonomy, golden fixtures, how to add tests.
- [operations.md](operations.md) - run lifecycle, watermarks, ingestion_run, replay, failure isolation, housekeeping.
- [security.md](security.md) - least privilege, identity, secrets, logging hygiene.
- [troubleshooting.md](troubleshooting.md) - common failures and fixes.
- [developer-handover.md](developer-handover.md) - ownership checklist, status, first tasks, known limitations.

## Decisions
- [adr/](adr/) - Architecture Decision Records 0001-0007.
