"""
Example of RAG Integration with Echoes

This script demonstrates how to use the EchoesRAG class to enhance
generation with retrieved context.
"""

import logging
from pathlib import Path

# Add parent directory to path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.rag_integration import EchoesRAG

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def mock_generation(prompt: str, **kwargs) -> str:
    """Mock generation function for demonstration."""
    print("\n" + "=" * 80)
    print("GENERATION PROMPT:")
    print("-" * 80)
    print(prompt)
    print("=" * 80 + "\n")

    # In a real implementation, this would call your LLM
    return "This is a mock response based on the provided context."


def main():
    """Run the RAG integration example."""
    # Initialize the RAG system
    rag = EchoesRAG()

    # Example documents (in a real application, these would be your knowledge base)
    documents = [
        {
            "text": "Echoes is an advanced AI system that uses vector embeddings and resonance to process information. It can maintain context across multiple interactions.",
            "metadata": {"source": "system_overview.txt", "type": "documentation"},
        },
        {
            "text": "Caraxes is the core reasoning Glimpse in Echoes, responsible for processing and generating responses based on learned patterns and retrieved information.",
            "metadata": {"source": "caraxes_docs.md", "type": "documentation"},
        },
        {
            "text": "The RAG (Retrieval-Augmented Generation) system allows Echoes to retrieve relevant information from a knowledge base before generating responses.",
            "metadata": {"source": "rag_integration.txt", "type": "documentation"},
        },
    ]

    # Add documents to the RAG system
    logger.info("Adding documents to RAG system...")
    rag.add_documents(documents)

    # Example query
    query = "How does Echoes use RAG to improve responses?"

    # Generate a response with context
    logger.info(f"Generating response for query: {query}")
    response = rag.generate_with_context(user_prompt=query, generation_func=mock_generation)

    print("\n" + "=" * 80)
    print("FINAL RESPONSE:")
    print("-" * 80)
    print(response)
    print("=" * 80)


if __name__ == "__main__":
    main()
