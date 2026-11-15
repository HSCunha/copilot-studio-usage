import json
import os

from csu.sources.sessions import parse_transcript_content, normalize_sessions

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "transcripts")


def _load(name):
    with open(os.path.join(FIX, name), "r", encoding="utf-8") as fh:
        return fh.read()


def test_parse_normal_two_messages():
    r = parse_transcript_content(_load("normal.json"))
    assert r["message_count"] == 2
    assert r["channel"] == "webchat"
    assert r["user_id"] == "user-aaa"
    assert r["engaged"] is True
    assert r["parse_error"] is None


def test_parse_accepts_list_and_dict():
    acts = json.loads(_load("normal.json"))
    assert parse_transcript_content(acts)["message_count"] == 2            # dict
    assert parse_transcript_content(acts["activities"])["message_count"] == 2  # list


def test_parse_missing_optional_fields():
    r = parse_transcript_content({"activities": [{"type": "message"}]})
    assert r["message_count"] == 1
    assert r["channel"] is None and r["user_id"] is None


def test_parse_malformed_never_raises():
    r = parse_transcript_content(_load("malformed.txt"))
    assert r["parse_error"] is not None
    assert r["message_count"] == 0


def test_parse_unknown_activity_collected():
    r = parse_transcript_content(_load("unknown_activity.json"))
    assert "typing" in r["unknown_activity_types"]
    assert "handoff" in r["unknown_activity_types"]
    assert r["message_count"] == 1


def test_parse_empty_and_none():
    assert parse_transcript_content(None)["message_count"] == 0
    assert parse_transcript_content("")["message_count"] == 0


def test_normalize_prefers_botsession_outcome_csat():
    botsessions = [{"msdyn_botsessionid": "S1", "_msdyn_botid_value": "A1",
                    "createdon": "2026-11-01T10:00:00Z", "msdyn_outcome": "Resolved",
                    "msdyn_csat": 5, "msdyn_engaged": True}]
    transcripts = [{"_msdyn_botsession_value": "S1", "content": _load("normal.json")}]
    recs = normalize_sessions(botsessions, transcripts, "env")
    assert len(recs) == 1
    s = recs[0]
    assert s.outcome == "Resolved" and s.csat == 5        # from botsession
    assert s.channel == "webchat" and s.message_count == 2  # from transcript
    assert s.engaged is True and s.row_hash


def test_normalize_no_transcript_is_safe():
    botsessions = [{"msdyn_botsessionid": "S9", "_msdyn_botid_value": "A1",
                    "createdon": "x", "msdyn_outcome": None, "msdyn_csat": None}]
    recs = normalize_sessions(botsessions, [], "env")
    assert recs[0].message_count == 0 and recs[0].parse_error is None
