"""Azure Functions host scaffold (Phase 5 - included for context only).

Uses only the standard library ``logging`` (no Application Insights / telemetry
SDK, per project scope). Two triggers and a status endpoint are sketched; the
business logic lives in the ``csu`` package.

This module is intentionally NOT imported by tests.
"""
from __future__ import annotations
import logging

logger = logging.getLogger("csu.backend")

try:
    import azure.functions as func  # type: ignore
    app = func.FunctionApp()

    @app.schedule(schedule="0 0 2 * * *", arg_name="timer", run_on_startup=False)
    def collect_sessions_timer(timer) -> None:
        """Daily Dataverse engagement collection (Lane A)."""
        logger.info("Timer trigger fired: Dataverse session collection")
        # from csu.collector import collect_sessions; write via DeltaRsEngine ...

    @app.blob_trigger(arg_name="blob", path="landing/{name}", connection="LANDING_STORAGE")
    def ingest_credit_csv(blob) -> None:
        """Ingest a PPAC MCSMessages CSV when it lands (Lane B)."""
        logger.info("Blob trigger fired: PPAC credit CSV ingestion")
        # from csu.sources.credits_csv import parse_credit_csv ...

    @app.route(route="status", methods=["GET"])
    def status(req):
        return func.HttpResponse('{"status":"ok"}', mimetype="application/json")

except ImportError:  # azure-functions not installed in local/dev
    app = None
    logger.info("azure-functions not installed; backend host is scaffold-only.")
