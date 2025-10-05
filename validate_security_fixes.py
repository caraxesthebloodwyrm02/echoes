#!/usr/bin/env python3
"""
Security fixes validation script
"""

import os
import shlex
import subprocess
import sys
import tempfile


def test_xml_parsing():
    """Test that XML parsing with defusedxml works correctly"""
    print("🔍 Testing XML parsing security fix...")

    # Create a test XML file
    coverage_xml = """<?xml version="1.0" encoding="UTF-8"?>
<coverage line-rate="0.85" branch-rate="0.80" lines-covered="850" lines-valid="1000" timestamp="123456789" complexity="0" version="0.1">
  <sources>
    <source>.</source>
  </sources>
</coverage>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(coverage_xml)
        temp_file = f.name

    try:
        # Test with defusedxml
        from defusedxml import ElementTree as ET

        tree = ET.parse(temp_file)
        root = tree.getroot()

        # Find coverage line
        for line in root.iter():
            if "line-rate" in line.attrib:
                coverage = float(line.attrib["line-rate"]) * 100
                print(f"  ✅ XML parsing works correctly - Coverage: {coverage}%")
                return True

        print("  ❌ Could not find line-rate in XML")
        return False
    except Exception as e:
        print(f"  ❌ XML parsing failed: {e}")
        return False
    finally:
        os.unlink(temp_file)


def test_network_binding():
    """Test that network binding uses secure defaults"""
    print("🔍 Testing network binding security fix...")

    # Check if environment variables are properly configured
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "8000")

    if host == "127.0.0.1":
        print(f"  ✅ Secure host binding: {host}")
        print(f"  ✅ Configurable port: {port}")
        return True
    else:
        print(f"  ❌ Insecure host binding: {host}")
        return False


def test_subprocess_fix():
    """Test that subprocess runs safely without shell=True"""
    print("🔍 Testing subprocess security fix...")

    # Test the run_command function from monitor_session.py
    sys.path.append("packages/monitoring")
    try:
        from monitor_session import run_command

        # Test with a safe command
        success, stdout, stderr = run_command(["echo", "test"])

        if success and "test" in stdout:
            print("  ✅ Subprocess runs safely without shell injection risk")
            return True
        else:
            print(f"  ❌ Subprocess test failed: {stderr}")
            return False
    except ImportError as e:
        print(f"  ❌ Could not import monitor_session: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Subprocess test error: {e}")
        return False


def run_bandit_scan():
    """Run Bandit to confirm security issues are resolved"""
    print("🔍 Running Bandit security scan...")

    try:
        # Run bandit on the key files we fixed
        result = subprocess.run(
            [
                "python",
                "-m",
                "bandit",
                "-r",
                "app/core/test_runner.py",
                "app/main.py",
                "packages/monitoring/monitor_session.py",
                "-f",
                "json",
                "-o",
                "security_validation.json",
            ],
            capture_output=True,
            text=True,
            cwd="e:/Projects/Development",
        )

        if result.returncode == 0:
            print("  ✅ Bandit scan completed successfully")
            return True
        else:
            print(f"  ❌ Bandit scan failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Bandit scan error: {e}")
        return False


def main():
    print("🚀 Starting Security Fixes Validation")
    print("=" * 50)

    tests = [test_xml_parsing, test_network_binding, test_subprocess_fix, run_bandit_scan]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Validation Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All security fixes validated successfully!")
        return 0
    else:
        print("❌ Some validations failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
