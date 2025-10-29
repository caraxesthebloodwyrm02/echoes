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

# MIT License
#
# Copyright (c) 2025 Echoes Project

"""
Configuration Diagnostics Tool
Scans all configuration files for stability and security issues
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def scan_config_files() -> Dict[str, Any]:
    """Scan all configuration files for issues"""

    issues = []
    files_scanned = []

    # Define config files to scan
    config_files = [
        "packages/core/config/__init__.py",
        "config/settings.py",
        "ai_modules/minicon/config.py",
        ".windsurf/config.json",
    ]

    workspace_root = Path(__file__).parent.parent

    for config_file in config_files:
        file_path = workspace_root / config_file
        if not file_path.exists():
            continue

        files_scanned.append(str(config_file))

        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Check for problematic patterns

        # 1. Check for extra="allow" (security risk)
        if 'extra="allow"' in content or "extra='allow'" in content:
            issues.append(
                {
                    "severity": "CRITICAL",
                    "file": config_file,
                    "issue": "extra='allow' permits unvalidated data",
                    "line": _find_line_number(content, r'extra\s*=\s*["\']allow["\']'),
                    "fix": "Change to extra='forbid'",
                }
            )

        # 2. Check for missing timeout settings
        if "timeout" not in content.lower() and config_file.endswith(".py"):
            issues.append(
                {
                    "severity": "HIGH",
                    "file": config_file,
                    "issue": "No timeout configuration found",
                    "line": None,
                    "fix": "Add timeout settings to prevent hangs",
                }
            )

        # 3. Check for hardcoded API keys (security)
        if re.search(r"(sk-|key-)[a-zA-Z0-9]{20,}", content):
            issues.append(
                {
                    "severity": "CRITICAL",
                    "file": config_file,
                    "issue": "Hardcoded API key detected",
                    "line": None,
                    "fix": "Move to environment variables",
                }
            )

        # 4. Check for infinite retries
        if re.search(r"(retry|retries)\s*=\s*(-1|None|0)", content, re.IGNORECASE):
            issues.append(
                {
                    "severity": "HIGH",
                    "file": config_file,
                    "issue": "Infinite retry configuration detected",
                    "line": _find_line_number(content, r"(retry|retries)\s*=\s*(-1|None|0)"),
                    "fix": "Set max_retries to finite value (e.g., 3)",
                }
            )

        # 5. Check for disabled validation
        if "validate" in content.lower() and "false" in content.lower():
            if re.search(r"validat\w*\s*[:=]\s*False", content, re.IGNORECASE):
                issues.append(
                    {
                        "severity": "MEDIUM",
                        "file": config_file,
                        "issue": "Validation disabled",
                        "line": _find_line_number(content, r"validat\w*\s*[:=]\s*False"),
                        "fix": "Enable validation for data integrity",
                    }
                )

    return {
        "files_scanned": files_scanned,
        "issues": issues,
        "issue_count": len(issues),
        "critical_count": sum(1 for i in issues if i["severity"] == "CRITICAL"),
        "high_count": sum(1 for i in issues if i["severity"] == "HIGH"),
    }


def _find_line_number(content: str, pattern: str) -> int:
    """Find line number of pattern match"""
    try:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return content[: match.start()].count("\n") + 1
    except Exception:
        pass
    return None


def check_workspace_settings() -> Dict[str, Any]:
    """Check workspace settings using new unified config"""
    try:
        from config.workspace_settings import validate_workspace_settings

        return validate_workspace_settings()
    except ImportError as e:
        return {
            "status": "ERROR",
            "message": f"Cannot import workspace_settings: {e}",
            "problems": [],
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Validation error: {e}",
            "problems": [],
        }


def generate_report() -> str:
    """Generate diagnostic report"""
    print("=" * 80)
    print("CONFIGURATION DIAGNOSTICS REPORT")
    print("=" * 80)
    print()

    # Scan config files
    print("Scanning configuration files...")
    scan_results = scan_config_files()

    print(f"   Files scanned: {len(scan_results['files_scanned'])}")
    for f in scan_results["files_scanned"]:
        print(f"   - {f}")
    print()

    # Report issues
    print(f"Issues found: {scan_results['issue_count']}")
    print(f"   CRITICAL: {scan_results['critical_count']}")
    print(f"   HIGH: {scan_results['high_count']}")
    print()

    if scan_results["issues"]:
        print("=" * 80)
        print("ISSUES DETECTED:")
        print("=" * 80)

        for i, issue in enumerate(scan_results["issues"], 1):
            severity_icon = "[CRITICAL]" if issue["severity"] == "CRITICAL" else "[HIGH]"
            print(f"\n{i}. {severity_icon} {issue['severity']}: {issue['file']}")
            print(f"   Issue: {issue['issue']}")
            if issue["line"]:
                print(f"   Line: {issue['line']}")
            print(f"   Fix: {issue['fix']}")

    print()
    print("=" * 80)

    # Check workspace settings
    print("\nValidating workspace settings...")
    ws_validation = check_workspace_settings()

    if ws_validation.get("status") == "ERROR":
        print(f"   ERROR: {ws_validation['message']}")
    else:
        print(f"   Status: {ws_validation['status']}")

        if ws_validation.get("problems"):
            print("\n   Problems detected:")
            for prob in ws_validation["problems"]:
                severity_icon = (
                    "[CRITICAL]"
                    if prob["severity"] == "CRITICAL"
                    else "[HIGH]" if prob["severity"] == "HIGH" else "[WARN]"
                )
                print(f"   {severity_icon} {prob['severity']}: {prob['setting']}")
                print(f"      Issue: {prob['issue']}")
                print(f"      Fix: {prob['fix']}")

    print()
    print("=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)

    recommendations = []

    if scan_results["critical_count"] > 0:
        recommendations.append("1. FIX CRITICAL ISSUES IMMEDIATELY - These can cause crashes or security breaches")

    if scan_results["high_count"] > 0:
        recommendations.append("2. Address HIGH severity issues - These affect stability")

    recommendations.extend(
        [
            "3. Review .windsurf/config.json for proper timeout settings",
            "4. Use config/workspace_settings.py for unified configuration",
            "5. Set environment variables for API keys (never hardcode)",
            "6. Enable auto-save and health checks to prevent data loss",
        ]
    )

    for rec in recommendations:
        print(f"   {rec}")

    print()
    print("=" * 80)

    # Summary
    status = "[CRITICAL]" if scan_results["critical_count"] > 0 else "[OK]"
    print(f"\nOverall Status: {status}")
    print()

    return status


if __name__ == "__main__":
    try:
        status = generate_report()
        sys.exit(1 if "CRITICAL" in status else 0)
    except Exception as e:
        print(f"\nDiagnostic tool failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(2)
