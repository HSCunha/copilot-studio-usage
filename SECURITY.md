# Security Policy

## Secrets and credentials

- **No secrets are stored in this repository.** Configuration samples contain
  placeholders only (`<tenant-id>`, `<client-id>`, `<storage-account>`, etc.).
- Credentials are provided at runtime via environment variables or a secret
  store (e.g., Azure Key Vault) and consumed through a managed identity or a
  service principal. See `docs/security.md`.
- `local.settings.json`, `.local/`, key material (`*.pem`, `*.key`, `*.pfx`) and
  `*.jsonl` runtime output are git-ignored and must never be committed.

## Least privilege

- The Dataverse service principal is added as an **Application User** with read
  access limited to `bot`, `msdyn_botsession`, and `conversationtranscript`
  (plus the Bot Transcript Viewer-equivalent role). See `docs/dataverse-source.md`.
- Storage access uses managed identity / `azure-identity`-compatible credentials;
  account keys are never used.

## Sensitive usage data

- Transcript content can contain end-user text. Bronze raw payloads should be
  access-controlled and subject to the same retention policy as the source.
- Logging uses the standard library only and must not log secrets or full
  transcript bodies.

## Reporting a vulnerability

Report suspected vulnerabilities to the repository owner assigned by the
receiving team (see `docs/developer-handover.md`). Do not open a public issue
containing exploit details or sensitive data.
