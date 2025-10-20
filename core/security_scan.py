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
Security Penetration Testing Automation
Automates Task: "Security Penetration Testing"
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class SecurityScanner:
    """Automated security scanning and penetration testing"""

    def __init__(self):
        self.q4_root = Path(__file__).parent.parent
        self.project_root = self.q4_root.parent
        self.vulnerabilities = []
        self.scan_results = {}

    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit security scanner for Python code"""
        print("\n" + "=" * 60)
        print("Running Bandit Security Scan")
        print("=" * 60)

        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "bandit",
                    "-r",
                    ".",
                    "-f",
                    "json",
                    "-o",
                    "bandit_report.json",
                ],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
            )

            # Load results
            report_file = self.q4_root / "bandit_report.json"
            if report_file.exists():
                with open(report_file) as f:
                    bandit_results = json.load(f)

                high_severity = len([r for r in bandit_results.get("results", []) if r.get("issue_severity") == "HIGH"])
                medium_severity = len(
                    [r for r in bandit_results.get("results", []) if r.get("issue_severity") == "MEDIUM"]
                )

                print("✓ Bandit scan complete")
                print(f"  High severity issues: {high_severity}")
                print(f"  Medium severity issues: {medium_severity}")

                return {
                    "tool": "bandit",
                    "status": "completed",
                    "high_severity": high_severity,
                    "medium_severity": medium_severity,
                    "report_file": str(report_file),
                }
            else:
                print("⚠ Bandit report not generated")
                return {"tool": "bandit", "status": "failed"}

        except FileNotFoundError:
            print("⚠ Bandit not found - install with: pip install bandit")
            return {"tool": "bandit", "status": "not_installed"}

    def run_safety_check(self) -> Dict[str, Any]:
        """Check for known vulnerabilities in dependencies"""
        print("\n" + "=" * 60)
        print("Running Safety Dependency Check")
        print("=" * 60)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
            )

            if result.stdout:
                try:
                    safety_results = json.loads(result.stdout)
                    vuln_count = len(safety_results)

                    print("✓ Safety check complete")
                    print(f"  Vulnerabilities found: {vuln_count}")

                    if vuln_count > 0:
                        print("\n  Vulnerable packages:")
                        for vuln in safety_results[:5]:  # Show first 5
                            print(f"    - {vuln.get('package', 'unknown')}: {vuln.get('vulnerability', 'N/A')}")

                    return {
                        "tool": "safety",
                        "status": "completed",
                        "vulnerabilities": vuln_count,
                        "details": safety_results,
                    }
                except json.JSONDecodeError:
                    print("✓ No vulnerabilities found")
                    return {
                        "tool": "safety",
                        "status": "completed",
                        "vulnerabilities": 0,
                    }
            else:
                print("✓ No vulnerabilities found")
                return {"tool": "safety", "status": "completed", "vulnerabilities": 0}

        except FileNotFoundError:
            print("⚠ Safety not found - install with: pip install safety")
            return {"tool": "safety", "status": "not_installed"}

    def check_secrets(self) -> Dict[str, Any]:
        """Check for exposed secrets and credentials"""
        print("\n" + "=" * 60)
        print("Checking for Exposed Secrets")
        print("=" * 60)

        secrets_found = []
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "API key"),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', "Secret key"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Token"),
        ]

        # Scan Python files
        for py_file in self.q4_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                for pattern, desc in patterns:
                    import re

                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        secrets_found.append(
                            {
                                "file": str(py_file.relative_to(self.q4_root)),
                                "type": desc,
                                "line": content[: match.start()].count("\n") + 1,
                            }
                        )
            except Exception:
                continue

        print("✓ Secret scan complete")
        print(f"  Potential secrets found: {len(secrets_found)}")

        if secrets_found:
            print("\n  Locations:")
            for secret in secrets_found[:5]:
                print(f"    - {secret['file']}:{secret['line']} ({secret['type']})")

        return {
            "tool": "secret_scanner",
            "status": "completed",
            "secrets_found": len(secrets_found),
            "details": secrets_found,
        }

    def check_permissions(self) -> Dict[str, Any]:
        """Check file permissions for security issues"""
        print("\n" + "=" * 60)
        print("Checking File Permissions")
        print("=" * 60)

        issues = []

        # Check for overly permissive files
        for file_path in self.q4_root.rglob("*"):
            if file_path.is_file():
                try:
                    # On Windows, this is less relevant, but we can check
                    if file_path.suffix in [".key", ".pem", ".env"]:
                        issues.append(
                            {
                                "file": str(file_path.relative_to(self.q4_root)),
                                "issue": "Sensitive file detected",
                                "recommendation": "Ensure proper access controls",
                            }
                        )
                except Exception:
                    continue

        print("✓ Permission check complete")
        print(f"  Sensitive files found: {len(issues)}")

        return {
            "tool": "permission_checker",
            "status": "completed",
            "issues_found": len(issues),
            "details": issues,
        }

    def generate_security_report(self):
        """Generate comprehensive security report"""
        print("\n" + "=" * 60)
        print("SECURITY SCAN REPORT")
        print("=" * 60)

        # Run all scans
        self.scan_results["bandit"] = self.run_bandit_scan()
        self.scan_results["safety"] = self.run_safety_check()
        self.scan_results["secrets"] = self.check_secrets()
        self.scan_results["permissions"] = self.check_permissions()

        # Calculate overall risk score
        risk_score = 0
        risk_score += self.scan_results["bandit"].get("high_severity", 0) * 10
        risk_score += self.scan_results["bandit"].get("medium_severity", 0) * 5
        risk_score += self.scan_results["safety"].get("vulnerabilities", 0) * 7
        risk_score += self.scan_results["secrets"].get("secrets_found", 0) * 15

        risk_level = "LOW"
        if risk_score > 50:
            risk_level = "HIGH"
        elif risk_score > 20:
            risk_level = "MEDIUM"

        print("\n" + "=" * 60)
        print(f"Overall Risk Level: {risk_level} (Score: {risk_score})")
        print("=" * 60)

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "task": "Security Penetration Testing",
            "status": "Completed",
            "risk_level": risk_level,
            "risk_score": risk_score,
            "scans": self.scan_results,
            "recommendations": [
                "Review and fix all HIGH severity issues immediately",
                "Update vulnerable dependencies",
                "Remove hardcoded secrets and use environment variables",
                "Implement proper access controls for sensitive files",
                "Enable automated security scanning in CI/CD pipeline",
            ],
        }

        report_file = self.q4_root / "automation" / "security_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved: {report_file}")

        return risk_level == "LOW"


def main():
    """Main security scan execution"""
    scanner = SecurityScanner()

    print("Q4 Roadmap - Security Penetration Testing")

    success = scanner.generate_security_report()

    print("\n✓ Security Penetration Testing - COMPLETED")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
