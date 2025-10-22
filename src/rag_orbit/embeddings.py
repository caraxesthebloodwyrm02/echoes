"""
Embedding generation module for RAG Orbit.

Provides high-quality semantic embeddings using sentence-transformers
with caching, batch processing, and provenance tracking.
"""

import hashlib
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, asdict
import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbeddingMetadata:
    """Metadata for an embedding."""

    text_checksum: str
    model_name: str
    embedding_dim: int
    created_at: str
    chunk_id: Optional[str] = None


class EmbeddingCache:
    """
    Disk-based cache for embeddings to avoid recomputation.

    Uses SHA-256 hashes of (text, model_name) as cache keys.
    """

    def __init__(self, cache_dir: Path = Path(".cache/embeddings")):
        """Initialize cache with storage directory."""
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key from text and model."""
        combined = f"{model_name}:{text}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def get(self, text: str, model_name: str) -> Optional[tuple[np.ndarray, EmbeddingMetadata]]:
        """Retrieve embedding from cache if available."""
        key = self._cache_key(text, model_name)
        cache_file = self.cache_dir / f"{key}.npz"
        metadata_file = self.cache_dir / f"{key}.json"

        if cache_file.exists() and metadata_file.exists():
            try:
                # Load embedding
                data = np.load(cache_file)
                embedding = data["embedding"]

                # Load metadata
                with open(metadata_file, "r") as f:
                    metadata_dict = json.load(f)
                metadata = EmbeddingMetadata(**metadata_dict)

                return embedding, metadata
            except Exception:
                # Cache corrupted, ignore
                return None

        return None

    def put(
        self,
        text: str,
        model_name: str,
        embedding: np.ndarray,
        metadata: EmbeddingMetadata,
    ) -> None:
        """Store embedding in cache."""
        key = self._cache_key(text, model_name)
        cache_file = self.cache_dir / f"{key}.npz"
        metadata_file = self.cache_dir / f"{key}.json"

        # Save embedding
        np.savez_compressed(cache_file, embedding=embedding)

        # Save metadata
        with open(metadata_file, "w") as f:
            json.dump(asdict(metadata), f, indent=2)

    def clear(self) -> int:
        """Clear all cached embeddings. Returns count of deleted files."""
        count = 0
        for file in self.cache_dir.glob("*"):
            file.unlink()
            count += 1
        return count // 2  # Each embedding has 2 files


class EmbeddingGenerator:
    """
    Generate semantic embeddings using sentence-transformers.

    Supports batch processing, caching, and multiple model backends.
    Default model: all-mpnet-base-v2 (768-dim, best quality/speed balance)
    """

    def __init__(
        self,
        model_name: str = "all-mpnet-base-v2",
        use_cache: bool = True,
        cache_dir: Optional[Path] = None,
        device: str = "cpu",
    ):
        """
        Initialize embedding generator.

        Args:
            model_name: HuggingFace model identifier
            use_cache: Enable disk caching
            cache_dir: Custom cache directory
            device: "cpu" or "cuda"
        """
        self.model_name = model_name
        self.device = device
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        self.use_cache = use_cache
        self.cache = EmbeddingCache(cache_dir) if use_cache else None

    def embed_text(
        self,
        text: str,
        chunk_id: Optional[str] = None,
    ) -> tuple[np.ndarray, EmbeddingMetadata]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text
            chunk_id: Optional chunk identifier for provenance

        Returns:
            (embedding_vector, metadata)
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(text, self.model_name)
            if cached is not None:
                return cached

        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)

        # Create metadata
        text_checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
        from datetime import datetime, timezone

        metadata = EmbeddingMetadata(
            text_checksum=text_checksum,
            model_name=self.model_name,
            embedding_dim=self.embedding_dim,
            created_at=datetime.now(timezone.utc).isoformat(),
            chunk_id=chunk_id,
        )

        # Cache if enabled
        if self.cache:
            self.cache.put(text, self.model_name, embedding, metadata)

        return embedding, metadata

    def embed_batch(
        self,
        texts: List[str],
        chunk_ids: Optional[List[str]] = None,
        batch_size: int = 32,
    ) -> tuple[np.ndarray, List[EmbeddingMetadata]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of input texts
            chunk_ids: Optional list of chunk identifiers
            batch_size: Batch size for model inference

        Returns:
            (embedding_matrix, list_of_metadata)
        """
        if chunk_ids is None:
            chunk_ids = [None] * len(texts)

        embeddings_list: List[np.ndarray] = []
        metadata_list: List[EmbeddingMetadata] = []

        # Check cache for each text
        uncached_indices: List[int] = []
        uncached_texts: List[str] = []

        for i, text in enumerate(texts):
            if self.cache:
                cached = self.cache.get(text, self.model_name)
                if cached is not None:
                    embeddings_list.append(cached[0])
                    metadata_list.append(cached[1])
                    continue

            uncached_indices.append(i)
            uncached_texts.append(text)

        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.model.encode(
                uncached_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(uncached_texts) > 100,
            )

            from datetime import datetime, timezone

            for i, (text, embedding) in enumerate(zip(uncached_texts, new_embeddings)):
                idx = uncached_indices[i]
                text_checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
                metadata = EmbeddingMetadata(
                    text_checksum=text_checksum,
                    model_name=self.model_name,
                    embedding_dim=self.embedding_dim,
                    created_at=datetime.now(timezone.utc).isoformat(),
                    chunk_id=chunk_ids[idx],
                )

                # Cache new embedding
                if self.cache:
                    self.cache.put(text, self.model_name, embedding, metadata)

                embeddings_list.append(embedding)
                metadata_list.append(metadata)

        # Stack embeddings into matrix
        embeddings_matrix = np.vstack(embeddings_list)

        return embeddings_matrix, metadata_list

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Returns:
            Similarity score in [0, 1] (higher = more similar)
        """
        # Normalize vectors
        norm1 = embedding1 / np.linalg.norm(embedding1)
        norm2 = embedding2 / np.linalg.norm(embedding2)

        # Cosine similarity
        similarity = np.dot(norm1, norm2)

        # Map from [-1, 1] to [0, 1]
        return (similarity + 1) / 2


# Factory functions
def create_standard_generator(use_cache: bool = True) -> EmbeddingGenerator:
    """Create generator with standard all-mpnet-base-v2 model."""
    return EmbeddingGenerator(
        model_name="all-mpnet-base-v2",
        use_cache=use_cache,
    )


def create_fast_generator(use_cache: bool = True) -> EmbeddingGenerator:
    """Create generator with faster all-MiniLM-L6-v2 model (384-dim)."""
    return EmbeddingGenerator(
        model_name="all-MiniLM-L6-v2",
        use_cache=use_cache,
    )


def create_multilingual_generator(use_cache: bool = True) -> EmbeddingGenerator:
    """Create generator with multilingual support."""
    return EmbeddingGenerator(
        model_name="paraphrase-multilingual-mpnet-base-v2",
        use_cache=use_cache,
    )
