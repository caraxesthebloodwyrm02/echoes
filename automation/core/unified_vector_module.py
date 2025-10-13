"""
Batch Compilation Module for Unified Embedding, Indexing, Compression, and Vector Operations

This module provides a unified interface for batch processing of text/data, generating embeddings via
OpenAI endpoints, building searchable indexes, compressing vectors, and performing vector-based operations.
Designed for integration with Symphony workflows (e.g., caching, retrieval, AI assistance).

Features:
- Batch embedding using OpenAI's embedding API.
- Indexing with FAISS for efficient similarity search.
- Compression via quantization or PCA.
- Hybrid search (BM25 + vector).
- Code-aware chunking for semantic splits.
- Quality evaluation metrics.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
import pickle
import ast

import faiss
from rank_bm25 import BM25Okapi
from minicon.config import Config

logger = logging.getLogger(__name__)


class UnifiedVectorModule:
    """
    Unified module for batch compilation: embedding → indexing → compression → vector ops.
    """

    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        compress_dim: int = 128,
        batch_size: int = 32,
        embedding_client: Optional[Any] = None,
    ):
        """
        Initialize with embedding model and dimensions.
        
        Args:
            embedding_model: OpenAI embedding model identifier.
            compress_dim: Compressed dimension for efficiency.
            batch_size: Batch size for embedding requests.
            embedding_client: Optional pre-configured OpenAI client.
        """
        self.embedding_model = embedding_model
        self.compress_dim = compress_dim
        self.batch_size = batch_size
        self.index_dim: Optional[int] = None
        self.compress_dim = compress_dim
        self.index: Optional[faiss.Index] = None
        self.compressed_vectors: Optional[np.ndarray] = None
        self.quantization_params: Optional[Tuple[float, float]] = None  # min_val, max_val for dequantization
        self.metadata: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None
        config = Config.from_env()
        if embedding_client is not None:
            self.embedding_client = embedding_client
        else:
            # Reuse Config-managed OpenAI client
            self.embedding_client = config.openai_client

    def chunk_code_files(self, code_texts: List[str], chunk_size: int = 256) -> List[str]:
        """Chunk code by AST (functions/classes) for semantic granularity."""
        chunks = []
        for code in code_texts:
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        # Extract function/class code
                        start = node.lineno - 1
                        end = getattr(node, 'end_lineno', start + 10)
                        lines = code.splitlines()
                        if start < len(lines) and end <= len(lines):
                            chunk = "\n".join(lines[start:end])
                            if len(chunk) > chunk_size // 2:  # Filter small chunks
                                chunks.append(chunk[:chunk_size])
            except SyntaxError:
                # Fallback: split by lines
                lines = code.splitlines()
                chunks.extend(["\n".join(lines[i:i+chunk_size//10]) for i in range(0, len(lines), chunk_size//20)])
        return chunks

    def batch_embed(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of input texts.
            batch_size: Batch size for processing.
        
        Returns:
            Numpy array of embeddings (shape: len(texts) x embedding_dim).
        """
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        batch_size = batch_size or self.batch_size
        logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}")
        vectors: List[List[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=batch,
            )
            vectors.extend([record.embedding for record in response.data])

        embeddings = np.array(vectors, dtype=np.float32)
        if embeddings.size == 0:
            return embeddings

        if self.index_dim is None:
            self.index_dim = embeddings.shape[1]
        return embeddings

    def build_index(self, vectors: np.ndarray, index_type: str = "IndexFlatIP") -> faiss.Index:
        """
        Build a FAISS index for similarity search.
        
        Args:
            vectors: Embedding vectors.
            index_type: FAISS index type (e.g., 'IndexFlatIP' for inner product).
        
        Returns:
            Trained FAISS index.
        """
        if self.index_dim is None:
            raise ValueError("index_dim is unset. Ensure embeddings are generated before building the index.")

        logger.info(f"Building {index_type} index for {len(vectors)} vectors")
        if index_type == "IndexFlatIP":
            self.index = faiss.IndexFlatIP(self.index_dim)
        elif index_type == "IndexIVFFlat":
            quantizer = faiss.IndexFlatIP(self.index_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.index_dim, 100)  # 100 clusters
            self.index.train(vectors)
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        self.index.add(vectors)
        return self.index

    def compress_vectors(self, vectors: np.ndarray, method: str = "pca") -> np.ndarray:
        """
        Compress vectors to reduce dimensionality.
        
        Args:
            vectors: Original vectors.
            method: Compression method ('pca', 'random_projection', 'quantization').
        
        Returns:
            Compressed vectors.
        """
        logger.info(f"Compressing {len(vectors)} vectors from {self.index_dim} to {self.compress_dim} dims using {method}")
        if method == "pca":
            from sklearn.decomposition import PCA
            pca = PCA(n_components=self.compress_dim)
            self.compressed_vectors = pca.fit_transform(vectors)
        elif method == "random_projection":
            from sklearn.random_projection import GaussianRandomProjection
            rp = GaussianRandomProjection(n_components=self.compress_dim)
            self.compressed_vectors = rp.fit_transform(vectors)
        elif method == "quantization":
            self.compressed_vectors, min_val, max_val = self.quantize_vectors(vectors)
            self.quantization_params = (min_val, max_val)
        else:
            raise ValueError(f"Unsupported compression method: {method}")
        
        return self.compressed_vectors

    def quantize_vectors(self, vectors: np.ndarray, bits: int = 8) -> Tuple[np.ndarray, float, float]:
        """Scalar quantization for compression."""
        min_val, max_val = vectors.min(), vectors.max()
        scale = (2**bits - 1) / (max_val - min_val + 1e-8)
        quantized = np.round((vectors - min_val) * scale).astype(np.uint8)
        return quantized, min_val, max_val

    def unified_batch_process(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None, 
                             index_type: str = "IndexFlatIP", compress: bool = True, compress_method: str = "pca",
                             chunk_code: bool = False) -> Dict[str, Any]:
        """
        Unified pipeline: chunk (optional) → embed → index → compress (optional).
        
        Args:
            texts: List of texts to process.
            metadata: Optional list of metadata dicts for each text.
            index_type: FAISS index type.
            compress: Whether to compress vectors.
            compress_method: Compression method.
            chunk_code: Whether to apply code-aware chunking.
        
        Returns:
            Dict with index, compressed vectors, and metadata.
        """
        logger.info("Starting unified batch processing")
        
        # Optional chunking
        if chunk_code:
            texts = self.chunk_code_files(texts)
            logger.info(f"Chunked into {len(texts)} semantic pieces")
        
        # Step 1: Embed
        embeddings = self.batch_embed(texts)
        
        # Step 2: Index
        self.index = self.build_index(embeddings, index_type)
        
        # Step 3: Compress (optional)
        if compress:
            self.compressed_vectors = self.compress_vectors(embeddings, compress_method)
        
        # Store metadata and setup BM25
        self.metadata = metadata or [{"id": i, "content": text} for i, text in enumerate(texts)]
        tokenized = [m["content"].split() for m in self.metadata]
        self.bm25 = BM25Okapi(tokenized)
        
        return {
            "index": self.index,
            "embeddings": embeddings,
            "compressed": self.compressed_vectors,
            "metadata": self.metadata
        }

    def hybrid_search(self, query: str, top_k: int = 5, keyword_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Hybrid BM25 + vector search."""
        if not self.index or not self.bm25 or not self.metadata:
            raise ValueError("Index and BM25 not initialized. Run unified_batch_process first.")
        
        # BM25 scores
        bm25_scores = self.bm25.get_scores(query.split())
        
        # Vector search
        query_emb = self._embed_text(query)
        vec_scores, vec_indices = self.index.search(np.array([query_emb]), top_k * 2)
        vec_scores = vec_scores[0]
        vec_indices = vec_indices[0]

        # Combine scores
        combined_results = []
        seen_ids = set()
        for score, idx in zip(vec_scores, vec_indices):
            if idx < len(self.metadata) and idx not in seen_ids:
                bm25_score = bm25_scores[int(idx)]
                combined_score = keyword_weight * bm25_score + (1 - keyword_weight) * score
                result = self.metadata[int(idx)].copy()
                result["score"] = float(combined_score)
                combined_results.append(result)
                seen_ids.add(idx)
                if len(combined_results) >= top_k:
                    break
        
        return combined_results

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search on the index.
        
        Args:
            query: Query text.
            top_k: Number of top results.
        
        Returns:
            List of results with scores and metadata.
        """
        if self.index is None:
            raise ValueError("Index not built. Run unified_batch_process first.")
        
        query_emb = self._embed_text(query)
        scores, indices = self.index.search(np.array([query_emb]), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["score"] = float(score)
                results.append(result)
        
        return results

    def evaluate_quality(self, queries: List[str], ground_truth: List[List[int]], top_k: int = 5) -> Dict[str, float]:
        """Evaluate retrieval quality with MRR and NDCG."""
        mrr_scores = []
        ndcg_scores = []
        for query, gt in zip(queries, ground_truth):
            results = self.search(query, top_k=top_k)
            retrieved_ids = [r["id"] for r in results if "id" in r]
            
            # MRR
            mrr = 0
            for rank, rid in enumerate(retrieved_ids, 1):
                if rid in gt:
                    mrr = 1 / rank
                    break
            mrr_scores.append(mrr)
            
            # NDCG (simplified)
            dcg = 0
            for rank, rid in enumerate(retrieved_ids, 1):
                if rid in gt:
                    dcg += 1 / np.log2(rank + 1)
            idcg = sum(1 / np.log2(i + 1) for i in range(1, len(gt) + 1))
            ndcg = dcg / idcg if idcg > 0 else 0
            ndcg_scores.append(ndcg)
        
        return {"MRR": np.mean(mrr_scores), "NDCG": np.mean(ndcg_scores)}

    def save_module(self, path: str):
        """Save the module state."""
        data = {
            "index": faiss.serialize_index(self.index) if self.index else None,
            "compressed": self.compressed_vectors,
            "quantization_params": self.quantization_params,
            "metadata": self.metadata
        }
        with open(path, "wb") as f:
            pickle.dump(data, f)
        logger.info(f"Module saved to {path}")

    def load_module(self, path: str):
        """Load the module state."""
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.index = faiss.deserialize_index(data["index"]) if data["index"] else None
        if self.index is not None:
            self.index_dim = self.index.d
        self.compressed_vectors = data["compressed"]
        self.quantization_params = data.get("quantization_params")
        self.metadata = data["metadata"]
        # Rebuild BM25
        tokenized = [m["content"].split() for m in self.metadata]
        self.bm25 = BM25Okapi(tokenized)
        logger.info(f"Module loaded from {path}")

    def _embed_text(self, text: str) -> np.ndarray:
        response = self.embedding_client.embeddings.create(
            model=self.embedding_model,
            input=[text],
        )
        vector = np.array(response.data[0].embedding, dtype=np.float32)
        if self.index_dim is None:
            self.index_dim = vector.shape[0]
        return vector


# Example Usage
if __name__ == "__main__":
    module = UnifiedVectorModule()
    
    # Sample code texts
    code_texts = [
        "def health_check():\n    return {'status': 'ok'}",
        "class Assistant:\n    def query(self):\n        pass"
    ]
    
    # Unified processing with chunking and quantization
    result = module.unified_batch_process(code_texts, compress=True, compress_method="quantization", chunk_code=True)
    print("Processing complete with optimizations.")
    
    # Hybrid search
    results = module.hybrid_search("check health", top_k=2)
    print("Hybrid search results:", results)
