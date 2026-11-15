# Configuration

Configuration is modeled in `src/csu/config.py`. A sample lives at
`config/environments.sample.yml`. **Secrets are never stored in configuration.**

## Fields

| Field | Meaning | Example |
|-------|---------|---------|
| `tenant_id` | Entra tenant | `<tenant-id>` |
| `client_id` | app registration (client) id | `<client-id>` |
| `identity_mode` | `managed_identity` / `service_principal` / `azure_cli` | `managed_identity` |
| `delta_base_uri` | base URI for Delta tables | `abfss://usage@<storage-account>.dfs.core.windows.net/csu` |
| `storage_account` | ADLS Gen2 account name | `<storage-account>` |
| `storage_container` | container for Delta output | `usage` |
| `landing_container` | container where PPAC CSVs land | `landing` |
| `page_size` | Dataverse OData page size | `5000` |
| `enable_user_level_credit_api` | **keep false** (ADR 0004) | `false` |
| `environments[]` | `environment_id` + `dataverse_url` allow-list | see sample |

## Environment variables (runtime secrets)

| Variable | Used by |
|----------|---------|
| `AZURE_CLIENT_SECRET` | service-principal credential (if not using managed identity) |
| `IDENTITY_ENDPOINT` / `MSI_ENDPOINT` | managed-identity discovery on the host |
| `LANDING_STORAGE` | backend blob-trigger connection reference |

## Identity modes

- **managed_identity (recommended):** no secret in app settings; delta-rs/object
  store discovers the MSI endpoint.
- **service_principal:** `client_id` + `tenant_id` from config, `client_secret`
  from the environment / a secret store.
- **azure_cli:** developer convenience for local runs only.

## Loading

`Config.from_yaml(path)` (requires the `config` extra for PyYAML) or construct
`Config(...)` directly. The offline e2e does not require configuration - it reads
fixtures.
