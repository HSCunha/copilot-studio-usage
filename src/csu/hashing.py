"""Deterministic hashing helpers for business keys and change detection.

Pure and dependency-free so they can be unit-tested offline and produce
identical values across runs (enabling idempotent MERGE).
"""
from __future__ import annotations
import hashlib
from typing import Any

_SEP = chr(31).encode("utf-8")  # unit separator


def _sha1(*parts: Any) -> str:
    h = hashlib.sha1()
    for p in parts:
        h.update(("" if p is None else str(p)).encode("utf-8"))
        h.update(_SEP)
    return h.hexdigest()


def session_key(environment_id: Any, session_id: Any) -> str:
    """Composite surrogate key for a session (avoids cross-environment collisions)."""
    return _sha1(environment_id, session_id)


def credit_key(environment_id, agent_name, report_type, usage_date,
               product_feature, channel, llm_model, knowledge_or_tool, user_id) -> str:
    """Business key for a credit row at the agent x feature x window grain."""
    return _sha1(environment_id, agent_name, report_type, usage_date,
                 product_feature, channel, llm_model, knowledge_or_tool, user_id)


def row_hash(*parts: Any) -> str:
    """Content hash used to decide whether a matched row must be UPDATEd."""
    return _sha1(*parts)
