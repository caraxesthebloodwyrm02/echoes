"""
Comprehensive Test Runner for Self-Aware Routing System
Runs all tests and generates a report on system readiness.
"""

import asyncio
import subprocess
import sys
import os
from typing import Dict, List, Tuple


class TestRunner:
    """Runs all tests and generates a readiness report."""

    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.total_passed = 0
        self.total_failed = 0

    async def run_tests(self) -> Dict:
        """Run all test suites and collect results."""
        print("🧪 Running Comprehensive Test Suite")
        print("=" * 60)

        test_suites = [
            ("Component Tests", "tests/test_self_aware_routing.py::TestComponent"),
            ("Smoke Tests", "tests/test_self_aware_routing.py::TestSmoke"),
            (
                "Basic Routing Tests",
                "tests/test_self_aware_routing.py::TestSelfAwareRouter::test_router_initialization",
                "tests/test_self_aware_routing.py::TestSelfAwareRouter::test_register_component",
                "tests/test_self_aware_routing.py::TestSelfAwareRouter::test_route_request_healthy",
                "tests/test_self_aware_routing.py::TestSelfAwareRouter::test_route_request_unhealthy",
            ),
            (
                "Client Smoke Tests",
                "tests/test_intelligent_client_smoke.py::TestIntelligentClientSmoke",
            ),
            (
                "Integration Tests",
                "tests/test_intelligent_client_smoke.py::TestIntegrationSmoke",
            ),
        ]

        for suite in test_suites:
            if isinstance(suite, tuple):
                name = suite[0]
                tests = suite[1:] if len(suite) > 1 else [suite[1]]
            else:
                name = suite
                tests = [suite]

            print(f"\n📋 Running {name}...")
            passed, failed, total = await self._run_test_suite(tests)

            self.results[name] = {
                "passed": passed,
                "failed": failed,
                "total": total,
                "success_rate": (passed / total * 100) if total > 0 else 0,
            }

            self.total_tests += total
            self.total_passed += passed
            self.total_failed += failed

            status = "✅ PASSED" if failed == 0 else f"❌ FAILED ({failed} failures)"
            print(f"   {status} - {passed}/{total} tests passed")

        return self.results

    async def _run_test_suite(self, test_paths: List[str]) -> Tuple[int, int, int]:
        """Run a specific test suite."""
        all_passed = 0
        all_failed = 0
        all_total = 0

        for test_path in test_paths:
            try:
                # Run pytest and capture output
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", test_path, "-q", "--tb=no"],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                )

                # Parse results from pytest output
                if result.returncode == 0:
                    # Look for the summary line like "5 passed in 0.05s"
                    output_lines = result.stdout.strip().split("\n")
                    for line in output_lines:
                        if " passed" in line and (
                            " failed" not in line or " 0 failed" in line
                        ):
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "passed":
                                    passed = int(parts[i - 1])
                                    all_passed += passed
                                    all_total += passed
                                    break
                else:
                    # Parse failures
                    output_lines = result.stdout.strip().split("\n")
                    for line in output_lines:
                        if " failed" in line and " passed" in line:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "failed":
                                    failed = int(parts[i - 1])
                                    all_failed += failed
                                elif part == "passed":
                                    passed = int(parts[i - 1])
                                    all_passed += passed
                                    all_total += passed + failed
                                    break

            except Exception as e:
                print(f"   Error running {test_path}: {e}")
                all_failed += 1
                all_total += 1

        return all_passed, all_failed, all_total

    def generate_report(self):
        """Generate a comprehensive readiness report."""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        overall_success_rate = (
            (self.total_passed / self.total_tests * 100) if self.total_tests > 0 else 0
        )

        print("\n🎯 Overall Results:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.total_passed} ✅")
        print(f"   Failed: {self.total_failed} ❌")
        print(f"   Success Rate: {overall_success_rate:.1f}%")

        print("\n📋 Suite Breakdown:")
        for suite_name, results in self.results.items():
            status_icon = "✅" if results["failed"] == 0 else "❌"
            print(f"   {status_icon} {suite_name}:")
            print(
                f"      Passed: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)"
            )
            if results["failed"] > 0:
                print(f"      Failed: {results['failed']}")

        print("\n🚀 System Readiness Assessment:")
        if overall_success_rate >= 95:
            print("   🌟 EXCELLENT - System is production-ready!")
            print("   ✨ All critical features working perfectly")
        elif overall_success_rate >= 85:
            print("   ✅ GOOD - System is ready for deployment")
            print("   🔧 Minor issues that don't affect core functionality")
        elif overall_success_rate >= 70:
            print("   ⚠️ ACCEPTABLE - System needs attention before production")
            print("   🛠️ Some features may have issues")
        else:
            print("   ❌ NOT READY - System requires significant fixes")
            print("   🚨 Critical issues must be resolved")

        # Recommendations
        print("\n💡 Recommendations:")
        if self.total_failed == 0:
            print("   • All tests passed! System is ready for production use")
            print("   • Consider running the demo to see the system in action")
        else:
            print("   • Review and fix failing tests before deployment")
            print("   • Focus on integration tests for end-to-end functionality")
            print("   • Check test logs for specific failure details")

        return {
            "overall_success_rate": overall_success_rate,
            "total_tests": self.total_tests,
            "total_passed": self.total_passed,
            "total_failed": self.total_failed,
            "ready_for_production": overall_success_rate >= 85,
        }


async def main():
    """Main test runner."""
    runner = TestRunner()

    # Run all tests
    await runner.run_tests()

    # Generate report
    report = runner.generate_report()

    # Return exit code based on readiness
    if report["ready_for_production"]:
        print("\n🎉 System is READY! Run the demo with:")
        print("   python core/routing/demo_self_aware.py")
        return 0
    else:
        print("\n⚠️ System needs fixes before demo")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
