# Databricks / Unity Catalog Handoff

This is a **data contract**, not deployment guidance.

## Storage layout

The writer produces one Delta table per entity under `delta_base_uri`:

```
<delta_base_uri>/dim_agent
<delta_base_uri>/fact_agent_session
<delta_base_uri>/fact_agent_credit_consumption
<delta_base_uri>/ingestion_run
```

where `delta_base_uri` is typically
`abfss://usage@<storage-account>.dfs.core.windows.net/csu`.

## Unity Catalog external tables

Register an external location backed by a storage credential (access connector /
managed identity), then create external tables over the Delta paths:

```sql
CREATE EXTERNAL LOCATION IF NOT EXISTS csu_usage
  URL 'abfss://usage@<storage-account>.dfs.core.windows.net/csu'
  WITH (STORAGE CREDENTIAL <access_connector_credential>);

CREATE TABLE copilot_usage.silver.dim_agent
  USING DELTA LOCATION 'abfss://usage@<storage-account>.dfs.core.windows.net/csu/dim_agent';

CREATE TABLE copilot_usage.silver.fact_agent_session
  USING DELTA LOCATION 'abfss://usage@<storage-account>.dfs.core.windows.net/csu/fact_agent_session';

CREATE TABLE copilot_usage.silver.fact_agent_credit_consumption
  USING DELTA LOCATION 'abfss://usage@<storage-account>.dfs.core.windows.net/csu/fact_agent_credit_consumption';

CREATE TABLE copilot_usage.silver.ingestion_run
  USING DELTA LOCATION 'abfss://usage@<storage-account>.dfs.core.windows.net/csu/ingestion_run';
```

Grant the writing principal `WRITE FILES` on the external location; grant readers
`SELECT` on the tables.

## Keys and schemas

See `docs/data-model.md`. Keys: `dim_agent.agent_id`,
`fact_agent_session.session_key`, `fact_agent_credit_consumption.credit_key`,
`ingestion_run.run_id`.

## Partitioning

- Small tenants: **no partitioning** (partitioning hurts tiny tables).
- Large tenants: partition `fact_agent_session` by a derived `event_date` and
  credits by `usage_date` only past roughly 1 GB per table.

## Querying the two grains

Query sessions and credits independently. Billing totals can legitimately exceed
transcript-native cost, so reconcile but do not force-join (ADR 0002).
