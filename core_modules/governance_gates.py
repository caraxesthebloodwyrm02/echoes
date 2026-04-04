"""
Governance Gates: composes consent check + value threshold into a single GateVerdict.

Wires CognitiveAccountingSystem.can_process() and ValueSystem scoring into
a unified authorization surface with provenance emission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

_SCOPE_PROTECTION = {
    "personal": "maximum",
    "creative": "standard",
    "general": "minimal",
}


@dataclass
class GateVerdict:
    """Result of a governance gate evaluation."""

    allowed: bool
    reason: str
    provenance_id: str = field(default_factory=lambda: str(uuid4()))
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def check(
    accounting,
    operation_type: str,
    user_id: str,
    scope: str,
    value_threshold: float = 0.5,
) -> GateVerdict:
    """Evaluate whether an operation is permitted.

    Composes:
      1. Consent gate via accounting.can_process(user_id, data_type)
      2. Value threshold via ValueSystem (if available)

    Args:
        accounting: CognitiveAccountingSystem instance (or None for pass-through).
        operation_type: Kind of operation ("chat", "simulation", "analogy", etc.).
        user_id: Session user identifier.
        scope: Data scope ("personal", "creative", "general").
        value_threshold: Minimum overall value score to authorize (default 0.5).

    Returns:
        GateVerdict with allowed status, reason, provenance_id, and confidence.
    """
    if accounting is None:
        return GateVerdict(
            allowed=True,
            reason="No accounting system configured; pass-through mode",
            confidence=0.5,
        )

    try:
        from legal_safeguards import ProtectionLevel
        protection_map = {
            "personal": ProtectionLevel.MAXIMUM,
            "creative": ProtectionLevel.STANDARD,
            "general": ProtectionLevel.MINIMAL,
        }
        protection = protection_map.get(scope, ProtectionLevel.STANDARD)
        accounting.set_protection(scope, protection)
    except ImportError:
        pass

    consent_allowed = accounting.can_process(user_id, scope)
    if not consent_allowed:
        return GateVerdict(
            allowed=False,
            reason=f"Consent gate denied: user={user_id}, scope={scope}",
            confidence=0.95,
        )

    try:
        from app.values import get_value_system
        vs = get_value_system()
        scores = vs.evaluate_response(
            f"Operation: {operation_type} for scope: {scope}",
            context={"user_id": user_id, "operation": operation_type},
        )
        overall = vs.get_overall_score(scores)
        if overall < value_threshold:
            return GateVerdict(
                allowed=False,
                reason=f"Value threshold not met: {overall:.2f} < {value_threshold}",
                confidence=overall,
            )
        return GateVerdict(
            allowed=True,
            reason=f"Authorized: consent=pass, values={overall:.2f}",
            confidence=overall,
        )
    except (ImportError, Exception):
        return GateVerdict(
            allowed=True,
            reason="Authorized: consent=pass, value system unavailable",
            confidence=0.7,
        )
