"""Typed records for the usage-focused Delta model.

Two grains are kept strictly separate and never force-joined:
  * SessionRecord -> fact_agent_session            (engagement grain, Dataverse)
  * CreditRecord  -> fact_agent_credit_consumption (credit grain, PPAC CSV)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentRecord:
    agent_id: str
    name: Optional[str]
    environment_id: str
    orchestration: Optional[str] = None
    is_managed: Optional[bool] = None
    row_hash: str = ""


@dataclass
class SessionRecord:
    session_key: str
    session_id: str
    agent_id: Optional[str]
    environment_id: str
    start_time: Optional[str]
    channel: Optional[str]
    user_id: Optional[str]
    message_count: int
    engaged: Optional[bool]
    outcome: Optional[str]
    csat: Optional[int]
    parse_error: Optional[str] = None
    row_hash: str = ""


@dataclass
class CreditRecord:
    credit_key: str
    environment_id: str
    agent_name: Optional[str]
    report_type: str
    usage_date: Optional[str]
    product_feature: Optional[str]
    channel: Optional[str]
    llm_model: Optional[str]
    knowledge_or_tool: Optional[str]
    user_id: Optional[str]
    billed_credits: float
    non_billed_credits: float
    row_hash: str = ""


@dataclass
class IngestionRun:
    run_id: str
    source: str
    started: str
    ended: Optional[str] = None
    rows: int = 0
    status: str = "running"
    detail: str = ""
