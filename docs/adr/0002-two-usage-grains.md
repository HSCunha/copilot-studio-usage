# ADR 0002: Keep two usage grains separate

## Status
Accepted.

## Context
Engagement usage (sessions) and credit usage (PPAC) answer different questions and
are produced at different grains and identifiers (sessions by `botid`, credits by
agent **name**). Billing totals can legitimately exceed transcript-native cost.

## Decision
Model two separate fact tables - `fact_agent_session` and
`fact_agent_credit_consumption` - and **never force-join** them. A small
`dim_agent` exists only to label facts.

## Consequences
- Correct, honest reporting; no fabricated joins.
- Reconciliation compares each grain to its own source.
- Cross-grain analysis (name+environment) is explicitly approximate.
