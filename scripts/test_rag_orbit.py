#!/usr/bin/env python3
"""
Test script for the RAG Orbit system.

This script demonstrates how to use the RAGOrbit class to index and search
through memory assets.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.rag_orbit import RAGOrbit, RAGConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("rag_orbit_test.log")],
)
logger = logging.getLogger(__name__)


def main():
    """Main function to test the RAG system."""
    # Configuration
    config = RAGConfig(
        memory_dir=Path("memory/"),
        vector_db_path=Path("data/vector_store"),
        embedding_model_name="sentence-transformers/all-mpnet-base-v2",
        chunk_size=1000,
        chunk_overlap=200,
        top_k=3,
    )

    try:
        # Initialize RAG system
        logger.info("Initializing RAG system...")
        rag = RAGOrbit(config)

        # Load memory assets
        logger.info("Loading memory assets...")
        num_loaded = rag.load_memory_assets()
        logger.info(f"Loaded {num_loaded} document chunks from memory assets")

        if num_loaded == 0:
            logger.warning(
                "No documents were loaded. Check if the memory directory exists and contains supported files."
            )
            return

        # Interactive search
        logger.info("\nRAG System Ready!")
        logger.info("Enter your search query (or 'exit' to quit):")

        while True:
            try:
                query = input("\nSearch: ").strip()
                if query.lower() in ["exit", "quit", "q"]:
                    break

                if not query:
                    continue

                # Perform search
                results = rag.search(query)

                # Display results
                if not results:
                    print("No results found.")
                    continue

                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n--- Result {i} (Relevance: {result['score']:.4f}) ---")
                    print(f"Source: {result['metadata'].get('source', 'Unknown')}")
                    print(f"Content: {result['content'][:300]}...")

            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break
            except Exception as e:
                logger.error(f"Error during search: {str(e)}", exc_info=True)
                print(f"An error occurred: {str(e)}")

    except Exception as e:
        logger.critical("Fatal error in RAG system", exc_info=True)
        print(f"Fatal error: {str(e)}")
        return 1

    logger.info("Exiting RAG test script")
    return 0


if __name__ == "__main__":
    sys.exit(main())
