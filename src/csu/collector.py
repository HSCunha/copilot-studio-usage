"""High-level collection helpers that use a DataverseReader.

The web app stays peripheral; these functions are what a Timer-triggered
backend calls. They are source-agnostic thanks to the ``DataverseReader``
Protocol, so unit tests inject ``FakeDataverseReader``.
"""
from __future__ import annotations
from typing import List, Optional

from .sources.agents import normalize_agents
from .sources.sessions import normalize_sessions
from .models import AgentRecord, SessionRecord

BOT_SELECT = ["botid", "name", "ismanaged", "configuration"]
SESSION_SELECT = ["msdyn_botsessionid", "_msdyn_botid_value", "createdon",
                  "msdyn_outcome", "msdyn_csat", "msdyn_engaged"]


def collect_agents(reader, environment_id: str) -> List[AgentRecord]:
    bots = reader.query("bots", select=BOT_SELECT)
    return normalize_agents(bots, environment_id)


def collect_sessions(reader, environment_id: str, since: Optional[str] = None) -> List[SessionRecord]:
    flt = f"createdon gt {since}" if since else None
    botsessions = reader.query("msdyn_botsessions", select=SESSION_SELECT, filter=flt)
    transcripts = reader.query("conversationtranscripts",
                               select=["conversationtranscriptid", "_msdyn_botsession_value", "content", "createdon"],
                               filter=flt)
    return normalize_sessions(botsessions, transcripts, environment_id)
