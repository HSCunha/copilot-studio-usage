# ADR 0004: Disable the user-level credit API in the production path

## Status
Accepted.

## Context
A user-level consumption endpoint exists, but stable app-only/unattended support
is not confirmed and may change.

## Decision
Keep the user-level credit API **disabled** in the production path. `credits_api.py`
is an inert placeholder behind `Config.enable_user_level_credit_api` (default
`false`) and is never imported by the collector, CLI, or tests.

## Consequences
- No dependency on an unconfirmed endpoint.
- If stable app-only support is later proven, enable it behind the flag with a
  security review; the CSV lane remains the backbone.
