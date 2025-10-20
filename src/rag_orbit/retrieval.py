"""
FAISS-based retrieval module for RAG Orbit.

Provides efficient similarity search over document embeddings with
filtering, ranking, and provenance tracking.
"""

import faiss
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import json


@dataclass
class RetrievalResult:
    """A single retrieval result with metadata."""

    chunk_id: str
    text: str
    similarity_score: float
    metadata: Dict[str, Any]
    rank: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "similarity_score": float(self.similarity_score),
            "metadata": self.metadata,
            "rank": self.rank,
        }


@dataclass
class RetrievalMetrics:
    """Metrics for a retrieval operation."""

    query_time_ms: float
    num_results: int
    avg_similarity: float
    min_similarity: float
    max_similarity: float
    filtered_count: int = 0


class FAISSRetriever:
    """
    FAISS-based vector similarity search for RAG.

    Supports multiple index types, filtering, and efficient batch retrieval.
    """

    def __init__(
        self,
        embedding_dim: int = 768,
        index_type: str = "flat",
        metric: str = "cosine",
    ):
        """
        Initialize FAISS retriever.

        Args:
            embedding_dim: Dimension of embeddings
            index_type: "flat" (exact) or "ivf" (approximate)
            metric: "cosine" or "l2"
        """
        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.metric = metric

        # Create FAISS index
        if index_type == "flat":
            if metric == "cosine":
                # Cosine similarity = inner product on normalized vectors
                self.index = faiss.IndexFlatIP(embedding_dim)
            else:
                self.index = faiss.IndexFlatL2(embedding_dim)
        elif index_type == "ivf":
            # IVF index for larger datasets (approximate search)
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
            self.trained = False
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Metadata storage (parallel to FAISS index)
        self.chunk_texts: List[str] = []
        self.chunk_metadata: List[Dict[str, Any]] = []
        self.chunk_ids: List[str] = []

    def add_documents(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadata: List[Dict[str, Any]],
        chunk_ids: List[str],
    ) -> None:
        """
        Add documents to the index.

        Args:
            embeddings: Embedding matrix (N x embedding_dim)
            texts: List of chunk texts
            metadata: List of metadata dicts
            chunk_ids: List of chunk identifiers
        """
        if len(texts) != len(metadata) != len(chunk_ids) != embeddings.shape[0]:
            raise ValueError("Mismatched lengths for texts, metadata, chunk_ids, and embeddings")

        # Normalize embeddings for cosine similarity
        if self.metric == "cosine":
            faiss.normalize_L2(embeddings)

        # Train IVF index if needed
        if self.index_type == "ivf" and not self.trained:
            self.index.train(embeddings)
            self.trained = True

        # Add to FAISS index
        self.index.add(embeddings)

        # Add to metadata storage
        self.chunk_texts.extend(texts)
        self.chunk_metadata.extend(metadata)
        self.chunk_ids.extend(chunk_ids)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        min_similarity: float = 0.0,
        category_filter: Optional[str] = None,
    ) -> tuple[List[RetrievalResult], RetrievalMetrics]:
        """
        Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            category_filter: Filter by category ("empirical", "experiential", etc.)

        Returns:
            (list_of_results, metrics)
        """
        import time

        start_time = time.perf_counter()

        # Normalize query for cosine similarity
        if self.metric == "cosine":
            query_normalized = query_embedding.copy()
            faiss.normalize_L2(query_normalized.reshape(1, -1))
            query_embedding = query_normalized.reshape(-1)

        # Search FAISS index (retrieve more for filtering)
        search_k = min(top_k * 3, self.index.ntotal)
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1),
            search_k,
        )

        # Convert distances to similarity scores
        if self.metric == "cosine":
            similarities = distances[0]  # Already in [0, 1] for cosine
        else:
            # Convert L2 distance to similarity
            similarities = 1 / (1 + distances[0])

        # Build results with filtering
        results: List[RetrievalResult] = []
        filtered_count = 0

        for idx, similarity in zip(indices[0], similarities):
            if idx == -1:  # FAISS padding
                continue

            # Apply similarity threshold
            if similarity < min_similarity:
                filtered_count += 1
                continue

            # Apply category filter
            metadata = self.chunk_metadata[idx]
            if category_filter and metadata.get("category") != category_filter:
                filtered_count += 1
                continue

            # Create result
            result = RetrievalResult(
                chunk_id=self.chunk_ids[idx],
                text=self.chunk_texts[idx],
                similarity_score=float(similarity),
                metadata=metadata,
                rank=len(results) + 1,
            )
            results.append(result)

            # Stop at top_k
            if len(results) >= top_k:
                break

        # Compute metrics
        end_time = time.perf_counter()
        query_time_ms = (end_time - start_time) * 1000

        metrics = RetrievalMetrics(
            query_time_ms=query_time_ms,
            num_results=len(results),
            avg_similarity=float(np.mean([r.similarity_score for r in results])) if results else 0.0,
            min_similarity=float(min([r.similarity_score for r in results])) if results else 0.0,
            max_similarity=float(max([r.similarity_score for r in results])) if results else 0.0,
            filtered_count=filtered_count,
        )

        return results, metrics

    def batch_search(
        self,
        query_embeddings: np.ndarray,
        top_k: int = 10,
        min_similarity: float = 0.0,
    ) -> List[tuple[List[RetrievalResult], RetrievalMetrics]]:
        """
        Search for multiple queries in batch.

        Args:
            query_embeddings: Query embedding matrix (N x embedding_dim)
            top_k: Number of results per query
            min_similarity: Minimum similarity threshold

        Returns:
            List of (results, metrics) tuples
        """
        all_results: List[tuple[List[RetrievalResult], RetrievalMetrics]] = []

        for i in range(query_embeddings.shape[0]):
            query_emb = query_embeddings[i]
            results, metrics = self.search(query_emb, top_k, min_similarity)
            all_results.append((results, metrics))

        return all_results

    def save(self, save_dir: Path) -> None:
        """
        Save index and metadata to disk.

        Args:
            save_dir: Directory to save index files
        """
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_path = save_dir / "faiss.index"
        faiss.write_index(self.index, str(index_path))

        # Save metadata
        metadata_path = save_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(
                {
                    "chunk_texts": self.chunk_texts,
                    "chunk_metadata": self.chunk_metadata,
                    "chunk_ids": self.chunk_ids,
                    "config": {
                        "embedding_dim": self.embedding_dim,
                        "index_type": self.index_type,
                        "metric": self.metric,
                    },
                },
                f,
                indent=2,
            )

    @classmethod
    def load(cls, save_dir: Path) -> "FAISSRetriever":
        """
        Load index and metadata from disk.

        Args:
            save_dir: Directory containing saved index

        Returns:
            Loaded FAISSRetriever instance
        """
        # Load metadata
        metadata_path = save_dir / "metadata.json"
        with open(metadata_path, "r") as f:
            data = json.load(f)

        # Create retriever
        config = data["config"]
        retriever = cls(
            embedding_dim=config["embedding_dim"],
            index_type=config["index_type"],
            metric=config["metric"],
        )

        # Load FAISS index
        index_path = save_dir / "faiss.index"
        retriever.index = faiss.read_index(str(index_path))

        # Load metadata
        retriever.chunk_texts = data["chunk_texts"]
        retriever.chunk_metadata = data["chunk_metadata"]
        retriever.chunk_ids = data["chunk_ids"]

        if config["index_type"] == "ivf":
            retriever.trained = True

        return retriever

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_documents": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "index_type": self.index_type,
            "metric": self.metric,
            "categories": list(set(m.get("category", "unknown") for m in self.chunk_metadata)),
        }


# Factory functions
def create_standard_retriever(embedding_dim: int = 768) -> FAISSRetriever:
    """Create retriever with standard settings (exact search, cosine)."""
    return FAISSRetriever(
        embedding_dim=embedding_dim,
        index_type="flat",
        metric="cosine",
    )


def create_fast_retriever(embedding_dim: int = 768) -> FAISSRetriever:
    """Create retriever with approximate search for large datasets."""
    return FAISSRetriever(
        embedding_dim=embedding_dim,
        index_type="ivf",
        metric="cosine",
    )
