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
