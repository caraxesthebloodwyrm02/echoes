#!/usr/bin/env python3
"""
Load Testing Suite
Automates Task: "Load Testing Suite" - Comprehensive performance testing
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class LoadTestingSuite:
    """Automated load testing for Q4 applications"""

    def __init__(self):
        self.q4_root = Path(__file__).parent.parent
        self.project_root = self.q4_root.parent
        self.test_results = []

    def run_locust_tests(self) -> Dict[str, Any]:
        """Run load tests with Locust"""
        print("\n" + "=" * 60)
        print("Running Locust Load Tests")
        print("=" * 60)

        locust_file = self.q4_root / "tests" / "load" / "locustfile.py"

        if not locust_file.exists():
            print("⚠ Load test file not found - creating template")
            self.create_locust_template()

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
            if result.stderr:
                print("STDERR:", result.stderr)

            success = result.returncode == 0

            # Extract key metrics from output
            metrics = self._parse_locust_output(result.stdout)

            result_data = {
                "tool": "locust",
                "status": "completed" if success else "failed",
                "total_requests": metrics.get("total_requests", 0),
                "total_failures": metrics.get("total_failures", 0),
                "avg_response_time": metrics.get("avg_response_time", 0),
                "max_response_time": metrics.get("max_response_time", 0),
                "requests_per_second": metrics.get("requests_per_second", 0),
                "report_file": str(locust_file),
            }

            print(
                f"✓ Locust tests complete - {result_data['total_requests']} requests, {result_data['requests_per_second']:.1f} RPS"
            )
            return result_data

        except FileNotFoundError:
            print("⚠ Locust not found - install with: pip install locust")
            return {"tool": "locust", "status": "not_installed"}
        except subprocess.TimeoutExpired:
            print("⚠ Load tests timed out")
            return {"tool": "locust", "status": "timeout"}
        except Exception as e:
            print(f"✗ Load test error: {e}")
            return {"tool": "locust", "status": "error", "error": str(e)}

    def _parse_locust_output(self, output: str) -> Dict[str, float]:
        """Parse key metrics from Locust output"""
        metrics = {}

        # Simple parsing for key metrics
        lines = output.split("\n")
        for line in lines:
            if "Total" in line and "requests" in line:
                try:
                    parts = line.split()
                    if len(parts) >= 4:
                        metrics["total_requests"] = int(parts[1])
                        metrics["total_failures"] = int(parts[3])
                except (ValueError, IndexError) as error:
                    print(f"⚠ Failed to parse total requests line '{line}': {error}")
            elif "Average" in line and "response" in line:
                try:
                    parts = line.split()
                    if len(parts) >= 3:
                        metrics["avg_response_time"] = float(parts[2])
                except (ValueError, IndexError) as error:
                    print(f"⚠ Failed to parse average response line '{line}': {error}")
            elif "Maximum" in line and "response" in line:
                try:
                    parts = line.split()
                    if len(parts) >= 3:
                        metrics["max_response_time"] = float(parts[2])
                except (ValueError, IndexError) as error:
                    print(f"⚠ Failed to parse max response line '{line}': {error}")
            elif "RPS" in line:
                try:
                    parts = line.split()
                    if len(parts) >= 2:
                        metrics["requests_per_second"] = float(parts[1])
                except (ValueError, IndexError) as error:
                    print(f"⚠ Failed to parse RPS line '{line}': {error}")

        return metrics

    def create_locust_template(self):
        """Create a basic Locust test template"""
        locust_file = self.q4_root / "tests" / "load" / "locustfile.py"
        locust_file.parent.mkdir(parents=True, exist_ok=True)

        template = '''"""
