"""Transcript/session parsing boundary (ADR 0005).

ALL parsing of ``conversationtranscript.Content`` lives here. It is defensive:
unknown activity shapes are recorded, malformed JSON is captured as
``parse_error`` and NEVER raised, and the raw payload is preserved upstream
(bronze). Schema drift is therefore a one-file change protected by golden
fixtures.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from ..models import SessionRecord
from ..hashing import session_key, row_hash


def parse_transcript_content(content: Any) -> Dict[str, Any]:
    """Parse a transcript ``Content`` payload. Returns a summary dict; never raises."""
    result: Dict[str, Any] = {
        "message_count": 0,
        "channel": None,
        "user_id": None,
        "engaged": None,
        "unknown_activity_types": [],
        "parse_error": None,
    }
    activities = _extract_activities(content, result)
    if activities is None:  # malformed; parse_error already set
        return result

    for act in activities:
        if not isinstance(act, dict):
            continue
        atype = act.get("type")
        if atype == "message":
            result["message_count"] += 1
            if result["channel"] is None:
                ch = act.get("channelId") or act.get("channel")
                if ch:
                    result["channel"] = ch
            frm = act.get("from")
            if isinstance(frm, dict) and frm.get("role") == "user" and result["user_id"] is None:
                result["user_id"] = frm.get("id")
        elif atype == "event" and act.get("name") == "SessionInfo":
            val = act.get("value")
            if isinstance(val, dict):
                hint = val.get("valueType") or val.get("engagementStatus")
                if hint is not None:
                    result["engaged"] = str(hint).strip().lower() in ("engaged", "true", "1", "yes")
        else:
            if atype and atype not in result["unknown_activity_types"]:
                result["unknown_activity_types"].append(atype)
    return result


def _extract_activities(content: Any, result: Dict[str, Any]) -> Optional[List[Any]]:
    try:
        if content is None:
            return []
        if isinstance(content, (bytes, bytearray)):
            content = content.decode("utf-8")
        if isinstance(content, str):
            content = content.strip()
            if not content:
                return []
            content = json.loads(content)
        if isinstance(content, list):
            return content
        if isinstance(content, dict):
            acts = content.get("activities")
            return acts if isinstance(acts, list) else []
        return []
    except (ValueError, TypeError) as exc:
        result["parse_error"] = f"malformed_content: {type(exc).__name__}"
        return None


def normalize_sessions(botsessions: List[dict], transcripts: List[dict],
                       environment_id: str) -> List[SessionRecord]:
    """Join sessions to their transcript and normalize to the engagement grain.

    Outcome / CSAT / engagement come from ``msdyn_botsession`` (authoritative);
    channel / user / message_count come from the parsed transcript JSON.
    """
    tmap: Dict[Any, dict] = {}
    for t in transcripts:
        link = (t.get("_msdyn_botsession_value") or t.get("botsessionid")
                or t.get("conversationtranscriptid"))
        tmap[link] = t

    records: List[SessionRecord] = []
    for s in botsessions:
        sid = s.get("msdyn_botsessionid")
        agent_id = s.get("_msdyn_botid_value") or s.get("botid")
        transcript = tmap.get(sid)
        parsed = parse_transcript_content(transcript.get("content") if transcript else None)

        bs_engaged = s.get("msdyn_engaged")
        engaged = bs_engaged if bs_engaged is not None else parsed["engaged"]

        rec = SessionRecord(
            session_key=session_key(environment_id, sid),
            session_id=sid,
            agent_id=agent_id,
            environment_id=environment_id,
            start_time=s.get("createdon"),
            channel=parsed["channel"],
            user_id=parsed["user_id"],
            message_count=parsed["message_count"],
            engaged=engaged,
            outcome=s.get("msdyn_outcome"),
            csat=s.get("msdyn_csat"),
            parse_error=parsed["parse_error"],
        )
        rec.row_hash = row_hash(rec.agent_id, rec.channel, rec.user_id, rec.message_count,
                                rec.engaged, rec.outcome, rec.csat)
        records.append(rec)
    return records
