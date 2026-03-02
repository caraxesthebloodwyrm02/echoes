#!/usr/bin/env python3
"""
Direct RAG System - OpenAI API Only (No Middlemen)

A pure RAG implementation using only OpenAI API calls for:
- Document embedding generation
- Query embedding generation
- Response generation with retrieved context

No external libraries, no middleware, just direct OpenAI API calls.
"""

import hashlib
import os
from datetime import datetime
from typing import Any

import numpy as np
from openai import OpenAI


class DirectRAGSystem:
    """
    Pure RAG system using only OpenAI API calls.

    Features:
    - Direct OpenAI embeddings for documents and queries
    - In-memory vector storage with numpy
    - Cosine similarity search
    - Context-augmented response generation
    """

    def __init__(self, api_key: str | None = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = OpenAI(api_key=self.api_key)

        # In-memory storage
        self.documents: list[str] = []
        self.embeddings: list[list[float]] = []
        self.metadata: list[dict[str, Any]] = []

        # Configuration
        self.embedding_model = "text-embedding-3-small"
        self.completion_model = "gpt-4o-mini"
        self.max_tokens = 1000
        self.temperature = 0.7
        self.top_k = 3

        print("✅ Direct RAG System initialized with OpenAI API")

    def add_document(self, text: str, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a document to the RAG system using direct OpenAI API calls.

        Args:
            text: Document text to add
            metadata: Optional metadata

        Returns:
            Document ID
        """
        if not text or not text.strip():
            raise ValueError("Document text cannot be empty")

        # Generate embedding using OpenAI API directly
        embedding = self._generate_embedding(text)

        # Generate document ID
        doc_id = hashlib.md5(f"{text}_{len(self.documents)}".encode()).hexdigest()[:16]

        # Store document and embedding
        self.documents.append(text)
        self.embeddings.append(embedding)
        self.metadata.append(metadata or {})

        print(f"✅ Document added: {doc_id} ({len(text)} chars)")
        return doc_id

    def add_documents(
        self, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> list[str]:
        """Add multiple documents."""
        doc_ids = []
        metadatas = metadatas or [{}] * len(texts)

        for text, metadata in zip(texts, metadatas):
            doc_id = self.add_document(text, metadata)
            doc_ids.append(doc_id)

        return doc_ids

    def search(self, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        """
        Search for relevant documents using direct OpenAI API calls.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents with scores
        """
        if not query or not query.strip():
            return []

        top_k = top_k or self.top_k

        # Generate query embedding using OpenAI API
        query_embedding = self._generate_embedding(query)

        if not self.embeddings:
            return []

        # Calculate cosine similarities using numpy
        similarities = self._calculate_similarities(query_embedding, self.embeddings)

        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append(
                    {
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "score": float(similarities[idx]),
                        "rank": len(results) + 1,
                    }
                )

        print(f"🔍 Search completed: {len(results)} results for query")
        return results

    def generate_response(
        self, query: str, context_docs: list[dict[str, Any]] | None = None
    ) -> str:
        """
        Generate response using retrieved context via direct OpenAI API calls.

        Args:
            query: User query
            context_docs: Optional pre-retrieved context documents

        Returns:
            Generated response
        """
        # Retrieve relevant context if not provided
        if context_docs is None:
            context_docs = self.search(query, top_k=self.top_k)

        # Format context for prompt
        context_text = self._format_context(context_docs)

        # Create augmented prompt
        prompt = f"""You are a knowledgeable AI assistant with access to relevant information.

Context Information:
{context_text}

User Query: {query}

Based on the context provided above, please provide a comprehensive and accurate answer to the user's query. If the context doesn't contain relevant information, say so clearly."""

        # Generate response using OpenAI API directly
        try:
            response = self.client.chat.completions.create(
                model=self.completion_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant with access to retrieved context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            generated_response = response.choices[0].message.content

            print(f"🤖 Response generated: {len(generated_response)} characters")
            return generated_response
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"

    def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding using OpenAI API directly."""
        # Truncate text if too long (OpenAI has token limits)
        truncated_text = text[:8000]  # Conservative limit

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model, input=truncated_text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536  # text-embedding-3-small dimension

    def _calculate_similarities(
        self, query_embedding: list[float], doc_embeddings: list[list[float]]
    ) -> np.ndarray:
        """Calculate cosine similarities between query and documents."""
        query_vec = np.array(query_embedding)
        doc_matrix = np.array(doc_embeddings)

        # Cosine similarity: (A · B) / (||A|| * ||B||)
        dot_products = np.dot(doc_matrix, query_vec)
        query_norm = np.linalg.norm(query_vec)
        doc_norms = np.linalg.norm(doc_matrix, axis=1)

        # Avoid division by zero
        doc_norms = np.where(doc_norms == 0, 1e-8, doc_norms)

        similarities = dot_products / (doc_norms * query_norm)
        return similarities

    def _format_context(self, context_docs: list[dict[str, Any]]) -> str:
        """Format retrieved documents for context."""
        if not context_docs:
            return "No relevant context found."

        formatted_docs = []
        for i, doc in enumerate(context_docs, 1):
            content = doc.get("content", "")[:1000]  # Limit context length
            score = doc.get("score", 0)
            formatted_docs.append(
                f"Document {i} (relevance: {score:.3f}):\n{content}\n"
            )

        return "\n".join(formatted_docs)

    def get_stats(self) -> dict[str, Any]:
        """Get system statistics."""
        return {
            "total_documents": len(self.documents),
            "embedding_model": self.embedding_model,
            "completion_model": self.completion_model,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def clear_documents(self):
        """Clear all documents from the system."""
        self.documents.clear()
        self.embeddings.clear()
        self.metadata.clear()
        print("🧹 All documents cleared from RAG system")


async def create_direct_rag_system(api_key: str | None = None) -> DirectRAGSystem:
    """
    Create a direct RAG system instance.

    Args:
        api_key: OpenAI API key (optional, will use env var if not provided)

    Returns:
        Configured DirectRAGSystem instance
    """
    return DirectRAGSystem(api_key=api_key)


# Example usage and testing
def demo_direct_rag():
    """Demonstrate the direct RAG system."""
    print("🚀 Direct RAG System Demo")
    print("=" * 40)

    # Initialize system
    rag = DirectRAGSystem()

    # Add sample documents
    documents = [
        "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
        "Machine learning is a subset of artificial intelligence that enables systems to automatically learn and improve from experience without being explicitly programmed.",
        "OpenAI is an AI research company that develops artificial general intelligence (AGI) with the goal of benefiting humanity.",
        "Retrieval-Augmented Generation (RAG) combines the strengths of retrieval-based methods and generative models to provide more accurate and context-aware responses.",
    ]

    print("\\n📄 Adding documents...")
    rag.add_documents(documents)

    # Test search
    print("\\n🔍 Testing search...")
    query = "What is Python programming?"
    results = rag.search(query, top_k=2)

    print(f"Query: {query}")
    for result in results:
        print(".3f")

    # Test response generation (synchronous now)
    print("\\n🤖 Testing response generation...")
    response = rag.generate_response(query)
    print(f"Generated response: {response[:200]}...")

    # Show stats
    stats = rag.get_stats()
    print(f"\\n📊 System stats: {stats}")


if __name__ == "__main__":
    # Run demo
    demo_direct_rag()
