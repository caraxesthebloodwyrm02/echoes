# echoes/core/rag_v2.py
"""
RAG V2 interface wrapper for the Echoes AI Assistant.
Provides backward compatibility with the expected RAG API.
Uses OpenAI embeddings for OpenAI-first approach.
"""

from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path to import openai_rag modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from openai_rag.openai_embeddings import OpenAIEmbeddings
    from openai_rag.rag_openai import create_rag_system_openai
    OPENAI_RAG_AVAILABLE = True
except ImportError:
    OPENAI_RAG_AVAILABLE = False
    print("Warning: OpenAI RAG not available. Check OpenAI API key.")

try:
    from core.rag_integration import EchoesRAG
    LEGACY_RAG_AVAILABLE = True
except ImportError:
    LEGACY_RAG_AVAILABLE = False


class RAGSystem:
    """RAG System wrapper class."""

    def __init__(self, rag_instance):
        """Initialize with any RAG instance."""
        self.rag = rag_instance

    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add documents to the RAG system."""
        doc_ids = []
        for doc in documents:
            if isinstance(doc, dict) and "text" in doc:
                result = self.rag.add_document(doc["text"], doc.get("metadata", {}))
                if isinstance(result, list):
                    doc_ids.extend(result)
            else:
                result = self.rag.add_document(str(doc), {})
                if isinstance(result, list):
                    doc_ids.extend(result)

        return {"total_chunks": len(doc_ids)}

    def search(self, query: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """Search for relevant documents."""
        results = self.rag.search(query, top_k=top_k, **kwargs)
        
        # Handle different result formats
        if isinstance(results, list):
            # Already in the right format
            formatted_results = results
        elif isinstance(results, dict) and "results" in results:
            # Has results attribute
            formatted_results = results["results"]
        else:
            # Unexpected format
            formatted_results = []
        
        # Ensure each result has the expected fields
        final_results = []
        for result in formatted_results:
            final_results.append({
                "content": result.get("content", result.get("text", "")),
                "score": result.get("score", 0.0),
                "metadata": result.get("metadata", {}),
            })
        
        # Return object with results attribute
        return {"results": final_results}

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        if hasattr(self.rag, 'get_stats'):
            return self.rag.get_stats()
        else:
            return {"status": "stats_not_available"}


def create_rag_system(preset: str = "balanced", **kwargs) -> RAGSystem:
    """
    Create a RAG system instance.
    Tries OpenAI RAG first, falls back to legacy if needed.
    
    Args:
        preset: Configuration preset
        **kwargs: Additional configuration
        
    Returns:
        RAGSystem wrapper instance
    """
    # Try OpenAI RAG first (OpenAI-first approach)
    if OPENAI_RAG_AVAILABLE:
        try:
            rag_instance = create_rag_system_openai(preset=preset, **kwargs)
            print(f"✓ Using OpenAI RAG system with preset: {preset}")
            return RAGSystem(rag_instance)
        except Exception as e:
            print(f"⚠️ OpenAI RAG initialization failed: {e}")
    
    # Fall back to legacy RAG
    if LEGACY_RAG_AVAILABLE:
        try:
            from core.rag_integration import EchoesRAG
            rag_instance = EchoesRAG(kwargs)
            print(f"✓ Using legacy RAG system with preset: {preset}")
            return RAGSystem(rag_instance)
        except Exception as e:
            print(f"⚠️ Legacy RAG initialization failed: {e}")
    
    # No RAG available
    print("❌ No RAG system available")
    return None


