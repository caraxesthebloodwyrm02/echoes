# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
from typing import Any, Dict, List

from packages.core import get_logger
from packages.core.schemas import CacheEntry

logger = get_logger(__name__)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    den = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return 0.0 if den == 0 else num / den


class PromptCache:
    def __init__(self) -> None:
        self.entries: List[CacheEntry] = []

    def add(self, template_id: str, context_vec: List[float], prompt: str, score: float) -> None:
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
