import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from math import sqrt
from typing import Any


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    similarity_score: float


@dataclass
class RetrievalMetrics:
    num_results: int


class _IndexCompat:
    """Minimal index-like object for test compatibility (ntotal)."""

    def __init__(self, ntotal: int):
        self.ntotal = ntotal


class FAISSRetriever:
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self._embeddings: list[list[float]] = []
        self._texts: list[str] = []
        self._metadata: list[dict[str, Any]] = []
        self._chunk_ids: list[str] = []

    @property
    def index(self) -> _IndexCompat:
        return _IndexCompat(ntotal=len(self._texts))

    @property
    def chunk_texts(self) -> list[str]:
        return self._texts

    @property
    def chunk_ids(self) -> list[str]:
        return self._chunk_ids

    def add_documents(
        self,
        embeddings: Sequence[Sequence[float]],
        texts: list[str],
        metadata: list[dict[str, Any]],
        chunk_ids: list[str],
    ):
        for embedding in embeddings:
            self._embeddings.append([float(value) for value in embedding])
        self._texts.extend(texts)
        self._metadata.extend(metadata)
        self._chunk_ids.extend(chunk_ids)

    def search(
        self,
        query_embedding: Sequence[float],
        top_k: int = 5,
        category_filter: str | None = None,
    ):
        if not len(self._texts):
            return [], RetrievalMetrics(num_results=0)

        query = [float(value) for value in query_embedding]
        qn = sqrt(sum(value * value for value in query)) or 1.0

        rows = []
        for idx, emb in enumerate(self._embeddings):
            md = self._metadata[idx] if idx < len(self._metadata) else {}
            if category_filter and md.get("category") != category_filter:
                continue
            en = sqrt(sum(value * value for value in emb)) or 1.0
            score = float(
                sum(left * right for left, right in zip(query, emb, strict=False)) / (qn * en)
            )
            rows.append((score, idx))

        rows.sort(key=lambda x: x[0], reverse=True)
        selected = rows[:top_k]
        results = [
            RetrievalResult(
                chunk_id=self._chunk_ids[idx],
                text=self._texts[idx],
                metadata=self._metadata[idx],
                similarity_score=score,
            )
            for score, idx in selected
        ]
        return results, RetrievalMetrics(num_results=len(results))

    def get_stats(self):
        categories = sorted(
            {
                str(md.get("category"))
                for md in self._metadata
                if md.get("category") is not None
            }
        )
        return {
            "total_documents": len(self._texts),
            "embedding_dim": self.embedding_dim,
            "categories": categories,
        }

    def save(self, save_dir: Path | str) -> None:
        path = Path(save_dir)
        path.mkdir(parents=True, exist_ok=True)
        state = {
            "embedding_dim": self.embedding_dim,
            "embeddings": self._embeddings,
            "texts": self._texts,
            "metadata": self._metadata,
            "chunk_ids": self._chunk_ids,
        }
        with open(path / "index.json", "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load(cls, save_dir: Path | str) -> "FAISSRetriever":
        path = Path(save_dir) / "index.json"
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
        r = cls(embedding_dim=state["embedding_dim"])
        r._embeddings = state["embeddings"]
        r._texts = state["texts"]
        r._metadata = state["metadata"]
        r._chunk_ids = state["chunk_ids"]
        return r


def create_standard_retriever(embedding_dim: int = 384) -> FAISSRetriever:
    return FAISSRetriever(embedding_dim=embedding_dim)
