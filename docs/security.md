# Security

## Principles

- **No secrets in the repository.** Samples use placeholders only.
- **Least privilege** for every identity.
- **Managed identity preferred** over stored secrets.

## Identity and permissions

- **Dataverse (Lane A):** a service principal added as an **Application User** in
  each environment, with read limited to `bot`, `msdyn_botsession`, and
  `conversationtranscript` (plus the Bot Transcript Viewer-equivalent role for
  transcripts). One app registration can span environments; the Application User
  must exist per environment.
- **Storage / Delta:** managed identity or an `azure-identity` credential with
  `WRITE FILES` on the external location. **Account keys are never used.**

## Secret handling

- Secrets come from environment variables or a secret store (e.g., Azure Key
  Vault) at runtime. `Config.storage_options()` reads `AZURE_CLIENT_SECRET` /
  `IDENTITY_ENDPOINT` from the environment and never persists them.
- `.gitignore` excludes `local.settings.json`, `.local/`, `*.jsonl`, and key
  material (`*.pem`, `*.key`, `*.pfx`).

## Sensitive data

- Transcript content may contain end-user text. Treat bronze raw payloads as
  sensitive; apply the same access control and retention as the source.
- Logging uses the standard library only and must not emit secrets or full
  transcript bodies.

## The disabled credit API

The user-level credit API is disabled in the production path (ADR 0004). Do not
enable it without confirmed, stable app-only support and a security review.
