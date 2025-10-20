"""
RAG Orbit - Unified Retrieval-Augmented Generation System

This module provides a comprehensive RAG (Retrieval-Augmented Generation) system
that integrates with the existing Echoes platform. It handles document ingestion,
vector storage, semantic search, and context management.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, TypeVar, Set
from datetime import datetime
from dataclasses import dataclass, field
import hashlib

# Ensure TypedDict is available
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

# Type variable for document type
T = TypeVar("T")

# Conditional import for LangchainDocument
try:
    from langchain.docstore.document import Document as LangchainDocument
except ImportError:
    # Fallback for when LangchainDocument is not available
    class LangchainDocument:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}
            # Add a unique ID for each document
            # Try to use document_id from metadata if available, otherwise generate a new one
            self.id = self.metadata.get("chunk_id", str(id(self)))
            # Ensure the ID is also in metadata for consistency
            self.metadata["chunk_id"] = self.id


# Define the type alias for document lists
DocumentList = List[LangchainDocument]


def check_dependencies():
    """Check if all required dependencies are installed and importable."""
    missing = []

    try:
        import sentence_transformers
    except ImportError:
        missing.append("sentence-transformers")

    try:
        import faiss
    except ImportError:
        missing.append("faiss-cpu")

    try:
        import langchain
    except ImportError:
        missing.append("langchain")

    try:
        import torch
    except ImportError:
        missing.append("torch")

    return missing


# Check dependencies on module import
missing_deps = check_dependencies()
RAG_DEPENDENCIES_AVAILABLE = len(missing_deps) == 0

# Now try to import everything if available
if RAG_DEPENDENCIES_AVAILABLE:
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    import torch

    RAG_DEPENDENCIES_AVAILABLE = True
else:
    RAG_DEPENDENCIES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Type definitions
class SearchResult(TypedDict):
    """Structure for search results."""

    content: str
    metadata: Dict[str, Any]
    score: float


@dataclass
class RAGConfig:
    """Configuration for the RAG system with enhanced features."""

    # Model and chunking
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_type: str = "huggingface"  # 'ollama' or 'huggingface'
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 3

    # Directories
    asset_dirs: List[Path] = field(default_factory=lambda: [Path("memory/"), Path("assets/")])
    vector_db_path: Path = Path("vector_index/")
    log_dir: Path = Path("logs/")
    memory_dir: Path = Path("memory/")
    cache_dir: Path = Path(".cache/")

    # Memory dynamics
    enable_recency_bias: bool = True
    recency_decay_days: int = 30
    min_relevance_score: float = 0.5

    # Context fusion
    enable_context_fusion: bool = True
    max_context_tokens: int = 2000

    # Semantic threading
    enable_semantic_threading: bool = True
    default_topics: List[str] = field(default_factory=lambda: ["architecture", "philosophy", "caraxes", "temporal"])

    # Device and performance
    device: str = None
    batch_size: int = 32

    def __post_init__(self):
        # Set device
        if self.device is None:
            try:
                import torch

                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"

        # Ensure directories exist
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Convert string paths to Path objects if needed
        if not isinstance(self.asset_dirs, list):
            self.asset_dirs = [Path(d) if isinstance(d, str) else d for d in self.asset_dirs]

        # Ensure all asset directories exist
        for asset_dir in self.asset_dirs:
            asset_dir = Path(asset_dir)
            asset_dir.mkdir(parents=True, exist_ok=True)

        # Convert paths to absolute
        self.memory_dir = Path(self.memory_dir).absolute()
        self.vector_db_path = Path(self.vector_db_path).absolute()
        self.cache_dir = Path(self.cache_dir).absolute()

        # Create directories if they don't exist
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


class RAGOrbit:
    """
    Enhanced RAG system for Echoes platform with advanced features:
    - Multi-source document ingestion
    - Recency-biased retrieval
    - Context fusion
    - Semantic threading
    - Feedback loop integration
    """

    def __init__(self, config: Optional[Union[Dict, RAGConfig]] = None):
        """
        Initialize the RAG system with optional configuration.

        Args:
            config: Either a RAGConfig instance or a dictionary of config overrides.
        """
        if not RAG_DEPENDENCIES_AVAILABLE:
            missing = check_dependencies()
            raise ImportError(
                "Required RAG dependencies not found. Please install missing packages: "
                f"pip install {' '.join(missing)}\n"
                "Full installation command:\n"
                "pip install sentence-transformers faiss-cpu langchain tqdm torch"
            )

        # Initialize configuration
        if isinstance(config, dict):
            self.config = RAGConfig(**config)
        else:
            self.config = config if config is not None else RAGConfig()

        # Core components
        self.embedding_model = None
        self.vector_store = None
        self.tokenizer = None

        # State tracking
        self.document_count = 0
        self.last_updated = None
        self.topic_index = {topic: set() for topic in self.config.default_topics}

        # Feedback loop
        self.feedback_log = self.config.log_dir / "rag_feedback.jsonl"

        # Initialize components
        self._initialize_components()

        # Load existing vector store if available
        self._load_vector_store()

    def _load_vector_store(self) -> None:
        """Load existing vector store if available."""
        vector_store_path = self.config.vector_db_path / "faiss_index"
        if vector_store_path.exists():
            try:
                self.vector_store = FAISS.load_local(
                    str(vector_store_path), self.embedding_model, allow_dangerous_deserialization=True
                )
                self.document_count = len(self.vector_store.docstore._dict)
                logger.info(f"Loaded vector store with {self.document_count} documents")
            except Exception as e:
                logger.warning(f"Failed to load vector store: {e}. Creating new one.")
                self.vector_store = None

    def _save_vector_store(self) -> None:
        """Save the current vector store to disk."""
        if self.vector_store is not None:
            vector_store_path = self.config.vector_db_path / "faiss_index"
            self.vector_store.save_local(str(vector_store_path))
            logger.info(f"Saved vector store with {self.document_count} documents")

    def _initialize_components(self):
        """Initialize the embedding model and tokenizer."""
        logger.info(f"Initializing RAG system with device: {self.config.device}")

        # Set device
        if self.config.device is None:
            self.config.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initialize embedding model
        try:
            if self.config.embedding_type.lower() == "ollama":
                from .ollama_embeddings import OllamaWithFallback

                self.embedding_model = OllamaWithFallback(
                    model_name=self.config.embedding_model_name,
                    fallback_model="sentence-transformers/all-mpnet-base-v2",
                )
                logger.info(f"Using Ollama embeddings with model: {self.config.embedding_model_name}")
            else:  # Default to HuggingFace
                self.embedding_model = HuggingFaceEmbeddings(
                    model_name=self.config.embedding_model_name,
                    model_kwargs={"device": self.config.device},
                    cache_folder=str(self.config.cache_dir),
                )
                logger.info(f"Using HuggingFace embeddings with model: {self.config.embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise

        # Initialize tokenizer for context fusion
        try:
            from transformers import AutoTokenizer

            # For Ollama models, use a reasonable default tokenizer
            if self.config.embedding_type.lower() == "ollama":
                tokenizer_name = "sentence-transformers/all-mpnet-base-v2"
            else:
                tokenizer_name = self.config.embedding_model_name

            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, cache_dir=str(self.config.cache_dir))
        except Exception as e:
            logger.warning(f"Failed to initialize tokenizer, using simple token counting: {e}")
            self.tokenizer = None

    def _chunk_document(self, text: str, metadata: Dict[str, Any]) -> List[LangchainDocument]:
        """
        Split a document into chunks with metadata.

        Args:
            text: The text to chunk
            metadata: Metadata to associate with each chunk

        Returns:
            List of LangchainDocument objects with unique chunk IDs
        """
        # Ensure we have a document ID
        if "doc_id" not in metadata:
            import hashlib

            doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            metadata["doc_id"] = f"doc_{doc_hash[:16]}"

        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=lambda x: (
                len(self.tokenizer.encode(x, add_special_tokens=False)) if self.tokenizer else len(x.split())
            ),
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        # Split text into chunks
        chunks = text_splitter.split_text(text)
        if not chunks:
            return []

        # Create document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks, 1):
            # Create a copy of metadata for this chunk
            chunk_metadata = metadata.copy()

            # Generate a unique chunk ID using content and metadata
            chunk_id = self._generate_unique_id(
                content=chunk,
                metadata={"doc_id": metadata["doc_id"], "chunk_index": i, "source": metadata.get("source", "unknown")},
                index=i,
            )

            # Add chunk-specific metadata
            chunk_metadata.update(
                {
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": metadata.get("source", "unknown"),
                    "is_chunk": len(chunks) > 1,
                }
            )

            # Create document with unique ID
            doc = LangchainDocument(page_content=chunk, metadata=chunk_metadata)
            documents.append(doc)

        return documents

    def _extract_topics(self, text: str, metadata: Dict[str, Any]) -> Set[str]:
        """Extract relevant topics from text and metadata."""
        topics = set()

        # Add topics from metadata
        if "topics" in metadata:
            if isinstance(metadata["topics"], str):
                topics.update(t.lower().strip() for t in metadata["topics"].split(","))
            elif isinstance(metadata["topics"], (list, set, tuple)):
                topics.update(t.lower().strip() for t in metadata["topics"])

        # Add default topics that appear in the text
        text_lower = text.lower()
        for topic in self.config.default_topics:
            if topic.lower() in text_lower:
                topics.add(topic.lower())

        return topics

    def _apply_recency_bias(self, results: List[Dict]) -> List[Dict]:
        """Apply recency bias to search results."""
        if not self.config.enable_recency_bias:
            return results

        now = datetime.utcnow()

        for result in results:
            metadata = result["metadata"]
            if "created_at" in metadata:
                try:
                    # Parse creation time
                    created_at = datetime.fromisoformat(metadata["created_at"].replace("Z", "+00:00"))
                    # Calculate recency score (0-1, 1 being most recent)
                    days_old = (now - created_at).days
                    recency_score = max(0, 1 - (days_old / self.config.recency_decay_days))
                    # Apply recency boost to score
                    result["score"] *= 1 + recency_score * 0.5  # Up to 50% boost
                except (ValueError, TypeError) as e:
                    logger.debug(f"Could not parse creation time: {e}")

        # Re-sort results by updated scores
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def _fuse_context(self, results: List[Dict]) -> str:
        """Fuse multiple retrieved contexts into a coherent summary."""
        if not self.config.enable_context_fusion or not results:
            return "\n\n".join(r["page_content"] for r in results)

        # Simple concatenation if no tokenizer available
        if self.tokenizer is None:
            return "\n\n".join(r["page_content"] for r in results)

        # Sort by score and limit by token count
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)

        fused_context = []
        total_tokens = 0

        for result in sorted_results:
            content = result["page_content"]
            tokens = self.tokenizer.encode(content, add_special_tokens=False)

            if total_tokens + len(tokens) > self.config.max_context_tokens:
                break

            fused_context.append(content)
            total_tokens += len(tokens)

        return "\n\n".join(
            f"[Source: {r['metadata'].get('source', 'unknown')}]\n{r['page_content']}"
            for r in sorted_results[: len(fused_context)]
        )

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of dictionaries with 'text' and 'metadata' keys

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        try:
            # Process documents into chunks
            all_chunks = []
            for doc in documents:
                if not isinstance(doc, dict) or "text" not in doc:
                    continue

                text = doc["text"]
                metadata = doc.get("metadata", {})

                # Ensure metadata has required fields
                if "source" not in metadata:
                    metadata["source"] = "unknown"

                # Generate unique document ID if not provided
                if "doc_id" not in metadata:
                    import hashlib

                    doc_hash = hashlib.md5(text.encode()).hexdigest()
                    metadata["doc_id"] = f"doc_{doc_hash}"

                # Split document into chunks
                chunks = self._chunk_document(text, metadata)

                # Add unique chunk IDs
                for i, chunk in enumerate(chunks):
                    if not hasattr(chunk, "metadata"):
                        chunk.metadata = {}
                    chunk.metadata["chunk_id"] = f"{metadata['doc_id']}_chunk{i}"
                    all_chunks.append(chunk)

            if not all_chunks:
                return 0

            # Add to vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(documents=all_chunks, embedding=self.embedding_model)
            else:
                self.vector_store.add_documents(all_chunks)

            # Update document count and save
            self.document_count += len(all_chunks)
            self.last_updated = datetime.utcnow()
            self._save_vector_store()

            logger.info(f"Added {len(all_chunks)} chunks to vector store. Total: {self.document_count}")
            return len(all_chunks)

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        topics: Optional[List[str]] = None,
        min_score: Optional[float] = None,
    ) -> List[Dict]:
        """
        Search the vector store for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return (defaults to config.top_k)
            topics: Optional list of topics to filter by
            min_score: Minimum relevance score (0-1)

        Returns:
            List of search results with scores and metadata
        """
        if self.vector_store is None:
            return []

        top_k = top_k or self.config.top_k
        min_score = min_score or self.config.min_relevance_score

        try:
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(
                query, k=top_k * 2  # Get extra results for filtering
            )

            # Convert to result format
            search_results = []
            for doc, score in results:
                # Skip if below minimum score
                if score < min_score:
                    continue

                # Filter by topics if specified
                if topics:
                    doc_topics = set(doc.metadata.get("topics", []))
                    if not any(topic.lower() in doc_topics for topic in topics):
                        continue

                search_results.append(
                    {"content": doc.page_content, "metadata": dict(doc.metadata), "score": float(score)}
                )

            # Apply recency bias and other post-processing
            search_results = self._apply_recency_bias(search_results)

            # Return top-k results
            return search_results[:top_k]

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def get_context(self, query: str, top_k: Optional[int] = None, topics: Optional[List[str]] = None) -> str:
        """
        Get context for a query by retrieving and fusing relevant documents.

        Args:
            query: The query to get context for
            top_k: Number of documents to retrieve
            topics: Optional list of topics to filter by

        Returns:
            Fused context string
        """
        results = self.search(query, top_k=top_k, topics=topics)
        return self._fuse_context(results)

    def add_feedback(
        self,
        query: str,
        relevant_doc_ids: List[str],
        irrelevant_doc_ids: List[str] = None,
        feedback_score: Optional[float] = None,
    ) -> None:
        """
        Add feedback about search results to improve future retrievals.

        Args:
            query: The original search query
            relevant_doc_ids: List of document IDs that were relevant
            irrelevant_doc_ids: List of document IDs that were not relevant
            feedback_score: Optional overall relevance score (0-1)
        """
        feedback = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "relevant": relevant_doc_ids or [],
            "irrelevant": irrelevant_doc_ids or [],
            "score": feedback_score,
        }

        # Append to feedback log
        with open(self.feedback_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback) + "\n")

        logger.info(f"Added feedback for query: {query[:50]}...")

    def get_related_topics(self, topic: str, top_n: int = 5) -> List[Dict]:
        """
        Get topics related to the given topic based on co-occurrence.

        Args:
            topic: The topic to find related topics for
            top_n: Number of related topics to return

        Returns:
            List of related topics with scores
        """
        topic = topic.lower()
        co_occurrence = {}

        if not self.vector_store:
            return []

        # Get all documents that mention the topic
        results = self.search(topic, top_k=50)

        # Count co-occurring topics
        for result in results:
            doc_topics = result["metadata"].get("topics", [])
            for doc_topic in doc_topics:
                if doc_topic.lower() != topic:
                    co_occurrence[doc_topic] = co_occurrence.get(doc_topic, 0) + result["score"]

        # Sort by co-occurrence score
        sorted_topics = sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)

        return [{"topic": t, "score": s} for t, s in sorted_topics[:top_n]]

    def _generate_unique_id(self, content: str, metadata: Dict[str, Any], index: int = 0) -> str:
        """
        Generate a unique ID for a document chunk.

        Args:
            content: The text content of the chunk
            metadata: Metadata associated with the chunk
            index: Chunk index (for multi-chunk documents)

        Returns:
            A unique string ID
        """
        import hashlib
        import json

        # Create a unique string based on content, metadata, and index
        content_preview = content[:1000].encode("utf-8")
        metadata_str = json.dumps(metadata, sort_keys=True).encode("utf-8")

        # Create a hash that combines content, metadata, and index
        hash_obj = hashlib.sha256()
        hash_obj.update(content_preview)
        hash_obj.update(metadata_str)
        hash_obj.update(str(index).encode("utf-8"))

        # Include source and index in the ID for better debugging
        source = metadata.get("source", "unknown")
        source_hash = hashlib.md5(source.encode("utf-8")).hexdigest()[:8]

        return f"chunk_{source_hash}_{index:03d}_{hash_obj.hexdigest()[:16]}"

    def _prepare_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare documents for addition to the vector store."""
        prepared_docs = []

        for doc in documents:
            text = doc.get("text", "").strip()
            if not text:
                continue

            metadata = doc.get("metadata", {}).copy()

            # Generate a document ID if not provided
            if "doc_id" not in metadata:
                metadata["doc_id"] = self._generate_unique_id(text, metadata)

            # Add source information if available
            if "source" not in metadata and "file_path" in metadata:
                metadata["source"] = str(metadata["file_path"])

            # Add timestamp if not present
            if "timestamp" not in metadata:
                from datetime import datetime

                metadata["timestamp"] = datetime.utcnow().isoformat()

            prepared_docs.append({"text": text, "metadata": metadata})

        return prepared_docs

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store with proper ID handling.

        Args:
            documents: List of dictionaries containing 'text' and 'metadata' keys.

        Returns:
            List of document IDs for the added documents.
        """
        if not documents:
            logger.warning("No documents to add")
            return []

        # Prepare documents with proper metadata
        prepared_docs = self._prepare_documents(documents)
        if not prepared_docs:
            logger.warning("No valid documents to add after preparation")
            return []

        # Process documents in batches to avoid memory issues
        batch_size = 10
        all_doc_ids = []

        for i in range(0, len(prepared_docs), batch_size):
            batch = prepared_docs[i : i + batch_size]
            batch_chunks = []

            for doc in batch:
                # Generate chunks for each document
                chunks = self._chunk_document(doc["text"], doc["metadata"])

                # Add chunk-specific metadata
                for chunk_idx, chunk in enumerate(chunks):
                    if not hasattr(chunk, "metadata"):
                        chunk.metadata = {}

                    # Ensure we have a unique ID for each chunk
                    chunk_metadata = {**doc["metadata"], "chunk_index": chunk_idx}
                    chunk_id = self._generate_unique_id(chunk.page_content, chunk_metadata, len(batch_chunks))

                    # Update chunk metadata
                    chunk.metadata.update(
                        {
                            "chunk_id": chunk_id,
                            "chunk_index": chunk_idx,
                            "total_chunks": len(chunks),
                            "doc_id": doc["metadata"]["doc_id"],
                            "source": doc["metadata"].get("source", "unknown"),
                            "is_chunk": len(chunks) > 1,
                        }
                    )

                    batch_chunks.append(chunk)

            if not batch_chunks:
                logger.warning(f"No chunks generated for batch starting at index {i}")
                continue

            try:
                # Add chunks to vector store
                if self.vector_store is None:
                    self.vector_store = FAISS.from_documents(batch_chunks, self.embedding_model)
                    logger.info(f"Created new vector store with {len(batch_chunks)} chunks")
                else:
                    # Check for duplicate IDs before adding
                    existing_ids = set()
                    if hasattr(self.vector_store, "docstore") and hasattr(self.vector_store.docstore, "_dict"):
                        existing_ids = set(self.vector_store.docstore._dict.keys())

                    # Filter out chunks that already exist
                    new_chunks = [chunk for chunk in batch_chunks if chunk.metadata["chunk_id"] not in existing_ids]

                    if new_chunks:
                        self.vector_store.add_documents(new_chunks)
                        logger.info(f"Added {len(new_chunks)} new chunks to vector store")
                    else:
                        logger.info("All chunks already exist in vector store")

                # Update document count and save
                self.document_count += len(batch_chunks)
                self.last_updated = datetime.utcnow()
                self._save_vector_store()

                # Add document IDs to return list
                all_doc_ids.extend([chunk.metadata["chunk_id"] for chunk in batch_chunks])

            except Exception as e:
                logger.error(f"Error adding batch {i//batch_size + 1}: {str(e)}", exc_info=True)
                # Try to continue with next batch
                continue

        return all_doc_ids

    def get_document_count(self) -> Dict[str, Any]:
        """
        Get statistics about the documents in the vector store.

        Returns:
            Dict containing document statistics including:
            - total_documents: Total number of document chunks
            - unique_sources: Number of unique document sources
            - last_updated: Timestamp of last update
            - vector_store_type: Type of vector store being used
            - embedding_model: Name of the embedding model
        """
        if self.vector_store is None:
            return {
                "total_documents": 0,
                "unique_sources": 0,
                "last_updated": None,
                "vector_store_type": "None",
                "embedding_model": self.embedding_model_name if hasattr(self, "embedding_model_name") else "unknown",
            }

        # Try to get unique sources if we can access the docstore
        unique_sources = set()
        total_chunks = 0

        if hasattr(self.vector_store, "docstore") and hasattr(self.vector_store.docstore, "_dict"):
            try:
                for doc in self.vector_store.docstore._dict.values():
                    if hasattr(doc, "metadata") and isinstance(doc.metadata, dict):
                        if "source" in doc.metadata:
                            unique_sources.add(doc.metadata["source"])
                    total_chunks += 1
            except Exception as e:
                logger.warning(f"Could not calculate unique sources: {str(e)}")
                total_chunks = self.document_count
        else:
            total_chunks = self.document_count

        return {
            "total_documents": total_chunks,
            "unique_sources": len(unique_sources),
            "last_updated": (
                self.last_updated.isoformat() if hasattr(self, "last_updated") and self.last_updated else None
            ),
            "vector_store_type": type(self.vector_store).__name__,
            "embedding_model": self.embedding_model_name if hasattr(self, "embedding_model_name") else "unknown",
            "sources_sample": list(unique_sources)[:5] if unique_sources else None,
        }

    def search(self, query: str, top_k: Optional[int] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Search the vector store for relevant documents.

        Args:
            query: Search query
            top_k: Number of results to return (defaults to config.top_k)
            **kwargs: Additional arguments to pass to the search

        Returns:
            List of search results with content, metadata, and scores
        """
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            return []

        if self.vector_store is None:
            logger.warning("Vector store not initialized. No documents have been added yet.")
            return []

        try:
            top_k = min(top_k or self.config.top_k, 20)  # Limit to 20 results max

            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(query, k=top_k, **kwargs)

            # Format results
            formatted_results = []
            for doc, score in results:
                if not hasattr(doc, "page_content") or not hasattr(doc, "metadata"):
                    logger.warning(f"Skipping malformed document in results: {doc}")
                    continue

                # Ensure metadata is a dictionary
                metadata = getattr(doc, "metadata", {})
                if not isinstance(metadata, dict):
                    metadata = {}

                # Ensure we have required fields
                result = {
                    "content": str(getattr(doc, "page_content", "")),
                    "metadata": metadata,
                    "score": float(score) if score is not None else 0.0,
                    "id": metadata.get("chunk_id", metadata.get("doc_id", str(id(doc)))),
                    "source": metadata.get("source", "unknown"),
                }

                # Add any additional metadata fields that might be useful
                for field in ["title", "chunk_index", "total_chunks"]:
                    if field in metadata and field not in result:
                        result[field] = metadata[field]

                formatted_results.append(result)

            logger.info(f"Found {len(formatted_results)} results for query: '{query}'")
            return formatted_results

        except Exception as e:
            logger.error(f"Error during search: {str(e)}", exc_info=True)
            return []

    def load_memory_assets(self, update_only: bool = False) -> int:
        """
        Load and index memory assets from all configured asset directories.

        Args:
            update_only: If True, only process files modified since last update

        Returns:
            int: Number of documents processed
        """
        documents = []
        processed_files = set()

        # Get last update time if we're only updating
        last_update = self.last_updated.timestamp() if update_only and self.last_updated else 0

        # Process each asset directory
        for asset_dir in self.config.asset_dirs:
            if not asset_dir.exists():
                logger.warning(f"Asset directory not found: {asset_dir}")
                continue

            # Process different file types
            text_extensions = {".txt", ".md", ".json", ".yaml", ".yml", ".log", ".py"}

            # Track processed files to avoid duplicates across directories
            for ext in text_extensions:
                for file_path in asset_dir.rglob(f"*{ext}"):
                    try:
                        # Skip if we've already processed this file
                        if file_path in processed_files:
                            continue

                        # Skip if we're only updating and file hasn't changed
                        mtime = file_path.stat().st_mtime
                        if update_only and mtime <= last_update:
                            continue

                        # Read file content
                        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()

                        # Generate document ID based on path and content hash
                        doc_id = hashlib.md5((str(file_path) + content).encode()).hexdigest()

                        # Extract metadata
                        metadata = {
                            "source": str(file_path.relative_to(asset_dir)),
                            "type": "text",
                            "format": ext.lstrip("."),
                            "last_modified": datetime.fromtimestamp(mtime).isoformat(),
                            "doc_id": doc_id,
                            "version": 1,  # Will be updated if doc exists
                            "access_count": 0,  # Track how often this doc is retrieved
                            "last_accessed": None,  # Track when this doc was last retrieved
                        }

                        # Check if this is an update to an existing document
                        if hasattr(self, "_document_versions"):
                            existing_version = self._document_versions.get(doc_id, 0)
                            if existing_version > 0:
                                metadata["version"] = existing_version + 1

                        # Extract topics for semantic threading
                        topics = self._extract_topics(content, metadata)
                        if topics:
                            metadata["topics"] = topics

                        documents.append({"text": content, "metadata": metadata})

                        processed_files.add(file_path)

                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")

        # Add documents to vector store
        if documents:
            return self.add_documents(documents)
        return 0


# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = RAGOrbit()

    # Load memory assets
    print("Loading memory assets...")
    num_loaded = rag.load_memory_assets()
    print(f"Loaded {num_loaded} document chunks from memory assets")

    # Example search
    if num_loaded > 0:
        query = "What is the main purpose of this project?"
        print(f"\nSearching for: {query}")
        results = rag.search(query)

        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (Score: {result['score']:.4f}) ---")
            print(f"Source: {result['metadata'].get('source', 'Unknown')}")
            print(f"Content: {result['content'][:200]}...\n")
