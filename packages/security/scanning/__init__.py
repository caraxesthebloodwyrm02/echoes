"""Vulnerability scanning and analysis."""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from packages.core import get_logger

logger = get_logger("security.scanning")


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""

    cve_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    affected_package: str
    affected_version: str
    fixed_version: Optional[str]
    discovered_at: datetime


class VulnerabilityScanner:
    """Scans code and dependencies for vulnerabilities."""

    def __init__(self) -> None:
        self.logger = logger

    def scan_dependencies(self, requirements_file: Path) -> List[Vulnerability]:
        """
        Scan dependencies for known vulnerabilities.

        Args:
            requirements_file: Path to requirements.txt file

        Returns:
            List of vulnerabilities found
        """
        self.logger.info(f"Scanning dependencies from {requirements_file}")

        vulnerabilities = []

        try:
            # Use safety to scan for vulnerabilities
            result = subprocess.run(
                ["safety", "check", "-r", str(requirements_file), "--json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # No vulnerabilities found
                self.logger.info("No vulnerabilities found in dependencies")
                return []

            # Parse safety output
            if result.stdout:
                safety_data = json.loads(result.stdout)
                for vuln in safety_data:
                    vulnerabilities.append(
                        Vulnerability(
                            cve_id=vuln.get("id", "UNKNOWN"),
                            severity=vuln.get("severity", "MEDIUM"),
                            description=vuln.get("advisory", ""),
                            affected_package=vuln.get("package_name", ""),
                            affected_version=vuln.get("installed_version", ""),
                            fixed_version=vuln.get("fixed_versions", [None])[0],
                            discovered_at=datetime.now(),
                        )
                    )

        except (
            subprocess.TimeoutExpired,
            json.JSONDecodeError,
            FileNotFoundError,
        ) as e:
            self.logger.warning(f"Safety scan failed: {e}")

        return vulnerabilities

    def scan_code(self, path: Path) -> List[Dict[str, Any]]:
        """
        Scan code for security issues using bandit.

        Args:
            path: Path to scan

        Returns:
            List of security issues found
        """
        self.logger.info(f"Scanning code at {path}")

        issues = []

        try:
            result = subprocess.run(
                ["bandit", "-r", str(path), "-f", "json"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.stdout:
                bandit_data = json.loads(result.stdout)
                issues = bandit_data.get("results", [])

        except (
            subprocess.TimeoutExpired,
            json.JSONDecodeError,
            FileNotFoundError,
        ) as e:
            self.logger.warning(f"Bandit scan failed: {e}")

        return issues


class CodeReviewer:
    """Automated code review for security issues."""

    def __init__(self) -> None:
        self.logger = get_logger("security.code_review")

    def review_python_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Review Python code for security issues.

        Args:
            file_path: Path to Python file

        Returns:
            List of security issues found
        """
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for common security anti-patterns
            line_num = 0
            for line in content.splitlines():
                line_num += 1
                line_lower = line.lower().strip()

                # Check for hardcoded secrets
                if any(
                    keyword in line_lower
                    for keyword in ["password =", "secret =", "api_key =", "token ="]
                ):
                    if not line_lower.startswith("#"):  # Ignore comments
                        issues.append(
                            {
                                "type": "hardcoded_secret",
                                "line": line_num,
                                "description": "Potential hardcoded secret detected",
                                "severity": "HIGH",
                            }
                        )

                # Check for dangerous functions
                if any(func in line_lower for func in ["eval(", "exec(", "os.system("]):
                    issues.append(
                        {
                            "type": "dangerous_function",
                            "line": line_num,
                            "description": "Dangerous function usage detected",
                            "severity": "MEDIUM",
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error reviewing file {file_path}: {e}")

        return issues


__all__ = ["Vulnerability", "VulnerabilityScanner", "CodeReviewer"]
