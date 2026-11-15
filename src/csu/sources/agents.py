"""Thin normalization of the Dataverse ``bot`` table into ``dim_agent``.

Only the small set of attributes needed to interpret usage facts is kept; this
is deliberately NOT a full agent/model/tool inventory (ADR 0002).
"""
from __future__ import annotations
from typing import List, Optional

from ..models import AgentRecord
from ..hashing import row_hash


def orchestration_of(bot: dict) -> Optional[str]:
    """Heuristic orchestration hint; refined during live integration if needed."""
    if bot.get("configuration"):
        return "generative"
    return None


def normalize_agents(bots: List[dict], environment_id: str) -> List[AgentRecord]:
    records: List[AgentRecord] = []
    for b in bots:
        rec = AgentRecord(
            agent_id=b.get("botid"),
            name=b.get("name"),
            environment_id=environment_id,
            orchestration=orchestration_of(b),
            is_managed=b.get("ismanaged"),
        )
        rec.row_hash = row_hash(rec.name, rec.environment_id, rec.orchestration, rec.is_managed)
        records.append(rec)
    return records
