#!/usr/bin/env python3
"""
Enhanced test to demonstrate superstition filtering (kushongskaar) from patterns.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import LogicSystem, LogicType


def test_superstition_filtering():
    """Demonstrate superstition filtering with better pattern matching."""

    print("🧠 Enhanced Superstition Filtering Demonstration")
    print("=" * 60)
    print("Testing 'kushongskaar' - culturally implemented beliefs")
    print("vs reasoned from scientific understanding\n")

    # Initialize Logic System
    logic = LogicSystem()

    # Test cases with clear superstition patterns
    test_cases = [
        {
            "name": "Classic Bad Luck Superstitions",
            "text": "Always avoid breaking mirrors because it will cause 7 years of bad luck. Never walk under ladders or else misfortune will follow you. If a black cat crosses your path, then evil spirits will curse you.",
            "expected_superstitions": 3,
        },
        {
            "name": "Cultural Beliefs vs Science",
            "text": "The elders say that you must not cut nails at night or the spirits will get angry. Tradition forbids eating certain foods during specific phases of the moon. Ancestors demand that we perform rituals for good harvests.",
            "expected_superstitions": 3,
        },
        {
            "name": "Mixed Content (Facts + Superstitions)",
            "text": "Research shows that vitamin C boosts immunity. However, old wisdom says you must never swim after eating or you will drown. Studies indicate exercise is healthy, but folklore claims that certain numbers are unlucky and must be avoided.",
            "expected_superstitions": 2,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        print("-" * 60)

        result = logic.process_text(test_case["text"], LogicType.SUPERSTITION_FILTERING)

        print(f"Input: {test_case['text']}")
        print(f"Processed: {result.processed_text}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Superstitions Found: {result.metadata.get('superstitions_found', 0)}")

        if result.suggestions:
            print("💡 Suggestions:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")

        # Check if filtering worked
        if "[SUPERSTITION FILTERED]" in result.processed_text:
            print("✅ Superstitions successfully filtered!")
        else:
            print("⚠️  No superstitions detected (patterns may need adjustment)")

        print()

    # Show the pattern matching logic
    print("🔧 Superstition Pattern Matching Logic")
    print("-" * 60)
    print("The Logic System looks for these patterns:")
    for i, pattern in enumerate(logic.superstition_patterns, 1):
        print(f"{i}. {pattern}")
    print()

    # Show final statistics
    print("📊 Final Statistics")
    print("-" * 60)
    stats = logic.get_statistics()
    for key, value in stats["statistics"].items():
        if "superstition" in key.lower() or "processed" in key.lower():
            print(f"{key.replace('_', ' ').title()}: {value}")

    print("\n✅ Demonstration Complete!")
    print("=" * 60)
    print("The Logic System demonstrates how 'logic' works as:")
    print("• An invisible background system (like grids in graphs)")
    print("• A filter that separates cultural beliefs from evidence")
    print("• A compressor of complex ideas into understandable forms")
    print("• A stress-reducer by eliminating unfounded fears")
    print("• A bridge between tradition and scientific understanding")


if __name__ == "__main__":
    test_superstition_filtering()