Load Testing with Locust for Q4 Applications
"""

from locust import HttpUser, task, between, events
import json
import time

class Q4User(HttpUser):
    """Simulates a user interacting with Q4 applications"""

    wait_time = between(1, 3)

    def on_start(self):
        """Called when a simulated user starts"""
        self.headers = {"Content-Type": "application/json"}

    @task(3)
    def view_roadmap(self):
        """Test roadmap API endpoint"""
        response = self.client.get("/api/roadmap", headers=self.headers)
        if response.status_code != 200:
            response.failure(f"Got status code {response.status_code}")

    @task(2)
    def view_metrics(self):
        """Test metrics API endpoint"""
        response = self.client.get("/api/metrics", headers=self.headers)
        if response.status_code != 200:
            response.failure(f"Got status code {response.status_code}")

    @task(1)
    def create_item(self):
        """Test item creation endpoint"""
        data = {
            "title": f"Test Item {time.time()}",
            "phase": "Discovery",
            "status": "Not Started",
            "priority": "Medium",
            "owner": "Load Test"
        }
        response = self.client.post("/api/roadmap", json=data, headers=self.headers)
        if response.status_code not in [200, 201]:
            response.failure(f"Got status code {response.status_code}")

    @task(1)
    def heavy_computation(self):
        """Test computationally intensive endpoint"""
        # Simulate UBI simulation request
        data = {
            "ubi_amount": 1000,
            "eligibility_threshold": 30000,
            "phase_out_rate": 0.5
        }
        response = self.client.post("/api/simulate", json=data, headers=self.headers)
        if response.status_code != 200:
            response.failure(f"Got status code {response.status_code}")

@events.request.add_listener
def hook_request_success(request_type, name, response_time, response_length, **kwargs):
    """Log successful requests"""
    print(f"✓ {request_type} {name} - {response_time}ms")

@events.request.add_listener
def hook_request_failure(request_type, name, response_time, exception, **kwargs):
    """Log failed requests"""
    print(f"✗ {request_type} {name} - {exception}")
'''

        with open(locust_file, "w") as f:
            f.write(template)

        print(f"✓ Created Locust test template: {locust_file}")

    def run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests to find breaking points"""
        print("\n" + "=" * 60)
        print("Running Stress Tests")
        print("=" * 60)

        stress_results = []

        # Test with increasing load
        user_counts = [1, 5, 10, 25, 50]

        for users in user_counts:
            print(f"\nTesting with {users} concurrent users...")

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "locust",
                        "-f",
                        "tests/load/locustfile.py",
                        "--headless",
                        "--users",
                        str(users),
                        "--spawn-rate",
                        str(min(users, 5)),
                        "--run-time",
                        "10s",
                        "--host",
                        "http://localhost:8000",
                    ],
                    cwd=self.q4_root,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                metrics = self._parse_locust_output(result.stdout)
                stress_results.append(
                    {
                        "users": users,
                        "success": result.returncode == 0,
                        "metrics": metrics,
                    }
                )

                if result.returncode == 0:
                    print(f"✓ {users} users: {metrics.get('requests_per_second', 0):.1f} RPS")
                else:
                    print(f"✗ {users} users: Failed")

            except subprocess.TimeoutExpired:
                print(f"⚠ {users} users: Timeout")
                stress_results.append({"users": users, "success": False, "error": "timeout"})
            except Exception as e:
                print(f"✗ {users} users: {e}")
                stress_results.append({"users": users, "success": False, "error": str(e)})

        return {
            "tool": "stress_test",
            "status": "completed",
            "tests": stress_results,
            "max_successful_users": max((r["users"] for r in stress_results if r["success"]), default=0),
        }

    def generate_load_report(self):
        """Generate comprehensive load testing report"""
        print("\n" + "=" * 60)
        print("LOAD TESTING REPORT")
        print("=" * 60)

        # Run all load tests
        locust_results = self.run_locust_tests()
        stress_results = self.run_stress_tests()

        self.test_results.extend([locust_results, stress_results])

        # Calculate overall performance metrics
        total_requests = sum(
            r.get("total_requests", 0) for r in self.test_results if isinstance(r, dict) and "total_requests" in r
        )

        successful_tests = sum(1 for r in self.test_results if isinstance(r, dict) and r.get("status") == "completed")

        # Determine performance level
        if locust_results.get("status") == "completed" and stress_results.get("max_successful_users", 0) >= 25:
            performance_level = "EXCELLENT"
        elif locust_results.get("status") == "completed" and stress_results.get("max_successful_users", 0) >= 10:
            performance_level = "GOOD"
        elif locust_results.get("status") == "completed":
            performance_level = "FAIR"
        else:
            performance_level = "NEEDS IMPROVEMENT"

        print("\n" + "=" * 60)
        print(f"Performance Level: {performance_level}")
        print(f"Total Requests: {total_requests}")
        print(f"Successful Tests: {successful_tests}/{len(self.test_results)}")
        print("=" * 60)

        # Generate recommendations
        recommendations = []

        if locust_results.get("total_failures", 0) > 0:
            failure_rate = locust_results["total_failures"] / max(locust_results["total_requests"], 1) * 100
            if failure_rate > 5:
                recommendations.append("High failure rate detected - investigate error handling")

        if locust_results.get("avg_response_time", 0) > 1000:
            recommendations.append("Slow response times detected - optimize performance")

        if stress_results.get("max_successful_users", 0) < 10:
            recommendations.append("Low concurrent user capacity - scale infrastructure")

        if not recommendations:
            recommendations.append("Performance looks good - consider increasing test load")

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "task": "Load Testing Suite",
            "status": "Completed",
            "performance_level": performance_level,
            "total_requests": total_requests,
            "successful_tests": successful_tests,
            "test_results": self.test_results,
            "recommendations": recommendations,
            "metrics": {
                "avg_response_time": locust_results.get("avg_response_time", 0),
                "max_response_time": locust_results.get("max_response_time", 0),
                "requests_per_second": locust_results.get("requests_per_second", 0),
                "max_concurrent_users": stress_results.get("max_successful_users", 0),
            },
        }

        report_file = self.q4_root / "automation" / "load_testing_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved: {report_file}")

        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        return performance_level in ["EXCELLENT", "GOOD"]


def main():
    """Main load testing execution"""
    tester = LoadTestingSuite()

    print("Q4 Roadmap - Load Testing Suite")

    success = tester.generate_load_report()

    print("\n✓ Load Testing Suite - COMPLETED")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
