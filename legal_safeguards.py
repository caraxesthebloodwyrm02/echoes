"""
Legal Safeguards module — Decision Chain of Custody (DCoC) backed.

Provides cognitive accounting and legal safeguards for the Echoes assistant.
Consent changes and data processing decisions produce tamper-evident
Decision Provenance Records (DPRs) for regulatory traceability.

LIMITATIONS: Keyword-based consent/protection checks are not sufficient
for production safety without classifier context.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import uuid


class ConsentType(Enum):
    """Types of consent for data processing."""

    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    NONE = "none"


class ProtectionLevel(Enum):
    """Levels of data protection."""

    MINIMAL = "minimal"
    STANDARD = "standard"
    MAXIMUM = "maximum"


@dataclass
class CognitiveEffortMetrics:
    """Metrics for tracking cognitive effort."""

    processing_time: float
    complexity_score: float
    memory_usage: float
    confidence_level: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CognitiveAccountingSystem:
    """Simple cognitive accounting system."""

    def __init__(self):
        self.metrics_history: List[CognitiveEffortMetrics] = []
        self.consent_records: Dict[str, ConsentType] = {}
        self.protection_settings: Dict[str, ProtectionLevel] = {}
        self.provenance_chain: List[Dict[str, Any]] = []

    def record_effort(self, metrics: CognitiveEffortMetrics):
        """Record cognitive effort metrics."""
        self.metrics_history.append(metrics)

    def set_consent(self, user_id: str, consent_type: ConsentType):
        """Set consent for a user. Emits a provenance record."""
        previous = self.consent_records.get(user_id, ConsentType.NONE)
        self.consent_records[user_id] = consent_type
        self._emit_provenance(
            decision_type="consent_change",
            action_taken="consent_update",
            actor_id=user_id,
            reasoning=f"Consent changed from {previous.value} to {consent_type.value}",
            authority="human_consent",
        )

    def get_consent(self, user_id: str) -> ConsentType:
        """Get consent for a user."""
        return self.consent_records.get(user_id, ConsentType.NONE)

    def set_protection(self, data_type: str, level: ProtectionLevel):
        """Set protection level for data type."""
        self.protection_settings[data_type] = level

    def get_protection(self, data_type: str) -> ProtectionLevel:
        """Get protection level for data type."""
        return self.protection_settings.get(data_type, ProtectionLevel.STANDARD)

    def can_process(self, user_id: str, data_type: str) -> bool:
        """Check if data can be processed based on consent and protection."""
        consent = self.get_consent(user_id)
        protection = self.get_protection(data_type)

        # Simple rules: explicit consent allows all, implicit allows standard and below
        if consent == ConsentType.EXPLICIT:
            allowed = True
        elif consent == ConsentType.IMPLICIT:
            allowed = protection in [ProtectionLevel.MINIMAL, ProtectionLevel.STANDARD]
        else:
            allowed = protection == ProtectionLevel.MINIMAL

        self._emit_provenance(
            decision_type="gate_verdict",
            action_taken="data_processing_authorization",
            actor_id=user_id,
            reasoning=(
                f"Processing {'authorized' if allowed else 'denied'}: "
                f"consent={consent.value}, protection={protection.value}"
            ),
            authority="system_policy",
            verdict="pass" if allowed else "block",
            gate_id=f"consent_gate:{data_type}",
        )
        return allowed

    def get_average_metrics(self) -> Dict[str, float]:
        """Get average cognitive effort metrics."""
        if not self.metrics_history:
            return {
                "avg_processing_time": 0.0,
                "avg_complexity": 0.0,
                "avg_memory": 0.0,
                "avg_confidence": 0.0,
            }

        return {
            "avg_processing_time": sum(m.processing_time for m in self.metrics_history)
            / len(self.metrics_history),
            "avg_complexity": sum(m.complexity_score for m in self.metrics_history)
            / len(self.metrics_history),
            "avg_memory": sum(m.memory_usage for m in self.metrics_history)
            / len(self.metrics_history),
            "avg_confidence": sum(m.confidence_level for m in self.metrics_history)
            / len(self.metrics_history),
        }

    def export_report(self) -> Dict[str, Any]:
        """Export accounting report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_records": len(self.metrics_history),
            "consent_records": len(self.consent_records),
            "protection_settings": len(self.protection_settings),
            "average_metrics": self.get_average_metrics(),
            "provenance_records": len(self.provenance_chain),
            "provenance_version": "1.0.0",
        }

    def _emit_provenance(
        self,
        *,
        decision_type: str,
        action_taken: str,
        actor_id: str,
        reasoning: str,
        authority: str = "system_policy",
        verdict: str = "pass",
        gate_id: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Create and store a Decision Provenance Record (DPR)."""
        try:
            dpr_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).isoformat()
            parent = self.provenance_chain[-1] if self.provenance_chain else None
            seq = (parent["sequence_number"] + 1) if parent else 0

            partial = {
                "dpr_id": dpr_id,
                "parent_dpr_id": parent["dpr_id"] if parent else None,
                "timestamp": timestamp,
                "sequence_number": seq,
                "decision_type": decision_type,
                "action_taken": action_taken,
                "reasoning_summary": reasoning,
                "authority_type": authority,
                "actor_id": actor_id,
                "safety_verdicts": [
                    {"gate_id": gate_id, "verdict": verdict}
                ] if gate_id else [],
                "provenance_version": "1.0.0",
            }

            serialized = json.dumps(partial, sort_keys=True)
            parent_hash = parent["chain_hash"] if parent else "genesis"
            chain_hash = hashlib.sha256(
                (parent_hash + serialized).encode()
            ).hexdigest()

            dpr = {**partial, "chain_hash": chain_hash}
            full_serialized = json.dumps(dpr, sort_keys=True)

            secret = os.environ.get("JWT_SECRET", "echoes-default-secret")
            signature = hmac.new(
                secret.encode(), full_serialized.encode(), hashlib.sha256
            ).hexdigest()
            dpr["signature"] = signature

            self.provenance_chain.append(dpr)
            return dpr
        except Exception:
            return None

    def get_provenance_chain(self) -> List[Dict[str, Any]]:
        """Return the full provenance chain for audit."""
        return list(self.provenance_chain)

    def verify_provenance_chain(self) -> Dict[str, Any]:
        """Verify integrity of the provenance chain."""
        if not self.provenance_chain:
            return {"valid": True, "total": 0, "broken_at": None}
        for i, dpr in enumerate(self.provenance_chain):
            parent_hash = (
                self.provenance_chain[i - 1]["chain_hash"] if i > 0 else "genesis"
            )
            without_sig = {k: v for k, v in dpr.items() if k not in ("signature",)}
            without_chain = {k: v for k, v in without_sig.items() if k != "chain_hash"}
            serialized = json.dumps(without_chain, sort_keys=True)
            expected = hashlib.sha256(
                (parent_hash + serialized).encode()
            ).hexdigest()
            if dpr["chain_hash"] != expected:
                return {"valid": False, "total": len(self.provenance_chain), "broken_at": i}
        return {"valid": True, "total": len(self.provenance_chain), "broken_at": None}


# Global instance
_accounting = CognitiveAccountingSystem()


def get_cognitive_accounting() -> CognitiveAccountingSystem:
    """Get the global cognitive accounting system."""
    return _accounting


# Export symbols for backward compatibility
__all__ = [
    "get_cognitive_accounting",
    "CognitiveEffortMetrics",
    "ConsentType",
    "ProtectionLevel",
    "CognitiveAccountingSystem",
]


def _self_test():
    """Quick self-test for provenance integration."""
    cas = CognitiveAccountingSystem()
    cas.set_consent("user-1", ConsentType.EXPLICIT)
    result = cas.can_process("user-1", "session_data")
    assert result is True
    assert len(cas.provenance_chain) == 2
    integrity = cas.verify_provenance_chain()
    assert integrity["valid"] is True
    assert integrity["total"] == 2
    print(f"DCoC self-test passed: {integrity['total']} DPRs, chain valid.")


if __name__ == "__main__":
    _self_test()
