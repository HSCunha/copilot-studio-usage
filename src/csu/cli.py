"""Local CLI runner (no deployment infrastructure).

Commands:
  * ``csu check``  - validate Dataverse connectivity (needs live credentials).
  * ``csu e2e``    - run fixtures through normalization + local Delta + reconcile.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from typing import Dict, List

from .sources.agents import normalize_agents
from .sources.sessions import normalize_sessions
from .sources.credits_csv import parse_credit_csv
from .sink.delta_writer import DeltaWriter, LocalEngine
from .sink.recon import reconcile, summarize
from .state.runlog import start_run, finish_run


def run_e2e(fixtures_dir: str, out_dir: str) -> Dict:
    with open(os.path.join(fixtures_dir, "dataverse_e2e.json"), "r", encoding="utf-8") as fh:
        dv = json.load(fh)
    env_id = dv["environment_id"]

    agents = normalize_agents(dv["bots"], env_id)
    sessions = normalize_sessions(dv["msdyn_botsessions"], dv["conversationtranscripts"], env_id)

    credit_csv = os.path.join(fixtures_dir, "ppac_agent_report.csv")
    credits = parse_credit_csv(credit_csv, environment_id=env_id)

    engine = LocalEngine(out_dir)
    writer = DeltaWriter(engine)

    run = start_run("e2e-fixtures")
    m_agent = writer.upsert("dim_agent", agents, "agent_id")
    m_sess = writer.upsert("fact_agent_session", sessions, "session_key")
    m_credit = writer.upsert("fact_agent_credit_consumption", credits, "credit_key")
    finish_run(run, rows=m_agent["source_rows"] + m_sess["source_rows"] + m_credit["source_rows"])
    writer.upsert("ingestion_run", [run], "run_id")

    checks = reconcile(engine, sessions, credits, [credit_csv], source_session_count=len(dv["msdyn_botsessions"]))
    return {
        "metrics": {"dim_agent": m_agent, "fact_agent_session": m_sess,
                    "fact_agent_credit_consumption": m_credit},
        "checks": [c.as_dict() for c in checks],
        "passed": all(c.passed for c in checks),
        "out_dir": out_dir,
    }


def _cmd_e2e(args) -> int:
    result = run_e2e(args.fixtures, args.out)
    print("Table output dir:", result["out_dir"])
    for table, m in result["metrics"].items():
        print(f"  {table}: inserted={m['inserted']} updated={m['updated']} "
              f"skipped={m['skipped']} duplicates_collapsed={m['duplicates_collapsed']}")
    from .sink.recon import Check
    print(summarize([Check(**c) for c in result["checks"]]))
    return 0 if result["passed"] else 1


def _cmd_check(args) -> int:
    print("Dataverse connectivity check requires live credentials.")
    print("Configure a service principal and run against your environment URL.")
    print("See docs/dataverse-source.md and docs/local-development.md.")
    return 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="csu", description="Copilot Studio usage collector")
    sub = parser.add_subparsers(dest="command", required=True)

    p_e2e = sub.add_parser("e2e", help="run fixtures -> local Delta -> reconcile")
    p_e2e.add_argument("--fixtures", default="tests/fixtures")
    p_e2e.add_argument("--out", default=".local/delta")
    p_e2e.set_defaults(func=_cmd_e2e)

    p_check = sub.add_parser("check", help="validate Dataverse connectivity (live)")
    p_check.set_defaults(func=_cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
