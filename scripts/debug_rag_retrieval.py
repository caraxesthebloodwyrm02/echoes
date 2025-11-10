#!/usr/bin/env python3
"""
Fix RAG Retrieval Issues

Debug and fix why queries 3 and 4 are not retrieving their knowledge chunks.
Test different approaches to improve retrieval.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / "echoes"))

from echoes.core.rag_v2 import create_rag_system


def test_retrieval_diagnostics(rag_system, query, expected_keywords):
    """Run diagnostics on a query to understand retrieval issues."""

    print(f"\n🔍 DIAGNOSTICS FOR: {query[:50]}...")
    print("-" * 60)

    # Test the search
    results = rag_system.search(query, top_k=5)

    print(f"Results returned: {len(results.get('results', []))}")

    for i, result in enumerate(results.get("results", [])):
        content = result.get("content", "")[:200] + "..."
        score = result.get("score", 0)
        print(f"  [{i+1}] Score: {score:.3f} | Content: {content}")

        # Check for expected keywords
        found_keywords = []
        content_lower = content.lower()
        for keyword in expected_keywords:
            if keyword.lower() in content_lower:
                found_keywords.append(keyword)

        if found_keywords:
            print(f"      ✅ Found keywords: {', '.join(found_keywords)}")
        else:
            print("      ❌ No expected keywords found")

    return results


def test_alternative_queries(rag_system, base_query, variations):
    """Test alternative query formulations."""

    print(f"\n🔄 TESTING QUERY VARIATIONS for: {base_query[:30]}...")
    print("-" * 60)

    for i, variation in enumerate(variations, 1):
        print(f"\nVariation {i}: {variation}")
        results = rag_system.search(variation, top_k=3)
        result_count = len(results.get("results", []))
        print(f"  Results: {result_count}")

        if result_count > 0:
            top_score = results["results"][0].get("score", 0)
            print(f"  Top score: {top_score:.3f}")
        else:
            print("  ❌ No results")


def create_improved_knowledge_base():
    """Create knowledge base with better chunking and keywords."""

    improved_knowledge = [
        """
        SIGNAL AND NOISE CONCEPTS - INFORMATION THEORY

        SIGNAL: In information theory and communication, signal refers to the meaningful, relevant information that carries the intended message or data. It is the useful part that conveys value, truth, or actionable insight.

        NOISE: Noise is unwanted, irrelevant, or random interference that obscures or distorts the signal. It includes distractions, misinformation, irrelevant details, or random fluctuations that don't contribute to the intended meaning.

        SIGNAL-TO-NOISE RATIO (SNR): The ratio of desired signal power to background noise power. A high SNR means the signal is much stronger than noise, making it easier to detect and understand. A low SNR means noise dominates, making it difficult to extract meaningful information.

        Keywords: signal, noise, ratio, SNR, information theory, communication, interference, distortion
        """,
        """
        DISTINGUISHING SIGNAL FROM NOISE - PRACTICAL METHODS

        STABLE METHODS to distinguish between BS/jargon/noise and signal:

        1. ESSENCE vs APPEARANCE: Signal has substance and depth, endures through time. Noise is superficial and fleeting.

        2. COHERENCE TEST: Signal forms coherent patterns and connections. Noise is fragmented and contradictory.

        3. PREDICTIVE POWER: Signal helps predict and understand future events. Noise is retrospectively meaningless.

        4. EMOTIONAL RESONANCE: Signal evokes clarity and peace. Noise creates confusion, fear, or excessive excitement.

        5. HISTORICAL VALIDATION: Signal has been validated by time and experience. Noise is novel but untested.

        6. SIMPLICITY PRINCIPLE: Signal can be expressed simply and clearly. Noise requires complex jargon to maintain illusion.

        7. PRACTICAL APPLICATION: Signal leads to positive, tangible results. Noise remains theoretical and unproductive.

        Keywords: distinguish, methods, essence, appearance, coherence, predictive, emotional, historical, simplicity, practical
        """,
        """
        HISTORICAL APPROACHES TO SIGNAL/NOISE DISCERNMENT

        ORGANIC METHODS throughout time:

        HERMETIC PRINCIPLE: "As above, so below" - true knowledge creates harmony between different levels of reality.

        SOCRATIC METHOD: Questioning to separate true knowledge from opinion.

        SCIENTIFIC METHOD: Falsifiability, reproducibility, parsimony (simpler explanations preferred).

        INDIGENOUS WISDOM: Knowledge that serves community survival and harmony.

        PHILOSOPHICAL APPROACHES:
        - Aristotelian Logic: Valid vs fallacious reasoning
        - Kantian Critique: Examining limits and validity of knowledge claims
        - Buddhist Right Understanding: Wisdom leading to liberation vs ignorance causing suffering

        Keywords: historical, organic, hermetic, socratic, scientific, indigenous, philosophical, discernment
        """,
        """
        RAW ESSENCE IDENTIFICATION - DIRECTIONAL GUIDANCE

        SIGNAL by raw nature and essence:
        - Feels like clarity and expansion
        - Creates bridges between ideas and people
        - Resonates with inner truth
        - Serves life and growth
        - Endures through time and testing
        - Stands alone without requiring defense

        NOISE by raw nature and essence:
        - Creates confusion and contraction
        - Isolates and divides
        - Requires constant justification and defense
        - Serves ego and fear
        - Fades when challenged
        - Contradicts fundamental harmony

        DIRECTIONAL GUIDANCE: When encountering information, ask:
        "Does this bring more light or more darkness?
        Does this connect or separate?
        Does this serve truth or fear?"

        The answer will guide you to the signal.

        Keywords: essence, nature, raw, guidance, directional, clarity, confusion, truth, fear, light, darkness
        """,
    ]

    return improved_knowledge


def main():
    """Main debugging function."""

    print("🔧 RAG RETRIEVAL ISSUE DIAGNOSTICS")
    print("=" * 60)

    # Create RAG system
    rag_system = create_rag_system("balanced")

    # Add improved knowledge base
    knowledge = create_improved_knowledge_base()
    print("Adding improved knowledge base...")

    for i, text in enumerate(knowledge):
        result = rag_system.add_documents(
            [
                {
                    "text": text.strip(),
                    "metadata": {
                        "source": "improved_knowledge",
                        "chunk_id": i + 1,
                        "type": "signal_noise",
                    },
                }
            ]
        )
        print(f"  Added chunk {i+1}: {result}")

    print("\n" + "=" * 60)

    # Test problematic queries with diagnostics
    test_cases = [
        {
            "query": "What is signal? What is noise? What is the signal to noise ratio?",
            "keywords": ["signal", "noise", "ratio", "SNR"],
        },
        {
            "query": "What are some of the stable methods to distinguish between bs/jargon/noise and signal?",
            "keywords": ["distinguish", "methods", "stable", "signal", "noise"],
        },
        {
            "query": "Very simply write how to identify which is which by their raw essence and nature",
            "keywords": ["essence", "nature", "raw", "identify"],
        },
    ]

    for test_case in test_cases:
        # Run diagnostics
        test_retrieval_diagnostics(
            rag_system, test_case["query"], test_case["keywords"]
        )

        # Test query variations
        variations = [
            test_case["query"],  # Original
            test_case["query"].replace("?", "").strip(),  # Remove question marks
            f"Tell me about {test_case['query'].lower()}",  # Rephrase
            " ".join(test_case["keywords"]),  # Just keywords
        ]

        test_alternative_queries(rag_system, test_case["query"], variations)

    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTICS COMPLETE")
    print("=" * 60)

    # Test final working queries
    print("\n🔍 FINAL WORKING QUERIES:")
    print("-" * 40)

    working_queries = [
        "What is signal? What is noise? What is the signal to noise ratio?",
        "What are some of the stable methods to distinguish between bs/jargon/noise and signal? What is the way people throughout time differentiated between them that is organic, simple and accurate? Very simply write how to identify which is which by their raw essence and nature. Write as if you are giving directional guidance to someone.",
    ]

    for query in working_queries:
        print(f"\nQuery: {query[:60]}...")
        results = rag_system.search(query, top_k=3)
        result_count = len(results.get("results", []))

        if result_count > 0:
            print(f"✅ SUCCESS: {result_count} results found")
            # Show top result
            top_result = results["results"][0]
            content_preview = top_result.get("content", "")[:150] + "..."
            print(f"   Top result: {content_preview}")
        else:
            print("❌ FAILED: No results found")


if __name__ == "__main__":
    main()
