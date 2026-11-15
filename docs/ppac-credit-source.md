# PPAC Credit Source (Lane B - credit usage)

## Why CSV, not an API

There is **no reliable unattended API** for per-agent Copilot credits. The robust
source is the Power Platform admin-center consumption export (`MCSMessages`),
downloaded by an administrator and **landed** into storage for ingestion
(ADR 0003). The user-level credit API remains disabled (ADR 0004).

## Report variants

The exporter produces up to three report types; the collector detects the type
from the filename (`detect_report_type`):

| Report type | Grain |
|-------------|-------|
| `environment` | per environment (and day where available) |
| `agent` | per agent (window total) |
| `user` | per user (window total) |

Per-agent and per-user reports are **window totals** (commonly a ~30-day window),
not a daily breakdown. Upsert on `credit_key` for the window rather than per day.

## Field mapping

`credits_csv.py` is alias-tolerant (headers vary slightly between variants) and
comma-safe for numbers:

| Logical | Example source headers |
|---------|------------------------|
| `agent_name` | `Agent_Name`, `Agent name`, `Agent` |
| `usage_date` | `Usage_Date`, `Date`, `Month` |
| `product_feature` | `Product / AI feature`, `Feature` |
| `channel` | `Channel` |
| `llm_model` | `LLM model`, `Model` |
| `knowledge_or_tool` | `Knowledge sources / Tool used`, `Tool used` |
| `user_id` | `User`, `User principal name` |
| `billed_credits` | `Billed_credit`, `Billed credits` |
| `non_billed_credits` | `Non_billed_credit`, `Non-billed credits` |

## Limitations

- Per-conversation or per-message credit allocation is **not** available.
- Token counts are not in the reports.
- Developer-environment usage may not be recorded at all.
- Because credits identify the agent by **name**, mapping to a `botid` is
  approximate; keep credit and session facts separate (ADR 0002).

## Landing

The ingestion contract (naming, dedupe, completeness) and the optional
client-supplied Power Automate flow are described in
[optional-power-automate-ppac-landing.md](optional-power-automate-ppac-landing.md).
The collector ingests any valid `MCSMessages` CSV placed in the landing location
by any approved mechanism.
