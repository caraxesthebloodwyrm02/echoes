#!/usr/bin/env python3
"""Test script for OpenAI RAG system."""

from echoes.core.rag_v2 import create_rag_system

def test_openai_rag():
    """Test the OpenAI RAG system."""
    
    print("Testing OpenAI RAG system...")
    
    # Create RAG system
    rag = create_rag_system(preset="balanced")
    
    if rag is None:
        print("❌ Failed to create RAG system")
        return
    
    print("✓ RAG system created successfully")
    
    # Test adding documents
    test_docs = [
        {"text": "Echoes is an AI assistant built with OpenAI.", "metadata": {"source": "test"}},
        {"text": "The assistant can interact with files using function calling.", "metadata": {"source": "test"}},
        {"text": "OpenAI provides powerful embedding models for semantic search.", "metadata": {"source": "test"}}
    ]
    
    result = rag.add_documents(test_docs)
    print(f"✓ Added {result['total_chunks']} document chunks")
    
    # Test search
    search_results = rag.search("AI assistant files", top_k=3)
    print(f"✓ Search found {len(search_results['results'])} results")
    
    for i, res in enumerate(search_results['results'], 1):
        print(f"  Result {i}: Score={res['score']:.3f}, Content='{res['content'][:50]}...'")
    
    # Get stats
    stats = rag.get_stats()
    print(f"✓ RAG stats: {stats}")
    
    print("\n✅ OpenAI RAG system working correctly!")

if __name__ == "__main__":
    test_openai_rag()
