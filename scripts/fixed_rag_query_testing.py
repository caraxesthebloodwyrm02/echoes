#!/usr/bin/env python3
"""
Fixed RAG Query Testing - Direct Answers

Run the 4 queries through a working RAG system and get direct answers.
Uses the echoes/core/rag_v2.py wrapper for reliable results.
"""

import sys
from pathlib import Path
import time

# Add the echoes directory to path
sys.path.insert(0, str(Path(__file__).parent / "echoes"))

from echoes.core.rag_v2 import create_rag_system


def setup_knowledge_base(rag_system):
    """Add symbolic and philosophical knowledge to the RAG system."""

    knowledge = [
        """
        NUMEROLOGY AND SYMBOLISM:

        Number 5: Freedom, adventure, versatility, curiosity, senses. Represents the human experience and need for variety. Associated with pentagram and five elements.

        Number 6: Harmony, balance, responsibility, nurturing, service. Represents family, community, material world. Symbolizes union of opposites - material and spiritual.

        Transition 5→6: Journey from personal exploration to communal responsibility. Shift from sensory freedom to balanced nurturing, achieving harmony while maintaining vitality.

        Sun Symbolism: Consciousness, enlightenment, vitality, life force, masculine energy. Represents higher self, spiritual awakening, divine masculine. Symbolizes clarity, illumination, power of creation.
        """,
        """
        NUMBERS 8-11 AND LUNAR SYMBOLISM:

        Number 8: Infinity, abundance, power, material success, karma. Infinity loop symbol representing infinite possibilities and law of cause and effect.

        Number 9: Completion, humanitarianism, wisdom, spiritual enlightenment. End of cycle, new wisdom. Represents mastery and new beginnings.

        Number 10: Completion of cycle, new beginnings, divine order. Combines leadership (1) and potential (0), representing mastery and new cycles.

        Number 11: Master number - intuition, spiritual insight, enlightenment, connection to higher realms. "Spiritual messenger."

        Moon Symbolism: Subconscious, intuition, emotions, feminine energy, cycles, divine feminine. Mystery, dreams, psychic abilities, inner world. Lunar cycles = change, renewal, natural rhythms.
        """,
        """
        SIGNAL VS NOISE CONCEPTS:

        Signal: Meaningful, relevant information carrying intended message/data. Useful part conveying value, truth, actionable insight.

        Noise: Unwanted interference obscuring/distorting signal. Distractions, misinformation, irrelevant details, random fluctuations not contributing to meaning.

        Signal-to-Noise Ratio (SNR): Ratio of desired signal power to background noise power. High SNR = signal stronger than noise, easier detection/understanding. Low SNR = noise dominates, difficult extracting meaning.

        Human cognition: Signal = truth, wisdom, valuable insight. Noise = confusion, misinformation, distractions.
        """,
        """
        DISTINGUISHING SIGNAL FROM NOISE:

        Stable Methods:
        1. Essence vs Appearance: Signal has substance/depth, endures. Noise superficial/transient.
        2. Coherence Test: Signal forms coherent patterns/connections. Noise fragmented/contradictory.
        3. Predictive Power: Signal predicts future events. Noise retrospectively meaningless.
        4. Emotional Resonance: Signal evokes clarity/peace. Noise creates confusion/fear/excess excitement.
        5. Historical Validation: Signal validated by time/experience. Noise novel/untested.
        6. Simplicity Principle: Signal expressible simply/clearly. Noise requires complex jargon.
        7. Practical Application: Signal leads to positive/tangible results. Noise theoretical/unproductive.

        Organic Historical Methods:
        - Hermetic: "As above, so below" - true knowledge creates harmony between levels
        - Socratic: Questioning separates true knowledge from opinion
        - Scientific: Falsifiability, reproducibility, parsimony
        - Indigenous: Knowledge serving community survival

        Raw Essence Identification:
        Signal feels like: clarity, expansion, connection, truth, endurance, service
        Noise feels like: confusion, contraction, isolation, fear, fragility, self-service

        Directional Guidance: When encountering information, ask: "Does this bring more light or darkness? Connect or separate? Serve truth or fear?" The answer guides to signal.
        """,
    ]

    print("Adding knowledge base to RAG system...")
    for i, text in enumerate(knowledge):
        result = rag_system.add_documents(
            [
                {
                    "text": text.strip(),
                    "metadata": {"source": "symbolic_knowledge", "chunk_id": i + 1},
                }
            ]
        )
        print(f"  Added chunk {i+1}: {result}")

    print("Knowledge base setup complete")


