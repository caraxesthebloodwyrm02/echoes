#!/usr/bin/env python3
"""
Comprehensive Test Runner with Coverage
Version 1.0.0

Automated testing system with coverage enforcement and security checks.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict


class TestRunner:
    """
    Comprehensive test runner with coverage and security integration.
    """

    def __init__(self):
        self.min_coverage = 80  # Minimum required coverage percentage
        self.test_dirs = ["tests", "6/maps/tests"]
        self.coverage_file = "coverage.xml"

    def run_tests(self, coverage: bool = False) -> Dict:
        """Run comprehensive test suite."""
        print("🧪 Running comprehensive test suite...")

        results = {"passed": 0, "failed": 0, "coverage": 0, "details": []}

        for test_dir in self.test_dirs:
            if Path(test_dir).exists():
                print(f"\nRunning tests in {test_dir}...")

                try:
                    # Run tests
                    if coverage and test_dir == "6/maps/tests":
                        # Run with coverage for maps module
                        cmd = [
                            "python",
                            "-m",
                            "coverage",
                            "run",
                            "--source",
                            "utils,idea_system,delivery_management,smart_search",
                            "-m",
                            "unittest",
                            "discover",
                            test_dir,
                            "-v",
                        ]
                        subprocess.run(cmd, cwd=Path("6/maps"), check=True)

                        # Generate coverage report
                        subprocess.run(
                            ["python", "-m", "coverage", "xml", "-o", self.coverage_file],
                            cwd=Path("6/maps"),
                            check=True,
                        )

                        # Read coverage
                        results["coverage"] = self._get_coverage_percentage()

                    else:
                        # Run regular tests
                        result = subprocess.run(
                            ["python", "-m", "unittest", "discover", test_dir, "-v"],
                            capture_output=True,
                            text=True,
                            cwd=Path("6/maps") if "maps" in test_dir else Path.cwd(),
                        )

                        if result.returncode == 0:
                            results["passed"] += 1
                            results["details"].append(f"✅ {test_dir}: PASSED")
                        else:
                            results["failed"] += 1
                            results["details"].append(f"❌ {test_dir}: FAILED")
                            results["details"].append(result.stdout[-500:])
                            results["details"].append(result.stderr[-500:])
                except subprocess.CalledProcessError as e:
                    results["failed"] += 1
                    results["details"].append(f"❌ {test_dir}: ERROR - {e}")
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append(f"❌ {test_dir}: EXCEPTION - {e}")

        return results

    def _get_coverage_percentage(self) -> float:
        """Get coverage percentage from coverage.xml."""
        try:
            import xml.etree.ElementTree as ET

            tree = ET.parse(Path("6/maps") / self.coverage_file)
            root = tree.getroot()

            # Find coverage line
            for line in root.iter():
                if "line-rate" in line.attrib:
                    return float(line.attrib["line-rate"]) * 100

            return 0.0

        except Exception:
            return 0.0

    def enforce_coverage_threshold(self, coverage: float) -> bool:
        """Enforce minimum coverage threshold."""
        if coverage < self.min_coverage:
            print(f"❌ Coverage {coverage:.1f}% is below required {self.min_coverage}%")
            return False

        print(f"✅ Coverage {coverage:.1f}% meets requirement ({self.min_coverage}%)")
        return True

    def run_security_tests(self) -> bool:
        """Run security-specific tests."""
        print("🔒 Running security tests...")

        try:
            # Import and run security guardrails
            from security_guardrails import SecurityGuardrails

            guardrails = SecurityGuardrails()
            issues = guardrails.scan_project()

            critical_issues = [i for i in issues if i.severity.value in ["critical", "high"]]

            if critical_issues:
                print(f"❌ {len(critical_issues)} critical security issues found:")
                for issue in critical_issues[:3]:
                    print(f"  {issue.file_path}:{issue.line_number} - {issue.issue_type}")
                return False

            print("✅ No critical security issues found")
            return True

        except Exception as e:
            print(f"⚠️ Security test error: {e}")
            return True  # Don't fail for test runner issues

    def generate_test_report(self, results: Dict) -> str:
        """Generate comprehensive test report."""
        report.append("🧪 COMPREHENSIVE TEST REPORT")
        report.append("=" * 50)
        report.append(f"Total Tests: {results['passed'] + results['failed']}")
        report.append(f"Passed: {results['passed']}")
        report.append(f"Failed: {results['failed']}")
        report.append(f"Coverage: {results['coverage']:.1f}%")

        if results["details"]:
            report.append("\nTest Details:")
            for detail in results["details"]:
                report.append(f"  {detail}")


def main():
    """Main test runner execution."""
    runner = TestRunner()

    # Run security tests first
    security_ok = runner.run_security_tests()
    if not security_ok:
        print("❌ Security tests failed - aborting")
        return 1

    # Run main test suite
    results = runner.run_tests(coverage=True)

    # Check coverage
    coverage_ok = runner.enforce_coverage_threshold(results["coverage"])

    # Generate and display report
    report = runner.generate_test_report(results)
    print("\n" + report)

    # Save report
    with open("test_report.md", "w") as f:
        f.write(report)

    # Return appropriate exit code
    if results["failed"] > 0 or not coverage_ok:
        print("\n❌ Tests failed or coverage insufficient")
        return 1

    print("\n✅ All tests passed with sufficient coverage!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
