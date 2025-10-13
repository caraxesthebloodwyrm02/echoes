import math
from typing import Any, Dict, List

<<<<<<< Updated upstream
=======

from packages.core import get_logger
from packages.core.schemas import CacheEntry

logger = get_logger(__name__)
>>>>>>> Stashed changes


def cosine_similarity(a: List[float], b: List[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    den = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return 0.0 if den == 0 else num / den


class PromptCache:
    def __init__(self) -> None:
        self.entries: List[CacheEntry] = []

<<<<<<< Updated upstream
    def add(self, template_id: str, context_vec: List[float], prompt: str, score: float) -> None:
        self.entries.append(
            {
                "template_id": template_id,
                "vec": context_vec,
                "prompt": prompt,
                "score": score,
            }
        )

    def find(self, query_vec: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        ranked = [{**e, "sim": cosine_similarity(query_vec, e["vec"])} for e in self.entries]
        ranked.sort(key=lambda x: (x["sim"], x["score"]), reverse=True)
        return ranked[:top_k]
=======
    def add(
        self, template_id: str, context_vec: List[float], prompt: str, score: float
    ) -> None:
        entry = CacheEntry(
            template_id=template_id,
            vec=context_vec,
            prompt=prompt,
            score=score,
        )
        self.entries.append(entry)
        logger.debug(f"Added cache entry for template {template_id}")

    def find(self, query_vec: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        logger.debug(f"Searching cache for top {top_k} matches")
        ranked = [
            {
                "template_id": e.template_id,
                "vec": e.vec,
                "prompt": e.prompt,
                "score": e.score,
                "sim": cosine_similarity(query_vec, e.vec),
            }
            for e in self.entries
        ]
        ranked.sort(key=lambda x: (x["sim"], x["score"]), reverse=True)
        result = ranked[:top_k]
        logger.debug(f"Found {len(result)} cache matches")
        return result
>>>>>>> Stashed changes
