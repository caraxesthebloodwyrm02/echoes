"""
Document chunking module for RAG Orbit.

Provides intelligent text segmentation with configurable chunk sizes,
overlap strategies, and metadata preservation for provenance tracking.
"""

import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime, timezone


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""

    chunk_id: str
    source_document: str
    chunk_index: int
    char_start: int
    char_end: int
    token_count: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    category: str = "unknown"  # "empirical" or "experiential" or "mixed"
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "source_document": self.source_document,
            "chunk_index": self.chunk_index,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "token_count": self.token_count,
            "created_at": self.created_at.isoformat(),
            "category": self.category,
            "checksum": self.checksum,
        }


@dataclass
class Chunk:
    """A text chunk with metadata."""

    text: str
    metadata: ChunkMetadata

    def compute_checksum(self) -> str:
        """Compute SHA-256 checksum of chunk text."""
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


class DocumentChunker:
    """
    Intelligent document chunking with overlap and metadata tracking.

    Implements configurable chunking strategies for optimal RAG performance:
    - Fixed-size chunks with overlap (default: 500 tokens, 50 overlap)
    - Semantic boundary detection (paragraph/sentence breaks)
    - Category-aware metadata (empirical vs experiential)
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 50,
        respect_boundaries: bool = True,
    ):
        """
        Initialize chunker with configuration.

        Args:
            chunk_size: Target tokens per chunk
            overlap: Overlap tokens between chunks
            respect_boundaries: Try to break at sentence/paragraph boundaries
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.respect_boundaries = respect_boundaries

    def chunk_document(
        self,
        text: str,
        source_document: str,
        category: str = "unknown",
    ) -> List[Chunk]:
        """
        Chunk a document into overlapping segments.

        Args:
            text: Document text to chunk
            source_document: Source filename or identifier
            category: Data category ("empirical", "experiential", "mixed")

        Returns:
            List of Chunk objects with metadata
        """
        if not text.strip():
            return []

        # Simple whitespace tokenization (for baseline; replace with proper tokenizer later)
        tokens = text.split()
        chunks: List[Chunk] = []

        start_idx = 0
        chunk_index = 0

        while start_idx < len(tokens):
            # Extract chunk tokens
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = " ".join(chunk_tokens)

            # Find character positions in original text
            char_start = text.find(chunk_tokens[0], 0 if start_idx == 0 else chunks[-1].metadata.char_end)
            char_end = char_start + len(chunk_text)

            # Respect sentence boundaries if enabled
            if self.respect_boundaries and end_idx < len(tokens):
                # Look for sentence-ending punctuation in last 20% of chunk
                boundary_start = int(len(chunk_text) * 0.8)
                last_period = chunk_text.rfind(".", boundary_start)
                last_question = chunk_text.rfind("?", boundary_start)
                last_exclaim = chunk_text.rfind("!", boundary_start)

                boundary_pos = max(last_period, last_question, last_exclaim)
                if boundary_pos > 0:
                    chunk_text = chunk_text[: boundary_pos + 1]
                    # Recalculate token count
                    chunk_tokens = chunk_text.split()

            # Generate chunk ID
            chunk_id = hashlib.sha256(f"{source_document}:{chunk_index}".encode("utf-8")).hexdigest()[:16]

            # Create metadata
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                source_document=source_document,
                chunk_index=chunk_index,
                char_start=char_start,
                char_end=char_end,
                token_count=len(chunk_tokens),
                category=category,
            )

            # Create chunk
            chunk = Chunk(text=chunk_text, metadata=metadata)
            chunk.metadata.checksum = chunk.compute_checksum()
            chunks.append(chunk)

            # Move to next chunk with overlap
            start_idx += self.chunk_size - self.overlap
            chunk_index += 1

        return chunks

    def chunk_batch(
        self,
        documents: List[tuple[str, str, str]],
    ) -> List[Chunk]:
        """
        Chunk multiple documents in batch.

        Args:
            documents: List of (text, source_document, category) tuples

        Returns:
            Flattened list of all chunks
        """
        all_chunks: List[Chunk] = []
        for text, source, category in documents:
            chunks = self.chunk_document(text, source, category)
            all_chunks.extend(chunks)
        return all_chunks

    def validate_chunks(self, chunks: List[Chunk]) -> tuple[bool, List[str]]:
        """
        Validate chunk integrity.

        Returns:
            (is_valid, list_of_errors)
        """
        errors: List[str] = []

        for chunk in chunks:
            # Check for empty chunks
            if not chunk.text.strip():
                errors.append(f"Empty chunk: {chunk.metadata.chunk_id}")

            # Verify checksum
            computed = chunk.compute_checksum()
            if computed != chunk.metadata.checksum:
                errors.append(
                    f"Checksum mismatch for {chunk.metadata.chunk_id}: "
                    f"expected {chunk.metadata.checksum}, got {computed}"
                )

            # Check token count
            actual_tokens = len(chunk.text.split())
            if abs(actual_tokens - chunk.metadata.token_count) > 5:  # Allow small variance
                errors.append(
                    f"Token count mismatch for {chunk.metadata.chunk_id}: "
                    f"metadata says {chunk.metadata.token_count}, actual is {actual_tokens}"
                )

        return (len(errors) == 0, errors)


# Factory function for common configurations
def create_standard_chunker() -> DocumentChunker:
    """Create chunker with standard RAG settings."""
    return DocumentChunker(chunk_size=500, overlap=50, respect_boundaries=True)


def create_precise_chunker() -> DocumentChunker:
    """Create chunker with smaller chunks for precise retrieval."""
    return DocumentChunker(chunk_size=300, overlap=75, respect_boundaries=True)


def create_contextual_chunker() -> DocumentChunker:
    """Create chunker with larger chunks for more context."""
    return DocumentChunker(chunk_size=800, overlap=100, respect_boundaries=True)
