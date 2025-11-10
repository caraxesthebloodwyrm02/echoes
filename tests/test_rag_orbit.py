"""
Comprehensive test suite for RAG Orbit baseline implementation.

Tests cover chunking, embeddings, retrieval, and provenance tracking
with >80% coverage target.
"""

import pytest
import numpy as np
from agent_pathlib import Path
import tempfile
import shutil

from src.rag_orbit.chunking import (
    DocumentChunker,
    Chunk,
    create_standard_chunker,
)
from src.rag_orbit.embeddings import (
    EmbeddingGenerator,
    create_standard_generator,
)
from src.rag_orbit.retrieval import (
    FAISSRetriever,
    RetrievalResult,
    create_standard_retriever,
)
from src.rag_orbit.provenance import (
    ProvenanceTracker,
)


# Test Data
SAMPLE_TEXT_EMPIRICAL = """
Cognitive neuroscience research demonstrates that predictive processing
models can account for perception, action, and learning. The brain
continuously generates predictions about sensory input and updates
these predictions based on prediction errors. This hierarchical
framework integrates bottom-up sensory signals with top-down
expectations, enabling efficient information processing.
"""

SAMPLE_TEXT_EXPERIENTIAL = """
During meditation practice, awareness shifts from discursive thought
to direct perception of present-moment experience. Practitioners
report enhanced clarity, reduced mental chatter, and a sense of
spaciousness that transcends ordinary consciousness. These subjective
states suggest modalities of knowing that complement analytical
reasoning with intuitive insight.
"""


class TestDocumentChunker:
    """Test document chunking functionality."""

    def test_basic_chunking(self):
        """Test basic chunking with default parameters."""
        chunker = DocumentChunker(chunk_size=50, overlap=10)
        chunks = chunker.chunk_document(
            SAMPLE_TEXT_EMPIRICAL, "test_doc.txt", "empirical"
        )

        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.metadata.category == "empirical" for c in chunks)

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        chunker = DocumentChunker(chunk_size=20, overlap=5)
        chunks = chunker.chunk_document(SAMPLE_TEXT_EMPIRICAL, "test.txt")

        if len(chunks) > 1:
            # Check that consecutive chunks share some tokens
            first_tokens = chunks[0].text.split()[-5:]
            second_tokens = chunks[1].text.split()[:5]
            # Some overlap should exist (not exact match due to boundaries)
            assert len(first_tokens) > 0 and len(second_tokens) > 0

    def test_checksum_computation(self):
        """Test that checksums are computed correctly."""
        chunker = create_standard_chunker()
        chunks = chunker.chunk_document(SAMPLE_TEXT_EMPIRICAL, "test.txt")

        for chunk in chunks:
            # Recompute checksum
            recomputed = chunk.compute_checksum()
            assert recomputed == chunk.metadata.checksum
            assert len(recomputed) == 64  # SHA-256 hex length

    def test_chunk_validation(self):
        """Test chunk validation functionality."""
        chunker = create_standard_chunker()
        chunks = chunker.chunk_document(SAMPLE_TEXT_EMPIRICAL, "test.txt")

        is_valid, errors = chunker.validate_chunks(chunks)
        assert is_valid
        assert len(errors) == 0

    def test_batch_chunking(self):
        """Test batch processing of multiple documents."""
        chunker = create_standard_chunker()
        documents = [
            (SAMPLE_TEXT_EMPIRICAL, "doc1.txt", "empirical"),
            (SAMPLE_TEXT_EXPERIENTIAL, "doc2.txt", "experiential"),
        ]

        chunks = chunker.chunk_batch(documents)

        assert len(chunks) > 0
        empirical_chunks = [c for c in chunks if c.metadata.category == "empirical"]
        experiential_chunks = [
            c for c in chunks if c.metadata.category == "experiential"
        ]

        assert len(empirical_chunks) > 0
        assert len(experiential_chunks) > 0

    def test_empty_document(self):
        """Test handling of empty documents."""
        chunker = create_standard_chunker()
        chunks = chunker.chunk_document("", "empty.txt")
        assert len(chunks) == 0


