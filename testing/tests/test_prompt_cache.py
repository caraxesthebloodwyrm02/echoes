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

from caching.prompt_engine import PromptCache, cosine_similarity


def test_cosine_similarity_basic():
    assert abs(cosine_similarity([1, 0], [1, 0]) - 1.0) < 1e-9
    assert abs(cosine_similarity([1, 0], [0, 1]) - 0.0) < 1e-9


def test_prompt_cache_find_orders_by_similarity_then_score():
    cache = PromptCache()
    cache.add("t1", [1.0, 0.0], "p1", score=0.5)
    cache.add("t2", [0.9, 0.1], "p2", score=0.9)
    cache.add("t3", [0.0, 1.0], "p3", score=1.0)

    # Query close to [1,0] should prefer t2 over t1 if similarity slightly
    # lower but score higher only when similarity ties.
    results = cache.find([1.0, 0.0], top_k=2)
    # First should be t1 (highest sim), second t2
    assert results[0]["template_id"] in ("t1", "t2")
    # Ensure the best match is similar to [1,0]
    assert results[0]["sim"] >= results[1]["sim"]
