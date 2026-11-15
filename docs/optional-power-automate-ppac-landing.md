# OPTIONAL / CLIENT-SUPPLIED: PPAC Credit CSV Landing (Power Automate)

> **This component is OPTIONAL and CLIENT-OWNED.** The Python project does **not**
> depend on it at runtime or in tests. The collector ingests any valid
> `MCSMessages` CSV placed in the configured landing location by **any** approved
> mechanism (Power Automate, controlled manual upload, AzCopy, another
> integration). Browser/UI scraping is explicitly out of scope and unsupported.

## Purpose
Automate delivery of the Power Platform admin-center Copilot Studio consumption
exports (`MCSMessages`) into the storage location the collector reads, so credit
ingestion is hands-off and auditable.

## Prerequisites and permissions
- A governed SharePoint document library (the drop-zone) where an administrator
  places the exported CSVs.
- A Power Automate connection with **least-privilege** access to that library.
- A storage connection (Azure Blob / ADLS Gen2) scoped to the landing container
  with **Storage Blob Data Contributor** on that container only.

## Trigger and accepted inputs
- **Trigger:** "When a file is created" in the drop-zone library.
- **Accepted inputs:** native per-environment / per-agent / per-user
  `MCSMessages` CSV exports.

## Validation
- Extension is `.csv`; size > 0.
- Report type is resolvable (name contains `agent` / `user` / `environment`).
- Reject anything else to a `/rejected` folder with a reason.

## Deterministic rename
Rename to a stable convention before landing, for example:

```
MCSMessages_{agent|user|tenant}_{yyyyMM}_{timestamp}_{slug}.csv
```

This makes duplicate detection and report-type inference reliable.

## Land and dedupe
- Copy/write to the configured ADLS Gen2 / Blob landing container.
- If the deterministic target name already exists, skip (idempotent).
- Move the source file to a `/processed` folder on success.
- The collector additionally dedupes on `credit_key`, so a re-landed file is safe.

## Success / failure handling
- On success: log and move to `/processed`.
- On failure: retry per the connector policy; on final failure move to `/rejected`
  and raise an alert to the client-owned operations channel.

## Sample expressions (pseudo-config)
- Report type: if `toLower(triggerBody()?['Name'])` contains `agent` then `agent`,
  else `user` if it contains `user`, else `environment`.
- Target name: `concat('MCSMessages_', variables('reportType'), '_',
  formatDateTime(utcNow(),'yyyyMM'), '_', formatDateTime(utcNow(),'yyyyMMddHHmmss'),
  '_', variables('slug'), '.csv')`.

## Security guidance
- Use least-privilege connections; do not grant account-wide storage roles.
- Keep the drop-zone access-controlled; the files may contain usage detail.
- No secrets in the flow definition; use managed connections.

## Test checklist / acceptance criteria
- [ ] A valid agent report lands with the deterministic name in the container.
- [ ] A non-CSV or empty file is rejected with a reason.
- [ ] Re-submitting the same export does not create a duplicate (idempotent).
- [ ] The collector ingests the landed file and reconciliation passes.
- [ ] Removing the flow and dropping a file manually still ingests correctly
      (proves the collector has no hard dependency on the flow).
