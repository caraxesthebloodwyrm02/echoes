"""
Benchmark script for the OpenAI-backed sampler.
Measures real API latency, retry behavior, and error handling.
"""

import asyncio
import time
from statistics import mean

from glimpse.Glimpse import Draft, GlimpseEngine
from glimpse.sampler_openai import openai_sampler


async def run_once():
    GlimpseEngine(sampler=openai_sampler)
    draft = Draft(
        "Summarize the quarterly sales report for leadership.",
        "summarize quarterly sales",
        "keep it under 150 words",
    )
    start = time.perf_counter()
    await Glimpse.glimpse(draft)
    return time.perf_counter() - start


async def main(iterations=5):
    print(f"Running {iterations} OpenAI sampler iterations...")
    samples = [await run_once() for _ in range(iterations)]
    print("Samples:", [round(s, 4) for s in samples])
    print(f"Average: {mean(samples):.4f}s")
    print(f"Min: {min(samples):.4f}s, Max: {max(samples):.4f}s")


if __name__ == "__main__":
    asyncio.run(main())
