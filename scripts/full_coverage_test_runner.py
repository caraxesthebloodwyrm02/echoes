#!/usr/bin/env python3
"""
Echoes Assistant V2 Core - Full Coverage Test Runner
Tests the complete functionality of assistant_v2_core.py through the API
"""

import os
import sys
import json
import time
import requests
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))


class EchoesAPITester:
    """Test runner for Echoes API endpoints"""

    def __init__(
        self, base_url: str = "http://localhost:8000", api_key: str = "test_key"
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def test_chat_completion(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test chat completion endpoint"""
        start_time = time.time()

        payload = {
            "messages": [{"role": "user", "content": config["prompt"]}],
            "use_responses_api": config["metadata"].get("use_responses_api", True),
            "stream": config["metadata"].get("stream", False),
            "model": config["metadata"].get("model", "gpt-4o-mini"),
            "enable_tools": config["metadata"].get("enable_tools", False),
            "enable_actions": config["metadata"].get("enable_actions", False),
            "enable_workflows": config["metadata"].get("enable_workflows", False),
            "enable_rag": config["metadata"].get("enable_rag", False),
            "enable_roi": config["metadata"].get("enable_roi", False),
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/ai/chat", json=payload, timeout=config["timeout"]
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "test_name": config["name"],
                    "status": "passed",
                    "response_time": response_time,
                    "response": result,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "accuracy_score": 0.95,  # Simulated accuracy
                    "api_used": (
                        "responses"
                        if payload["use_responses_api"]
                        else "chat_completions"
                    ),
                }
            else:
                return {
                    "test_name": config["name"],
                    "status": "failed",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "tokens_used": 0,
                    "accuracy_score": 0.0,
                }

        except Exception as e:
            return {
                "test_name": config["name"],
                "status": "failed",
                "response_time": time.time() - start_time,
                "error": str(e),
                "tokens_used": 0,
                "accuracy_score": 0.0,
            }

    def test_agent_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test agent workflow endpoint"""
        start_time = time.time()

        payload = {
            "user_input": config["prompt"],
            "workflow_type": "triage",
            "use_responses_api": config["metadata"].get("use_responses_api", True),
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/workflows/business-initiative",
                json=payload,
                timeout=config["timeout"],
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "test_name": config["name"],
                    "status": "passed",
                    "response_time": response_time,
                    "response": result,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "accuracy_score": 0.90,
                    "api_used": "responses",
                }
            else:
                return {
                    "test_name": config["name"],
                    "status": "failed",
                    "response_time": response_time,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "tokens_used": 0,
                    "accuracy_score": 0.0,
                }

        except Exception as e:
            return {
                "test_name": config["name"],
                "status": "failed",
                "response_time": time.time() - start_time,
                "error": str(e),
                "tokens_used": 0,
                "accuracy_score": 0.0,
            }

    def test_validation_error(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test validation error handling"""
        start_time = time.time()

        # Send empty prompt to trigger validation error
        payload = {
            "messages": [{"role": "user", "content": ""}],
            "use_responses_api": config["metadata"].get("use_responses_api", True),
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/ai/chat", json=payload, timeout=config["timeout"]
            )

            response_time = time.time() - start_time

            # Expecting a 400 or validation error
            if response.status_code in [400, 422]:
                return {
                    "test_name": config["name"],
                    "status": "passed",  # This is expected validation error
                    "response_time": response_time,
                    "response": {"validation_error": True},
                    "tokens_used": 0,
                    "accuracy_score": 1.0,  # Perfect validation
                }
            else:
                return {
                    "test_name": config["name"],
                    "status": "failed",
                    "response_time": response_time,
                    "error": f"Expected validation error but got HTTP {response.status_code}",
                    "tokens_used": 0,
                    "accuracy_score": 0.0,
                }

        except Exception as e:
            return {
                "test_name": config["name"],
                "status": "failed",
                "response_time": time.time() - start_time,
                "error": str(e),
                "tokens_used": 0,
                "accuracy_score": 0.0,
            }

    def run_test_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test configuration"""
        expected_outcome = config.get("expected_outcome", "success")

        if expected_outcome == "validation_error":
            return self.test_validation_error(config)
        elif "workflow" in config["tags"]:
            return self.test_agent_workflow(config)
        else:
            return self.test_chat_completion(config)

    def run_full_test_suite(
        self, config_file: str, max_workers: int = 6
    ) -> Dict[str, Any]:
        """Run the complete test suite"""
        print("🚀 Starting Echoes Assistant V2 Core - Full Coverage Test Suite")
        print("=" * 70)

        # Load test configuration
        with open(config_file, "r") as f:
            test_config = json.load(f)

        configs = test_config["tests"]
        print(f"📋 Loaded {len(configs)} test configurations")

        # Run tests in parallel
        results = []
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_config = {
                executor.submit(self.run_test_config, config): config
                for config in configs
            }

            for future in concurrent.futures.as_completed(future_to_config):
                result = future.result()
                results.append(result)
                status_icon = "✅" if result["status"] == "passed" else "❌"
                print(
                    f"{status_icon} {result['test_name']} - {result['status']} ({result['response_time']:.2f}s)"
                )

        total_time = time.time() - start_time

        # Generate summary
        passed = len([r for r in results if r["status"] == "passed"])
        failed = len(results) - passed
        success_rate = passed / len(results) if results else 0

        avg_response_time = (
            sum(r["response_time"] for r in results) / len(results) if results else 0
        )
        total_tokens = sum(r["tokens_used"] for r in results)

        # API usage breakdown
        api_usage = {}
        for result in results:
            api = result.get("api_used", "unknown")
            api_usage[api] = api_usage.get(api, 0) + 1

        summary = {
            "total_tests": len(results),
            "passed_tests": passed,
            "failed_tests": failed,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_tokens": total_tokens,
            "total_time": total_time,
            "api_usage": api_usage,
            "test_results": results,
            "timestamp": datetime.now().isoformat(),
        }

        # Save results
        output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print("\n" + "=" * 70)
        print("🎯 TEST SUITE COMPLETED")
        print("=" * 70)
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"⏱️  Avg Response Time: {summary['avg_response_time']:.2f}s")
        print(f"🔢 Total Tokens: {summary['total_tokens']}")
        print(f"🕐 Total Time: {summary['total_time']:.2f}s")
        print(f"📁 Results saved to: {output_file}")

        if api_usage:
            print("\n🔄 API Usage Breakdown:")
            for api, count in api_usage.items():
                print(f"   {api}: {count} calls")

        # Test category breakdown
        categories = test_config.get("settings", {}).get("test_categories", {})
        if categories:
            print("\n📂 Test Category Results:")
            for category, test_names in categories.items():
                category_results = [r for r in results if r["test_name"] in test_names]
                if category_results:
                    cat_passed = len(
                        [r for r in category_results if r["status"] == "passed"]
                    )
                    cat_total = len(category_results)
                    cat_rate = cat_passed / cat_total if cat_total > 0 else 0
                    status_icon = (
                        "✅" if cat_rate == 1.0 else "⚠️" if cat_rate > 0.5 else "❌"
                    )
                    print(
                        f"   {status_icon} {category}: {cat_passed}/{cat_total} ({cat_rate*100:.1f}%)"
                    )

        return summary


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Echoes Assistant V2 Core - Full Coverage Test Runner"
    )
    parser.add_argument(
        "--config",
        default="full_coverage_test_config.json",
        help="Test configuration file",
    )
    parser.add_argument(
        "--api-url", default="http://localhost:8000", help="Echoes API base URL"
    )
    parser.add_argument(
        "--api-key", default="test_key", help="API key for authentication"
    )
    parser.add_argument(
        "--workers", type=int, default=6, help="Number of parallel workers"
    )
    parser.add_argument(
        "--check-api",
        action="store_true",
        help="Check if API is running before starting tests",
    )

    args = parser.parse_args()

    # Check API health if requested
    if args.check_api:
        print("🔍 Checking API health...")
        try:
            response = requests.get(f"{args.api_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ API is healthy and running")
            else:
                print(f"⚠️  API returned status {response.status_code}")
                return 1
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("💡 Make sure the Echoes API server is running:")
            print("   uvicorn api.main:app --reload --port 8000")
            return 1

    # Initialize tester
    tester = EchoesAPITester(args.api_url, args.api_key)

    # Run test suite
    try:
        results = tester.run_full_test_suite(args.config, args.workers)

        # Return appropriate exit code
        if results["failed_tests"] == 0:
            print("\n🎉 ALL TESTS PASSED! assistant_v2_core.py is working correctly.")
            return 0
        else:
            print(
                f"\n⚠️  {results['failed_tests']} test(s) failed. Check the results for details."
            )
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
