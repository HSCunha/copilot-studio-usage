# Changelog

All notable changes to this project are documented here. The project follows a
release-by-release structure.

## [0.3.1] - Developer handover
### Added
- Professional `README.md` and a complete `docs/` set, including seven ADRs.
- Governance files: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  `.editorconfig`, `.gitignore`.
### Changed
- Repository made fully organization-neutral; all examples use synthetic
  placeholders (`ExampleTenant`, `ExampleEnvironment`, `example.com`,
  `<storage-account>`, `<dataverse-org>`, all-zero GUIDs).
### Preserved
- All Phase 1-3 functionality and tests (unchanged behavior).

## [0.3.0] - Phase 3: Delta writer
### Added
- `sink/delta_writer.py` with pure-Python `plan_upsert`, `LocalEngine`,
  and `DeltaRsEngine` (delta-rs idempotent MERGE).
- `sink/recon.py` reconciliation checks and summary.
- CLI `e2e` command and end-to-end + reconciliation tests.

## [0.2.0] - Phase 2: Normalization
### Added
- `sources/sessions.py` transcript parser boundary with golden fixtures.
- `sources/agents.py` and `sources/credits_csv.py`.

## [0.1.0] - Phase 1: Source access
### Added
- `sources/dataverse_client.py` (`DataverseReader` Protocol + official SDK,
  Web API fallback, in-memory fake), config, hashing, retry.
