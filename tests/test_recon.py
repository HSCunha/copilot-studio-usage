import os
from csu.sink.delta_writer import LocalEngine, DeltaWriter
from csu.sink.recon import reconcile
from csu.sources.sessions import normalize_sessions
from csu.sources.credits_csv import parse_credit_csv

FIX = os.path.join(os.path.dirname(__file__), "fixtures")
CSV = os.path.join(FIX, "ppac_agent_report.csv")


def _sessions():
    bs = [{"msdyn_botsessionid": "S1", "_msdyn_botid_value": "A1", "createdon": "x",
           "msdyn_outcome": "Resolved", "msdyn_csat": 5, "msdyn_engaged": True}]
    tr = [{"_msdyn_botsession_value": "S1", "content": '{"activities":[{"type":"message"}]}'}]
    return normalize_sessions(bs, tr, "env")


def test_recon_all_pass(tmp_path):
    eng = LocalEngine(str(tmp_path))
    w = DeltaWriter(eng)
    sessions = _sessions()
    credits = parse_credit_csv(CSV, environment_id="env")
    w.upsert("fact_agent_session", sessions, "session_key")
    w.upsert("fact_agent_credit_consumption", credits, "credit_key")
    checks = reconcile(eng, sessions, credits, [CSV], source_session_count=1)
    assert all(c.passed for c in checks)
    assert any(c.name == "grains_separate" and c.passed for c in checks)


def test_recon_detects_count_mismatch(tmp_path):
    eng = LocalEngine(str(tmp_path))
    w = DeltaWriter(eng)
    sessions = _sessions()
    credits = parse_credit_csv(CSV, environment_id="env")
    w.upsert("fact_agent_session", sessions, "session_key")
    w.upsert("fact_agent_credit_consumption", credits, "credit_key")
    checks = reconcile(eng, sessions, credits, [CSV], source_session_count=99)
    assert any(c.name == "sessions_normalized_vs_source" and not c.passed for c in checks)
