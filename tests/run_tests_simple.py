"""
Simple Test Runner for Self-Aware Routing System
"""

import subprocess
import sys
import os


def run_test_suite():
    """Run all test suites and report results."""
    print("🧪 Running Test Suite")
    print("=" * 50)

    test_suites = [
        ("Component Tests", "tests/test_self_aware_routing.py::TestComponent -v"),
        ("Smoke Tests", "tests/test_self_aware_routing.py::TestSmoke -v"),
        (
            "Client Smoke Tests",
            "tests/test_intelligent_client_smoke.py::TestIntelligentClientSmoke -v",
        ),
        (
            "Integration Tests",
            "tests/test_intelligent_client_smoke.py::TestIntegrationSmoke -v",
        ),
    ]

    all_passed = 0
    all_failed = 0

    for name, cmd in test_suites:
        print(f"\n📋 Running {name}...")

        result = subprocess.run(
            [sys.executable, "-m", "pytest"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        # Count passed/failed from output
        output = result.stdout
        if "passed" in output:
            lines = output.split("\n")
            for line in lines:
                if "passed" in line and ("failed" not in line or "0 failed" in line):
                    # Extract number before "passed"
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            passed = int(parts[i - 1])
                            all_passed += passed
                            print(f"   ✅ {passed} tests passed")
                            break
                elif "failed" in line and "passed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed":
                            failed = int(parts[i - 1])
                        elif part == "passed":
                            passed = int(parts[i - 1])
                            all_passed += passed
                            all_failed += failed
                            print(f"   ⚠️ {passed} passed, {failed} failed")
                            break

    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Total Passed: {all_passed} ✅")
    print(f"Total Failed: {all_failed} ❌")

    if all_failed == 0:
        print("\n🎉 All tests passed! System is ready.")
        print("\nRun the demo:")
        print("   python core/routing/demo_self_aware.py")
        return 0
    else:
        print(f"\n⚠️ {all_failed} tests failed. Review before deployment.")
        return 1


if __name__ == "__main__":
    exit_code = run_test_suite()
    sys.exit(exit_code)
