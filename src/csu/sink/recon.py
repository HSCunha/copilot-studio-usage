"""Reconciliation checks (ADR 0006 companion).

Produces machine-readable ``Check`` records plus a human summary. Failures are
explicit and testable, never silently logged.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from ..sources.credits_csv import raw_csv_credit_total


@dataclass
class Check:
    name: str
    passed: bool
    expected: Any
    actual: Any
    detail: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def reconcile(engine, sessions, credits, credit_csv_paths, source_session_count) -> List[Check]:
    checks: List[Check] = []

    checks.append(Check("sessions_normalized_vs_source",
                        len(sessions) == source_session_count,
                        source_session_count, len(sessions)))

    norm_total = round(sum(c.billed_credits + c.non_billed_credits for c in credits), 4)
    raw_total = raw_csv_credit_total(credit_csv_paths)
    checks.append(Check("credit_total_normalized_vs_raw",
                        norm_total == raw_total, raw_total, norm_total))

    delta_credit = engine.read("fact_agent_credit_consumption")
    delta_billed = round(sum(float(r["billed_credits"]) for r in delta_credit), 4)
    norm_billed = round(sum(c.billed_credits for c in credits), 4)
    checks.append(Check("delta_billed_vs_norm",
                        delta_billed == norm_billed, norm_billed, delta_billed))

    delta_session = engine.read("fact_agent_session")
    skeys = [r["session_key"] for r in delta_session]
    checks.append(Check("session_keys_unique",
                        len(skeys) == len(set(skeys)), len(set(skeys)), len(skeys)))

    ckeys = [r["credit_key"] for r in delta_credit]
    checks.append(Check("credit_keys_unique",
                        len(ckeys) == len(set(ckeys)), len(set(ckeys)), len(ckeys)))

    leak = any("credit_key" in r for r in delta_session) or any("session_key" in r for r in delta_credit)
    checks.append(Check("grains_separate", not leak, True, not leak,
                        "session and credit facts must stay in separate tables"))

    checks.append(Check("delta_session_count_vs_norm",
                        len(delta_session) == len(sessions), len(sessions), len(delta_session)))
    return checks


def summarize(checks: List[Check]) -> str:
    passed = sum(1 for c in checks if c.passed)
    lines = [f"Reconciliation: {'PASS' if passed == len(checks) else 'FAIL'} ({passed}/{len(checks)} checks)"]
    for c in checks:
        flag = "ok " if c.passed else "FAIL"
        lines.append(f"  [{flag}] {c.name}: expected={c.expected} actual={c.actual}")
    return "\n".join(lines)
