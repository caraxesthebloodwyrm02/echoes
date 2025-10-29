"""
OpenAI Embeddings Provider for RAG System

Provides OpenAI-based embeddings as an alternative to sentence-transformers.
Follows the OpenAI-first approach as requested.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
import json
import time
import hashlib

logger = logging.getLogger(__name__)


class OpenAIEmbeddings:
    """
    OpenAI embeddings provider compatible with langchain interface.
    Uses OpenAI's embedding models for vector generation.
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        """
        Initialize OpenAI embeddings.
        
        Args:
            model_name: OpenAI embedding model to use
            api_key: OpenAI API key (if not provided, will use environment)
        """
        self.model_name = model_name
        self._client = None
        self._api_key = api_key
        
        # Initialize OpenAI client
        self._init_client()
        
        # Embedding dimensions for different models
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        self.dimension = self._dimensions.get(model_name, 1536)
    
    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            import os
            
            api_key = self._api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
            self._client = OpenAI(api_key=api_key)
            logger.info(f"OpenAI embeddings initialized with model: {self.model_name}")
            
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents using OpenAI.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        
        # Process in batches to avoid rate limits
        batch_size = 100  # OpenAI rate limit is high, but we'll be conservative
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self._client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay to avoid rate limiting
                if i + batch_size < len(texts):
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error embedding batch {i//batch_size}: {str(e)}")
                # Return zero vectors for failed embeddings
                zero_vector = [0.0] * self.dimension
                embeddings.extend([zero_vector] * len(batch))
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text using OpenAI.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self._client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error embedding query: {str(e)}")
            # Return zero vector for failed embedding
            return [0.0] * self.dimension
    
    def __call__(self, text: str) -> List[float]:
        """Make the object callable for compatibility."""
        return self.embed_query(text)


class OpenAIVectorStore:
    """
    Simple vector store using OpenAI embeddings and numpy for similarity search.
    Provides FAISS-like functionality without requiring FAISS installation.
    """
    
    def __init__(self, embedding_function: OpenAIEmbeddings):
        """
        Initialize vector store.
        
        Args:
            embedding_function: OpenAI embeddings instance
        """
        self.embedding_function = embedding_function
        self.documents = []
        self.embeddings = []
        self.metadata = []
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of texts to add
            metadatas: Optional metadata for each text
            
        Returns:
            List of document IDs
        """
        if not texts:
            return []
        
        # Generate embeddings
        new_embeddings = self.embedding_function.embed_documents(texts)
        
        # Generate IDs
        doc_ids = []
        for i, text in enumerate(texts):
            doc_id = hashlib.md5(f"{text}_{time.time()}_{i}".encode()).hexdigest()[:16]
            doc_ids.append(doc_id)
            
            self.documents.append(text)
            self.embeddings.append(new_embeddings[i])
            self.metadata.append(metadatas[i] if metadatas else {})
        
        logger.info(f"Added {len(texts)} documents to vector store")
        return doc_ids
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query: Query text
            k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        if not self.embeddings:
            return []
        
        # Embed query
        query_embedding = self.embedding_function.embed_query(query)
        query_embedding = np.array(query_embedding)
        
        # Calculate similarities
        embeddings_matrix = np.array(self.embeddings)
        
        # Compute cosine similarity using only numpy
        # Cosine similarity = (A · B) / (||A|| * ||B||)
        dot_products = np.dot(embeddings_matrix, query_embedding)
        query_norm = np.linalg.norm(query_embedding)
        doc_norms = np.linalg.norm(embeddings_matrix, axis=1)
        
        # Avoid division by zero
        doc_norms = np.where(doc_norms == 0, 1e-8, doc_norms)
        similarities = dot_products / (doc_norms * query_norm)
        
        # Get top k results
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "content": self.documents[idx],
                "metadata": self.metadata[idx],
                "score": float(similarities[idx])
            })
        
        return results
    
    def save_local(self, folder_path: str):
        """Save the vector store to disk."""
        path = Path(folder_path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save data
        with open(path / "documents.json", "w") as f:
            json.dump(self.documents, f)
        
        with open(path / "metadata.json", "w") as f:
            json.dump(self.metadata, f)
        
        # Save embeddings as numpy array
        np.save(path / "embeddings.npy", np.array(self.embeddings))
        
        # Save config
        config = {
            "model_name": self.embedding_function.model_name,
            "dimension": self.embedding_function.dimension,
            "num_documents": len(self.documents)
        }
        
        with open(path / "config.json", "w") as f:
            json.dump(config, f)
        
        logger.info(f"Vector store saved to {folder_path}")
    
    @classmethod
    def load_local(cls, folder_path: str, embedding_function: OpenAIEmbeddings):
        """Load the vector store from disk."""
        path = Path(folder_path)
        
        if not path.exists():
            raise ValueError(f"Vector store not found at {folder_path}")
        
        # Load data
        with open(path / "documents.json", "r") as f:
            documents = json.load(f)
        
        with open(path / "metadata.json", "r") as f:
            metadata = json.load(f)
        
        # Load embeddings
        embeddings = np.load(path / "embeddings.npy").tolist()
        
        # Create instance
        instance = cls(embedding_function)
        instance.documents = documents
        instance.embeddings = embeddings
        instance.metadata = metadata
        
        logger.info(f"Vector store loaded from {folder_path}")
        return instance


def create_openai_vector_store(model_name: str = "text-embedding-3-small") -> OpenAIVectorStore:
    """
    Create a vector store with OpenAI embeddings.
    
    Args:
        model_name: OpenAI embedding model to use
        
    Returns:
        OpenAIVectorStore instance
    """
    embeddings = OpenAIEmbeddings(model_name=model_name)
    return OpenAIVectorStore(embeddings)
