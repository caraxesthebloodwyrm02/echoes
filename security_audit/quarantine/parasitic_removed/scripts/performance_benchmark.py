#!/usr/bin/env python3
"""
Echoes Assistant V2 - Performance Benchmarking Script
Tests and validates performance claims: < 2.5s average response time
"""

import concurrent.futures
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from assistant_v2_core import EchoesAssistantV2
from openai import OpenAI


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for Echoes Assistant V2"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.assistant = EchoesAssistantV2(
            enable_rag=False,  # Disable for pure API performance testing
            enable_tools=False,  # Disable for pure API performance testing
            enable_streaming=False,
        )

    def benchmark_api_latency(self, iterations: int = 50) -> dict[str, Any]:
        """Benchmark raw OpenAI API latency"""
        print("🔬 Benchmarking OpenAI API Latency...")

        latencies = []
        for i in range(iterations):
            start_time = time.time()

            try:
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Count to {i+1} in words"}],
                    max_tokens=50,
                )
                latency = time.time() - start_time
                latencies.append(latency)
                print(f"  Request {i+1}/{iterations}: {latency:.3f}s")
            except Exception as e:
                print(f"  Request {i+1}/{iterations}: Failed - {e}")
                continue

        if latencies:
            return {
                "test_name": "OpenAI API Latency",
                "iterations": len(latencies),
                "mean_latency": statistics.mean(latencies),
                "median_latency": statistics.median(latencies),
                "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)],
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "success_rate": len(latencies) / iterations,
            }
        return {"error": "No successful requests"}

    def benchmark_assistant_responses(self, iterations: int = 20) -> dict[str, Any]:
        """Benchmark full assistant response times"""
        print("🤖 Benchmarking Assistant Response Times...")

        test_prompts = [
            "Hello, how are you?",
            "What is Python?",
            "Explain machine learning briefly",
            "Tell me a short joke",
            "What is the capital of France?",
        ]

        latencies = []
        for i in range(iterations):
            prompt = test_prompts[i % len(test_prompts)]
            start_time = time.time()

            try:
                response = self.assistant.chat(prompt, stream=False)
                latency = time.time() - start_time
                latencies.append(latency)
                print(
                    f"  Response {i+1}/{iterations}: {latency:.3f}s (len: {len(response)} chars)"
                )
            except Exception as e:
                print(f"  Response {i+1}/{iterations}: Failed - {e}")
                continue

        if latencies:
            return {
                "test_name": "Assistant Response Time",
                "iterations": len(latencies),
                "mean_latency": statistics.mean(latencies),
                "median_latency": statistics.median(latencies),
                "p95_latency": sorted(latencies)[int(len(latencies) * 0.95)],
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "success_rate": len(latencies) / iterations,
                "claim_validation": "PASS"
                if statistics.mean(latencies) < 2.5
                else "FAIL",
            }
        return {"error": "No successful responses"}

    def benchmark_concurrent_load(
        self, concurrent_users: int = 5, requests_per_user: int = 10
    ) -> dict[str, Any]:
        """Benchmark concurrent load handling"""
        print(
            f"⚡ Benchmarking Concurrent Load ({concurrent_users} users, {requests_per_user} reqs each)..."
        )

        def user_session(user_id: int):
            latencies = []
            for req in range(requests_per_user):
                start_time = time.time()
                try:
                    self.assistant.chat(
                        f"User {user_id} request {req+1}", stream=False
                    )
                    latency = time.time() - start_time
                    latencies.append(latency)
                except Exception as e:
                    print(f"  User {user_id} req {req+1}: Failed - {e}")
                    continue
            return latencies

        start_time = time.time()
        all_latencies = []

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_users
        ) as executor:
            futures = [
                executor.submit(user_session, i) for i in range(concurrent_users)
            ]
            for future in concurrent.futures.as_completed(futures):
                all_latencies.extend(future.result())

        total_time = time.time() - start_time

        if all_latencies:
            return {
                "test_name": "Concurrent Load Test",
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": len(all_latencies),
                "total_time": total_time,
                "throughput": len(all_latencies) / total_time,
                "mean_latency": statistics.mean(all_latencies),
                "median_latency": statistics.median(all_latencies),
                "p95_latency": sorted(all_latencies)[int(len(all_latencies) * 0.95)],
            }
        return {"error": "No successful concurrent requests"}

    def run_comprehensive_benchmark(self) -> dict[str, Any]:
        """Run all benchmarks and generate report"""
        print("🚀 Starting Comprehensive Performance Benchmark")
        print("=" * 60)

        results = {"timestamp": datetime.now().isoformat(), "benchmarks": []}

        # API Latency Benchmark
        api_results = self.benchmark_api_latency()
        results["benchmarks"].append(api_results)

        # Assistant Response Benchmark
        assistant_results = self.benchmark_assistant_responses()
        results["benchmarks"].append(assistant_results)

        # Concurrent Load Benchmark
        concurrent_results = self.benchmark_concurrent_load()
        results["benchmarks"].append(concurrent_results)

        # Generate summary
        results["summary"] = self._generate_summary(results["benchmarks"])

        return results

    def _generate_summary(self, benchmarks: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate performance summary and claim validation"""
        summary = {
            "overall_status": "PASS",
            "claim_validations": {},
            "recommendations": [],
        }

        # Check assistant response time claim (< 2.5s)
        for benchmark in benchmarks:
            if benchmark.get("test_name") == "Assistant Response Time":
                mean_time = benchmark.get("mean_latency", float("inf"))
                if mean_time < 2.5:
                    summary["claim_validations"]["response_time_claim"] = "PASS"
                    print(f"✅ Response time claim validated: {mean_time:.2f}s < 2.5s")
                else:
                    summary["claim_validations"]["response_time_claim"] = "FAIL"
                    summary["overall_status"] = "FAIL"
                    print(f"❌ Response time claim failed: {mean_time:.2f}s >= 2.5s")
                    summary["recommendations"].append(
                        f"Response time ({mean_time:.2f}s) exceeds claimed <2.5s threshold"
                    )

        # Check concurrent performance
        for benchmark in benchmarks:
            if benchmark.get("test_name") == "Concurrent Load Test":
                throughput = benchmark.get("throughput", 0)
                if throughput > 5:  # Basic throughput check
                    summary["claim_validations"]["concurrent_performance"] = "PASS"
                    print(f"✅ Concurrent performance validated: {throughput:.1f} req/s")
                else:
                    summary["claim_validations"]["concurrent_performance"] = "REVIEW"
                    summary["recommendations"].append(
                        f"Concurrent throughput ({throughput:.1f} req/s) may need optimization"
                    )

        return summary

    def save_report(self, results: dict[str, Any], filename: str = None) -> str:
        """Save benchmark results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_benchmark_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"📊 Results saved to: {filename}")
        return filename


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Echoes Assistant V2 Performance Benchmark"
    )
    parser.add_argument(
        "--iterations", type=int, default=20, help="Number of test iterations"
    )
    parser.add_argument(
        "--concurrent-users", type=int, default=3, help="Number of concurrent users"
    )
    parser.add_argument("--output", help="Output filename for results")

    args = parser.parse_args()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        return 1

    try:
        benchmark = PerformanceBenchmark()

        # Modify concurrent test based on args
        concurrent_results = benchmark.benchmark_concurrent_load(
            concurrent_users=args.concurrent_users,
            requests_per_user=max(5, args.iterations // args.concurrent_users),
        )

        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark()

        # Override concurrent results
        for i, bench in enumerate(results["benchmarks"]):
            if bench.get("test_name") == "Concurrent Load Test":
                results["benchmarks"][i] = concurrent_results
                break

        # Save and display results
        benchmark.save_report(results, args.output)

        print("\n" + "=" * 60)
        print("🏁 PERFORMANCE BENCHMARK COMPLETE")
        print("=" * 60)

        summary = results.get("summary", {})
        status = summary.get("overall_status", "UNKNOWN")
        status_icon = "✅" if status == "PASS" else "⚠️" if status == "REVIEW" else "❌"

        print(f"Overall Status: {status_icon} {status}")

        if summary.get("claim_validations"):
            print("\n📋 Claim Validations:")
            for claim, result in summary["claim_validations"].items():
                icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
                print(f"  {icon} {claim}: {result}")

        if summary.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  • {rec}")

        # Display key metrics
        for benchmark in results["benchmarks"]:
            if benchmark.get("test_name") == "Assistant Response Time":
                mean_time = benchmark.get("mean_latency", 0)
                print(
                    f"\n⏱️  Assistant Response Time: {mean_time:.2f}s (claimed: <2.5s)"
                )
            elif benchmark.get("test_name") == "Concurrent Load Test":
                throughput = benchmark.get("throughput", 0)
                print(f"⚡ Concurrent Throughput: {throughput:.1f} req/s")

        return 0 if status == "PASS" else 1

    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
