#!/usr/bin/env python3
"""
Load Testing Script for Model Rate Limiting

Tests model endpoints with various loads to identify rate limiting thresholds
and optimal request patterns.
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for load testing"""

    model: str
    concurrent_requests: int = 5
    total_requests: int = 50
    ramp_up_time: float = 10.0  # seconds
    test_duration: float = 300.0  # 5 minutes
    cooldown_time: float = 30.0  # seconds
    request_timeout: float = 60.0  # seconds


@dataclass
class LoadTestResult:
    """Results from a load test"""

    timestamp: str
    config: LoadTestConfig
    total_requests: int
    successful_requests: int
    failed_requests: int
    rate_limited_requests: int
    response_times: List[float]
    errors: Dict[str, int]
    throughput_rps: float
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float


class LoadTester:
    """Comprehensive load testing for model rate limiting"""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.concurrent_requests)

    def run_load_test(self) -> LoadTestResult:
        """Run comprehensive load test"""
        logger.info(f"Starting load test for {self.config.model}")
        logger.info(f"Concurrent requests: {self.config.concurrent_requests}")
        logger.info(f"Total requests: {self.config.total_requests}")

        start_time = time.time()
        futures = []
        results = []

        # Ramp up requests gradually
        request_interval = self.config.ramp_up_time / self.config.total_requests

        for i in range(self.config.total_requests):
            # Submit request
            future = self.executor.submit(self._execute_test_request, i)
            futures.append(future)

            # Respect ramp-up time
            if i < self.config.total_requests - 1:
                time.sleep(request_interval)

        # Collect results
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Request failed: {e}")
                results.append({"success": False, "response_time": 0.0, "error": str(e), "rate_limited": False})

        total_time = time.time() - start_time

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        rate_limited = [r for r in results if r.get("rate_limited", False)]

        response_times = [r["response_time"] for r in successful]
        errors = {}
        for r in failed:
            error = r.get("error", "Unknown")
            errors[error] = errors.get(error, 0) + 1

        # Calculate percentiles
        if response_times:
            response_times.sort()
            p95_idx = int(len(response_times) * 0.95)
            p99_idx = int(len(response_times) * 0.99)
            p95_response_time = response_times[min(p95_idx, len(response_times) - 1)]
            p99_response_time = response_times[min(p99_idx, len(response_times) - 1)]
            avg_response_time = statistics.mean(response_times)
        else:
            p95_response_time = p99_response_time = avg_response_time = 0.0

        throughput_rps = len(successful) / total_time if total_time > 0 else 0

        result = LoadTestResult(
            timestamp=datetime.now().isoformat(),
            config=self.config,
            total_requests=len(results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            rate_limited_requests=len(rate_limited),
            response_times=response_times,
            errors=errors,
            throughput_rps=throughput_rps,
            avg_response_time=avg_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
        )

        self.executor.shutdown(wait=True)
        return result

    def _execute_test_request(self, request_id: int) -> Dict[str, Any]:
        """Execute a single test request"""
        test_prompt = "What is the capital of France? Please explain briefly."
        start_time = time.time()

        try:
            result = subprocess.run(
                ["ollama", "run", self.config.model, test_prompt],
                capture_output=True,
                timeout=self.config.request_timeout,
            )

            # Decode output safely
            try:
                response = result.stdout.decode("utf-8", errors="replace")
                error_output = result.stderr.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                # Fallback to latin-1 which can decode any byte sequence
                response = result.stdout.decode("latin-1", errors="replace")
                error_output = result.stderr.decode("latin-1", errors="replace")

            response_time = time.time() - start_time

            if result.returncode == 0:
                # Check for rate limiting indicators in response
                rate_limited = self._detect_rate_limiting(response)

                return {
                    "success": True,
                    "response_time": response_time,
                    "response_length": len(response),
                    "rate_limited": rate_limited,
                    "request_id": request_id,
                }
            else:
                rate_limited = self._detect_rate_limiting(error_output)

                return {
                    "success": False,
                    "response_time": response_time,
                    "error": error_output,
                    "rate_limited": rate_limited,
                    "request_id": request_id,
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": "Timeout",
                "rate_limited": False,
                "request_id": request_id,
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e),
                "rate_limited": False,
                "request_id": request_id,
            }

    def _detect_rate_limiting(self, text: str) -> bool:
        """Detect rate limiting from response/error text"""
        indicators = [
            "rate limit",
            "too many requests",
            "429",
            "throttle",
            "quota exceeded",
            "try again later",
            "request limit exceeded",
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indicators)

    def run_stress_test(self) -> Dict[str, Any]:
        """Run stress test to find breaking points"""
        logger.info("Starting stress test")

        # Start with low concurrency and increase
        concurrency_levels = [1, 2, 3, 5, 8, 10]
        results = []

        for concurrency in concurrency_levels:
            logger.info(f"Testing concurrency level: {concurrency}")

            config = LoadTestConfig(
                model=self.config.model,
                concurrent_requests=concurrency,
                total_requests=min(concurrency * 10, 50),  # Scale requests with concurrency
                ramp_up_time=5.0,
            )

            tester = LoadTester(config)
            result = tester.run_load_test()
            results.append(
                {
                    "concurrency": concurrency,
                    "success_rate": result.successful_requests / result.total_requests,
                    "throughput_rps": result.throughput_rps,
                    "avg_response_time": result.avg_response_time,
                    "rate_limited_requests": result.rate_limited_requests,
                }
            )

            # Check if we're hitting rate limits
            if result.rate_limited_requests > result.total_requests * 0.3:  # 30% rate limited
                logger.warning(f"High rate limiting detected at concurrency {concurrency}")
                break

            time.sleep(10)  # Cool down between tests

        return {"stress_test_results": results, "recommended_concurrency": self._find_optimal_concurrency(results)}

    def _find_optimal_concurrency(self, results: List[Dict[str, Any]]) -> int:
        """Find optimal concurrency based on results"""
        if not results:
            return 1

        # Find concurrency with best throughput while keeping success rate > 90%
        best_concurrency = 1
        best_throughput = 0

        for result in results:
            if result["success_rate"] > 0.9 and result["throughput_rps"] > best_throughput:
                best_throughput = result["throughput_rps"]
                best_concurrency = result["concurrency"]

        return best_concurrency