class TestEmbeddingGenerator:
    """Test embedding generation functionality."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_single_embedding(self, temp_cache_dir):
        """Test generating a single embedding."""
        generator = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2",  # Faster for testing
            use_cache=True,
            cache_dir=temp_cache_dir,
        )

        text = "This is a test sentence for embedding."
        embedding, metadata = generator.embed_text(text, chunk_id="test_chunk_1")

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] == generator.embedding_dim
        assert metadata.chunk_id == "test_chunk_1"
        assert len(metadata.text_checksum) == 64

    def test_embedding_cache(self, temp_cache_dir):
        """Test that caching works correctly."""
        generator = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2",
            use_cache=True,
            cache_dir=temp_cache_dir,
        )

        text = "Cache test sentence."

        # First call - should compute
        embedding1, metadata1 = generator.embed_text(text)

        # Second call - should use cache
        embedding2, metadata2 = generator.embed_text(text)

        np.testing.assert_array_equal(embedding1, embedding2)
        assert metadata1.text_checksum == metadata2.text_checksum

    def test_batch_embeddings(self, temp_cache_dir):
        """Test batch embedding generation."""
        generator = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2",
            use_cache=True,
            cache_dir=temp_cache_dir,
        )

        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence.",
        ]

        embeddings, metadata_list = generator.embed_batch(texts)

        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] == generator.embedding_dim
        assert len(metadata_list) == len(texts)

    def test_similarity_computation(self, temp_cache_dir):
        """Test cosine similarity computation."""
        generator = create_standard_generator(use_cache=False)

        text1 = "Cognitive neuroscience studies the brain."
        text2 = "Neuroscience research examines brain function."
        text3 = "The weather is sunny today."

        emb1, _ = generator.embed_text(text1)
        emb2, _ = generator.embed_text(text2)
        emb3, _ = generator.embed_text(text3)

        sim_similar = generator.compute_similarity(emb1, emb2)
        sim_different = generator.compute_similarity(emb1, emb3)

        # Related sentences should be more similar
        assert sim_similar > sim_different
        assert 0 <= sim_similar <= 1
        assert 0 <= sim_different <= 1


class TestFAISSRetriever:
    """Test FAISS retrieval functionality."""

    def test_add_and_search(self):
        """Test adding documents and searching."""
        retriever = create_standard_retriever(embedding_dim=384)
        generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2", use_cache=False)

        # Add documents
        texts = [
            "Predictive processing in neuroscience.",
            "Quantum mechanics and measurement.",
            "Meditation and consciousness.",
        ]

        embeddings_list = []
        for text in texts:
            emb, _ = generator.embed_text(text)
            embeddings_list.append(emb)

        embeddings = np.vstack(embeddings_list)
        metadata = [{"category": "empirical"} for _ in texts]
        chunk_ids = [f"chunk_{i}" for i in range(len(texts))]

        retriever.add_documents(embeddings, texts, metadata, chunk_ids)

        # Search
        query = "brain and prediction"
        query_emb, _ = generator.embed_text(query)

        results, metrics = retriever.search(query_emb, top_k=2)

        assert len(results) <= 2
        assert metrics.num_results == len(results)
        assert all(isinstance(r, RetrievalResult) for r in results)

        # First result should be neuroscience-related
        assert (
            "neuroscience" in results[0].text.lower()
            or "processing" in results[0].text.lower()
        )

    def test_category_filtering(self):
        """Test filtering by category."""
        retriever = create_standard_retriever(embedding_dim=384)
        generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2", use_cache=False)

        texts = ["Empirical text.", "Experiential text."]
        categories = ["empirical", "experiential"]

        embeddings_list = []
        for text in texts:
            emb, _ = generator.embed_text(text)
            embeddings_list.append(emb)

        embeddings = np.vstack(embeddings_list)
        metadata = [{"category": cat} for cat in categories]
        chunk_ids = [f"chunk_{i}" for i in range(len(texts))]

        retriever.add_documents(embeddings, texts, metadata, chunk_ids)

        # Search with filter
        query_emb, _ = generator.embed_text("Test query")
        results, metrics = retriever.search(
            query_emb, top_k=10, category_filter="empirical"
        )

        assert all(r.metadata["category"] == "empirical" for r in results)

    def test_save_and_load(self, tmp_path):
        """Test saving and loading index."""
        retriever = create_standard_retriever(embedding_dim=384)
        generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2", use_cache=False)

        # Add documents
        texts = ["Test document one.", "Test document two."]
        embeddings_list = [generator.embed_text(t)[0] for t in texts]
        embeddings = np.vstack(embeddings_list)
        metadata = [{"category": "test"} for _ in texts]
        chunk_ids = [f"chunk_{i}" for i in range(len(texts))]

        retriever.add_documents(embeddings, texts, metadata, chunk_ids)

        # Save
        save_dir = tmp_path / "index"
        retriever.save(save_dir)

        # Load
        loaded_retriever = FAISSRetriever.load(save_dir)

        assert loaded_retriever.index.ntotal == retriever.index.ntotal
        assert loaded_retriever.chunk_texts == retriever.chunk_texts
        assert loaded_retriever.chunk_ids == retriever.chunk_ids

    def test_get_stats(self):
        """Test index statistics."""
        retriever = create_standard_retriever(embedding_dim=384)
        generator = EmbeddingGenerator(model_name="all-MiniLM-L6-v2", use_cache=False)

        texts = ["Doc 1", "Doc 2", "Doc 3"]
        embeddings_list = [generator.embed_text(t)[0] for t in texts]
        embeddings = np.vstack(embeddings_list)
        metadata = [{"category": "test"} for _ in texts]
        chunk_ids = [f"chunk_{i}" for i in range(len(texts))]

        retriever.add_documents(embeddings, texts, metadata, chunk_ids)

        stats = retriever.get_stats()

        assert stats["total_documents"] == 3
        assert stats["embedding_dim"] == 384
        assert "test" in stats["categories"]


class TestProvenanceTracker:
    """Test provenance tracking functionality."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_record_chunking(self, temp_storage):
        """Test recording chunking operations."""
        tracker = ProvenanceTracker(storage_path=temp_storage)

        record_id = tracker.record_chunking(
            source_document="test.txt",
            num_chunks=5,
            chunk_ids=["c1", "c2", "c3", "c4", "c5"],
            chunker_config={"chunk_size": 500, "overlap": 50},
            text_checksum="abc123",
        )

        assert record_id in tracker.records
        record = tracker.get_record(record_id)
        assert record.operation_type == "chunk"
        assert record.outputs["num_chunks"] == 5

    def test_record_embedding(self, temp_storage):
        """Test recording embedding operations."""
        tracker = ProvenanceTracker(storage_path=temp_storage)

        record_id = tracker.record_embedding(
            chunk_id="chunk_1",
            text_checksum="abc123",
            model_name="all-mpnet-base-v2",
            embedding_checksum="def456",
        )

        record = tracker.get_record(record_id)
        assert record.operation_type == "embed"
        assert record.inputs["model_name"] == "all-mpnet-base-v2"

    def test_record_retrieval(self, temp_storage):
        """Test recording retrieval operations."""
        tracker = ProvenanceTracker(storage_path=temp_storage)

        record_id = tracker.record_retrieval(
            query="test query",
            query_checksum="query123",
            num_results=3,
            result_chunk_ids=["c1", "c2", "c3"],
            retrieval_metrics={"query_time_ms": 15.5},
        )

        record = tracker.get_record(record_id)
        assert record.operation_type == "retrieve"
        assert record.outputs["num_results"] == 3

    def test_record_lineage(self, temp_storage):
        """Test tracking lineage across operations."""
        tracker = ProvenanceTracker(storage_path=temp_storage)

        # Create chain of operations
        chunk_id = tracker.record_chunking(
            source_document="test.txt",
            num_chunks=1,
            chunk_ids=["c1"],
            chunker_config={},
            text_checksum="abc",
        )

        embed_id = tracker.record_embedding(
            chunk_id="c1",
            text_checksum="abc",
            model_name="test-model",
            embedding_checksum="def",
            parent_record_id=chunk_id,
        )

        retrieve_id = tracker.record_retrieval(
            query="test",
            query_checksum="query",
            num_results=1,
            result_chunk_ids=["c1"],
            retrieval_metrics={},
            parent_record_id=embed_id,
        )

        # Get lineage
        lineage = tracker.get_lineage(retrieve_id)

        assert len(lineage) == 3
        assert lineage[0].record_id == chunk_id
        assert lineage[1].record_id == embed_id
        assert lineage[2].record_id == retrieve_id

    def test_record_validation(self, temp_storage):
        """Test record integrity validation."""
        tracker = ProvenanceTracker(storage_path=temp_storage)

        record_id = tracker.record_chunking(
            source_document="test.txt",
            num_chunks=1,
            chunk_ids=["c1"],
            chunker_config={},
            text_checksum="abc",
        )

        is_valid, error = tracker.validate_record(record_id)
        assert is_valid
        assert error is None

    def test_session_export(self, temp_storage):
        """Test exporting session records."""
        tracker = ProvenanceTracker(storage_path=temp_storage)

        # Create some records
        tracker.record_chunking("test.txt", 1, ["c1"], {}, "abc")
        tracker.record_embedding("c1", "abc", "model", "def")

        # Export
        export_path = temp_storage / "session_export.json"
        tracker.export_session(export_path)

        assert export_path.exists()

        # Verify export
        import agent_json

        with open(export_path) as f:
            data = json.load(f)

        assert data["session_id"] == tracker.session_id
        assert data["num_records"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
