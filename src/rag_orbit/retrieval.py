from dataclasses import dataclass
from math import sqrt
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    similarity_score: float


@dataclass
class RetrievalMetrics:
    num_results: int


class FAISSRetriever:
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self._embeddings: List[List[float]] = []
        self._texts: List[str] = []
        self._metadata: List[Dict[str, Any]] = []
        self._chunk_ids: List[str] = []

    def add_documents(
        self,
        embeddings: Sequence[Sequence[float]],
        texts: List[str],
        metadata: List[Dict[str, Any]],
        chunk_ids: List[str],
    ):
        for embedding in embeddings:
            self._embeddings.append([float(value) for value in embedding])
        self._texts.extend(texts)
        self._metadata.extend(metadata)
        self._chunk_ids.extend(chunk_ids)

    def search(self, query_embedding: Sequence[float], top_k: int = 5, category_filter: Optional[str] = None):
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
            score = float(sum(left * right for left, right in zip(query, emb)) / (qn * en))
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
        categories = sorted({str(md.get("category")) for md in self._metadata if md.get("category") is not None})
        return {
            "total_documents": len(self._texts),
            "categories": categories,
        }


def create_standard_retriever(embedding_dim: int = 384) -> FAISSRetriever:
    return FAISSRetriever(embedding_dim=embedding_dim)
