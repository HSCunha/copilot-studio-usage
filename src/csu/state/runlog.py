"""Build ``ingestion_run`` audit records for idempotency and reconciliation."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional

from ..models import IngestionRun


def start_run(source: str, run_id: Optional[str] = None) -> IngestionRun:
    return IngestionRun(
        run_id=run_id or str(uuid.uuid4()),
        source=source,
        started=datetime.now(timezone.utc).isoformat(),
    )


def finish_run(run: IngestionRun, rows: int, status: str = "succeeded", detail: str = "") -> IngestionRun:
    run.ended = datetime.now(timezone.utc).isoformat()
    run.rows = rows
    run.status = status
    run.detail = detail
    return run
