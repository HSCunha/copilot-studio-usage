# Dataverse Source (Lane A - engagement usage)

## Client choice

Lane A uses **function-direct Dataverse reads** via the official Microsoft
**PowerPlatform-Dataverse-Client** Python package, wrapped behind the
`DataverseReader` Protocol (`src/csu/sources/dataverse_client.py`). The abstraction
provides three implementations:

- `OfficialSdkDataverseReader` - the official client; accepts any `azure-identity`
  credential (use `ClientSecretCredential` or `CertificateCredential` for
  unattended app-only access); pages results and retries transient errors.
- `WebApiDataverseReader` - documented fallback using an `azure-identity`/MSAL
  token against the Dataverse Web API (OData) with standard-library HTTP only.
- `FakeDataverseReader` - in-memory reader for offline tests.

> **Live-integration note.** The exact import path / builder surface of the
> official client must be confirmed against the pinned package version. The reader
> imports it lazily, so offline tests never require it. If a release regresses,
> switch to `WebApiDataverseReader` without touching the collector.

## Authentication (app-only)

1. Register an Entra application (one registration can span environments).
2. In **each** environment, add the application as an **Application User**.
3. Grant read on the usage tables (a least-privilege custom role or the Bot
   Transcript Viewer-equivalent for transcripts).
4. Acquire a token with scope `https://<dataverse-org>.crm.dynamics.com/.default`
   using client credentials.

## Tables queried

| Entity set | Purpose | Key fields used |
|------------|---------|-----------------|
| `bots` | agent dimension | `botid`, `name`, `ismanaged`, `configuration` |
| `msdyn_botsessions` | session facts | `msdyn_botsessionid`, `_msdyn_botid_value`, `createdon`, `msdyn_outcome`, `msdyn_csat`, `msdyn_engaged` |
| `conversationtranscripts` | message/channel/user detail | `conversationtranscriptid`, `content`, link to session, `createdon` |

## Paging, retry, incremental

- **Paging:** the official client pages via its builder; the Web API fallback
  follows `@odata.nextLink`.
- **Retry:** `retry.py` backs off on transient errors (e.g., HTTP 429) honoring
  standard backoff; `sleep` is injectable for tests.
- **Incremental:** filter by `createdon gt <watermark>` (see
  `state/watermarks.py`) to pull only new sessions/transcripts.

## Limitations and coverage gaps

- Transcripts are commonly retained ~28 days at source; snapshot into Delta.
- Transcripts may not be written for developer or Dataverse-for-Teams
  environments, and can be disabled per environment.
- Content grounded in some knowledge sources may be redacted.
- Scope the collector to governed environments via `config/environments.*.yml`.
