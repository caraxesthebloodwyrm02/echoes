# run_rag_demo.py
import argparse
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

from echoes_core.rag_integration import EchoesRAG


def main():
    parser = argparse.ArgumentParser(description="Echoes RAG System Demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add document command
    add_parser = subparsers.add_parser("add", help="Add documents to the RAG system")
    add_parser.add_argument("paths", nargs="+", help="File or directory paths to add")
    add_parser.add_argument(
        "--extensions", nargs="*", help="File extensions to include (with leading .)"
    )
    add_parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of files to process in each batch",
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search the RAG system")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--top-k", type=int, default=5, help="Number of results to return"
    )
    search_parser.add_argument(
        "--filter", help="Filter by content type (text, image, document, etc.)"
    )

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear the RAG index")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get RAG system statistics")

    args = parser.parse_args()

    # Initialize RAG system
    rag = EchoesRAG()

    if args.command == "add":
        for path_str in args.paths:
            path = Path(path_str)
            if not path.exists():
                logger.error(f"Path does not exist: {path}")
                continue

            if path.is_file():
                try:
                    logger.info(f"Adding file: {path}")
                    doc_ids = rag.add_document(path)
                    logger.info(f"Added {len(doc_ids)} chunks from {path}")
                except Exception as e:
                    logger.error(f"Error adding {path}: {e}")
            else:
                logger.info(f"Processing directory: {path}")
                result = rag.add_directory(
                    path, extensions=args.extensions, batch_size=args.batch_size
                )
                logger.info(
                    f"Processed {result['total']} files: {result['success']} succeeded, {result['failed']} failed"
                )
                if result["errors"]:
                    logger.error("Errors encountered:")
                    for error in result["errors"]:
                        logger.error(f"  {error}")

    elif args.command == "search":
        results = rag.search(args.query, top_k=args.top_k, filter_by_type=args.filter)
        print(f"\nSearch results for: {args.query}\n" + "=" * 50)
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Score: {result['score']:.4f})")
            print(f"Source: {result['metadata'].get('source', 'N/A')}")
            if "chunk" in result["metadata"]:
                print(f"Chunk: {result['metadata']['chunk']}")
            print(
                "\n"
                + result["content"][:500]
                + ("..." if len(result["content"]) > 500 else "")
            )
            print("-" * 50)

    elif args.command == "clear":
        rag.clear_index()
        logger.info("RAG index cleared")

    elif args.command == "stats":
        stats = rag.get_stats()
        print("\nRAG System Statistics")
        print("=" * 50)
        print(f"Total Documents: {stats['document_count']}")
        print(f"Unique Sources: {stats['unique_sources']}")
        print(f"Last Updated: {stats['last_updated'] or 'Never'}")
        print(f"Vector Store: {stats['vector_store_type']}")
        print(f"Embedding Model: {stats['embedding_model']}")
        print(f"Chunk Size: {stats['chunk_size']}")
        print(f"Chunk Overlap: {stats['chunk_overlap']}")

        if stats.get("sources_sample"):
            print("\nSample Sources:")
            for source in stats["sources_sample"]:
                print(f"  - {source}")


if __name__ == "__main__":
    main()
