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

"""
Comprehensive Test Runner
Automates: Testing infrastructure for Q4 roadmap
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


class TestRunner:
    """Orchestrates all testing activities"""

    def __init__(self):
        self.q4_root = Path(__file__).parent.parent
        self.results = []

    def run_unit_tests(self) -> Tuple[bool, str]:
        """Run unit tests with pytest"""
        print("\n" + "=" * 60)
        print("Running Unit Tests")
        print("=" * 60)

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/unit",
                    "-v",
                    "--cov=.",
                    "--cov-report=term-missing",
                    "--cov-report=html:coverage_html",
                ],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            success = result.returncode == 0
            self.results.append(("Unit Tests", success))
            return success, result.stdout

        except FileNotFoundError:
            print("✗ pytest not found - install with: pip install pytest pytest-cov")
            self.results.append(("Unit Tests", False))
            return False, "pytest not found"

    def run_integration_tests(self) -> Tuple[bool, str]:
        """Run integration tests"""
        print("\n" + "=" * 60)
        print("Running Integration Tests")
        print("=" * 60)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/integration", "-v"],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            success = result.returncode == 0
            self.results.append(("Integration Tests", success))
            return success, result.stdout

        except FileNotFoundError:
            print("✗ pytest not found")
            self.results.append(("Integration Tests", False))
            return False, "pytest not found"

    def run_load_tests(self) -> Tuple[bool, str]:
        """Run load tests with locust"""
        print("\n" + "=" * 60)
        print("Running Load Tests")
        print("=" * 60)

        locust_file = self.q4_root / "tests" / "load" / "locustfile.py"

        if not locust_file.exists():
            print("⚠ Load test file not found - creating template")
            self.create_load_test_template()

        try:
            # Run headless load test
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "locust",
                    "-f",
                    str(locust_file),
                    "--headless",
                    "--users",
                    "10",
                    "--spawn-rate",
                    "2",
                    "--run-time",
                    "30s",
                    "--host",
                    "http://localhost:8000",
                ],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            print(result.stdout)
            success = result.returncode == 0
            self.results.append(("Load Tests", success))
            return success, result.stdout

        except FileNotFoundError:
            print("⚠ locust not found - install with: pip install locust")
            self.results.append(("Load Tests", False))
            return False, "locust not found"
        except subprocess.TimeoutExpired:
            print("⚠ Load tests timed out")
            self.results.append(("Load Tests", False))
            return False, "timeout"

    def create_load_test_template(self):
        """Create a basic load test template"""
        locust_file = self.q4_root / "tests" / "load" / "locustfile.py"
        locust_file.parent.mkdir(parents=True, exist_ok=True)

        template = '''"""
Load Testing with Locust
"""

from locust import HttpUser, task, between

class RoadmapUser(HttpUser):
    """Simulates a user interacting with the roadmap API"""
    wait_time = between(1, 3)

    @task(3)
    def view_roadmap(self):
        """View all roadmap items"""
        self.client.get("/api/roadmap")

    @task(2)
    def view_metrics(self):
        """View dashboard metrics"""
        self.client.get("/api/metrics")

    @task(1)
    def view_item(self):
        """View a specific roadmap item"""
        self.client.get("/api/roadmap/1")

    def on_start(self):
        """Called when a simulated user starts"""
        pass
'''

        with open(locust_file, "w") as f:
            f.write(template)

        print(f"✓ Created load test template: {locust_file}")

    def run_type_checking(self) -> Tuple[bool, str]:
        """Run mypy type checking"""
        print("\n" + "=" * 60)
        print("Running Type Checking")
        print("=" * 60)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "."],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
            )

            print(result.stdout)
            success = result.returncode == 0
            self.results.append(("Type Checking", success))
            return success, result.stdout

        except FileNotFoundError:
            print("⚠ mypy not found - install with: pip install mypy")
            self.results.append(("Type Checking", False))
            return False, "mypy not found"

    def run_linting(self) -> Tuple[bool, str]:
        """Run flake8 linting"""
        print("\n" + "=" * 60)
        print("Running Code Linting")
        print("=" * 60)

        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "."],
                cwd=self.q4_root,
                capture_output=True,
                text=True,
            )

            print(result.stdout if result.stdout else "✓ No linting issues found")
            success = result.returncode == 0
            self.results.append(("Linting", success))
            return success, result.stdout

        except FileNotFoundError:
            print("⚠ flake8 not found - install with: pip install flake8")
            self.results.append(("Linting", False))
            return False, "flake8 not found"

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("TEST REPORT")
        print("=" * 60)

        total = len(self.results)
        passed = sum(1 for _, success in self.results if success)

        for test_name, success in self.results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} - {test_name}")

        print("=" * 60)
        print(f"Total: {passed}/{total} test suites passed")
        print("=" * 60)

        # Save JSON report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_suites": total,
            "passed_suites": passed,
            "failed_suites": total - passed,
            "results": [{"name": name, "passed": success} for name, success in self.results],
        }

        report_file = self.q4_root / "automation" / "test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved: {report_file}")

        return passed == total


def main():
    """Main test execution"""
    runner = TestRunner()

    print("Q4 Roadmap - Comprehensive Test Suite")

    # Run all test suites
    runner.run_unit_tests()
    runner.run_integration_tests()
    runner.run_type_checking()
    runner.run_linting()
    # runner.run_load_tests()  # Uncomment when API is running

    # Generate report
    all_passed = runner.generate_report()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
