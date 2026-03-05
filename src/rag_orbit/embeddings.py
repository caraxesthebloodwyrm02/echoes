from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import md5
from math import sqrt
from pathlib import Path
from random import Random

import numpy as np


@dataclass
class EmbeddingMetadata:
    chunk_id: str
    text_checksum: str


class EmbeddingGenerator:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_cache: bool = False,
        cache_dir: Path | None = None,
    ):
        self.model_name = model_name
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.embedding_dim = 384
        self._cache = {}
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _embed(self, text: str) -> list[float]:
        seed = int(md5(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = Random(seed)
        vec = [rng.random() for _ in range(self.embedding_dim)]
        norm = sqrt(sum(value * value for value in vec)) or 1.0
        return [value / norm for value in vec]

    def embed_text(
        self, text: str, chunk_id: str | None = None
    ) -> tuple[np.ndarray, EmbeddingMetadata]:
        checksum = md5(text.encode("utf-8")).hexdigest()
        cache_key = f"{chunk_id}:{checksum}"
        if self.use_cache and cache_key in self._cache:
            emb = self._cache[cache_key]
        else:
            emb = self._embed(text)
            if self.use_cache:
                self._cache[cache_key] = emb
        arr = np.asarray(emb, dtype=np.float64)
        return arr, EmbeddingMetadata(
            chunk_id=chunk_id or checksum, text_checksum=checksum
        )

    def embed_batch(
        self, texts: list[str], chunk_ids: Sequence[str] | None = None
    ) -> tuple[np.ndarray, list[EmbeddingMetadata]]:
        metas = []
        vectors = []
        ids_for_texts: Sequence[str | None] = (
            list(chunk_ids) if chunk_ids is not None else [None] * len(texts)
        )
        for text, chunk_id in zip(texts, ids_for_texts, strict=False):
            emb, meta = self.embed_text(text, chunk_id=chunk_id)
            vectors.append(emb)
            metas.append(meta)
        return np.stack(vectors), metas

    def compute_similarity(self, emb1: list[float], emb2: list[float]) -> float:
        dot = sum(left * right for left, right in zip(emb1, emb2, strict=False))
        norm1 = sqrt(sum(value * value for value in emb1)) or 1.0
        norm2 = sqrt(sum(value * value for value in emb2)) or 1.0
        return float(dot / (norm1 * norm2))


def create_standard_generator(use_cache: bool = False) -> EmbeddingGenerator:
    return EmbeddingGenerator(use_cache=use_cache)
