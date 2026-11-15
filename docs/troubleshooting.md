# Troubleshooting

## Dataverse authentication / permissions
- **401/403 on read:** the service principal is not an Application User in that
  environment, or lacks read on the usage tables. Add it per environment with the
  least-privilege role (see `docs/dataverse-source.md`).
- **Empty results:** confirm the environment is in the allow-list and that
  transcripts are enabled there (not a developer/Teams environment).

## Throttling
- **HTTP 429:** handled by `retry.py` with backoff. Persistent throttling means
  the page size or run frequency is too aggressive - lower `page_size`.

## Transcript parsing
- **`parse_error` set on sessions:** the transcript JSON was malformed; the raw
  payload is preserved in bronze. Add a golden fixture reproducing the shape and
  extend `sessions.py` (one-file change).
- **Unknown activity types:** recorded in the parser summary; extend handling in
  `sessions.py` if the new type carries usage signal.

## Credit CSV
- **Columns not mapping:** add the new header to `COLUMN_ALIASES` in
  `credits_csv.py`.
- **Wrong report type:** detection is filename-based; ensure the file name
  contains `agent` / `user` / `environment`.
- **Totals off:** check comma-formatted numbers are quoted in the CSV; `_num`
  strips commas.

## Delta MERGE
- **Duplicate rows:** should not happen (keys + MERGE). If seen with LocalEngine,
  verify the key field is populated; a missing key raises by design.
- **`TableNotFoundError` (delta-rs):** first write creates the table; ensure the
  storage credential has write access.

## ADLS auth
- **AuthorizationFailure:** verify managed identity / credential has `WRITE FILES`
  on the external location and `storage_options()` targets the right account.

## Reconciliation failures
- Read the failing check name (see `docs/reconciliation.md`) to localize whether
  the issue is extraction, normalization, parsing, or a modeling leak.
