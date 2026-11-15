# ADR 0001: Function-direct Dataverse reads via the official Python client

## Status
Accepted.

## Context
Lane A needs unattended, app-only reads of Copilot Studio engagement data from
Dataverse. We want first-party tooling and no hidden dependency on an unofficial
package.

## Decision
Use **function-direct** Dataverse reads via the official Microsoft
**PowerPlatform-Dataverse-Client** Python package, wrapped behind a
`DataverseReader` Protocol. Provide a Web API fallback (`azure-identity`/MSAL +
OData, standard-library HTTP) and an in-memory fake for tests. App-only uses a
`ClientSecretCredential` or `CertificateCredential`.

## Consequences
- First-party, supported client; paging and transient-retry available.
- The exact import path must be confirmed against the pinned version at live
  integration; the lazy import keeps offline tests independent.
- If a 1.x release regresses, switch to the Web API reader without touching the
  collector.
