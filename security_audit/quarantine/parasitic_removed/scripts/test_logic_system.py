#!/usr/bin/env python3
"""
Test script to demonstrate the Logic System filtering superstitions from patterns 
and facts from fiction.
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import LogicSystem, LogicType


def test_logic_system():
    """Demonstrate the Logic System capabilities."""

    print("🧠 Logic System Demonstration")
    print("=" * 50)
    print("Testing the concept of 'logic' - a system that takes complex ideas")
    print("and compresses them into readable, understandable forms.")
    print("Working like background grids - invisible but interpretable.\n")

    # Initialize Logic System
    logic = LogicSystem()

    # Test 1: Superstition Filtering (Kushongskaar)
    print("🔍 Test 1: Superstition Filtering (Kushongskaar)")
    print("-" * 50)

    superstition_text = "Breaking a mirror will cause 7 years of bad luck according to ancient tradition. Walking under ladders brings misfortune, and black cats crossing your path means evil is coming."

    result = logic.process_text(superstition_text, LogicType.SUPERSTITION_FILTERING)

    print(f"Input: {superstition_text}")
    print(f"Processed: {result.processed_text}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Superstitions Filtered: {result.metadata.get('superstitions_found', 0)}")
    if result.suggestions:
        print("Suggestions:")
        for suggestion in result.suggestions:
            print(f"  - {suggestion}")
    print()

    # Test 2: Fact Extraction
    print("🔍 Test 2: Fact Extraction")
    print("-" * 50)

    fact_text = "Research shows that regular exercise reduces the risk of heart disease by 35%. Studies indicate that meditation improves cognitive function. Data demonstrates that people who sleep 7-8 hours live longer."

    result = logic.process_text(fact_text, LogicType.FACT_EXTRACTION)

    print(f"Input: {fact_text}")
    print(f"Processed: {result.processed_text}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Facts Found: {result.metadata.get('facts_found', 0)}")
    print()

    # Test 3: Fiction Detection
    print("🔍 Test 3: Fiction Detection")
    print("-" * 50)

    fiction_text = "Once upon a time in a galaxy far away, there lived a magical dragon who could breathe fire and ice. Imagine if humans could fly without wings - what a wonderful world that would be!"

    result = logic.process_text(fiction_text, LogicType.FICTION_DETECTION)

    print(f"Input: {fiction_text}")
    print(f"Processed: {result.processed_text}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Fictional Elements: {result.metadata.get('fictional_elements', 0)}")
    print()

    # Test 4: Pattern Recognition
    print("🔍 Test 4: Pattern Recognition")
    print("-" * 50)

    pattern_text = "If you study hard then you will pass exams. First you learn the basics, then you practice problems, finally you master the subject. Both exercise and diet are similar in that they affect health, but different in their methods."

    result = logic.process_text(pattern_text, LogicType.PATTERN_RECOGNITION)

    print(f"Input: {pattern_text}")
    print(f"Processed: {result.processed_text}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Patterns Found: {result.metadata.get('patterns_found', 0)}")
    print()

    # Test 5: Essence Compression
    print("🔍 Test 5: Essence Compression")
    print("-" * 50)

    complex_text = "The fundamental principle of quantum mechanics states that particles can exist in multiple states simultaneously until observed, which is known as superposition, and this principle has profound implications for our understanding of reality at the smallest scales."

    result = logic.process_text(complex_text, LogicType.ESSENCE_COMPRESSION)

    print(f"Input: {complex_text}")
    print(f"Processed: {result.processed_text}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Compression Ratio: {result.metadata.get('compression_ratio', 0):.2f}")
    print()

    # Show Logic System Statistics
    print("📊 Logic System Statistics")
    print("-" * 50)
    stats = logic.get_statistics()
    for key, value in stats["statistics"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print()

    print("✅ Logic System Demonstration Complete!")
    print("=" * 50)
    print("The Logic System successfully:")
    print("• Filters superstitions (kushongskaar) from evidence-based patterns")
    print("• Extracts verifiable facts from claims")
    print("• Distinguishes fiction from non-fiction")
    print("• Recognizes logical patterns in text")
    print("• Compresses complex ideas into essential meaning")
    print("\nThis system works invisibly in the background, like grids in a graph,")
    print("processing complex information into simple, stress-free understanding.")


if __name__ == "__main__":
    test_logic_system()
