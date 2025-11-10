from __future__ import annotations

from typing import Optional

from .policy_types import PolicyConfig, PolicyDecision, load_config


def decide(host: str, cfg: Optional[PolicyConfig] = None) -> PolicyDecision:
    """Pure decision function: returns allow/deny with reason and matched token.

    Rules:
    - If enforcement is disabled, allow with reason "enforcement disabled".
    - Otherwise, allow if any allowlist token is a substring of the host (case-insensitive).
    - Deny otherwise with reason "not in allowlist".
    """
    host_l = (host or "").lower()
    cfg = cfg or load_config()

    if not cfg.enforce:
        return PolicyDecision(True, "enforcement disabled", None)

    for token in cfg.allowlist:
        if token and token in host_l:
            return PolicyDecision(True, "allowlist match", token)

    return PolicyDecision(False, "not in allowlist", None)
