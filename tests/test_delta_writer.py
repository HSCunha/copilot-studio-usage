import pytest
from csu.sink.delta_writer import plan_upsert, LocalEngine, DeltaWriter, to_rows


def _row(k, h):
    return {"id": k, "row_hash": h, "val": h}


def test_plan_insert_all_new():
    plan = plan_upsert({}, [_row("a", "1"), _row("b", "2")], "id")
    assert len(plan["inserts"]) == 2 and not plan["updates"]


def test_plan_idempotent_skip():
    existing = {"a": _row("a", "1")}
    plan = plan_upsert(existing, [_row("a", "1")], "id")
    assert plan["skips"] and not plan["inserts"] and not plan["updates"]


def test_plan_update_on_hash_change():
    existing = {"a": _row("a", "1")}
    plan = plan_upsert(existing, [_row("a", "9")], "id")
    assert plan["updates"] and not plan["inserts"]


def test_plan_missing_key_raises():
    with pytest.raises(ValueError):
        plan_upsert({}, [{"row_hash": "1"}], "id")


def test_plan_empty_noop():
    plan = plan_upsert({"a": _row("a", "1")}, [], "id")
    assert not plan["inserts"] and not plan["updates"] and not plan["skips"]


def test_plan_duplicate_collapsed():
    plan = plan_upsert({}, [_row("a", "1"), _row("a", "2")], "id")
    assert plan["duplicates_collapsed"] == 1 and len(plan["inserts"]) == 1


def test_local_engine_upsert_and_rerun(tmp_path):
    eng = LocalEngine(str(tmp_path))
    m1 = eng.upsert("t", [_row("a", "1"), _row("b", "2")], "id")
    assert m1["inserted"] == 2
    m2 = eng.upsert("t", [_row("a", "1"), _row("b", "2")], "id")  # identical rerun
    assert m2["inserted"] == 0 and m2["updated"] == 0 and m2["skipped"] == 2
    assert len(eng.read("t")) == 2  # no duplicates


def test_local_engine_update_changes_row(tmp_path):
    eng = LocalEngine(str(tmp_path))
    eng.upsert("t", [_row("a", "1")], "id")
    m = eng.upsert("t", [_row("a", "9")], "id")
    assert m["updated"] == 1
    assert eng.read("t")[0]["row_hash"] == "9"


def test_to_rows_handles_dataclass():
    from csu.models import AgentRecord
    rows = to_rows([AgentRecord(agent_id="A1", name="x", environment_id="env")])
    assert rows[0]["agent_id"] == "A1"
