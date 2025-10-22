"""
Ollama Embeddings for RAG System

This module provides an embedding interface for Ollama models to be used with the RAG system.
"""

import logging
from typing import List, Dict, Any
import requests
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class OllamaEmbeddings(Embeddings):
    """Embedding model using Ollama's API."""

    def __init__(
        self,
        model_name: str = "embeddinggemma:latest",
        base_url: str = "http://localhost:11434",
        timeout: int = 60,
        **kwargs,
    ):
        """Initialize the Ollama embedding model.

        Args:
            model_name: Name of the Ollama model to use (default: "embeddinggemma:latest")
            base_url: Base URL of the Ollama server (default: "http://localhost:11434")
            timeout: Timeout in seconds for API requests (default: 60)
            **kwargs: Additional arguments to pass to the base class
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.embedding_endpoint = f"{self.base_url}/api/embeddings"

        # Test connection to Ollama server
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to Ollama server at {self.base_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server at {self.base_url}: {e}")
            raise RuntimeError(
                "Failed to connect to Ollama server. "
                "Please make sure Ollama is running and accessible at the specified URL."
            )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts using the Ollama model.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings, one for each input text
        """
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    self.embedding_endpoint, json={"model": self.model_name, "prompt": text}, timeout=self.timeout
                )
                response.raise_for_status()
                embedding = response.json().get("embedding")
                if not embedding:
                    raise ValueError("No embedding returned from Ollama API")
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error embedding text with Ollama: {e}")
                # Return a zero vector of the expected dimension (1024 for embeddinggemma)
                embeddings.append([0.0] * 1024)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text.

        Args:
            text: The text to embed

        Returns:
            The embedding for the input text
        """
        return self.embed_documents([text])[0]

    @property
    def model_kwargs(self) -> Dict[str, Any]:
        """Get the model kwargs."""
        return {"model_name": self.model_name, "base_url": self.base_url}

    @property
    def client(self) -> Any:
        """Get the underlying client (None for Ollama)."""
        return None


class FallbackEmbeddingMixin:
    """Mixin that falls back to HuggingFace embeddings if Ollama is not available."""

    def __init__(self, *args, fallback_model: str = "sentence-transformers/all-mpnet-base-v2", **kwargs):
        """Initialize the fallback embedding.

        Args:
            *args: Positional arguments to pass to the parent class
            fallback_model: HuggingFace model to use as fallback
            **kwargs: Keyword arguments to pass to the parent class
        """
        self._fallback_model = None
        self._fallback_model_name = fallback_model
        super().__init__(*args, **kwargs)

    def _get_fallback_model(self):
        """Lazily initialize the fallback model."""
        if self._fallback_model is None:
            try:
                from langchain.embeddings import HuggingFaceEmbeddings

                self._fallback_model = HuggingFaceEmbeddings(
                    model_name=self._fallback_model_name, model_kwargs={"device": "cpu"}
                )
                logger.info(f"Initialized fallback embedding model: {self._fallback_model_name}")
            except ImportError:
                logger.error("Failed to initialize fallback embedding model")
                raise
        return self._falldown_model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents with fallback to HuggingFace."""
        try:
            return super().embed_documents(texts)
        except Exception as e:
            logger.warning(f"Failed to embed with Ollama, falling back to {self._fallback_model_name}: {e}")
            return self._get_fallback_model().embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a query with fallback to HuggingFace."""
        try:
            return super().embed_query(text)
        except Exception as e:
            logger.warning(f"Failed to embed query with Ollama, falling back to {self._fallback_model_name}: {e}")
            return self._get_fallback_model().embed_query(text)


class OllamaWithFallback(OllamaEmbeddings, FallbackEmbeddingMixin):
    """Ollama embeddings with fallback to HuggingFace."""

    pass
