#!/usr/bin/env python3
"""
Debug complexity analysis
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from assistant import ContextAnalyzer


def debug_complexity():
    """Debug the complexity analysis."""

    print("🔍 Debugging Complexity Analysis")
    print("=" * 50)

    # Initialize analyzer
    analyzer = ContextAnalyzer()

    # Test queries
    queries = [
        "What's the capital of France?",
        "Explain quantum computing in detail",
        "Compare and contrast classical machine learning with deep learning, including use cases, advantages, and limitations of each approach",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)

        # Analyze the query
        analysis = analyzer.analyze_prompt(query, [])

        print(f"Domain: {analysis['domain']}")
        print(f"Complexity: {analysis['complexity']}")
        print(f"Recommended Model: {analysis['recommended_model']}")
        print(f"Confidence: {analysis['confidence']:.2f}")


if __name__ == "__main__":
    debug_complexity()
