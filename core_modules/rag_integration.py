# core/rag_integration.py
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Union
import re
from tqdm import tqdm

from .rag_orbit import RAGOrbit, RAGConfig
from .memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class EchoesRAG:
    """Enhanced RAG system with memory management and file processing."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the RAG system with optional configuration."""
        self.memory_manager = MemoryManager()
        self.config = self._load_config(config or {})
        self.rag = RAGOrbit(self.config)
        self.chunk_size = getattr(self.config, "chunk_size", 1000)
        self.chunk_overlap = getattr(self.config, "chunk_overlap", 200)

    def _load_config(self, config: Dict[str, Any]) -> RAGConfig:
        """Load and validate configuration."""
        rag_config = RAGConfig(
            embedding_model_name=config.get("embedding_model_name", "sentence-transformers/all-mpnet-base-v2"),
            chunk_size=config.get("chunk_size", 1000),
            chunk_overlap=config.get("chunk_overlap", 200),
            top_k=config.get("top_k", 3),
            asset_dirs=[Path(p) for p in config.get("asset_dirs", ["memory/", "assets/"])],
            vector_db_path=Path(config.get("vector_db_path", "vector_index/")),
            log_dir=Path(config.get("log_dir", "logs/rag")),
            memory_dir=Path(config.get("memory_dir", "memory/")),
            cache_dir=Path(config.get("cache_dir", ".cache/")),
            enable_recency_bias=config.get("enable_recency_bias", True),
            enable_context_fusion=config.get("enable_context_fusion", True),
            enable_semantic_threading=config.get("enable_semantic_threading", True),
        )
        return rag_config

    def _chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap, preserving paragraph and sentence boundaries.

        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk (in characters)
            overlap: Number of characters to overlap between chunks

        Returns:
            List of chunk dictionaries with text and position info
        """
        if not text or not text.strip():
            return []

        # Set default chunk size and overlap if not provided
        chunk_size = chunk_size or self.chunk_size
        overlap = min(overlap or self.chunk_overlap, chunk_size // 2)

        logger.info(f"Chunking text: {len(text)} characters, chunk_size={chunk_size}, overlap={overlap}")

        # First, split by paragraphs (double newlines)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If paragraph is too long, split it into sentences
            if len(para) > chunk_size * 1.5:
                # Split into sentences
                sentences = re.split(r"(?<=[.!?])\s+", para)
                for sentence in sentences:
                    if not sentence.strip():
                        continue

                    # If adding this sentence would exceed chunk size, finalize current chunk
                    if current_chunk and current_length + len(sentence) > chunk_size:
                        chunk_text = " ".join(current_chunk)
                        chunks.append(chunk_text)

                        # Start new chunk with overlap from the end of current chunk
                        overlap_text = " ".join(sentence.split()[:10])  # First 10 words as overlap
                        current_chunk = [overlap_text] if overlap_text else []
                        current_length = len(overlap_text)

                    current_chunk.append(sentence)
                    current_length += len(sentence) + 1  # +1 for space
            else:
                # If paragraph fits in current chunk, add it
                if current_chunk and current_length + len(para) > chunk_size:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_length = 0

                current_chunk.append(para)
                current_length += len(para) + 2  # +2 for newlines

        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        # Ensure no chunk is too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split large chunks by character count with word boundaries
                words = chunk.split()
                current_chunk = []
                current_length = 0

                for word in words:
                    if current_chunk and current_length + len(word) + 1 > chunk_size:
                        final_chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_length = 0

                    current_chunk.append(word)
                    current_length += len(word) + 1  # +1 for space

                if current_chunk:
                    final_chunks.append(" ".join(current_chunk))

        logger.info(f"Split text into {len(final_chunks)} chunks")
        return [
            {"text": chunk, "position": i, "total_chunks": len(final_chunks), "is_chunk": len(final_chunks) > 1}
            for i, chunk in enumerate(final_chunks, 1)
        ]

    def add_document(self, document: Union[str, Path, Dict], metadata: Optional[Dict] = None) -> List[str]:
        """
        Add a document to the RAG system.

        Args:
            document: The document content as string, file path, or dict with 'text' and 'metadata'
            metadata: Optional metadata for the document

        Returns:
            List of document IDs for the chunks
        """
        # Handle file paths
        if isinstance(document, (str, Path)) and Path(document).exists():
            return self._add_file_document(Path(document), metadata or {})

        # Handle dictionary input
        if isinstance(document, dict):
            text = document.get("text", "")
            doc_metadata = {**document.get("metadata", {}), **(metadata or {})}
            return self._add_text_document(text, doc_metadata)

        # Handle direct text input
        return self._add_text_document(str(document), metadata or {})

    def _add_file_document(self, file_path: Path, metadata: Dict[str, Any]) -> List[str]:
        """Add a file document to the RAG system."""
        try:
            # Process the file using memory manager
            file_metadata = self.memory_manager.process_file(file_path)
            if "error" in file_metadata:
                logger.error(f"Failed to process file {file_path}: {file_metadata['error']}")
                raise ValueError(f"Failed to process file: {file_metadata['error']}")

            # Extract content and update metadata
            content = file_metadata.pop("content", "")
            metadata.update(
                {
                    **file_metadata,
                    "source": str(file_path),
                    "file_name": file_path.name,
                    "file_size": file_metadata.get("file_size", file_path.stat().st_size),
                    "file_extension": file_path.suffix.lower(),
                }
            )

            # Add to RAG
            return self._add_text_document(content, metadata)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def _add_text_document(self, text: str, metadata: Dict[str, Any]) -> List[str]:
        """
        Add a text document to the RAG system with chunking.

        Args:
            text: The text content to add
            metadata: Metadata for the document

        Returns:
            List of document IDs for the added chunks
        """
        try:
            logger.info(f"Starting to add text document (size: {len(text)} chars, metadata: {metadata})")

            if not text or not text.strip():
                logger.warning("Skipping empty document")
                return []

            # Generate a unique document ID if not provided
            if "doc_id" not in metadata:
                import hashlib

                doc_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
                metadata["doc_id"] = f"doc_{doc_hash}"

            # Chunk the text
            try:
                chunks = self._chunk_text(text)
                if not chunks:
                    logger.warning("No content to add after chunking")
                    return []
                logger.info(f"Split document into {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error during chunking: {str(e)}", exc_info=True)
                raise ValueError(f"Failed to chunk document: {str(e)}")

            # Prepare documents for RAG
            docs_to_add = []
            total_chunks = len(chunks)

            for i, chunk_info in enumerate(chunks, 1):
                try:
                    # Get chunk text and position
                    chunk_text = chunk_info.get("text", "") if isinstance(chunk_info, dict) else str(chunk_info)
                    chunk_pos = chunk_info.get("position", i) if isinstance(chunk_info, dict) else i

                    if not chunk_text or not chunk_text.strip():
                        logger.warning(f"Skipping empty chunk {i}/{total_chunks}")
                        continue

                    # Create chunk metadata
                    chunk_meta = {
                        **metadata,  # Start with original metadata
                        "chunk_id": f"{metadata['doc_id']}_chunk{chunk_pos:03d}",
                        "chunk_index": chunk_pos,
                        "total_chunks": total_chunks,
                        "is_chunk": total_chunks > 1,
                        "source": metadata.get("source", "unknown"),
                        "doc_id": metadata["doc_id"],
                    }

                    # Add to documents to add
                    docs_to_add.append({"text": chunk_text, "metadata": chunk_meta})

                except Exception as e:
                    logger.error(f"Error preparing chunk {i}/{total_chunks}: {str(e)}", exc_info=True)
                    continue

            if not docs_to_add:
                logger.warning("No valid chunks to add after processing")
                return []

            # Add chunks to RAG system
            try:
                logger.info(f"Adding {len(docs_to_add)} chunks to RAG system")
                doc_ids = self.rag.add_documents(docs_to_add)
                logger.info(f"Successfully added {len(doc_ids)} chunks to RAG system")
                return doc_ids

            except Exception as e:
                logger.error(f"Failed to add documents to RAG system: {str(e)}", exc_info=True)

                # If we get a duplicate ID error, try to recover by creating a new vector store
                if "duplicate" in str(e).lower():
                    logger.warning("Duplicate ID detected, attempting to create new vector store")
                    try:
                        # Get the current config and update it to ensure a fresh start
                        config = self.rag.config

                        # Force create a new vector store with all documents
                        self.rag = RAGOrbit(
                            config={
                                "vector_db_path": config.vector_db_path,
                                "chunk_size": config.chunk_size,
                                "chunk_overlap": config.chunk_overlap,
                                "top_k": config.top_k,
                                "device": "cpu",  # Default to CPU to avoid CUDA issues
                            },
                            embedding_model=self.rag.embedding_model,
                        )

                        # Try adding documents again to the new store
                        doc_ids = self.rag.add_documents(docs_to_add)
                        logger.info(f"Successfully added {len(doc_ids)} chunks to new vector store")
                        return doc_ids

                    except Exception as e2:
                        logger.error(f"Failed to create new vector store: {str(e2)}", exc_info=True)

                        # As a last resort, try with a simple in-memory store
                        try:
                            logger.warning("Attempting to use simple in-memory store as fallback")
                            from langchain.vectorstores import InMemoryVectorStore

                            # Create a simple in-memory store
                            self.rag.vector_store = InMemoryVectorStore.from_documents(
                                documents=all_chunks, embedding=self.rag.embedding_model
                            )
                            logger.info("Successfully created in-memory vector store")
                            return list(range(len(all_chunks)))

                        except Exception as e3:
                            logger.error(f"Failed to create in-memory store: {str(e3)}", exc_info=True)
                            raise RuntimeError("All recovery attempts failed. Please check logs for details.")

                # If we get here, we couldn't recover from the error
                raise RuntimeError(f"RAG system error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in _add_text_document: {str(e)}", exc_info=True)
            raise

    def add_directory(
        self, dir_path: Union[str, Path], extensions: Optional[List[str]] = None, batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Add all files in a directory to the RAG system.

        Args:
            dir_path: Path to the directory
            extensions: List of file extensions to include (with leading .), or None for all
            batch_size: Number of files to process in each batch

        Returns:
            Dictionary with results including success/failure counts
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise ValueError(f"Not a directory: {dir_path}")

        # Find all matching files
        files = []
        if extensions:
            for ext in extensions:
                files.extend(dir_path.rglob(f"*{ext}"))
                files.extend(dir_path.rglob(f"*{ext.upper()}"))
            # Remove duplicates (case-insensitive)
            files = list({str(f).lower(): f for f in files}.values())
        else:
            files = list(dir_path.rglob("*"))

        # Filter out directories and non-files
        files = [f for f in files if f.is_file()]

        if not files:
            return {"total": 0, "success": 0, "failed": 0, "errors": []}

        # Process files in batches
        results = {"total": len(files), "success": 0, "failed": 0, "errors": []}

        with tqdm(total=len(files), desc="Processing files") as pbar:
            for i in range(0, len(files), batch_size):
                batch = files[i : i + batch_size]
                batch_results = self._process_batch(batch)

                # Update results
                results["success"] += batch_results["success"]
                results["failed"] += batch_results["failed"]
                results["errors"].extend(batch_results["errors"])

                pbar.update(len(batch))
                pbar.set_postfix({"success": results["success"], "failed": results["failed"]})

        return results

    def _process_batch(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process a batch of files."""
        results = {"success": 0, "failed": 0, "errors": []}

        for file_path in file_paths:
            try:
                self.add_document(file_path)
                results["success"] += 1
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["failed"] += 1

        return results

    def search(self, query: str, top_k: int = 5, filter_by_type: Optional[str] = None, **kwargs) -> List[Dict]:
        """
        Search for relevant documents with optional filtering by content type.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_by_type: Optional content type filter ('text', 'image', 'document', etc.)
            **kwargs: Additional search parameters

        Returns:
            List of search results with scores and metadata
        """
        # Apply content type filter if specified
        if filter_by_type:
            if "filters" not in kwargs:
                kwargs["filters"] = {}
            if "metadata" not in kwargs["filters"]:
                kwargs["filters"]["metadata"] = {}
            kwargs["filters"]["metadata"]["type"] = filter_by_type

        try:
            results = self.rag.search(query, top_k=top_k, **kwargs)

            # Process and format results
            formatted_results = []
            for result in results:
                if not isinstance(result, dict):
                    logger.warning(f"Unexpected result type: {type(result)}")
                    continue

                # Extract content, defaulting to empty string if not found
                content = result.get("content", "")

                # Extract metadata, defaulting to empty dict if not found
                metadata = result.get("metadata", {})

                # Extract score, defaulting to 0.0 if not found
                score = float(result.get("score", 0.0))

                # Include any additional fields from the result
                result_data = {
                    "content": content,
                    "score": score,
                    "metadata": metadata,
                }

                # Include any additional fields from the result
                for key, value in result.items():
                    if key not in result_data:
                        result_data[key] = value

                formatted_results.append(result_data)

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []

    def clear_index(self) -> None:
        """Clear the RAG index."""
        self.rag.clear_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        stats = self.rag.get_document_count()
        return {
            "document_count": stats.get("total_documents", 0),
            "unique_sources": stats.get("unique_sources", 0),
            "last_updated": stats.get("last_updated"),
            "vector_store_type": stats.get("vector_store_type", "unknown"),
            "embedding_model": stats.get("embedding_model", "unknown"),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "sources_sample": stats.get("sources_sample"),
        }
