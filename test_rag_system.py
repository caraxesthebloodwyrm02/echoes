"""
RAG System Test Script

This script provides test cases for the RAG (Retrieval-Augmented Generation) system.
Copy the code blocks into Jupyter notebook cells to test different functionalities.
"""

# Cell 1: Import required libraries
"""
import sys
import os
from pathlib import Path
from core.rag_integration import EchoesRAG
from pprint import pprint
"""

# Cell 2: Initialize the RAG system
"""
rag = EchoesRAG()
print("RAG system initialized successfully!")
"""

# Cell 3: Add test documents
"""
test_documents = [
    {
        'text': """Project Echoes - Core Features

Echoes is a personal knowledge management system with the following features:
- Document storage and retrieval
- Semantic search
- Context-aware AI assistance
- Cross-referencing of information

The system uses advanced NLP techniques to understand and organize your knowledge.
""",
        'metadata': {
            'title': 'Project Echoes Overview',
            'type': 'documentation',
            'category': 'project'
        }
    },
    {
        'text': """RAG System Architecture

The RAG (Retrieval-Augmented Generation) system consists of:
1. Document Processor: Handles document ingestion and chunking
2. Vector Store: Stores document embeddings for semantic search
3. Retriever: Finds relevant document chunks for a query
4. Generator: Generates responses using the retrieved context
""",
        'metadata': {
            'title': 'RAG Architecture',
            'type': 'technical',
            'category': 'system_design'
        }
    }
]

# Add documents to the RAG system
num_added = rag.add_documents(test_documents)
print(f"Added {num_added} documents to the RAG system.")
"""

# Cell 4: Test semantic search
"""
def test_search(query, top_k=2):
    print(f"\nSearching for: {query}")
    results = rag.search(query, top_k=top_k)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.3f}):")
        print("-" * 50)
        print(result['content'])
        print("\nMetadata:", result['metadata'])
        print("=" * 50)

# Test different queries
test_search("What is Project Echoes?")
test_search("How does the RAG system work?")
"""

# Cell 5: Test context-aware generation
"""
def generate_response(query):
    print(f"\nQuery: {query}")
    print("-" * 50)

    # Get context from RAG
    context_result = rag.get_context(query)

    # Simple generation function (in a real scenario, this would call an LLM)
    def simple_generation(prompt):
        # This is a placeholder - in practice, you'd use an actual LLM
        if "Project Echoes" in prompt:
            return "Project Echoes is a personal knowledge management system with features like document storage, semantic search, and AI assistance. It helps you organize and retrieve your knowledge efficiently."
        elif "RAG" in prompt:
            return "The RAG (Retrieval-Augmented Generation) system combines document retrieval with text generation to provide accurate and contextually relevant responses based on the available knowledge base."
        return "I don't have enough information to answer that question."

    # Generate response using the context
    response = rag.generate_with_context(
        user_prompt=query,
        generation_func=simple_generation
    )

    print("\nGenerated Response:")
    print("-" * 20)
    print(response['response'])

    print("\nSources:")
    for i, source in enumerate(response['sources'], 1):
        print(f"{i}. {source['source']} (Score: {source['score']:.3f})")

    return response

# Test generation
generate_response("Tell me about Project Echoes")
generate_response("Explain how the RAG system works")
"""

# Cell 6: Test feedback mechanism
"""
# First, perform a search to get a query_id
search_results = rag.get_context("What is Project Echoes?")
query_id = search_results['query_id']

# Provide feedback about the search results
feedback = rag.add_feedback(
    query_id=query_id,
    relevant_doc_ids=[doc['metadata']['doc_id'] for doc in search_results['sources']],
    rating=4,
    feedback_text="The results were relevant to my query about Project Echoes.",
    user_id="test_user"
)

print("Feedback submitted successfully:")
pprint(feedback)
"""

# Cell 7: Check for related topics
"""
related_topics = rag.get_related_topics("knowledge management")
print("Related topics for 'knowledge management':")
for topic, score in related_topics:
    print(f"- {topic} (relevance: {score:.3f})")
"""

# Cell 8: Test with custom configuration
"""
# Example of initializing with custom configuration
custom_config = {
    'chunk_size': 512,
    'chunk_overlap': 50,
    'embedding_model_name': 'sentence-transformers/all-mpnet-base-v2',
    'enable_recency_bias': True,
    'enable_context_fusion': True
}

custom_rag = EchoesRAG(config=custom_config)
print("Custom RAG instance created with configuration:")
pprint(custom_config)
"""
