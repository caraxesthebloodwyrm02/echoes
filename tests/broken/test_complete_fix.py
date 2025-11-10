#!/usr/bin/env python3
"""
Complete test of model selection fixes
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import IntelligentAssistant


def test_complete_fix():
    """Test all model selection fixes."""

    print("🧪 Complete Model Selection Fix Test")
    print("=" * 60)

    # Initialize assistant
    assistant = IntelligentAssistant()

    # Test cases with expected models
    test_cases = [
        {
            "query": "What's the capital of France?",
            "expected_complexity": "low",
            "expected_model": "gpt-3.5-turbo",
            "reason": "Simple factual question",
        },
        {
            "query": "Explain quantum computing in detail",
            "expected_complexity": "high",
            "expected_model": "gpt-4",
            "reason": "Complex scientific topic with detail request",
        },
        {
            "query": "List 3 benefits of exercise",
            "expected_complexity": "low",
            "expected_model": "gpt-3.5-turbo",
            "reason": "Simple list generation",
        },
        {
            "query": "Compare machine learning and deep learning approaches",
            "expected_complexity": "medium",
            "expected_model": "gpt-3.5-turbo",
            "reason": "Technical comparison",
        },
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test['reason']}")
        print(f"Query: {test['query']}")
        print("-" * 60)

        try:
            # Get response
            response = assistant.chat(test["query"])

            # Get the actual model used
            actual_model = assistant.get_last_used_model()

            # Get analysis info
            analysis = assistant._last_analysis

            print(f"Expected Complexity: {test['expected_complexity']}")
            print(f"Actual Complexity: {analysis.get('complexity', 'unknown')}")
            print(f"Expected Model: {test['expected_model']}")
            print(f"Actual Model: {actual_model}")

            # Check results
            complexity_match = analysis.get("complexity") == test["expected_complexity"]
            model_match = actual_model == test["expected_model"]

            if complexity_match and model_match:
                print("✅ PASS - Both complexity and model selection correct")
                status = "PASS"
            elif complexity_match:
                print(
                    "⚠️  PARTIAL - Complexity correct, model selection needs adjustment"
                )
                status = "PARTIAL"
            elif model_match:
                print(
                    "⚠️  PARTIAL - Model correct, complexity analysis needs adjustment"
                )
                status = "PARTIAL"
            else:
                print("❌ FAIL - Both complexity and model selection incorrect")
                status = "FAIL"

            # Check footer
            if "Auto-selected" in response:
                print("✅ Footer shows model selection info")
                footer_ok = True
            else:
                print("⚠️  Footer doesn't show model selection info")
                footer_ok = False

            results.append(
                {
                    "test": i,
                    "query": test["query"],
                    "expected_complexity": test["expected_complexity"],
                    "actual_complexity": analysis.get("complexity", "unknown"),
                    "expected_model": test["expected_model"],
                    "actual_model": actual_model,
                    "status": status,
                    "footer_ok": footer_ok,
                }
            )

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(
                {"test": i, "query": test["query"], "status": "ERROR", "error": str(e)}
            )

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"{'Test':<5} | {'Query':<35} | {'Status':<10} | {'Footer'}")
    print("-" * 60)

    for result in results:
        if "error" in result:
            print(
                f"Test {result['test']:<3} | {result['query'][:35]:<35} | {'ERROR':<10} | {'N/A':<8}"
            )
        else:
            footer = "✅" if result.get("footer_ok", False) else "⚠️"
            print(
                f"Test {result['test']:<3} | {result['query'][:35]:<35} | {result['status']:<10} | {footer:<8}"
            )

    # Count results
    pass_count = sum(1 for r in results if r.get("status") == "PASS")
    partial_count = sum(1 for r in results if r.get("status") == "PARTIAL")
    fail_count = sum(1 for r in results if r.get("status") == "FAIL")
    error_count = sum(1 for r in results if r.get("status") == "ERROR")

    print(
        f"\n📈 RESULTS: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL, {error_count} ERROR"
    )

    if pass_count == len(results):
        print("🎉 ALL TESTS PASSED! Model selection is working perfectly.")
    elif pass_count + partial_count == len(results):
        print("✅ GOOD PROGRESS! Most tests passing, some fine-tuning needed.")
    else:
        print("⚠️  NEEDS WORK! Several issues still need to be addressed.")


if __name__ == "__main__":
    test_complete_fix()
