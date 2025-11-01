"""
RAG V2 module - Simple implementation for assistant functionality.

Provides Retrieval-Augmented Generation capabilities for the Echoes assistant.
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


@dataclass
class Document:
    """Represents a document in the RAG system."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class SimpleRAGSystem:
    """Simple in-memory RAG system."""
    
    def __init__(self, preset: str = "balanced"):
        self.preset = preset
        self.documents: Dict[str, Document] = {}
        self.embeddings_cache: Dict[str, List[float]] = {}
        self.config = self._get_preset_config(preset)
    
    def _get_preset_config(self, preset: str) -> Dict[str, Any]:
        """Get configuration for preset."""
        configs = {
            "fast": {
                "max_results": 3,
                "similarity_threshold": 0.5,
                "chunk_size": 500
            },
            "balanced": {
                "max_results": 5,
                "similarity_threshold": 0.3,
                "chunk_size": 1000
            },
            "accurate": {
                "max_results": 10,
                "similarity_threshold": 0.1,
                "chunk_size": 2000
            }
        }
        return configs.get(preset, configs["balanced"])
    
    def _create_embedding(self, text: str) -> List[float]:
        """Create simple embedding using hash-based approach."""
        # Use text hash to create deterministic pseudo-embedding
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to float values
        embedding = []
        for i in range(0, min(len(hash_hex), 128), 2):
            hex_pair = hash_hex[i:i+2]
            if len(hex_pair) == 2:
                val = int(hex_pair, 16) / 255.0 - 0.5
                embedding.append(val)
        
        # Pad to 128 dimensions
        while len(embedding) < 128:
            embedding.append(0.0)
        
        return embedding[:128]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity."""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def add_documents(self, documents: Union[str, List[str], Dict[str, Any]]) -> Dict[str, Any]:
        """Add documents to the RAG system."""
        added_count = 0
        
        if isinstance(documents, str):
            documents = [documents]
        elif isinstance(documents, dict):
            documents = [documents]
        
        for doc in documents:
            if isinstance(doc, str):
                content = doc
                metadata = {}
            else:
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
            
            # Create document
            doc_id = hashlib.md5(content.encode()).hexdigest()[:16]
            embedding = self._create_embedding(content)
            
            document = Document(
                id=doc_id,
                content=content,
                metadata=metadata,
                embedding=embedding
            )
            
            self.documents[doc_id] = document
            added_count += 1
        
        return {
            "added": added_count,
            "total": len(self.documents),
            "total_chunks": added_count  # Simple implementation doesn't chunk
        }
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Document]:
        """Search for relevant documents."""
        if not query:
            return []
        
        query_embedding = self._create_embedding(query)
        max_results = max_results or self.config["max_results"]
        
        # Calculate similarities
        results = []
        for doc in self.documents.values():
            if doc.embedding:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                if similarity >= self.config["similarity_threshold"]:
                    results.append((doc, similarity))
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:max_results]]
    
    def generate_context(self, query: str, max_context_length: int = 2000) -> str:
        """Generate context from search results."""
        relevant_docs = self.search(query)
        
        context_parts = []
        current_length = 0
        
        for doc in relevant_docs:
            if current_length + len(doc.content) <= max_context_length:
                context_parts.append(doc.content)
                current_length += len(doc.content)
            else:
                # Add partial content if space allows
                remaining = max_context_length - current_length
                if remaining > 100:  # Only add if we can include meaningful content
                    context_parts.append(doc.content[:remaining-3] + "...")
                break
        
        return "\n\n".join(context_parts)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return {
            "total_documents": len(self.documents),
            "preset": self.preset,
            "config": self.config,
            "cache_size": len(self.embeddings_cache)
        }


def create_rag_system(preset: str = "balanced") -> SimpleRAGSystem:
    """Create a RAG system with specified preset."""
    return SimpleRAGSystem(preset)


# Check if OpenAI embeddings are available
OPENAI_RAG_AVAILABLE = False
try:
    # In a real implementation, would check for OpenAI client
    # For now, we'll use the simple implementation
    OPENAI_RAG_AVAILABLE = False
except:
    pass


# Export symbols
__all__ = [
    'create_rag_system',
    'SimpleRAGSystem',
    'Document',
    'OPENAI_RAG_AVAILABLE'
]
