from csu.hashing import session_key, credit_key, row_hash


def test_session_key_deterministic():
    assert session_key("env", "S1") == session_key("env", "S1")
    assert session_key("env", "S1") != session_key("env", "S2")


def test_credit_key_deterministic_and_distinct():
    a = credit_key("env", "Agent", "agent", "2026-11", "Gen", "web", "gpt-4o", "SP", "")
    b = credit_key("env", "Agent", "agent", "2026-11", "Gen", "web", "gpt-4o", "SP", "")
    c = credit_key("env", "Agent", "agent", "2026-11", "Classic", "web", "gpt-4o", "SP", "")
    assert a == b and a != c


def test_row_hash_changes_on_field_change():
    assert row_hash(1, "a") != row_hash(1, "b")
