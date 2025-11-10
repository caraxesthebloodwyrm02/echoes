"""
Security Audit Tool for Echoes Project
Scans for hardcoded credentials, API keys, security vulnerabilities, and dependency issues.
"""

import json
import re
import subprocess
from pathlib import Path


class SecurityAuditor:
    """Comprehensive security auditor"""

    # Patterns to detect secrets and credentials
    SECRET_PATTERNS = {
        "api_key": [
            r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']',
            r"api[_-]?key\s*[=:]\s*([a-zA-Z0-9_\-]{20,})",
            r'OPENAI_API_KEY\s*[=:]\s*["\']([^"\']+)["\']',
        ],
        "password": [
            r'password\s*[=:]\s*["\']([^"\']+)["\']',
            r'pwd\s*[=:]\s*["\']([^"\']+)["\']',
            r'passwd\s*[=:]\s*["\']([^"\']+)["\']',
        ],
        "token": [
            r'token\s*[=:]\s*["\']([^"\']{20,})["\']',
            r"bearer\s+([a-zA-Z0-9_\-\.]{20,})",
            r'secret[_-]?token\s*[=:]\s*["\']([^"\']+)["\']',
        ],
        "secret": [
            r'secret\s*[=:]\s*["\']([^"\']{10,})["\']',
            r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']',
        ],
        "credential": [
            r'credential\s*[=:]\s*["\']([^"\']+)["\']',
            r'credentials\s*[=:]\s*["\']([^"\']+)["\']',
        ],
        "aws_key": [
            r'AWS_ACCESS_KEY_ID\s*[=:]\s*["\']([^"\']+)["\']',
            r'AWS_SECRET_ACCESS_KEY\s*[=:]\s*["\']([^"\']+)["\']',
        ],
        "private_key": [
            r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
            r"ssh-rsa\s+([A-Za-z0-9+/]{100,})",
        ],
    }

    # Safe patterns (these are OK - environment variables, placeholders, etc.)
    SAFE_PATTERNS = [
        r"os\.getenv\(",
        r"os\.environ\[",
        r"os\.environ\.get\(",
        r"environment",
        r"env\[",
        r"\.env",
        r"example",
        r"placeholder",
        r"template",
        r"your[_-]?key",
        r"sk-your-key-here",
        r"YOUR[_-]?API[_-]?KEY",
        r"\$\{",
        r"<API_KEY>",
        r"REPLACE",
    ]

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.vulnerabilities: list[dict] = []
        self.config_security_issues: list[dict] = []
        self.gitignore_coverage: dict = {}
        self.dependency_vulnerabilities: list[dict] = []

    def scan_for_hardcoded_secrets(self):
        """Scan all files for hardcoded secrets"""
        print("Scanning for hardcoded secrets...")

        python_files = list(self.project_root.rglob("*.py"))
        config_files = list(self.project_root.rglob("*.{json,yaml,yml,env,ini,toml}"))
        all_files = python_files + config_files

        # Exclude certain directories
        excluded = {
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            "dist",
            "build",
            ".pytest_cache",
        }

        for file_path in all_files:
            if any(exclude in file_path.parts for exclude in excluded):
                continue

            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                rel_path = str(file_path.relative_to(self.project_root))

                for secret_type, patterns in self.SECRET_PATTERNS.items():
                    for pattern in patterns:
                        matches = re.finditer(
                            pattern, content, re.IGNORECASE | re.MULTILINE
                        )
                        for match in matches:
                            matched_text = match.group(0)
                            line_num = content[: match.start()].count("\n") + 1
                            line_content = (
                                lines[line_num - 1] if line_num <= len(lines) else ""
                            )

                            # Check if it's a safe pattern
                            is_safe = any(
                                re.search(safe_pattern, line_content, re.IGNORECASE)
                                for safe_pattern in self.SAFE_PATTERNS
                            )

                            if not is_safe:
                                self.vulnerabilities.append(
                                    {
                                        "severity": (
                                            "HIGH"
                                            if secret_type
                                            in ["api_key", "password", "token"]
                                            else "MEDIUM"
                                        ),
                                        "type": "hardcoded_secret",
                                        "secret_type": secret_type,
                                        "file": rel_path,
                                        "line": line_num,
                                        "match": matched_text[:100],  # Truncate
                                        "context": line_content.strip()[:200],
                                    }
                                )
            except Exception:
                pass  # Skip files that can't be read

    def check_gitignore_coverage(self):
        """Check if .gitignore properly excludes sensitive files"""
        print("Checking .gitignore coverage...")

        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            self.config_security_issues.append(
                {
                    "severity": "HIGH",
                    "type": "missing_gitignore",
                    "issue": "No .gitignore file found",
                }
            )
            return

        with open(gitignore_path) as f:
            gitignore_content = f.read()

        required_patterns = {
            ".env": ".env files",
            "*.key": "Key files",
            "*.pem": "Certificate files",
            "secrets/": "Secrets directory",
            "credentials/": "Credentials directory",
            "__pycache__/": "Python cache",
            "venv/": "Virtual environment",
        }

        missing_patterns = []
        for pattern, description in required_patterns.items():
            if (
                pattern not in gitignore_content
                and pattern.replace("/", "") not in gitignore_content
            ):
                missing_patterns.append(description)

        if missing_patterns:
            self.config_security_issues.append(
                {
                    "severity": "MEDIUM",
                    "type": "gitignore_gaps",
                    "issue": f'Missing patterns in .gitignore: {", ".join(missing_patterns)}',
                }
            )

        self.gitignore_coverage = {
            "total_patterns_checked": len(required_patterns),
            "missing_patterns": len(missing_patterns),
            "patterns": missing_patterns,
        }

    def check_configuration_security(self):
        """Check configuration files for security issues"""
        print("Checking configuration security...")

        # Check for .env files in repo
        env_files = list(self.project_root.rglob(".env"))
        actual_env_files = [
            f for f in env_files if "example" not in f.name and "template" not in f.name
        ]

        if actual_env_files:
            self.config_security_issues.append(
                {
                    "severity": "HIGH",
                    "type": "env_files_in_repo",
                    "issue": f"Found {len(actual_env_files)} .env files that may contain secrets",
                    "files": [
                        str(f.relative_to(self.project_root))
                        for f in actual_env_files[:5]
                    ],
                }
            )

        # Check config files for hardcoded secrets
        config_files = [
            self.project_root / "api" / "config.py",
            self.project_root / "echoes" / "config.py",
            self.project_root / "ATLAS" / "echoes" / "config.py",
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file) as f:
                        content = f.read()

                    # Check for hardcoded API keys
                    if re.search(
                        r'api[_-]?key\s*[=:]\s*["\'][^"\']{20,}["\']',
                        content,
                        re.IGNORECASE,
                    ):
                        if "os.getenv" not in content or "environment" not in content:
                            self.config_security_issues.append(
                                {
                                    "severity": "HIGH",
                                    "type": "hardcoded_config",
                                    "file": str(
                                        config_file.relative_to(self.project_root)
                                    ),
                                    "issue": "Potential hardcoded API key in configuration",
                                }
                            )
                except Exception:
                    pass

    def check_communication_security(self):
        """Check communication.py for password handling"""
        print("Checking communication module security...")

        comm_file = self.project_root / "communication.py"
        if comm_file.exists():
            try:
                with open(comm_file) as f:
                    content = f.read()
                    lines = content.split("\n")

                # Check lines 974-982 specifically
                for i in range(973, min(983, len(lines))):
                    line = lines[i]
                    if "password" in line.lower() and "=" in line:
                        # Check if password is hardcoded
                        if re.search(
                            r'password\s*[=:]\s*["\'][^"\']+["\']', line, re.IGNORECASE
                        ):
                            self.vulnerabilities.append(
                                {
                                    "severity": "HIGH",
                                    "type": "hardcoded_password",
                                    "file": "communication.py",
                                    "line": i + 1,
                                    "match": line.strip()[:100],
                                    "context": "Password handling in communication module",
                                }
                            )
            except Exception:
                pass

    def check_api_security(self):
        """Check API security configuration"""
        print("Checking API security configuration...")

        api_config = self.project_root / "api" / "config.py"
        if api_config.exists():
            try:
                with open(api_config) as f:
                    content = f.read()

                issues = []

                # Check CORS configuration
                if (
                    'cors_origins: list = ["*"]' in content
                    or 'cors_origins = ["*"]' in content
                ):
                    issues.append(
                        {
                            "severity": "MEDIUM",
                            "type": "cors_wildcard",
                            "issue": "CORS configured to allow all origins (*) - security risk",
                        }
                    )

                # Check rate limiting
                if "rate_limit" not in content.lower():
                    issues.append(
                        {
                            "severity": "MEDIUM",
                            "type": "missing_rate_limiting",
                            "issue": "Rate limiting not configured",
                        }
                    )

                # Check API key validation
                if "api_key_required" in content:
                    if "api_key_required: bool = False" in content:
                        issues.append(
                            {
                                "severity": "MEDIUM",
                                "type": "api_key_optional",
                                "issue": "API key validation is optional (False)",
                            }
                        )

                self.config_security_issues.extend(issues)
            except Exception:
                pass

    def check_dependency_security(self):
        """Check dependencies for known vulnerabilities"""
        print("Checking dependency security...")

        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.dependency_vulnerabilities.append(
                {
                    "severity": "INFO",
                    "type": "no_requirements",
                    "issue": "requirements.txt not found - cannot check dependencies",
                }
            )
            return

        # Try to use pip-audit or safety if available
        try:
            result = subprocess.run(
                [
                    "pip-audit",
                    "--requirement",
                    str(requirements_file),
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                for vuln in audit_data.get("vulnerabilities", []):
                    self.dependency_vulnerabilities.append(
                        {
                            "severity": vuln.get("severity", "UNKNOWN").upper(),
                            "type": "dependency_vulnerability",
                            "package": vuln.get("name"),
                            "version": vuln.get("installed_version"),
                            "vulnerability_id": vuln.get("id"),
                            "issue": vuln.get("description", "")[:200],
                        }
                    )
        except FileNotFoundError:
            self.dependency_vulnerabilities.append(
                {
                    "severity": "INFO",
                    "type": "missing_tool",
                    "issue": "pip-audit not installed - install with: pip install pip-audit",
                }
            )
        except subprocess.TimeoutExpired:
            self.dependency_vulnerabilities.append(
                {
                    "severity": "INFO",
                    "type": "timeout",
                    "issue": "Dependency check timed out",
                }
            )
        except Exception as e:
            self.dependency_vulnerabilities.append(
                {
                    "severity": "INFO",
                    "type": "check_error",
                    "issue": f"Could not check dependencies: {str(e)[:100]}",
                }
            )

    def generate_report(self) -> dict:
        """Generate security audit report"""
        print("\nGenerating security report...")

        high_severity = len(
            [v for v in self.vulnerabilities if v.get("severity") == "HIGH"]
        )
        medium_severity = len(
            [v for v in self.vulnerabilities if v.get("severity") == "MEDIUM"]
        )

        report = {
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "high_severity": high_severity,
                "medium_severity": medium_severity,
                "config_issues": len(self.config_security_issues),
                "dependency_vulnerabilities": len(
                    [
                        v
                        for v in self.dependency_vulnerabilities
                        if v.get("severity") != "INFO"
                    ]
                ),
            },
            "vulnerabilities": self.vulnerabilities[:100],  # Limit to first 100
            "configuration_issues": self.config_security_issues,
            "gitignore_coverage": self.gitignore_coverage,
            "dependency_vulnerabilities": [
                v
                for v in self.dependency_vulnerabilities
                if v.get("severity") != "INFO"
            ],
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> list[dict]:
        """Generate security recommendations"""
        recommendations = []

        hardcoded_secrets = [
            v for v in self.vulnerabilities if v.get("type") == "hardcoded_secret"
        ]
        if hardcoded_secrets:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "category": "Secrets Management",
                    "issue": f"Found {len(hardcoded_secrets)} potential hardcoded secrets",
                    "recommendation": "Immediately move all secrets to environment variables. Rotate any exposed credentials. Use secrets management service for production.",
                }
            )

        if any("cors_wildcard" in str(v) for v in self.config_security_issues):
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "API Security",
                    "issue": "CORS configured to allow all origins",
                    "recommendation": 'Restrict CORS origins to specific domains. Never use "*" in production.',
                }
            )

        env_files_issue = next(
            (
                v
                for v in self.config_security_issues
                if v.get("type") == "env_files_in_repo"
            ),
            None,
        )
        if env_files_issue:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Secrets Management",
                    "issue": ".env files found in repository",
                    "recommendation": "Remove .env files from repository. Add to .gitignore. Use .env.example for templates.",
                }
            )

        dependency_vulns = [
            v
            for v in self.dependency_vulnerabilities
            if v.get("severity") in ["HIGH", "CRITICAL"]
        ]
        if dependency_vulns:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Dependencies",
                    "issue": f"Found {len(dependency_vulns)} high/critical dependency vulnerabilities",
                    "recommendation": "Update vulnerable dependencies immediately. Run: pip-audit --requirement requirements.txt",
                }
            )

        return recommendations


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    auditor = SecurityAuditor(str(project_root))

    print("=" * 60)
    print("Echoes Project - Security Audit")
    print("=" * 60)

    auditor.scan_for_hardcoded_secrets()
    auditor.check_gitignore_coverage()
    auditor.check_configuration_security()
    auditor.check_communication_security()
    auditor.check_api_security()
    auditor.check_dependency_security()

    report = auditor.generate_report()

    # Save report
    output_file = project_root / "audit_results" / "security_audit_report.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {output_file}")
    print("\nSummary:")
    print(f"  Total vulnerabilities: {report['summary']['total_vulnerabilities']}")
    print(f"  High severity: {report['summary']['high_severity']}")
    print(f"  Medium severity: {report['summary']['medium_severity']}")
    print(f"  Configuration issues: {report['summary']['config_issues']}")
    print(
        f"  Dependency vulnerabilities: {report['summary']['dependency_vulnerabilities']}"
    )
    print(f"\nRecommendations: {len(report['recommendations'])}")
    for rec in report["recommendations"]:
        print(f"  [{rec['priority']}] {rec['category']}: {rec['issue']}")


if __name__ == "__main__":
    main()
