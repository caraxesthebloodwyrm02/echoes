# echoes/core/rag_v2.py
"""
RAG V2 interface wrapper for the Echoes AI Assistant.
Provides backward compatibility with the expected RAG API.
"""

from typing import List, Dict, Any, Optional
from core.rag_integration import EchoesRAG


class RAGSystem:
    """RAG System wrapper class."""

    def __init__(self, rag_instance: EchoesRAG):
        self.rag = rag_instance

    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add documents to the RAG system."""
        doc_ids = []
        for doc in documents:
            if isinstance(doc, dict) and "text" in doc:
                result = self.rag.add_document(doc["text"], doc.get("metadata", {}))
                if isinstance(result, list) and result:
                    doc_ids.extend(result)
            else:
                result = self.rag.add_document(str(doc), {})
                if isinstance(result, list) and result:
                    doc_ids.extend(result)

        return {"total_chunks": len(doc_ids)}

    def search(self, query: str, top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """Search for relevant documents."""
        results = self.rag.search(query, top_k=top_k, **kwargs)
        # Transform results to expected format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.get("content", ""),
                "score": result.get("score", 0.0),
                "metadata": result.get("metadata", {})
            })
        # Return object with results attribute
        return {"results": formatted_results}

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return self.rag.get_stats()


def create_rag_system(preset: str = "balanced") -> RAGSystem:
    """
    Create a RAG system instance.

    Args:
        preset: Configuration preset ("balanced", "fast", "accurate")

    Returns:
        Configured RAGSystem instance
    """
    # Configure based on preset
    config = {}

    if preset == "balanced":
        config.update({
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 3,
        })
    elif preset == "fast":
        config.update({
            "chunk_size": 500,
            "chunk_overlap": 100,
            "top_k": 2,
        })
    elif preset == "accurate":
        config.update({
            "chunk_size": 1500,
            "chunk_overlap": 300,
            "top_k": 5,
        })

    # Create the underlying RAG instance
    rag_instance = EchoesRAG(config=config)

    # Wrap it in our interface
    return RAGSystem(rag_instance)
