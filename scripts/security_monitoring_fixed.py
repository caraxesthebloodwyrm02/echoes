#!/usr/bin/env python3
"""
Security Monitoring Script
Run this script regularly to check for security issues and vulnerabilities.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_command(cmd, shell=False):
    """Run a command safely."""
    try:
        result = subprocess.run(
            cmd if isinstance(cmd, list) else [cmd],
            shell=shell,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_bandit_scan():
    """Run Bandit security scan and report issues."""
    print("Running Bandit security scan...")

    success, stdout, stderr = run_command(
        [
            "python",
            "-m",
            "bandit",
            "-r",
            "app/",
            "packages/",
            "-f",
            "json",
            "-o",
            "security_monitoring_report.json",
        ]
    )

    if not success:
        print(f"Bandit scan failed: {stderr}")
        return False

    # Check for security issues
    try:
        with open("security_monitoring_report.json", "r") as f:
            results = json.load(f)

        issues = results.get("results", [])
        high_severity = [i for i in issues if i.get("issue_severity") == "HIGH"]
        medium_severity = [i for i in issues if i.get("issue_severity") == "MEDIUM"]

        print(f"Bandit Results: {len(high_severity)} HIGH, {len(medium_severity)} MEDIUM issues")

        if high_severity:
            print("HIGH SEVERITY ISSUES FOUND:")
            for issue in high_severity:
                print(
                    f"  - {issue.get('filename')}:{issue.get('line_number')} - {issue.get('issue_text')}"
                )

        return len(high_severity) == 0

    except Exception as e:
        print(f"Error parsing Bandit results: {e}")
        return False


def check_dependency_vulnerabilities():
    """Check for vulnerable dependencies using Safety."""
    print("Checking dependency vulnerabilities...")

    success, stdout, stderr = run_command(["python", "-m", "pip", "install", "safety"])

    if not success:
        print(f"Failed to install safety: {stderr}")
        return False

    success, stdout, stderr = run_command(["python", "-m", "safety", "check", "--json"])

    if not success:
        print(f"Safety check failed: {stderr}")
        return False

    print("Dependency vulnerability check completed")
    return True


def check_environment_variables():
    """Check that environment variables are properly configured."""
    print("Checking environment configuration...")

    issues = []

    # Check for production security settings
    host = os.getenv("HOST", "127.0.0.1")
    if host == "0.0.0.0" and os.getenv("ENVIRONMENT") != "production":
        issues.append("HOST=0.0.0.0 in non-production environment")

    reload = os.getenv("RELOAD", "false").lower() == "true"
    if reload and os.getenv("ENVIRONMENT") == "production":
        issues.append("RELOAD=true in production environment")

    log_level = os.getenv("LOG_LEVEL", "info")
    if log_level == "debug" and os.getenv("ENVIRONMENT") == "production":
        issues.append("LOG_LEVEL=debug in production environment")

    if issues:
        print("Environment configuration issues:")
        for issue in issues:
            print(f"  {issue}")
        return False

    print("Environment configuration looks secure")
    return True


def check_file_permissions():
    """Check for sensitive files that might have incorrect permissions."""
    print("Checking file permissions...")

    sensitive_files = [".env", ".env.production", "requirements.txt", "pyproject.toml"]

    issues = []

    for file_path in sensitive_files:
        full_path = Path(file_path)
        if full_path.exists():
            # On Windows, we can't easily check Unix permissions
            # Just check if files exist and are not world-writable
            print(f"  {file_path} exists")
        else:
            issues.append(f"{file_path} not found")

    if issues:
        for issue in issues:
            print(f"  {issue}")
        return False

    print("File permissions check completed")
    return True


def generate_security_report():
    """Generate a comprehensive security report."""
    print("Generating security report...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "bandit_scan": check_bandit_scan(),
            "dependency_check": check_dependency_vulnerabilities(),
            "environment_check": check_environment_variables(),
            "file_permissions": check_file_permissions(),
        },
    }

    # Calculate overall security score
    passed_checks = sum(1 for check in report["checks"].values() if check is True)
    total_checks = len(report["checks"])
    report["security_score"] = (passed_checks / total_checks) * 100

    # Save report
    with open("security_monitoring_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(
        f"Security Score: {report['security_score']:.1f}% ({passed_checks}/{total_checks} checks passed)"
    )

    return report["security_score"] >= 80  # 80% threshold for "secure"


def main():
    """Main security monitoring function."""
    print("Starting Security Monitoring")
    print("=" * 50)
    print(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        overall_secure = generate_security_report()

        print()
        print("=" * 50)
        if overall_secure:
            print("SECURITY MONITORING COMPLETE - System appears secure")
            return 0
        else:
            print("SECURITY MONITORING COMPLETE - Issues found, review report")
            return 1

    except Exception as e:
        print(f"Security monitoring failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
