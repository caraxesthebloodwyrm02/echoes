"""
RAG Orbit: Retrieval-Augmented Generation system for Cross-Reality Cognition Framework.

This module provides the baseline infrastructure for document processing,
embedding generation, vector storage, and retrieval with provenance tracking.
"""

from .chunking import DocumentChunker, ChunkMetadata
from .embeddings import EmbeddingGenerator, EmbeddingCache
from .retrieval import FAISSRetriever, RetrievalResult
from .provenance import ProvenanceTracker, ProvenanceRecord

__version__ = "0.1.0"
__all__ = [
    "DocumentChunker",
    "ChunkMetadata",
    "EmbeddingGenerator",
    "EmbeddingCache",
    "FAISSRetriever",
    "RetrievalResult",
    "ProvenanceTracker",
    "ProvenanceRecord",
]
