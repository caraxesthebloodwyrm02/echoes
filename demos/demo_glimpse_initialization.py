#!/usr/bin/env python
"""
Glimpse Project Initialization Demo

Demonstrates the RAG Orbit baseline implementation with:
- Document chunking with metadata
- Embedding generation with caching
- FAISS-based retrieval
- Provenance tracking
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.rag_orbit.chunking import create_standard_chunker
from src.rag_orbit.embeddings import create_standard_generator
from src.rag_orbit.retrieval import create_standard_retriever
from src.rag_orbit.provenance import ProvenanceTracker


# Sample documents for demo
DOCUMENTS = {
    "neuroscience_paper.txt": {
        "text": """
        Predictive processing models have revolutionized our understanding of
        perception and cognition. The brain operates as a prediction machine,
        constantly generating hypotheses about incoming sensory data and
        updating these predictions based on prediction errors. This framework
        integrates bottom-up sensory signals with top-down expectations,
        enabling efficient information processing across hierarchical neural
        networks. Recent research demonstrates that predictive processing can
        account for phenomena ranging from visual perception to motor control,
        learning, attention, and even consciousness itself.
        """,
        "category": "empirical",
    },
    "meditation_experience.txt": {
        "text": """
        During focused attention meditation, practitioners report a distinctive
        shift in awareness. The usual stream of discursive thought quiets,
        revealing a more spacious, present-centered mode of knowing. In this
        state, the boundary between observer and observed seems to dissolve,
        replaced by a unified field of awareness. Practitioners describe
        enhanced clarity, reduced mental reactivity, and access to intuitive
        insights that transcend analytical reasoning. These experiential
        qualities suggest modalities of cognition that complement but differ
        from ordinary conceptual thought.
        """,
        "category": "experiential",
    },
    "quantum_physics.txt": {
        "text": """
        The quantum measurement problem remains one of the most profound
        mysteries in physics. When we measure a quantum system, the wave
        function appears to collapse from a superposition of states to a
        single definite outcome. The mechanism and interpretation of this
        collapse is deeply controversial. Some interpretations invoke the
        role of consciousness, others propose many worlds, and still others
        suggest that our mathematical formalism is incomplete. Understanding
        measurement may require rethinking the relationship between observer
        and observed at the most fundamental level.
        """,
        "category": "empirical",
    },
    "systems_thinking.txt": {
        "text": """
        Complex adaptive systems exhibit emergent properties that cannot be
        predicted from the behavior of individual components. In human
        organizations, ecosystems, and cognitive architectures, patterns
        arise through decentralized interactions rather than top-down control.
        Feedback loops, network effects, and self-organization generate
        novel structures and behaviors. Understanding such systems requires
        shifting from linear cause-and-effect thinking to recognizing circular
        causality, context-dependence, and the co-evolution of system and
        environment. This perspective reveals intelligence as a distributed,
        relational phenomenon rather than a property of isolated agents.
        """,
        "category": "empirical",
    },
}


def print_header(text: str) -> None:
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print("=" * 70)


def print_subheader(text: str) -> None:
    """Print formatted subsection header."""
    print(f"\n{'-'*70}")
    print(f"  {text}")
    print("-" * 70)


def main() -> None:
    """Run the initialization demo."""
    print_header("Glimpse: RAG Orbit Baseline Initialization Demo")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")

    # Initialize components
    print_subheader("1. Initializing Components")

    chunker = create_standard_chunker()
    print("✓ Document chunker initialized (500 tokens, 50 overlap)")

    generator = create_standard_generator(use_cache=True)
    print(f"✓ Embedding generator initialized (model: all-mpnet-base-v2, dim: {generator.embedding_dim})")

    retriever = create_standard_retriever(embedding_dim=generator.embedding_dim)
    print("✓ FAISS retriever initialized (metric: cosine, index: flat)")

    tracker = ProvenanceTracker()
    print(f"✓ Provenance tracker initialized (session: {tracker.session_id[:8]}...)")

    # Step 1: Chunk documents
    print_subheader("2. Chunking Documents")

    all_chunks = []
    for doc_name, doc_data in DOCUMENTS.items():
        chunks = chunker.chunk_document(doc_data["text"], doc_name, doc_data["category"])
        all_chunks.extend(chunks)

        # Record provenance
        text_checksum = chunks[0].compute_checksum() if chunks else "empty"
        tracker.record_chunking(
            source_document=doc_name,
            num_chunks=len(chunks),
            chunk_ids=[c.metadata.chunk_id for c in chunks],
            chunker_config={
                "chunk_size": chunker.chunk_size,
                "overlap": chunker.overlap,
            },
            text_checksum=text_checksum,
        )

        print(f"  {doc_name}: {len(chunks)} chunks ({doc_data['category']})")

    print(f"\n✓ Total chunks created: {len(all_chunks)}")

    # Validate chunks
    is_valid, errors = chunker.validate_chunks(all_chunks)
    if is_valid:
        print("✓ All chunks validated successfully")
    else:
        print(f"⚠ Validation errors: {errors}")

    # Step 2: Generate embeddings
    print_subheader("3. Generating Embeddings")

    texts = [chunk.text for chunk in all_chunks]
    chunk_ids = [chunk.metadata.chunk_id for chunk in all_chunks]

    print(f"  Embedding {len(texts)} chunks...")
    embeddings, embedding_metadata = generator.embed_batch(texts, chunk_ids)

    print(f"✓ Embeddings generated: shape {embeddings.shape}")
    print(f"  Cache hits: {len([m for m in embedding_metadata if m.created_at])}")

    # Step 3: Build retrieval index
    print_subheader("4. Building FAISS Index")

    metadata_dicts = [chunk.metadata.to_dict() for chunk in all_chunks]
    retriever.add_documents(embeddings, texts, metadata_dicts, chunk_ids)

    stats = retriever.get_stats()
    print("✓ Index built successfully")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Categories: {', '.join(stats['categories'])}")

    # Step 4: Demonstrate retrieval
    print_subheader("5. Testing Retrieval")

    queries = [
        ("How does the brain process predictions?", None),
        ("What is meditation like experientially?", "experiential"),
        ("Tell me about quantum measurement", "empirical"),
    ]

    for query_text, category_filter in queries:
        print(f'\n📝 Query: "{query_text}"')
        if category_filter:
            print(f"   Filter: {category_filter}")

        # Generate query embedding
        query_emb, _ = generator.embed_text(query_text)

        # Search
        results, metrics = retriever.search(
            query_emb,
            top_k=3,
            min_similarity=0.3,
            category_filter=category_filter,
        )

        # Record provenance
        tracker.record_retrieval(
            query=query_text,
            query_checksum=generator.model.encode(query_text, convert_to_numpy=True).tobytes().hex()[:16],
            num_results=len(results),
            result_chunk_ids=[r.chunk_id for r in results],
            retrieval_metrics={
                "query_time_ms": metrics.query_time_ms,
                "avg_similarity": metrics.avg_similarity,
            },
        )

        print(f"   ⚡ Query time: {metrics.query_time_ms:.2f}ms")
        print(f"   📊 Results: {metrics.num_results} (avg similarity: {metrics.avg_similarity:.3f})")

        for i, result in enumerate(results[:2], 1):
            print(f"\n   Result {i} (similarity: {result.similarity_score:.3f})")
            print(f"   Source: {result.metadata['source_document']}")
            print(f"   Category: {result.metadata['category']}")
            print(f"   Text: {result.text[:150]}...")

    # Step 5: Demonstrate provenance
    print_subheader("6. Provenance Tracking")

    print(f"  Total provenance records: {len(tracker.records)}")
    print(f"  Session ID: {tracker.session_id}")

    # Show record types
    record_types = {}
    for record in tracker.records.values():
        record_types[record.operation_type] = record_types.get(record.operation_type, 0) + 1

    print("\n  Records by type:")
    for op_type, count in record_types.items():
        print(f"    {op_type}: {count}")

    # Validate all records
    print("\n  Validating provenance integrity...")
    all_valid = True
    for record_id in tracker.records:
        is_valid, error = tracker.validate_record(record_id)
        if not is_valid:
            print(f"    ✗ Record {record_id[:8]}: {error}")
            all_valid = False

    if all_valid:
        print("  ✓ All provenance records validated")

    # Export session
    export_path = Path("results/rag_initialization_provenance.json")
    export_path.parent.mkdir(parents=True, exist_ok=True)
    tracker.export_session(export_path)
    print(f"\n  ✓ Provenance exported to: {export_path}")

    # Summary
    print_header("Initialization Complete")

    print(
        """
✅ RAG Orbit Baseline Status:

    ├─ Chunking: Operational (4 documents → {chunks} chunks)
    ├─ Embeddings: Operational ({dim}-dimensional vectors)
    ├─ Retrieval: Operational (FAISS index with {docs} documents)
    └─ Provenance: Operational ({records} records tracked)

📋 Next Steps:

    1. Review PHASE1_DELIVERABLES.md for remaining tasks
    2. Begin IRB pre-submission documentation
    3. Conduct literature review (cognitive neuroscience focus)
    4. Identify advisory board candidates
    5. Set up .windsurfrules configuration

🎯 Phase 1 Goal: Complete foundation by end of Week 3

    Target: Ethics protocol, secure environment, advisory board
    Progress: Technical infrastructure ✓ | Governance in-progress
    """.format(
            chunks=len(all_chunks),
            dim=generator.embedding_dim,
            docs=stats["total_documents"],
            records=len(tracker.records),
        )
    )

    print("=" * 70)
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
