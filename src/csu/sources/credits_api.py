"""User-level credit API adapter - DISABLED in the production path (ADR 0004).

App-only/unattended support for the user-level consumption endpoint is not
confirmed, so this adapter is intentionally inert. It exists only as an
interface placeholder behind ``Config.enable_user_level_credit_api`` and is
never imported by the collector, CLI, or tests.
"""
from __future__ import annotations
from typing import List, Dict


class UserLevelCreditApiDisabled(RuntimeError):
    pass


class UserLevelCreditApiAdapter:
    enabled = False

    def fetch(self, *args, **kwargs) -> List[Dict]:  # pragma: no cover - disabled
        raise UserLevelCreditApiDisabled(
            "User-level credit API is disabled. Use the PPAC CSV credit lane "
            "(credits_csv.py). See docs/adr/0004-user-level-credit-api-disabled.md"
        )
