"""Dataverse read access behind a narrow Protocol.

Primary implementation uses the official Microsoft **PowerPlatform-Dataverse-Client**
Python package (app-only via an ``azure-identity`` credential). A Web API
fallback and an in-memory fake are provided so the collector depends only on
the ``DataverseReader`` interface.

NOTE: the exact import path / builder surface of the official client must be
confirmed against the pinned package version during live integration; it is
imported lazily so offline tests never require it.
"""
from __future__ import annotations
from typing import Protocol, List, Dict, Any, Optional, runtime_checkable


@runtime_checkable
class DataverseReader(Protocol):
    def query(self, table: str, select: Optional[List[str]] = None,
              filter: Optional[str] = None, top: Optional[int] = None) -> List[Dict[str, Any]]:
        ...


class FakeDataverseReader:
    """Offline reader backed by an in-memory dict of {entity_set: [rows]}."""

    def __init__(self, tables: Dict[str, List[dict]]):
        self._tables = tables

    def query(self, table, select=None, filter=None, top=None):
        rows = list(self._tables.get(table, []))
        return rows[:top] if top else rows


def _import_official_client():
    attempts = [
        ("microsoft.powerplatform.dataverse.client", "DataverseClient"),
        ("powerplatform_dataverse_client", "DataverseClient"),
        ("dataverse_client", "DataverseClient"),
    ]
    errors = []
    for mod, attr in attempts:
        try:
            m = __import__(mod, fromlist=[attr])
            return getattr(m, attr)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{mod}: {exc}")
    raise ImportError(
        "Official Dataverse client not importable. Confirm the installed "
        "'PowerPlatform-Dataverse-Client' import path. Tried -> " + "; ".join(errors)
    )


class OfficialSdkDataverseReader:
    """Uses the official Microsoft Dataverse Python client (lazy import)."""

    def __init__(self, base_url: str, credential: Any, page_size: int = 5000):
        self._base_url = base_url
        self._credential = credential
        self._page_size = page_size
        self._client = None

    def _ensure(self):
        if self._client is None:
            DataverseClient = _import_official_client()
            self._client = DataverseClient(self._base_url, self._credential)
        return self._client

    def query(self, table, select=None, filter=None, top=None):
        client = self._ensure()
        builder = client.query.builder(table)
        if select:
            builder = builder.select(*select)
        if filter:
            builder = builder.filter(filter)
        builder = builder.page_size(self._page_size)
        rows: List[Dict[str, Any]] = []
        for page in builder.execute_pages():
            rows.extend(page)
            if top and len(rows) >= top:
                break
        return rows[:top] if top else rows


class WebApiDataverseReader:
    """Documented fallback: azure-identity/MSAL token + Dataverse Web API (OData).

    Uses only the standard library for HTTP so the fallback adds no hard
    dependency. ``token_provider`` returns a bearer token string.
    """

    def __init__(self, base_url: str, token_provider, api_version: str = "v9.2", page_size: int = 5000):
        self._base = base_url.rstrip("/")
        self._token_provider = token_provider
        self._api = api_version
        self._page_size = page_size

    def query(self, table, select=None, filter=None, top=None):
        import urllib.request
        import urllib.parse
        import json as _json
        params = {}
        if select:
            params["$select"] = ",".join(select)
        if filter:
            params["$filter"] = filter
        if top:
            params["$top"] = str(top)
        url = f"{self._base}/api/data/{self._api}/{table}"
        if params:
            url = url + "?" + urllib.parse.urlencode(params)
        rows: List[Dict[str, Any]] = []
        while url:
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {self._token_provider()}",
                "Accept": "application/json",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Prefer": f"odata.maxpagesize={self._page_size}",
            })
            with urllib.request.urlopen(req) as resp:  # nosec - enterprise endpoint
                payload = _json.loads(resp.read().decode("utf-8"))
            rows.extend(payload.get("value", []))
            url = payload.get("@odata.nextLink")
            if top and len(rows) >= top:
                return rows[:top]
        return rows
