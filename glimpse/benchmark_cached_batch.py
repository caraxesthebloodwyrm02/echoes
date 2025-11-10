"""
Benchmark to demonstrate caching and batching improvements.
Runs repeated and batched requests to measure latency reductions.
"""

import asyncio
import time
from statistics import mean

from glimpse.cache_helpers import get_default_cache
from glimpse.Glimpse import Draft, GlimpseEngine
from glimpse.sampler_openai import openai_sampler


async def run_once_unique():
    """Run a unique draft (cache miss)."""
    GlimpseEngine(sampler=openai_sampler)
    draft = Draft(
        f"Unique input {time.time()}",
        "summarize quarterly sales",
        "keep it under 150 words",
    )
    start = time.perf_counter()
    await Glimpse.glimpse(draft)
    return time.perf_counter() - start


async def run_once_repeated():
    """Run a repeated draft (should hit cache)."""
    GlimpseEngine(sampler=openai_sampler)
    draft = Draft(
        "Summarize the quarterly sales report for leadership.",
        "summarize quarterly sales",
        "keep it under 150 words",
    )
    start = time.perf_counter()
    await Glimpse.glimpse(draft)
    return time.perf_counter() - start


async def run_batch(drafts):
    """Run multiple drafts concurrently."""
    GlimpseEngine(sampler=openai_sampler)
    start = time.perf_counter()
    await asyncio.gather(*(Glimpse.glimpse(d) for d in drafts))
    return time.perf_counter() - start


async def main():
    print("=== Cache and Batch Benchmark ===")
    # Warm cache with one request
    await run_once_repeated()
    # Measure cache hits
    cache_times = [await run_once_repeated() for _ in range(5)]
    print("Cache-hit times (5 runs):", [round(t, 4) for t in cache_times])
    print(f"Cache-hit average: {mean(cache_times):.4f}s")
    # Measure unique requests (cache misses)
    unique_times = [await run_once_unique() for _ in range(3)]
    print("Unique request times (3 runs):", [round(t, 4) for t in unique_times])
    print(f"Unique average: {mean(unique_times):.4f}s")
    # Simple batch test
    batch_drafts = [
        Draft("Input A", "summarize", "short"),
        Draft("Input B", "summarize", "short"),
        Draft("Input C", "summarize", "short"),
    ]
    batch_time = await run_batch(batch_drafts)
    print(f"Batch of 3 concurrent time: {batch_time:.4f}s")
    # Cache stats
    cache = get_default_cache()
    print(f"Cache hit rate: {cache.get_hit_rate():.2%}")


if __name__ == "__main__":
    asyncio.run(main())
