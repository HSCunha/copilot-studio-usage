# Data Model

The model is intentionally small: two fact tables (one per grain), a thin agent
dimension, an audit table, and optional bronze raw tables for replay.

## Silver tables

### `dim_agent`
Thin dimension used only to label usage facts (not a full inventory).

| Field | Notes |
|-------|-------|
| `agent_id` (**key**) | Dataverse `botid` (GUID, globally unique) |
| `name` | agent display name |
| `environment_id` | environment scope |
| `orchestration` | heuristic hint (e.g., generative) |
| `is_managed` | managed solution flag |
| `row_hash` | change-detection hash |

### `fact_agent_session` - engagement grain
One row per session.

| Field | Notes |
|-------|-------|
| `session_key` (**key**) | `sha1(environment_id, session_id)` composite surrogate |
| `session_id` | `msdyn_botsessionid` |
| `agent_id` | `botid` of the agent |
| `environment_id` | environment scope |
| `start_time` | `createdon` |
| `channel` | from transcript (first message) |
| `user_id` | from transcript (first user-role message) |
| `message_count` | count of message activities |
| `engaged` | from `msdyn_botsession` (fallback: transcript SessionInfo) |
| `outcome`, `csat` | from `msdyn_botsession` (authoritative) |
| `parse_error` | set if transcript JSON was malformed; raw preserved in bronze |
| `row_hash` | change-detection hash |

### `fact_agent_credit_consumption` - credit grain
One row per agent x feature x window, from a PPAC `MCSMessages` export.

| Field | Notes |
|-------|-------|
| `credit_key` (**key**) | `sha1(environment_id, agent_name, report_type, usage_date, product_feature, channel, llm_model, knowledge_or_tool, user_id)` |
| `environment_id` | environment scope |
| `agent_name` | credits identify the agent by **name** (see limitation) |
| `report_type` | `agent` / `user` / `environment` (from filename) |
| `usage_date` | reporting date or window label |
| `product_feature` | billed feature (classic, generative, agent action, flow, tool) |
| `channel`, `llm_model`, `knowledge_or_tool`, `user_id` | optional dimensions when present |
| `billed_credits`, `non_billed_credits` | measures |
| `row_hash` | change-detection hash |

### `ingestion_run`
| Field | Notes |
|-------|-------|
| `run_id` (**key**) | UUID |
| `source`, `started`, `ended`, `rows`, `status`, `detail` | audit for idempotency & reconciliation |

## Bronze (optional, append-only)

`bronze_conversationtranscript`, `bronze_botsession`, `bronze_bot`,
`bronze_credit_ppac` preserve raw payloads with load metadata
(`_ingested_at`, `_run_id`, `_source`, `_env_id`). Bronze lets you re-derive
silver when parsing rules change, without re-pulling from the source.

## Keys, hashing and idempotency

- Keys are deterministic (`hashing.py`). `dim_agent` uses the GUID directly;
  sessions use a composite surrogate to avoid cross-environment collisions;
  credits are keyed at the credit grain.
- `row_hash` is a content hash over the business fields. Delta MERGE updates a
  matched row **only** when `row_hash` differs, which makes re-runs no-ops.

## Retention implications

Source retention is short (transcripts commonly ~28 days; PPAC per-agent/per-user
exports are window totals). Delta is therefore the durable system of record:
snapshot each run so history survives beyond the source window. See
`docs/dataverse-source.md` and `docs/ppac-credit-source.md`.

## Grain separation (important)

Credits are identified by agent **name**; sessions by **botid**. Billing totals
can legitimately exceed transcript-native cost. Keep the two facts separate;
reconcile but do not force-join (ADR 0002).
