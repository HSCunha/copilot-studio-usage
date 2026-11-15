"""Parse Power Platform admin-center ``MCSMessages`` consumption CSV exports.

There is no unattended API for per-agent credits, so these client-landed CSV
files are the robust credit source (ADR 0003). Column headers vary slightly
between report variants, so mapping is alias-tolerant and numbers are
comma-safe. Report type is detected from the file name.
"""
from __future__ import annotations
import csv
import os
from typing import Dict, List, Optional

from ..models import CreditRecord
from ..hashing import credit_key, row_hash

COLUMN_ALIASES: Dict[str, List[str]] = {
    "agent_name": ["Agent_Name", "Agent name", "AgentName", "Agent", "Copilot"],
    "usage_date": ["Usage_Date", "Usage date", "Date", "Billing_period", "Month"],
    "product_feature": ["Product / AI feature", "Product_AI_feature", "AI feature", "Feature", "Product"],
    "channel": ["Channel", "Channel_Id"],
    "llm_model": ["LLM model", "LLM_model", "Model"],
    "knowledge_or_tool": ["Knowledge sources / Tool used", "Tool used", "Knowledge_or_Tool", "Tool"],
    "user_id": ["User", "User_id", "UserId", "User principal name", "UPN"],
    "billed": ["Billed_credit", "Billed credits", "Billed_credits", "BilledCredits", "Billed"],
    "non_billed": ["Non_billed_credit", "Non-billed credits", "Non_billed_credits", "NonBilled_credits", "Non-billed"],
}


def detect_report_type(path: str) -> str:
    base = os.path.basename(path).lower()
    if "agent" in base:
        return "agent"
    if "user" in base:
        return "user"
    if "tenant" in base or "environment" in base or "env" in base:
        return "environment"
    return "unknown"


def _num(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    s = str(value).replace(",", "").strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def _pick(row: Dict[str, str], logical: str) -> Optional[str]:
    for alias in COLUMN_ALIASES[logical]:
        if alias in row and row[alias] not in (None, ""):
            return row[alias]
    lowered = {(k or "").lower(): v for k, v in row.items()}
    for alias in COLUMN_ALIASES[logical]:
        v = lowered.get(alias.lower())
        if v not in (None, ""):
            return v
    return None


def parse_credit_csv(path: str, environment_id: str = "ExampleEnvironment") -> List[CreditRecord]:
    report_type = detect_report_type(path)
    records: List[CreditRecord] = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            agent_name = _pick(row, "agent_name")
            usage_date = _pick(row, "usage_date")
            feature = _pick(row, "product_feature")
            channel = _pick(row, "channel")
            model = _pick(row, "llm_model")
            tool = _pick(row, "knowledge_or_tool")
            user_id = _pick(row, "user_id")
            billed = _num(_pick(row, "billed"))
            non_billed = _num(_pick(row, "non_billed"))
            key = credit_key(environment_id, agent_name, report_type, usage_date,
                             feature, channel, model, tool, user_id)
            rec = CreditRecord(
                credit_key=key,
                environment_id=environment_id,
                agent_name=agent_name,
                report_type=report_type,
                usage_date=usage_date,
                product_feature=feature,
                channel=channel,
                llm_model=model,
                knowledge_or_tool=tool,
                user_id=user_id,
                billed_credits=billed,
                non_billed_credits=non_billed,
            )
            rec.row_hash = row_hash(billed, non_billed, feature, channel, model, tool, user_id)
            records.append(rec)
    return records


def raw_csv_credit_total(paths: List[str]) -> float:
    """Independent sum of billed+non-billed used by reconciliation."""
    total = 0.0
    for path in paths:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                total += _num(_pick(row, "billed")) + _num(_pick(row, "non_billed"))
    return round(total, 4)
