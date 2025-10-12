import math
from typing import Any, Dict, List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    den = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return 0.0 if den == 0 else num / den


class PromptCache:
    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

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