def save_load_test_results(result: LoadTestResult, output_dir: Path):
    """Save load test results to file"""
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"load_test_{result.config.model.replace(':', '_')}_{result.timestamp.replace(':', '').replace('-', '').replace('T', '_').split('.')[0]}.json"
    filepath = output_dir / filename

    # Convert dataclass to dict for JSON serialization
    result_dict = {
        "timestamp": result.timestamp,
        "config": {
            "model": result.config.model,
            "concurrent_requests": result.config.concurrent_requests,
            "total_requests": result.config.total_requests,
        },
        "total_requests": result.total_requests,
        "successful_requests": result.successful_requests,
        "failed_requests": result.failed_requests,
        "rate_limited_requests": result.rate_limited_requests,
        "success_rate": result.successful_requests / result.total_requests if result.total_requests > 0 else 0,
        "throughput_rps": result.throughput_rps,
        "avg_response_time": result.avg_response_time,
        "p95_response_time": result.p95_response_time,
        "p99_response_time": result.p99_response_time,
        "errors": result.errors,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2)

    logger.info(f"Load test results saved to {filepath}")


def print_load_test_summary(result: LoadTestResult):
    """Print comprehensive load test summary"""
    print("\nLoad Test Summary")
    print(f"Model: {result.config.model}")
    print(f"Total Requests: {result.total_requests}")
    print(f"Successful: {result.successful_requests}")
    print(f"Failed: {result.failed_requests}")
    print(f"Rate Limited: {result.rate_limited_requests}")
    print(
        f"Success Rate: {(result.successful_requests / result.total_requests if result.total_requests > 0 else 0):.1%}"
    )
    print(f"Throughput: {result.throughput_rps:.1f} RPS")
    print(f"Avg Response Time: {result.avg_response_time:.2f}s")
    print(f"P95 Response Time: {result.p95_response_time:.2f}s")
    print(f"P99 Response Time: {result.p99_response_time:.2f}s")

    if result.errors:
        print("\nError Breakdown:")
        for error, count in result.errors.items():
            print(f"  {error}: {count}")


def main():
    """Main load testing function"""
    # Test configurations
    test_configs = [
        LoadTestConfig(model="mistral:7b-instruct", concurrent_requests=3, total_requests=30, ramp_up_time=10.0)
    ]

    output_dir = Path("load_test_results")
    output_dir.mkdir(exist_ok=True)

    for config in test_configs:
        try:
            # Run load test
            tester = LoadTester(config)
            result = tester.run_load_test()

            # Save and display results
            save_load_test_results(result, output_dir)
            print_load_test_summary(result)

            # Optional: Run stress test
            if input(f"Run stress test for {config.model}? (y/N): ").lower().startswith("y"):
                stress_results = tester.run_stress_test()

                stress_file = (
                    output_dir
                    / f"stress_test_{config.model.replace(':', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(stress_file, "w", encoding="utf-8") as f:
                    json.dump(stress_results, f, indent=2)

                print("\nStress Test Results:")
                for r in stress_results["stress_test_results"]:
                    print(
                        f"Concurrency {r['concurrency']}: {r['throughput_rps']:.1f} RPS, {r['success_rate']:.1%} success"
                    )
                print(f"Recommended concurrency: {stress_results['recommended_concurrency']}")

        except Exception as e:
            logger.error(f"Load test failed for {config.model}: {e}")


if __name__ == "__main__":
    main()
