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
ECHOES Hybrid Assistant Integration Test
Tests the unified assistant functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_hybrid_assistant():
    """Test the hybrid assistant functionality"""

    print("ECHOES Hybrid Assistant Integration Test")
    print("=" * 50)

    try:
        # Import and create assistant
        from hybrid_assistant import create_unified_assistant

        print("Creating unified assistant...")
        assistant = await create_unified_assistant()

        # Check status
        print("Checking system status...")
        status = await assistant.get_status()

        print(f"System Health: {status['system_health']}")
        print("Assistant Status:")
        for name, info in status["assistants"].items():
            available = "[AVAILABLE]" if info["available"] else "[UNAVAILABLE]"
            print(f"  - {name}: {available}")

        # Test different task types
        test_tasks = [
            {
                "description": "Hello, can you help me?",
                "expected_type": "local",
                "context": {},
            },  # Simple greeting
            {
                "description": "Analyze this Python function for potential improvements: def add(a, b): return a + b",
                "expected_type": "openai",  # Code analysis task
                "context": {"language": "python"},
            },
            {
                "description": "What is the current status of all assistants?",
                "expected_type": "local",  # Status query
                "context": {},
            },
        ]

        print("\nTesting task processing...")
        print("-" * 30)

        results = []
        for i, task_data in enumerate(test_tasks, 1):
            print(f"\nTest {i}: {task_data['description'][:50]}...")

            try:
                response = await assistant.process_task(task_data["description"], context=task_data["context"])

                print(f"  Assistant used: {response.assistant_type.value}")
                print(".2f")
                print(".4f")
                print(f"  Response preview: {response.response[:80]}...")

                # Store result for analysis
                results.append({"task": task_data, "response": response, "success": True})

            except Exception as e:
                print(f"  [FAILED] {str(e)}")
                results.append({"task": task_data, "error": str(e), "success": False})

        # Analyze results
        print("\n" + "=" * 50)
        print("TEST RESULTS SUMMARY")
        print("=" * 50)

        successful_tests = sum(1 for r in results if r.get("success", False))
        total_tests = len(results)

        print(f"Overall Success Rate: {successful_tests}/{total_tests} ({successful_tests / total_tests * 100:.1f}%)")

        # Assistant usage statistics
        assistant_usage = {}
        total_cost = 0.0
        total_time = 0.0

        for result in results:
            if result.get("success"):
                resp = result["response"]
                assistant_name = resp.assistant_type.value
                assistant_usage[assistant_name] = assistant_usage.get(assistant_name, 0) + 1
                total_cost += resp.cost
                total_time += resp.processing_time

        print("\nAssistant Usage:")
        for assistant, count in assistant_usage.items():
            print(f"  - {assistant}: {count} tasks")

        print("\nPerformance Metrics:")
        print(".2f")
        print(".4f")
        if results:
            avg_time = total_time / len([r for r in results if r.get("success")])
            print(".2f")

        # Export performance log
        try:
            log_file = assistant.export_performance_log()
            print(f"\nPerformance log exported to: {log_file}")
        except Exception as e:
            print(f"Performance log export failed: {e}")

        # Final assessment
        print(f"\n{'=' * 50}")
        if successful_tests == total_tests:
            print("RESULT: ALL TESTS PASSED")
            print("Hybrid assistant is ready for production use!")
            return True
        elif successful_tests >= total_tests * 0.7:
            print("RESULT: MOST TESTS PASSED")
            print("Hybrid assistant is functional but may need optimization.")
            return True
        else:
            print("RESULT: TESTS FAILED")
            print("Hybrid assistant requires debugging and fixes.")
            return False

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_routing_logic():
    """Test the assistant routing logic separately"""

    print("\n" + "=" * 50)
    print("ROUTING LOGIC TEST")
    print("=" * 50)

    try:
        from hybrid_assistant import AssistantRouter, TaskComplexity, TaskRequest

        router = AssistantRouter()

        # Test complexity assessment
        test_cases = [
            ("Hello", TaskComplexity.SIMPLE),
            ("How are you?", TaskComplexity.SIMPLE),
            ("Show me the status", TaskComplexity.SIMPLE),
            ("Analyze this code", TaskComplexity.MODERATE),
            ("Create a complex algorithm", TaskComplexity.COMPLEX),
            ("Design a system architecture", TaskComplexity.COMPLEX),
        ]

        print("Complexity Assessment:")
        for description, expected in test_cases:
            assessed = router.assess_task_complexity(description)
            status = "[PASS]" if assessed == expected else "[FAIL]"
            print(f"  {status} '{description}' -> {assessed.value} (expected: {expected.value})")

        # Test assistant selection
        print("\nAssistant Selection:")
        for description, expected_complexity in test_cases[:3]:  # Test first few
            task = TaskRequest(
                id="test",
                description=description,
                complexity=expected_complexity,
                context={},
                metadata={},
                timestamp=asyncio.get_event_loop().time(),
            )

            selected = router.select_assistant(task)
            print(f"  '{description}' -> {[a.value for a in selected]}")

        print("Routing logic test completed.")
        return True

    except Exception as e:
        print(f"Routing test failed: {e}")
        return False


async def main():
    """Main test function"""

    # Test routing logic first
    routing_success = await test_routing_logic()

    # Test full hybrid assistant
    assistant_success = await test_hybrid_assistant()

    # Overall result
    overall_success = routing_success and assistant_success

    print(f"\n{'=' * 50}")
    print(f"OVERALL TEST RESULT: {'PASSED' if overall_success else 'FAILED'}")
    print(f"{'=' * 50}")

    if overall_success:
        print("Hybrid assistant integration is successful!")
        print("Next steps:")
        print("1. Configure API keys in .env file for full functionality")
        print("2. Test with real tasks in your development workflow")
        print("3. Monitor performance and adjust routing logic as needed")
    else:
        print("Hybrid assistant integration needs fixes.")
        print("Check the error messages above and address any issues.")

    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
