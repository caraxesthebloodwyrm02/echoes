#!/usr/bin/env python3
"""
Migration Test Suite: Establish baselines for current Chat Completions API usage

This script tests all 6 identified API call locations to establish performance
and behavioral baselines before migrating to Responses API.
"""

import json
import time
from typing import Any

from assistant_v2_core import EchoesAssistantV2


class MigrationBaselineTester:
    """Test all API call patterns and establish performance baselines."""

    def __init__(self):
        print("🚀 Initializing Migration Baseline Tester...")
        self.results = {
            "test_run_timestamp": time.time(),
            "api_calls_tested": [],
            "performance_metrics": {},
            "behavioral_checks": {},
            "errors": [],
        }

        # Initialize assistant with controlled settings
        self.assistant = EchoesAssistantV2(
            enable_tools=True,  # Test tool calling
            enable_rag=False,  # Skip RAG for cleaner tests
            enable_streaming=True,  # Test streaming
            enable_status=False,  # Reduce noise
            enable_value_system=True,  # Test value guard
        )

    def run_all_tests(self) -> dict[str, Any]:
        """Run comprehensive test suite."""
        print("\n" + "=" * 60)
        print("🧪 MIGRATION BASELINE TEST SUITE")
        print("=" * 60)

        try:
            # Test 1: Simple chat (baseline)
            self.test_simple_chat()

            # Test 2: Tool calling
            self.test_tool_calling()

            # Test 3: Streaming response
            self.test_streaming()

            # Test 4: Value guard improvement
            self.test_value_guard()

            # Test 5: Directory analysis
            self.test_directory_analysis()

            # Test 6: Error handling and fallbacks
            self.test_error_handling()

            # Summary
            self.generate_summary()

        except Exception as e:
            self.results["errors"].append(f"Test suite failed: {str(e)}")
            print(f"❌ Test suite error: {e}")

        return self.results

    def time_api_call(
        self, operation_name: str, func, *args, **kwargs
    ) -> dict[str, Any]:
        """Time an API call and record metrics."""
        print(f"\n⏱️  Testing: {operation_name}")

        start_time = time.time()
        success = False
        response_length = 0
        error = None

        try:
            result = func(*args, **kwargs)
            success = True
            if isinstance(result, str):
                response_length = len(result)
            elif isinstance(result, dict) and "analysis" in result:
                response_length = len(result.get("analysis", ""))
        except Exception as e:
            error = str(e)
            self.results["errors"].append(f"{operation_name}: {error}")

        response_time = time.time() - start_time

        metrics = {
            "operation": operation_name,
            "response_time_seconds": response_time,
            "success": success,
            "response_length_chars": response_length,
            "error": error,
            "timestamp": time.time(),
        }

        self.results["api_calls_tested"].append(metrics)
        self.results["performance_metrics"][operation_name] = metrics

        status = "✅" if success else "❌"
        print(f"  {status} {operation_name}: {response_time:.2f}s")
        return metrics

    def test_simple_chat(self):
        """Test basic chat functionality."""
        result = self.time_api_call(
            "simple_chat",
            self.assistant.chat,
            "What is machine learning?",
            stream=False,
        )

        # Behavioral check
        response = result.get("response", "")
        self.results["behavioral_checks"]["simple_chat_relevant"] = (
            "machine learning" in response.lower() or "ml" in response.lower()
        )

    def test_tool_calling(self):
        """Test tool calling with simple tool request."""
        # This tests the tool calling loop (locations 2 & 3)
        result = self.time_api_call(
            "tool_calling",
            self.assistant.chat,
            "Please help me calculate 15 + 27 using a calculator tool.",
            stream=False,
        )

        # Check if tool was used (look for tool results in response)
        response = result.get("response", "")
        self.results["behavioral_checks"]["tool_calling_used"] = (
            "42" in response or "forty-two" in response.lower()
        )

    def test_streaming(self):
        """Test streaming response functionality."""
        result = self.time_api_call(
            "streaming_response",
            self.assistant.chat,
            "Explain quantum computing in simple terms.",
            stream=True,
        )

        # Streaming returns empty string, so we check timing
        self.results["behavioral_checks"]["streaming_fast_start"] = (
            result["response_time_seconds"] < 15.0
        )  # Should start quickly

    def test_value_guard(self):
        """Test value guard improvement (indirectly tests location 1)."""
        # Create a response that should trigger value improvement
        bad_response = (
            "This is a terrible response. I don't care about you. This is stupid."
        )

        start_time = time.time()
        improved = self.assistant._apply_value_guard(bad_response)
        improvement_time = time.time() - start_time

        self.results["performance_metrics"]["value_guard_improvement"] = {
            "operation": "value_guard_improvement",
            "response_time_seconds": improvement_time,
            "improvement_applied": improved is not None,
            "original_length": len(bad_response),
            "improved_length": len(improved) if improved else 0,
        }

        self.results["behavioral_checks"]["value_guard_works"] = improved is not None

    def test_directory_analysis(self):
        """Test directory analysis functionality."""
        # Use current directory for analysis
        result = self.time_api_call(
            "directory_analysis",
            self.assistant.analyze_directory,
            directory_path=".",
            output_file=None,
            max_depth=3,
        )

        analysis = result.get("response", {})
        self.results["behavioral_checks"]["directory_analysis_complete"] = (
            isinstance(analysis, dict) and "analysis" in analysis
        )

    def test_error_handling(self):
        """Test error handling and fallback mechanisms."""
        # Test with invalid model to trigger fallback
        original_model = self.assistant.model
        self.assistant.model = "invalid-model-name"

        result = self.time_api_call(
            "error_fallback", self.assistant.chat, "Hello", stream=False
        )

        # Restore model
        self.assistant.model = original_model

        self.results["behavioral_checks"]["fallback_works"] = (
            result["success"] or "fallback" in str(result.get("error", "")).lower()
        )

    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.results["api_calls_tested"])
        successful_tests = sum(
            1 for t in self.results["api_calls_tested"] if t["success"]
        )
        total_time = sum(
            t["response_time_seconds"] for t in self.results["api_calls_tested"]
        )

        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Average Response Time: {total_time/total_tests:.2f}s")
        print(f"Total Test Time: {total_time:.2f}s")
        # Performance breakdown
        print("\n⏱️  Performance Breakdown:")
        for test in self.results["api_calls_tested"]:
            status = "✅" if test["success"] else "❌"
            print(
                f"  {status} {test['operation']}: {test['response_time_seconds']:.2f}s"
            )
        # Behavioral checks
        print("\n🧠 Behavioral Checks:")
        for check, result in self.results["behavioral_checks"].items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")

        # Errors
        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"][:3]:  # Show first 3
                print(f"  • {error[:100]}...")

        print("\n📄 Full results saved to: migration_baseline_results.json")

        # Save results
        with open("migration_baseline_results.json", "w") as f:
            json.dump(self.results, f, indent=2)


def main():
    """Run the baseline test suite."""
    tester = MigrationBaselineTester()
    results = tester.run_all_tests()

    return results


if __name__ == "__main__":
    main()
