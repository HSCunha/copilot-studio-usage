import os
from csu.sources.credits_csv import parse_credit_csv, detect_report_type, raw_csv_credit_total

FIX = os.path.join(os.path.dirname(__file__), "fixtures")
CSV = os.path.join(FIX, "ppac_agent_report.csv")


def test_parse_agent_report_rows():
    recs = parse_credit_csv(CSV, environment_id="env")
    assert len(recs) == 4
    assert all(r.report_type == "agent" for r in recs)


def test_comma_safe_number_parsing():
    recs = parse_credit_csv(CSV, environment_id="env")
    billed = {r.agent_name: 0 for r in recs}
    for r in recs:
        billed[r.agent_name] += r.billed_credits
    # Orders Assistant row1 uses "1,200.0" + row2 900.5
    assert round(billed["Orders Assistant"], 1) == 2100.5


def test_detect_report_type():
    assert detect_report_type("EntitlementConsumption_agent.csv") == "agent"
    assert detect_report_type("foo_user_bar.csv") == "user"
    assert detect_report_type("env_report.csv") == "environment"


def test_credit_keys_unique():
    recs = parse_credit_csv(CSV, environment_id="env")
    keys = [r.credit_key for r in recs]
    assert len(keys) == len(set(keys))


def test_raw_total_matches_normalized():
    recs = parse_credit_csv(CSV, environment_id="env")
    norm = round(sum(r.billed_credits + r.non_billed_credits for r in recs), 4)
    assert norm == raw_csv_credit_total([CSV]) == 3399.5
