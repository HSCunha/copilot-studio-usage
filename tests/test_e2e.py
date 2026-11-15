import os
from csu.cli import run_e2e

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def test_e2e_runs_and_reconciles(tmp_path):
    result = run_e2e(FIX, str(tmp_path / "delta"))
    assert result["passed"] is True
    m = result["metrics"]
    assert m["dim_agent"]["inserted"] == 2
    assert m["fact_agent_session"]["inserted"] == 2
    assert m["fact_agent_credit_consumption"]["inserted"] == 4
    names = {c["name"]: c for c in result["checks"]}
    assert names["credit_total_normalized_vs_raw"]["actual"] == 3399.5


def test_e2e_idempotent_second_run(tmp_path):
    out = str(tmp_path / "delta")
    run_e2e(FIX, out)
    second = run_e2e(FIX, out)
    for table, m in second["metrics"].items():
        assert m["inserted"] == 0 and m["updated"] == 0, table
    assert second["passed"] is True
