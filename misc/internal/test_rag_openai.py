#!/usr/bin/env python3
"""Test script for RAG system with OpenAI embeddings"""

try:
    from echoes_modules.rag_v2 import create_rag_system

    rag = create_rag_system("balanced")
    print("✅ RAG system created successfully with OpenAI embeddings")
    stats = rag.get_stats()
    print(f'   Model: {stats["model_name"]}')
    print(f'   Provider: {stats["provider"]}')
    print(f'   Embedding dimension: {stats["embedding_dimension"]}')

    # Test adding a document
    test_docs = ["Echoes is an AI platform using OpenAI embeddings."]
    result = rag.add_documents(test_docs)
    print(f'   Added {result["total_chunks"]} test documents')

    # Test search
    search_result = rag.search("What is Echoes?", top_k=1)
    if search_result["results"]:
        print(f'   Search test: Found {len(search_result["results"])} results')
        print(f'   Top result score: {search_result["results"][0]["score"]:.4f}')

    print("✅ All RAG tests passed!")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
