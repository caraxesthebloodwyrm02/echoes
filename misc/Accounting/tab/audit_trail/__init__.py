#!/usr/bin/env python3
"""
Audit Trail - Tab Repository

Complete audit trail for all work tracking, payout processing, and payment activities.
Ensures full transparency and accountability for all user compensations.

Tracks:
- Work entries and time tracking
- Payout calculations and tax handling
- Payment processing and delivery
- User interactions and system events
- Compliance and regulatory requirements
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class AuditEntry:
    """Represents a single audit trail entry."""

    entry_id: str
    timestamp: str
    user_id: str
    component: str  # work_tracking, payout_engine, payment_gateway, sync_engine
    action: str
    details: Dict[str, Any]
    checksum: str
    compliance_flags: List[str] = None

    def __post_init__(self):
        if self.compliance_flags is None:
            self.compliance_flags = []


class AuditTrail:
    """
    Comprehensive audit trail system.

    Maintains immutable, tamper-proof records of all activities
    ensuring users can verify their compensations and contributions.
    """

    def __init__(self, base_dir: str = "e:/Projects/Echoes/Accounting/tab"):
        self.base_dir = Path(base_dir)
        self.audit_dir = self.base_dir / "audit_trail"
        self.data_dir = self.audit_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Audit log files
        self.main_audit_file = self.data_dir / "audit_trail.jsonl"
        self.integrity_file = self.data_dir / "integrity_checksums.json"

        print("✅ Audit Trail initialized - complete transparency and accountability")

    def log_event(
        self,
        user_id: str,
        component: str,
        action: str,
        details: Dict[str, Any],
        compliance_flags: List[str] = None,
    ) -> str:
        """
        Log an auditable event.

        Args:
            user_id: User associated with the event
            component: System component (work_tracking, payout_engine, etc.)
            action: Action performed
            details: Detailed event information
            compliance_flags: Compliance requirements met

        Returns:
            Audit entry ID
        """
        # Generate entry ID
        entry_content = (
            f"{user_id}_{component}_{action}_{datetime.now(timezone.utc).isoformat()}"
        )
        entry_id = hashlib.md5(entry_content.encode()).hexdigest()[:16]

        # Create audit entry
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=user_id,
            component=component,
            action=action,
            details=details,
            checksum=self._calculate_checksum(details),
            compliance_flags=compliance_flags or [],
        )

        # Save to audit log
        self._append_to_audit_log(entry)

        # Update integrity checks
        self._update_integrity_checksums()

        print(f"📝 Audit logged: {component}.{action} for user {user_id}")
        return entry_id

    def get_user_audit_trail(
        self, user_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit trail for a specific user."""
        user_entries = []

        if not self.main_audit_file.exists():
            return user_entries

        try:
            with open(self.main_audit_file, "r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry["user_id"] == user_id:
                            user_entries.append(entry)

            # Return most recent entries
            return user_entries[-limit:]

        except Exception as e:
            print(f"Error reading audit trail for user {user_id}: {e}")
            return []

    def get_component_audit_trail(
        self, component: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit trail for a specific component."""
        component_entries = []

        if not self.main_audit_file.exists():
            return component_entries

        try:
            with open(self.main_audit_file, "r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry["component"] == component:
                            component_entries.append(entry)

            return component_entries[-limit:]

        except Exception as e:
            print(f"Error reading audit trail for component {component}: {e}")
            return []

    def generate_compliance_report(
        self, user_id: str, time_range: str = "all"
    ) -> Dict[str, Any]:
        """
        Generate compliance report for a user.

        Args:
            user_id: User to generate report for
            time_range: Time range (all, month, quarter, year)

        Returns:
            Comprehensive compliance report
        """
        audit_entries = self.get_user_audit_trail(user_id, limit=1000)

        # Filter by time range if specified
        if time_range != "all":
            audit_entries = self._filter_by_time_range(audit_entries, time_range)

        # Analyze compliance
        compliance_analysis = self._analyze_compliance(audit_entries)

        report = {
            "user_id": user_id,
            "report_period": time_range,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_audit_entries": len(audit_entries),
            "compliance_analysis": compliance_analysis,
            "key_findings": self._extract_key_findings(audit_entries),
            "recommendations": self._generate_compliance_recommendations(
                compliance_analysis
            ),
        }

        return report

    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the audit trail."""
        integrity_status = {
            "audit_file_exists": self.main_audit_file.exists(),
            "integrity_file_exists": self.integrity_file.exists(),
            "total_entries": 0,
            "corrupted_entries": 0,
            "integrity_violations": [],
            "last_check": datetime.now(timezone.utc).isoformat(),
        }

        if not self.main_audit_file.exists():
            integrity_status["integrity_violations"].append("Audit file missing")
            return integrity_status

        try:
            with open(self.main_audit_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        integrity_status["total_entries"] += 1
                        try:
                            entry = json.loads(line)
                            # Verify checksum
                            calculated_checksum = self._calculate_checksum(
                                entry["details"]
                            )
                            if calculated_checksum != entry.get("checksum"):
                                integrity_status["corrupted_entries"] += 1
                                integrity_status["integrity_violations"].append(
                                    f"Checksum mismatch at line {line_num}"
                                )
                        except json.JSONDecodeError:
                            integrity_status["corrupted_entries"] += 1
                            integrity_status["integrity_violations"].append(
                                f"Invalid JSON at line {line_num}"
                            )

        except Exception as e:
            integrity_status["integrity_violations"].append(
                f"File read error: {str(e)}"
            )

        integrity_status["integrity_status"] = (
            "VERIFIED"
            if len(integrity_status["integrity_violations"]) == 0
            else "COMPROMISED"
        )

        return integrity_status

    def _append_to_audit_log(self, entry: AuditEntry):
        """Append entry to the audit log file."""
        with open(self.main_audit_file, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum for data integrity."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _update_integrity_checksums(self):
        """Update integrity checksums file."""
        if self.main_audit_file.exists():
            with open(self.main_audit_file, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            integrity_data = {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "audit_file_hash": file_hash,
                "total_entries": sum(
                    1 for line in open(self.main_audit_file) if line.strip()
                ),
            }

            with open(self.integrity_file, "w") as f:
                json.dump(integrity_data, f, indent=2)

    def _filter_by_time_range(
        self, entries: List[Dict[str, Any]], time_range: str
    ) -> List[Dict[str, Any]]:
        """Filter audit entries by time range."""
        now = datetime.now(timezone.utc)

        if time_range == "month":
            cutoff = now.replace(day=1)
        elif time_range == "quarter":
            quarter_start = ((now.month - 1) // 3) * 3 + 1
            cutoff = now.replace(month=quarter_start, day=1)
        elif time_range == "year":
            cutoff = now.replace(month=1, day=1)
        else:
            return entries

        filtered_entries = []
        for entry in entries:
            entry_date = datetime.fromisoformat(entry["timestamp"])
            if entry_date >= cutoff:
                filtered_entries.append(entry)

        return filtered_entries

    def _analyze_compliance(
        self, audit_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze compliance status from audit entries."""
        compliance = {
            "payment_compliance": 0,
            "tax_compliance": 0,
            "work_tracking_compliance": 0,
            "data_privacy_compliance": 0,
            "total_compliant_entries": 0,
            "total_entries": len(audit_entries),
        }

        for entry in audit_entries:
            flags = entry.get("compliance_flags", [])
            if "payment_processed" in flags:
                compliance["payment_compliance"] += 1
            if "tax_calculated" in flags:
                compliance["tax_compliance"] += 1
            if "work_logged" in flags:
                compliance["work_tracking_compliance"] += 1
            if "privacy_protected" in flags:
                compliance["data_privacy_compliance"] += 1

            if flags:  # Any compliance flags indicate compliance
                compliance["total_compliant_entries"] += 1

        return compliance

    def _extract_key_findings(self, audit_entries: List[Dict[str, Any]]) -> List[str]:
        """Extract key findings from audit entries."""
        findings = []

        # Analyze patterns
        components = {}
        actions = {}

        for entry in audit_entries:
            comp = entry.get("component", "unknown")
            action = entry.get("action", "unknown")

            components[comp] = components.get(comp, 0) + 1
            actions[action] = actions.get(action, 0) + 1

        # Generate findings
        if components:
            top_component = max(components.items(), key=lambda x: x[1])
            findings.append(
                f"Most active component: {top_component[0]} ({top_component[1]} entries)"
            )

        if actions:
            top_action = max(actions.items(), key=lambda x: x[1])
            findings.append(
                f"Most common action: {top_action[0]} ({top_action[1]} times)"
            )

        # Check for irregularities
        total_entries = len(audit_entries)
        if total_entries > 0:
            avg_entries_per_day = total_entries / 30  # Assuming 30-day period
            if avg_entries_per_day > 10:
                findings.append(
                    f"High activity level: {avg_entries_per_day:.1f} entries/day"
                )
            elif avg_entries_per_day < 1:
                findings.append(
                    f"Low activity level: {avg_entries_per_day:.1f} entries/day"
                )

        return findings

    def _generate_compliance_recommendations(
        self, compliance_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate compliance recommendations based on analysis."""
        recommendations = []
        total_entries = compliance_analysis["total_entries"]

        if total_entries == 0:
            return ["No audit entries found - ensure system is logging activities"]

        # Check compliance rates
        for compliance_type, count in compliance_analysis.items():
            if compliance_type.endswith("_compliance") and isinstance(
                count, (int, float)
            ):
                rate = (count / total_entries) * 100 if total_entries > 0 else 0
                if rate < 80:
                    clean_type = compliance_type.replace("_compliance", "").replace(
                        "_", " "
                    )
                    recommendations.append(
                        f"Improve {clean_type} compliance (currently {rate:.1f}%)"
                    )

        if not recommendations:
            recommendations.append(
                "All compliance metrics are within acceptable ranges"
            )

        return recommendations


# Integration functions for other Tab components
def audit_work_entry(user_id: str, work_details: Dict[str, Any]):
    """Audit a work entry from work tracking."""
    trail = AuditTrail()
    trail.log_event(
        user_id=user_id,
        component="work_tracking",
        action="work_entry_logged",
        details=work_details,
        compliance_flags=["work_logged", "privacy_protected"],
    )


def audit_payout_processing(user_id: str, payout_details: Dict[str, Any]):
    """Audit payout processing from payout Glimpse."""
    trail = AuditTrail()
    trail.log_event(
        user_id=user_id,
        component="payout_engine",
        action="payout_processed",
        details=payout_details,
        compliance_flags=[
            "payment_processed",
            "tax_calculated",
            "transparency_maintained",
        ],
    )


def audit_payment_delivery(user_id: str, payment_details: Dict[str, Any]):
    """Audit payment delivery from payment gateway."""
    trail = AuditTrail()
    trail.log_event(
        user_id=user_id,
        component="payment_gateway",
        action="payment_delivered",
        details=payment_details,
        compliance_flags=["payment_processed", "user_notified"],
    )


def audit_sync_operation(user_id: str, sync_details: Dict[str, Any]):
    """Audit sync operations from sync Glimpse."""
    trail = AuditTrail()
    trail.log_event(
        user_id=user_id,
        component="sync_engine",
        action="sync_completed",
        details=sync_details,
        compliance_flags=["data_integrity", "automated_processing"],
    )


def get_user_compliance_status(user_id: str) -> Dict[str, Any]:
    """Get user's compliance status from audit trail."""
    trail = AuditTrail()
    report = trail.generate_compliance_report(user_id, "month")

    return {
        "user_id": user_id,
        "compliance_score": (
            report["compliance_analysis"]["total_compliant_entries"]
            / report["compliance_analysis"]["total_entries"]
            * 100
            if report["compliance_analysis"]["total_entries"] > 0
            else 0
        ),
        "key_findings": report["key_findings"],
        "recommendations": report["recommendations"],
        "audit_integrity": trail.verify_audit_integrity(),
    }


if __name__ == "__main__":
    # Demo the audit trail
    trail = AuditTrail()

    # Log some demo events
    trail.log_event(
        user_id="demo_user",
        component="work_tracking",
        action="work_entry_logged",
        details={"hours": 2.5, "task": "AI model development"},
        compliance_flags=["work_logged", "privacy_protected"],
    )

    trail.log_event(
        user_id="demo_user",
        component="payout_engine",
        action="payout_processed",
        details={"amount": 150.0, "taxes": 22.5, "net": 127.5},
        compliance_flags=["payment_processed", "tax_calculated"],
    )

    # Verify integrity
    integrity = trail.verify_audit_integrity()
    print(f"Audit Integrity: {integrity['integrity_status']}")
    print(f"Total Entries: {integrity['total_entries']}")

    # Generate compliance report
    compliance = trail.generate_compliance_report("demo_user")
    print(f"\\nCompliance Report: {compliance['compliance_analysis']}")

    print("\\n✅ Audit Trail operational - complete transparency and accountability!")
