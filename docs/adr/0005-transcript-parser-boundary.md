# ADR 0005: Transcript parser boundary with golden fixtures

## Status
Accepted.

## Context
The `conversationtranscript.Content` JSON shape is undocumented and evolves.
Scattering parsing would make schema drift risky and hard to test.

## Decision
Confine **all** transcript parsing to `src/csu/sources/sessions.py`. Parsing is
defensive (unknown shapes recorded, malformed JSON captured as `parse_error` and
never raised) and protected by golden fixtures.

## Consequences
- Schema drift is a one-file change plus a fixture and test.
- Raw payloads are preserved in bronze for re-derivation.
