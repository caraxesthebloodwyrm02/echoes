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

# MIT License
#
# Copyright (c) 2025 Echoes Project
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
Knowledge Graph Integration Demo
Demonstrates semantic search capabilities vs. keyword search
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompting.core.context_manager import ContextManager
from prompting.core.kg_bridge import KnowledgeGraphBridge


def demo_keyword_vs_semantic():
    """Compare keyword search vs semantic search"""

    print("=" * 80)
    print("KNOWLEDGE GRAPH INTEGRATION DEMO")
    print("=" * 80)
    print()

    # Create ContextManager with KG enabled
    print("1. Initializing ContextManager with Knowledge Graph integration...")
    cm_with_kg = ContextManager(storage_path="data/demo_context", enable_kg=True)

    # Create ContextManager without KG for comparison
    print("2. Initializing ContextManager without KG (keyword search only)...")
    cm_without_kg = ContextManager(
        storage_path="data/demo_context_no_kg", enable_kg=False
    )

    print()

    # Add sample insights
    print("3. Adding sample insights...")
    sample_insights = [
        (
            "Database query optimization improved response time by 40%",
            "performance",
            0.9,
        ),
        ("Authentication module needs security audit", "security", 0.85),
        ("Code refactoring reduced complexity in payment processing", "quality", 0.8),
        ("API endpoint requires rate limiting implementation", "security", 0.75),
        (
            "User interface responsiveness enhanced with lazy loading",
            "performance",
            0.88,
        ),
        ("Test coverage increased to 85% for core modules", "quality", 0.82),
        ("SQL injection vulnerability patched in login form", "security", 0.95),
        ("Memory leak fixed in background task processor", "performance", 0.87),
        ("Documentation updated for new API endpoints", "general", 0.7),
        ("Microservice architecture migration planning started", "architecture", 0.78),
    ]

    for insight, category, confidence in sample_insights:
        cm_with_kg.add_insight(insight, category, confidence)
        cm_without_kg.add_insight(insight, category, confidence)
        print(f"   ✓ Added: {insight[:60]}...")

    print()
    print("=" * 80)
    print()

    # Test queries
    queries = [
        ("database performance", "performance"),
        ("security vulnerabilities", "security"),
        ("code quality improvements", None),
        ("API security", "security"),
    ]

    for query, category in queries:
        print(f"Query: '{query}'" + (f" (category: {category})" if category else ""))
        print("-" * 80)

        # Keyword search results
        print("  KEYWORD SEARCH RESULTS:")
        keyword_results = cm_without_kg.get_relevant_insights(query, category, limit=3)
        if keyword_results:
            for i, result in enumerate(keyword_results, 1):
                print(
                    f"    {i}. [{result.get('category', 'N/A')}] {result['content'][:70]}..."
                )
                print(f"       Confidence: {result.get('confidence', 0):.2f}")
        else:
            print("    No results found")

        print()

        # Semantic search results
        print("  SEMANTIC SEARCH RESULTS:")
        semantic_results = cm_with_kg.get_relevant_insights(query, category, limit=3)
        if semantic_results:
            for i, result in enumerate(semantic_results, 1):
                content = result.get("content", "")
                cat = result.get("category", "N/A")
                conf = result.get("confidence", 0)
                sim = result.get("similarity", 0)
                score = result.get("combined_score", 0)

                print(f"    {i}. [{cat}] {content[:70]}...")
                print(
                    f"       Confidence: {conf:.2f} | Similarity: {sim:.2f} | Combined: {score:.2f}"
                )
        else:
            print("    No results found (falling back to keyword search)")

        print()
        print("=" * 80)
        print()

    # Show session summary
    print("SESSION SUMMARY:")
    print("-" * 80)

    summary_kg = cm_with_kg.get_session_summary()
    print(f"  Insights Generated: {summary_kg['insights_generated']}")
    print(f"  Session Duration: {summary_kg['duration']:.2f}s")

    if "kg_stats" in summary_kg:
        kg_stats = summary_kg["kg_stats"]
        print(f"  KG Status: {'Enabled' if kg_stats['enabled'] else 'Disabled'}")
        print(f"  Insights in KG: {kg_stats.get('insights_in_kg', 0)}")
        print(
            f"  Cache Size: {kg_stats.get('cache_size', 0)}/{kg_stats.get('cache_capacity', 0)}"
        )

    print()

    # Show KG-specific features
    if cm_with_kg.kg_bridge and cm_with_kg.kg_bridge.enabled:
        print("KNOWLEDGE GRAPH FEATURES:")
        print("-" * 80)

        # Pattern inference
        print("  Inferring patterns from knowledge graph...")
        patterns = cm_with_kg.kg_bridge.infer_patterns()
        if patterns:
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    print(f"    {pattern_type}: {len(pattern_list)} patterns found")

        print()

        # Recommendations
        print("  Generating recommendations...")
        recommendations = cm_with_kg.kg_bridge.get_recommendations()
        if recommendations:
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"    {i}. [{rec['priority']}] {rec['recommendation']}")

        print()

    print("=" * 80)
    print("Demo completed!")
    print()

    # Cleanup
    import shutil

    for path in ["data/demo_context", "data/demo_context_no_kg"]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)


def demo_kg_bridge_standalone():
    """Demonstrate KG bridge standalone usage"""

    print("=" * 80)
    print("KNOWLEDGE GRAPH BRIDGE STANDALONE DEMO")
    print("=" * 80)
    print()

    # Create KG bridge
    print("Creating KnowledgeGraphBridge...")
    kg_bridge = KnowledgeGraphBridge(enable_kg=True, cache_size=50)

    stats = kg_bridge.get_stats()
    print(f"  Status: {'Enabled' if stats['enabled'] else 'Disabled'}")
    print(f"  KG Available: {stats['kg_available']}")
    print()

    if not kg_bridge.enabled:
        print("⚠️  Knowledge graph not available. Install dependencies:")
        print("   pip install networkx>=3.1 rdflib>=6.3.0")
        return

    # Add test insights
    print("Adding insights to knowledge graph...")
    insights = [
        {
            "content": "Machine learning model accuracy improved to 94%",
            "category": "ml",
            "confidence": 0.9,
            "timestamp": "2025-01-15T10:00:00",
            "session_id": "demo_session",
        },
        {
            "content": "Neural network training time reduced by 30%",
            "category": "ml",
            "confidence": 0.85,
            "timestamp": "2025-01-15T11:00:00",
            "session_id": "demo_session",
        },
    ]

    synced = kg_bridge.sync_insights_to_kg(insights)
    print(f"  Synced {synced} insights")
    print()

    # Semantic search
    print("Performing semantic search...")
    results = kg_bridge.semantic_search("machine learning performance", limit=5)
    print(f"  Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"    {i}. {result['content'][:60]}...")
        print(f"       Score: {result.get('combined_score', 0):.2f}")
    print()

    # Stats
    final_stats = kg_bridge.get_stats()
    print("Final Statistics:")
    print(f"  Insights in KG: {final_stats.get('insights_in_kg', 0)}")
    print(f"  Cache entries: {final_stats['cache_size']}")
    print()


if __name__ == "__main__":
    print()

    # Run keyword vs semantic demo
    try:
        demo_keyword_vs_semantic()
    except Exception as e:
        print(f"Error in demo: {e}")
        import traceback

        traceback.print_exc()

    print()
    print()

    # Run standalone bridge demo
    try:
        demo_kg_bridge_standalone()
    except Exception as e:
        print(f"Error in standalone demo: {e}")
        import traceback

        traceback.print_exc()
