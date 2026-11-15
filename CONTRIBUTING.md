# Contributing

Thank you for helping maintain the Copilot Studio Usage Collector. This document
describes how to work in the repository after handover.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Principles

- **Keep the scope minimal.** Usage collection only. Do not add telemetry SDKs,
  Application Insights, IaC, CI/CD, or unrelated product collectors.
- **Keep the two grains separate.** Session (engagement) and credit facts live in
  different tables and are never force-joined.
- **Parser changes are localized.** All `conversationtranscript.Content` parsing
  stays in `src/csu/sources/sessions.py` and must be covered by golden fixtures.
- **Determinism.** Business keys and `row_hash` must stay stable so Delta MERGE
  remains idempotent. Add a test whenever you touch hashing or keys.

## Pull request checklist

- [ ] `pytest -q` passes.
- [ ] New/changed parsing has a golden fixture and a test.
- [ ] No secrets, client names, or real identifiers added (see `SECURITY.md`).
- [ ] Docs updated if behavior or configuration changed.
- [ ] `CHANGELOG.md` updated for user-visible changes.

## Commit style

Use clear, imperative commit messages (e.g., "Add MCSMessages user-report alias").
Group related changes; keep unrelated refactors in separate commits.

## Adding a new source variant

1. Add a golden fixture under `tests/fixtures/`.
2. Extend the relevant parser (`sessions.py` or `credits_csv.py`).
3. Add unit tests for normal, missing, malformed, and duplicate cases.
4. Confirm reconciliation still passes in the end-to-end run.
