"""
RAG System with OpenAI Embeddings

Modified version of RAG system that uses OpenAI embeddings instead of sentence-transformers.
Follows the OpenAI-first approach.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json
import hashlib
import time
from dataclasses import dataclass, field

from .openai_embeddings import OpenAIEmbeddings, OpenAIVectorStore, create_openai_vector_store

logger = logging.getLogger(__name__)


@dataclass
class RAGOpenAIConfig:
    """Configuration for OpenAI-based RAG system."""
    
    # OpenAI settings
    embedding_model: str = "text-embedding-3-small"
    openai_api_key: Optional[str] = None
    
    # Text processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Search settings
    top_k: int = 3
    similarity_threshold: float = 0.7
    
    # Storage paths
    vector_db_path: Path = field(default_factory=lambda: Path("vector_index_openai/"))
    memory_dir: Path = field(default_factory=lambda: Path("memory/"))
    cache_dir: Path = field(default_factory=lambda: Path(".cache/"))
    
    # Features
    enable_recency_bias: bool = True
    enable_context_fusion: bool = True
    enable_semantic_threading: bool = True


class RAGOpenAI:
    """
    RAG system using OpenAI embeddings.
    Provides document ingestion, storage, and semantic search.
    """
    
    def __init__(self, config: Optional[RAGOpenAIConfig] = None):
        """Initialize the RAG system."""
        self.config = config or RAGOpenAIConfig()
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model_name=self.config.embedding_model,
            api_key=self.config.openai_api_key
        )
        
        # Initialize vector store
        self.vector_store = create_openai_vector_store(self.config.embedding_model)
        
        # Ensure directories exist
        self.config.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.config.memory_dir.mkdir(parents=True, exist_ok=True)
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "documents_added": 0,
            "chunks_created": 0,
            "searches_performed": 0,
            "total_documents": 0
        }
        
        logger.info(f"RAG OpenAI system initialized with model: {self.config.embedding_model}")
    
    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        chunk_size = chunk_size or self.config.chunk_size
        overlap = overlap or self.config.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this is not the last chunk, try to break at a sentence
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunks.append(text[start:end].strip())
            
            # Move start position with overlap
            if end >= len(text):
                break
            
            start = max(start + 1, end - overlap)
        
        return [chunk for chunk in chunks if chunk]
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Add a document to the RAG system.
        
        Args:
            text: Document text
            metadata: Optional metadata
            
        Returns:
            List of chunk IDs
        """
        if not text or not text.strip():
            return []
        
        # Create metadata if not provided
        metadata = metadata or {}
        metadata.update({
            "added_at": time.time(),
            "source": metadata.get("source", "unknown")
        })
        
        # Split into chunks
        chunks = self._chunk_text(text)
        
        if not chunks:
            return []
        
        # Create metadata for each chunk
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_id": hashlib.md5(f"{chunk}_{time.time()}_{i}".encode()).hexdigest()[:16]
            })
            chunk_metadatas.append(chunk_metadata)
        
        # Add to vector store
        chunk_ids = self.vector_store.add_texts(chunks, chunk_metadatas)
        
        # Update statistics
        self.stats["documents_added"] += 1
        self.stats["chunks_created"] += len(chunks)
        self.stats["total_documents"] = len(self.vector_store.documents)
        
        logger.info(f"Added document: {len(chunks)} chunks created")
        return chunk_ids
    
    def search(self, query: str, top_k: int = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        if not query or not query.strip():
            return []
        
        top_k = top_k or self.config.top_k
        
        # Perform similarity search
        results = self.vector_store.similarity_search(query, k=top_k)
        
        # Filter by similarity threshold if configured
        if self.config.similarity_threshold > 0:
            results = [
                r for r in results 
                if r.get("score", 0) >= self.config.similarity_threshold
            ]
        
        # Update statistics
        self.stats["searches_performed"] += 1
        
        logger.info(f"Search completed: {len(results)} results found")
        return results
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add multiple texts to the RAG system.
        
        Args:
            texts: List of texts
            metadatas: Optional metadata for each text
            
        Returns:
            List of chunk IDs
        """
        all_chunk_ids = []
        
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}
            chunk_ids = self.add_document(text, metadata)
            all_chunk_ids.extend(chunk_ids)
        
        return all_chunk_ids
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        stats = self.stats.copy()
        stats.update({
            "embedding_model": self.config.embedding_model,
            "vector_dimension": self.embeddings.dimension,
            "config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "top_k": self.config.top_k
            }
        })
        return stats
    
    def save(self, path: Optional[str] = None):
        """Save the vector store to disk."""
        save_path = path or str(self.config.vector_db_path)
        self.vector_store.save_local(save_path)
        
        # Save stats
        stats_path = Path(save_path) / "stats.json"
        with open(stats_path, "w") as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"RAG system saved to {save_path}")
    
    def load(self, path: Optional[str] = None):
        """Load the vector store from disk."""
        load_path = path or str(self.config.vector_db_path)
        
        try:
            self.vector_store = OpenAIVectorStore.load_local(load_path, self.embeddings)
            
            # Load stats
            stats_path = Path(load_path) / "stats.json"
            if stats_path.exists():
                with open(stats_path, "r") as f:
                    self.stats = json.load(f)
            
            logger.info(f"RAG system loaded from {load_path}")
            
        except Exception as e:
            logger.warning(f"Could not load RAG system from {load_path}: {str(e)}")
    
    def clear(self):
        """Clear all documents from the RAG system."""
        self.vector_store = create_openai_vector_store(self.config.embedding_model)
        self.stats = {
            "documents_added": 0,
            "chunks_created": 0,
            "searches_performed": 0,
            "total_documents": 0
        }
        logger.info("RAG system cleared")


def create_rag_system_openai(preset: str = "balanced", **kwargs) -> RAGOpenAI:
    """
    Create a RAG system with OpenAI embeddings.
    
    Args:
        preset: Configuration preset ("fast", "balanced", "accurate")
        **kwargs: Additional configuration parameters
        
    Returns:
        RAGOpenAI instance
    """
    # Preset configurations
    presets = {
        "fast": {
            "embedding_model": "text-embedding-3-small",
            "chunk_size": 500,
            "chunk_overlap": 50,
            "top_k": 3
        },
        "balanced": {
            "embedding_model": "text-embedding-3-small",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 5
        },
        "accurate": {
            "embedding_model": "text-embedding-3-large",
            "chunk_size": 1500,
            "chunk_overlap": 300,
            "top_k": 7
        }
    }
    
    config_dict = presets.get(preset, presets["balanced"])
    config_dict.update(kwargs)
    
    config = RAGOpenAIConfig(**config_dict)
    return RAGOpenAI(config)
