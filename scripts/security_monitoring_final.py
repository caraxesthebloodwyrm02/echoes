#!/usr/bin/env python3
"""
Security Monitoring Script

This script performs automated security checks on the codebase,
including dependency scanning, code analysis, and configuration checks.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return (result.returncode == 0, result.stdout.strip(), result.stderr.strip())
    except Exception as e:
        return False, "", str(e)


def check_bandit_scan() -> Tuple[bool, str]:
    """Run Bandit security scanner on the codebase."""
    print("🔍 Running Bandit security scan...")

    # Check if Bandit is installed
    bandit_installed, _, _ = run_command([sys.executable, "-m", "pip", "show", "bandit"])
    if not bandit_installed:
        print("  ⚠️ Bandit not found. Installing...")
        success, _, err = run_command([sys.executable, "-m", "pip", "install", "bandit"])
        if not success:
            return False, f"Failed to install Bandit: {err}"

    # Run Bandit scan
    bandit_cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        "app",
        "packages",
        "-f",
        "json",
        "-o",
        "bandit-report.json",
    ]

    success, stdout, stderr = run_command(bandit_cmd)

    # Parse results
    if os.path.exists("bandit-report.json"):
        with open("bandit-report.json", "r") as f:
            results = json.load(f)

        issues = results.get("results", [])
        high_severity = [i for i in issues if i.get("issue_severity") == "HIGH"]
        medium_severity = [i for i in issues if i.get("issue_severity") == "MEDIUM"]

        summary = (
            f"Bandit found {len(high_severity)} HIGH and {len(medium_severity)} MEDIUM severity issues. "
            f"See bandit-report.json for details."
        )

        if high_severity:
            return False, f"❌ {summary}"
        return True, f"✅ {summary}"

    return False, f"❌ Bandit scan failed: {stderr or 'No report generated'}"


def check_dependencies() -> Tuple[bool, str]:
    """Check for vulnerable dependencies using safety."""
    print("🔍 Checking for vulnerable dependencies...")

    # Check if safety is installed
    safety_installed, _, _ = run_command([sys.executable, "-m", "pip", "show", "safety"])
    if not safety_installed:
        print("  ⚠️ Safety not found. Installing...")
        success, _, err = run_command([sys.executable, "-m", "pip", "install", "safety"])
        if not success:
            return False, f"Failed to install safety: {err}"

    # Run safety check
    success, stdout, stderr = run_command([sys.executable, "-m", "safety", "check", "--json"])

    if not success and "Vulnerabilities found" in stderr:
        return False, f"❌ Safety check found vulnerabilities: {stderr}"

    return True, "✅ No known vulnerabilities found in dependencies"


def check_environment() -> Tuple[bool, str]:
    """Check environment configuration for security issues."""
    print("🔍 Checking environment configuration...")

    issues = []

    # Check if .env files contain sensitive data
    env_files = [".env", ".env.production"]
    sensitive_patterns = ["SECRET_KEY", "PASSWORD", "API_KEY", "TOKEN"]

    for env_file in env_files:
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                content = f.read()
                for pattern in sensitive_patterns:
                    if pattern in content:
                        issues.append(f"⚠️  {env_file} contains potential sensitive data: {pattern}")

    # Check file permissions
    sensitive_files = [".env", ".env.production", "app/main.py"]
    for file in sensitive_files:
        if os.path.exists(file):
            if platform.system() != "Windows":
                mode = os.stat(file).st_mode
                if mode & 0o777 != 0o600:  # Check if permissions are too open
                    issues.append(f"⚠️  {file} has insecure permissions: {oct(mode)[-3:]}")

    if issues:
        return False, "\n  ".join(["❌ Environment issues found:"] + issues)
    return True, "✅ Environment configuration looks secure"


def generate_report(
    bandit_result: Tuple[bool, str], deps_result: Tuple[bool, str], env_result: Tuple[bool, str]
) -> Dict:
    """Generate a security report."""
    timestamp = datetime.now().isoformat()
    all_checks_passed = all([bandit_result[0], deps_result[0], env_result[0]])

    report = {
        "timestamp": timestamp,
        "overall_status": "PASS" if all_checks_passed else "FAIL",
        "checks": {
            "code_scan": {
                "status": "PASS" if bandit_result[0] else "FAIL",
                "message": bandit_result[1],
            },
            "dependencies": {
                "status": "PASS" if deps_result[0] else "FAIL",
                "message": deps_result[1],
            },
            "environment": {
                "status": "PASS" if env_result[0] else "WARNING",
                "message": env_result[1],
            },
        },
        "recommendations": [],
    }

    # Add recommendations
    if not bandit_result[0]:
        report["recommendations"].append(
            "Review and fix Bandit security findings in bandit-report.json"
        )
    if not deps_result[0]:
        report["recommendations"].append(
            "Update vulnerable dependencies using 'pip install --upgrade PACKAGE'"
        )
    if not env_result[0]:
        report["recommendations"].append("Review environment configuration and file permissions")

    return report


def main() -> int:
    """Run all security checks and generate a report."""
    print("🚀 Starting Security Audit")
    print("=" * 50)

    # Run security checks
    bandit_result = check_bandit_scan()
    deps_result = check_dependencies()
    env_result = check_environment()

    # Generate and print report
    report = generate_report(bandit_result, deps_result, env_result)

    print("\n📊 Security Report")
    print("=" * 50)
    print(f"📅 {report['timestamp']}")
    print(f"🏆 Overall Status: {report['overall_status']}")
    print("\n🔍 Check Results:")

    for check_name, result in report["checks"].items():
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"\n{status_icon} {check_name.upper()} - {result['status']}")
        print(f"   {result['message']}")

    if report["recommendations"]:
        print("\n📝 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")

    # Save report to file
    with open("security-audit-report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📝 Full report saved to security-audit-report.json")
    print("=" * 50)

    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n🛑 Security audit cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during security audit: {str(e)}")
        sys.exit(1)
