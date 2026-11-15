from csu.sources.agents import normalize_agents, orchestration_of


def test_normalize_agents_basic():
    bots = [{"botid": "A1", "name": "Orders", "ismanaged": False, "configuration": "{}"},
            {"botid": "A2", "name": "HR", "ismanaged": True}]
    recs = normalize_agents(bots, "env")
    assert [r.agent_id for r in recs] == ["A1", "A2"]
    assert recs[0].environment_id == "env" and recs[0].row_hash


def test_orchestration_detection():
    assert orchestration_of({"configuration": "{}"}) == "generative"
    assert orchestration_of({}) is None
