#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Compliance Audit Framework
Automates Task: "Compliance Audit Framework" - HIPAA/GDPR compliance verification
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class ComplianceAuditor:
    """Automated compliance checking for HIPAA, GDPR, and other regulations"""

    def __init__(self):
        self.q4_root = Path(__file__).parent.parent
        self.project_root = self.q4_root.parent
        self.findings = []

    def check_data_privacy(self) -> Dict[str, Any]:
        """Check for data privacy compliance"""
        print("\n" + "=" * 60)
        print("Checking Data Privacy Compliance")
        print("=" * 60)

        issues = []

        # Check for PII handling
        pii_patterns = [
            (r"ssn|social.security", "Social Security Number"),
            (r"credit.card|card.number", "Credit Card"),
            (r"email.?address", "Email Address"),
            (r"phone.?number", "Phone Number"),
            (r"medical.?record", "Medical Record"),
        ]

        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                for pattern, pii_type in pii_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        # Check if there's encryption/anonymization nearby
                        has_protection = bool(
                            re.search(
                                r"encrypt|hash|anonymize|redact", content, re.IGNORECASE
                            )
                        )
                        if not has_protection:
                            issues.append(
                                {
                                    "file": str(py_file.relative_to(self.q4_root)),
                                    "pii_type": pii_type,
                                    "has_protection": False,
                                    "severity": "HIGH",
                                }
                            )
            except OSError:
                continue

        print("✓ Data privacy check complete")
        print(f"  Unprotected PII references: {len(issues)}")

        return {
            "check": "data_privacy",
            "status": "completed",
            "issues": len(issues),
            "details": issues,
        }

    def check_consent_management(self) -> Dict[str, Any]:
        """Check for user consent management (GDPR requirement)"""
        print("\n" + "=" * 60)
        print("Checking Consent Management")
        print("=" * 60)

        consent_keywords = ["consent", "opt-in", "opt-out", "permission", "agree"]
        consent_found = False
        consent_files = []

        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text().lower()
                if any(keyword in content for keyword in consent_keywords):
                    consent_found = True
                    consent_files.append(str(py_file.relative_to(self.q4_root)))
            except OSError:
                continue

        print("✓ Consent management check complete")
        print(f"  Consent mechanisms found: {len(consent_files)}")

        return {
            "check": "consent_management",
            "status": "completed",
            "consent_found": consent_found,
            "files_with_consent": consent_files,
            "compliant": consent_found,
        }

    def check_data_retention(self) -> Dict[str, Any]:
        """Check for data retention policies"""
        print("\n" + "=" * 60)
        print("Checking Data Retention Policies")
        print("=" * 60)

        retention_keywords = ["retention", "delete", "purge", "expire", "ttl"]
        retention_found = False
        retention_files = []

        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text().lower()
                if any(keyword in content for keyword in retention_keywords):
                    retention_found = True
                    retention_files.append(str(py_file.relative_to(self.q4_root)))
            except OSError:
                continue

        print("✓ Data retention check complete")
        print(f"  Retention policies found: {len(retention_files)}")

        return {
            "check": "data_retention",
            "status": "completed",
            "retention_found": retention_found,
            "files_with_retention": retention_files,
            "compliant": retention_found,
        }

    def check_audit_logging(self) -> Dict[str, Any]:
        """Check for audit logging (HIPAA requirement)"""
        print("\n" + "=" * 60)
        print("Checking Audit Logging")
        print("=" * 60)

        logging_found = False
        audit_files = []

        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                if re.search(r"import logging|logger\.|audit", content, re.IGNORECASE):
                    logging_found = True
                    audit_files.append(str(py_file.relative_to(self.q4_root)))
            except OSError:
                continue

        print("✓ Audit logging check complete")
        print(f"  Files with logging: {len(audit_files)}")

        return {
            "check": "audit_logging",
            "status": "completed",
            "logging_found": logging_found,
            "files_with_logging": audit_files,
            "compliant": logging_found,
        }

    def check_encryption(self) -> Dict[str, Any]:
        """Check for encryption implementation"""
        print("\n" + "=" * 60)
        print("Checking Encryption Implementation")
        print("=" * 60)

        encryption_keywords = ["encrypt", "decrypt", "cipher", "ssl", "tls", "https"]
        encryption_found = False
        encryption_files = []

        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text().lower()
                if any(keyword in content for keyword in encryption_keywords):
                    encryption_found = True
                    encryption_files.append(str(py_file.relative_to(self.q4_root)))
            except OSError:
                continue

        print("✓ Encryption check complete")
        print(f"  Files with encryption: {len(encryption_files)}")

        return {
            "check": "encryption",
            "status": "completed",
            "encryption_found": encryption_found,
            "files_with_encryption": encryption_files,
            "compliant": encryption_found,
        }

    def check_access_controls(self) -> Dict[str, Any]:
        """Check for access control implementation"""
        print("\n" + "=" * 60)
        print("Checking Access Controls")
        print("=" * 60)

        access_keywords = ["authenticate", "authorize", "permission", "role", "rbac"]
        access_found = False
        access_files = []

        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text().lower()
                if any(keyword in content for keyword in access_keywords):
                    access_found = True
                    access_files.append(str(py_file.relative_to(self.q4_root)))
            except OSError:
                continue

        print("✓ Access control check complete")
        print(f"  Files with access controls: {len(access_files)}")

        return {
            "check": "access_controls",
            "status": "completed",
            "access_found": access_found,
            "files_with_access": access_files,
            "compliant": access_found,
        }

    def generate_compliance_report(self):
        """Generate comprehensive compliance report"""
        print("\n" + "=" * 60)
        print("COMPLIANCE AUDIT REPORT")
        print("=" * 60)

        # Run all checks
        checks = {
            "data_privacy": self.check_data_privacy(),
            "consent_management": self.check_consent_management(),
            "data_retention": self.check_data_retention(),
            "audit_logging": self.check_audit_logging(),
            "encryption": self.check_encryption(),
            "access_controls": self.check_access_controls(),
        }

        # Calculate compliance score
        total_checks = len(checks)
        compliant_checks = sum(
            1 for check in checks.values() if check.get("compliant", False)
        )
        compliance_score = (compliant_checks / total_checks) * 100

        # Determine compliance level
        if compliance_score >= 90:
            compliance_level = "EXCELLENT"
        elif compliance_score >= 70:
            compliance_level = "GOOD"
        elif compliance_score >= 50:
            compliance_level = "FAIR"
        else:
            compliance_level = "NEEDS IMPROVEMENT"

        print("\n" + "=" * 60)
        print(f"Compliance Score: {compliance_score:.1f}%")
        print(f"Compliance Level: {compliance_level}")
        print("=" * 60)

        print("\nCheck Results:")
        for check_name, result in checks.items():
            status = "✓" if result.get("compliant", False) else "✗"
            print(f"  {status} {check_name.replace('_', ' ').title()}")

        # Generate recommendations
        recommendations = []

        if checks["data_privacy"]["issues"] > 0:
            recommendations.append(
                "Implement PII encryption/anonymization for all sensitive data"
            )

        if not checks["consent_management"]["compliant"]:
            recommendations.append(
                "Implement user consent management system (GDPR requirement)"
            )

        if not checks["data_retention"]["compliant"]:
            recommendations.append("Define and implement data retention policies")

        if not checks["audit_logging"]["compliant"]:
            recommendations.append(
                "Implement comprehensive audit logging (HIPAA requirement)"
            )

        if not checks["encryption"]["compliant"]:
            recommendations.append(
                "Implement encryption for data at rest and in transit"
            )

        if not checks["access_controls"]["compliant"]:
            recommendations.append("Implement role-based access controls (RBAC)")

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "task": "Compliance Audit Framework",
            "status": "Completed",
            "compliance_score": compliance_score,
            "compliance_level": compliance_level,
            "checks": checks,
            "recommendations": recommendations,
            "frameworks": {
                "GDPR": {
                    "consent_management": checks["consent_management"]["compliant"],
                    "data_retention": checks["data_retention"]["compliant"],
                    "encryption": checks["encryption"]["compliant"],
                },
                "HIPAA": {
                    "audit_logging": checks["audit_logging"]["compliant"],
                    "encryption": checks["encryption"]["compliant"],
                    "access_controls": checks["access_controls"]["compliant"],
                },
            },
        }

        report_file = self.q4_root / "automation" / "compliance_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved: {report_file}")

        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        return compliance_score >= 70


def main():
    """Main compliance audit execution"""
    auditor = ComplianceAuditor()

    print("Q4 Roadmap - Compliance Audit Framework")

    success = auditor.generate_compliance_report()

    print("\n✓ Compliance Audit Framework - COMPLETED")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