def run_query(rag_system, query, query_num):
    """Run a single query and return formatted results."""
    print(f"\n{'='*60}")
    print(f"QUERY {query_num}: {query}")
    print("=" * 60)

    start_time = time.time()
    try:
        results = rag_system.search(query, top_k=3)
        response_time = time.time() - start_time

        print(".2f")
        print(f"Results found: {len(results.get('results', []))}")

        # Extract and format answer
        answer_parts = []
        for i, result in enumerate(results.get("results", [])):
            content = result.get("content", "").strip()
            score = result.get("score", 0)
            if content and score > 0.5:  # Only high-confidence results
                answer_parts.append(f"[{i+1}] {content}")

        if answer_parts:
            answer = " ".join(answer_parts)
            # Clean up formatting
            answer = answer.replace("  ", " ").replace("\n\n", "\n").strip()
            if len(answer) > 1500:
                answer = answer[:1500] + "..."
        else:
            answer = "No relevant information found in knowledge base."

        print(f"\nANSWER:\n{answer}")

        return {
            "query": query,
            "query_num": query_num,
            "answer": answer,
            "response_time": response_time,
            "results_count": len(results.get("results", [])),
            "success": True,
        }

    except Exception as e:
        response_time = time.time() - start_time
        print(f"❌ Error: {e}")
        return {
            "query": query,
            "query_num": query_num,
            "answer": f"Error processing query: {e}",
            "response_time": response_time,
            "results_count": 0,
            "success": False,
        }


def main():
    """Main execution function."""
    print("🔍 FIXED RAG QUERY TESTING - DIRECT ANSWERS")
    print("=" * 60)

    # Define queries
    queries = [
        "What is the symbolic meaning and significance of the transition from number 5 to 6 and sun?",
        "What is the symbolic meaning and significance of the number 8 to 11 and moon?",
        "What is signal? What is noise? What is the signal to noise ratio?",
        "What are some of the stable methods to distinguish between bs/jargon/noise and signal? What is the way people throughout time differentiated between them that is organic, simple and accurate? Very simply write how to identify which is which by their raw essence and nature. Write as if you are giving directional guidance to someone.",
    ]

    # Create RAG system
    print("Initializing RAG system...")
    rag_system = create_rag_system("balanced")

    if not rag_system:
        print("❌ Failed to initialize RAG system")
        return

    # Setup knowledge base
    setup_knowledge_base(rag_system)

    # Run queries
    results = []
    for i, query in enumerate(queries, 1):
        result = run_query(rag_system, query, i)
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)

    successful = sum(1 for r in results if r["success"])
    total_time = sum(r["response_time"] for r in results)

    print(f"Total Queries: {len(results)}")
    print(f"Successful: {successful}")
    print(".2f")
    print(".3f")

    # Save results
    import json

    output_file = "fixed_rag_query_results.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": time.time(),
                "results": results,
                "summary": {
                    "total_queries": len(results),
                    "successful_queries": successful,
                    "total_response_time": total_time,
                    "average_response_time": total_time / len(results),
                },
            },
            f,
            indent=2,
            default=str,
        )

    print(f"\n📄 Results saved to: {output_file}")
    print("✅ Query testing complete!")


if __name__ == "__main__":
    main()
