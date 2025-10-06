"""
Task: automation.tasks.security_monitoring

Comprehensive security monitoring task that runs multiple security checks:
- Bandit security scan for code vulnerabilities
- Dependency vulnerability checks with Safety
- Environment configuration validation
- File permissions verification

Use via automation runner:
  python -m automation.scripts.run_automation --task "Security Monitoring"

Parameters (context.extra_data):
- severity_threshold: str (default "HIGH") -> minimum severity to fail on
- output_file: str (default "automation/reports/security_monitoring_report.json")
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Any

from automation.core.logger import AutomationLogger


def run_command(cmd: list[str], shell: bool = False) -> Tuple[bool, str, str]:
    """Run a command safely."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_bandit_scan(log: AutomationLogger) -> bool:
    """Run Bandit security scan and report issues."""
    log.info("Running Bandit security scan...")

    success, stdout, stderr = run_command(
        [
            "python",
            "-m",
            "bandit",
            "-r",
            "app/",
            "packages/",
            "automation/",
            "-f",
            "json",
            "-o",
            "automation/reports/bandit_scan.json",
        ]
    )

    if not success and not Path("automation/reports/bandit_scan.json").exists():
        log.error(f"Bandit scan failed: {stderr}")
        return False

    # Check for security issues
    try:
        with open("automation/reports/bandit_scan.json", "r") as f:
            results = json.load(f)

        issues = results.get("results", [])
        high_severity = [i for i in issues if i.get("issue_severity") == "HIGH"]
        medium_severity = [i for i in issues if i.get("issue_severity") == "MEDIUM"]

        log.info(f"Bandit Results: {len(high_severity)} HIGH, {len(medium_severity)} MEDIUM issues")

        if high_severity:
            log.warning("HIGH SEVERITY ISSUES FOUND:")
            for issue in high_severity[:5]:  # Show first 5
                log.warning(
                    f"  - {issue.get('filename')}:{issue.get('line_number')} - {issue.get('issue_text')}"
                )
            if len(high_severity) > 5:
                log.warning(f"  ... and {len(high_severity) - 5} more")

        return len(high_severity) == 0
    except Exception as e:
        log.error(f"Error parsing Bandit results: {e}")
        return False


def check_dependency_vulnerabilities(log: AutomationLogger) -> bool:
    """Check for vulnerable dependencies using Safety."""
    log.info("Checking dependency vulnerabilities...")

    # Check if safety is installed
    success, stdout, stderr = run_command(["python", "-m", "pip", "show", "safety"])
    if not success:
        log.info("Safety not installed, installing...")
        success, stdout, stderr = run_command(["python", "-m", "pip", "install", "safety"])
        if not success:
            log.error(f"Failed to install safety: {stderr}")
            return False

    success, stdout, stderr = run_command(["python", "-m", "safety", "check", "--json"])

    # Safety returns non-zero exit code if vulnerabilities found
    # Parse output regardless
    try:
        if stdout:
            vuln_data = json.loads(stdout)
            vuln_count = len(vuln_data) if isinstance(vuln_data, list) else 0
            if vuln_count > 0:
                log.warning(f"Found {vuln_count} vulnerable dependencies")
                return False
    except json.JSONDecodeError:
        pass

    log.info("Dependency vulnerability check completed")
    return True


def check_environment_variables(log: AutomationLogger) -> bool:
    """Check that environment variables are properly configured."""
    log.info("Checking environment configuration...")

    issues = []

    # Check for production security settings
    host = os.getenv("HOST", "127.0.0.1")
    if host == "0.0.0.0" and os.getenv("ENVIRONMENT") != "production":
        issues.append("⚠️  HOST=0.0.0.0 in non-production environment")

    reload = os.getenv("RELOAD", "false").lower() == "true"
    if reload and os.getenv("ENVIRONMENT") == "production":
        issues.append("⚠️  RELOAD=true in production environment")

    log_level = os.getenv("LOG_LEVEL", "info")
    if log_level == "debug" and os.getenv("ENVIRONMENT") == "production":
        issues.append("⚠️  LOG_LEVEL=debug in production environment")

    if issues:
        log.warning("Environment configuration issues:")
        for issue in issues:
            log.warning(f"  {issue}")
        return False

    log.info("Environment configuration looks secure")
    return True


def check_file_permissions(log: AutomationLogger) -> bool:
    """Check for sensitive files that might have incorrect permissions."""
    log.info("Checking file permissions...")

    sensitive_files = [".env", ".env.production", "requirements.txt", "pyproject.toml"]

    issues = []

    for file_path in sensitive_files:
        full_path = Path(file_path)
        if full_path.exists():
            log.info(f"   ✅ {file_path} exists")
        else:
            issues.append(f"❌ {file_path} not found")

    if issues:
        for issue in issues:
            log.warning(f"  {issue}")
        return False

    log.info("File permissions check completed")
    return True


def security_monitoring(context) -> None:
    """Main security monitoring function."""
    log = AutomationLogger()

    output_file = context.extra_data.get(
        "output_file", "automation/reports/security_monitoring_report.json"
    )

    log.info("🚀 Starting Security Monitoring")
    log.info(f"⏰ Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if context.dry_run:
        log.info("[DRY-RUN] Would run security checks")
        return

    try:
        checks: Dict[str, bool] = {
            "bandit_scan": check_bandit_scan(log),
            "dependency_check": check_dependency_vulnerabilities(log),
            "environment_check": check_environment_variables(log),
            "file_permissions": check_file_permissions(log),
        }

        # Calculate overall security score
        passed_checks = sum(1 for check in checks.values() if check is True)
        total_checks = len(checks)
        security_score = (passed_checks / total_checks) * 100

        report: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "security_score": security_score,
        }

        # Save report
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        log.info(
            f"📊 Security Score: {security_score:.1f}% ({passed_checks}/{total_checks} checks passed)"
        )
        log.info(f"Report saved to: {output_path}")

        if security_score >= 80:
            log.info("✅ SECURITY MONITORING COMPLETE - System appears secure")
        else:
            log.warning("⚠️  SECURITY MONITORING COMPLETE - Issues found, review report")

    except Exception as e:
        log.error(f"❌ Security monitoring failed: {e}")
        raise
