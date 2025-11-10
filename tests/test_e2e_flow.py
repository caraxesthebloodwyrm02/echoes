import pytest
from agent_pathlib import Path
import sys

# Add src to path to allow for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_orbit.chunking import create_standard_chunker
from src.rag_orbit.embeddings import create_standard_generator
from src.rag_orbit.retrieval import create_standard_retriever
from src.rag_orbit.provenance import ProvenanceTracker

# --- Test Data (from demo script) ---
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
}


@pytest.fixture(scope="module")
def rag_pipeline():
    """
    Sets up and runs the full RAG pipeline once for the test module,
    returning the populated components for assertion.
    """
    # 1. Initialization
    chunker = create_standard_chunker()
    # Use a faster model for testing to speed up execution
    generator = create_standard_generator(use_cache=False)
    retriever = create_standard_retriever(embedding_dim=generator.embedding_dim)
    tracker = ProvenanceTracker()

    # 2. Ingestion and Processing
    all_chunks = []
    for doc_name, doc_data in DOCUMENTS.items():
        chunks = chunker.chunk_document(
            doc_data["text"], doc_name, doc_data["category"]
        )
        all_chunks.extend(chunks)
        tracker.record_chunking(
            source_document=doc_name,
            num_chunks=len(chunks),
            chunk_ids=[c.metadata.chunk_id for c in chunks],
            chunker_config={
                "chunk_size": chunker.chunk_size,
                "overlap": chunker.overlap,
            },
            text_checksum="test_checksum",
        )

    texts = [chunk.text for chunk in all_chunks]
    chunk_ids = [chunk.metadata.chunk_id for chunk in all_chunks]
    embeddings, _ = generator.embed_batch(texts, chunk_ids)

    metadata_dicts = [chunk.metadata.to_dict() for chunk in all_chunks]
    retriever.add_documents(embeddings, texts, metadata_dicts, chunk_ids)

    return {
        "chunker": chunker,
        "generator": generator,
        "retriever": retriever,
        "tracker": tracker,
    }


def test_e2e_implementation(rag_pipeline):
    """Tests that the core components are initialized and populated."""
    retriever = rag_pipeline["retriever"]
    stats = retriever.get_stats()

    assert stats["total_documents"] > 0, "No documents were added to the index."
    assert "empirical" in stats["categories"], "Empirical category is missing."
    assert "experiential" in stats["categories"], "Experiential category is missing."


def test_e2e_application_empirical_query(rag_pipeline):
    """Tests a targeted query to validate the application of the RAG system."""
    generator = rag_pipeline["generator"]
    retriever = rag_pipeline["retriever"]
    tracker = rag_pipeline["tracker"]

    # 3. Application (Query)
    query = "How does the brain make predictions?"
    query_emb, _ = generator.embed_text(query)
    results, metrics = retriever.search(query_emb, top_k=1, category_filter="empirical")

    # Find a chunking record to act as a parent
    parent_record_id = None
    for record in tracker.records.values():
        if record.operation_type == "chunk":
            parent_record_id = record.record_id
            break

    tracker.record_retrieval(
        query=query,
        query_checksum="test_query_checksum",
        num_results=len(results),
        result_chunk_ids=[r.chunk_id for r in results],
        retrieval_metrics=metrics.__dict__,
        parent_record_id=parent_record_id,
    )

    # 4. Assert on Results
    assert len(results) == 1, "Expected exactly one result for the empirical query."
    top_result = results[0]

    assert top_result.metadata["source_document"] == "neuroscience_paper.txt"
    assert top_result.metadata["category"] == "empirical"
    assert (
        "prediction machine" in top_result.text
    ), "Top result text does not match expected content."
    assert top_result.similarity_score > 0.5, "Similarity score is unexpectedly low."


def test_e2e_application_experiential_query(rag_pipeline):
    """Tests a query filtered for the experiential category."""
    generator = rag_pipeline["generator"]
    retriever = rag_pipeline["retriever"]

    query = "What is the feeling of meditation?"
    query_emb, _ = generator.embed_text(query)
    results, _ = retriever.search(query_emb, top_k=1, category_filter="experiential")

    assert len(results) == 1, "Expected exactly one result for the experiential query."
    top_result = results[0]

    assert top_result.metadata["source_document"] == "meditation_experience.txt"
    assert (
        "unified field of awareness" in top_result.text
    ), "Top result for experiential query is incorrect."


def test_e2e_results_provenance(rag_pipeline):
    """Tests that the results are verifiable through the provenance tracker."""
    tracker = rag_pipeline["tracker"]

    # Assert that operations were recorded
    record_types = [rec.operation_type for rec in tracker.records.values()]
    assert "chunk" in record_types, "Chunking operation was not recorded in provenance."
    assert (
        "retrieve" in record_types
    ), "Retrieval operation was not recorded in provenance."

    # Find the retrieval record and validate its integrity
    retrieval_record = None
    for record in tracker.records.values():
        if record.operation_type == "retrieve":
            retrieval_record = record
            break

    assert (
        retrieval_record is not None
    ), "Could not find the retrieval record in provenance."

    # Validate the record's internal checksum
    is_valid, error = tracker.validate_record(retrieval_record.record_id)
    assert is_valid, f"Provenance record is not valid: {error}"

    # Check that the retrieval record has a parent (the chunking record)
    lineage = tracker.get_lineage(retrieval_record.record_id)
    assert len(lineage) > 1, "Lineage is too short; parent records are missing."
    assert (
        lineage[0].operation_type == "chunk"
    ), "The parent of the retrieval should be a chunk operation."
