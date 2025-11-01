"""
Load test for OpenAI-backed Glimpse sampler.
Simulates multiple concurrent users with repeated prompts to stress
cache, retries, and error handling.
"""
import asyncio
import time
import random
from statistics import mean, median
from typing import List
from glimpse.Glimpse import GlimpseEngine, Draft
from glimpse.sampler_openai import openai_sampler
from glimpse.cache_helpers import get_default_cache

# A larger pool of prompts to simulate diverse workloads
PROMPT_POOL = [
    ("Summarize the quarterly sales report for leadership.", "summarize quarterly sales", "keep it under 150 words"),
    ("Explain the new API authentication flow.", "explain auth flow", "include code examples"),
    ("Generate a release notes draft for v2.1.", "generate release notes", "highlight breaking changes"),
    ("Outline the migration steps from old to new schema.", "outline migration steps", "assume PostgreSQL"),
    ("Write a brief intro for the blog post on AI ethics.", "write intro", "tone: professional"),
    ("Create a technical summary of the latest security patch.", "summarize security patch", "focus on CVEs"),
    ("Draft an email to stakeholders about the outage.", "notify stakeholders", "include RCA"),
    ("Provide a quick overview of the new feature flags.", "describe feature flags", "give examples"),
    ("Summarize user feedback from the last sprint.", "summarize feedback", "highlight themes"),
    ("Explain how the new caching layer works.", "explain caching", "include pseudo-code"),
]

async def simulate_user(user_id: int, requests_per_user: int) -> List[float]:
    """Simulate one user making sequential requests."""
    engine = GlimpseEngine(sampler=openai_sampler)
    latencies = []
    for i in range(requests_per_user):
        # Choose prompt: 70% from pool (cache hits), 30% unique (cache misses)
        if random.random() < 0.7:
            prompt, goal, constraints = random.choice(PROMPT_POOL)
        else:
            prompt = f"Unique input from user {user_id} at {time.time()}"
            goal = "summarize"
            constraints = "short"
        draft = Draft(prompt, goal, constraints)
        start = time.perf_counter()
        try:
            await Glimpse.glimpse(draft)
            latencies.append(time.perf_counter() - start)
        except Exception as e:
            print(f"User {user_id} request {i} failed: {e}")
            latencies.append(float('inf'))  # mark failure
        # Small think time between requests
        await asyncio.sleep(random.uniform(0.1, 0.4))
    return latencies

async def main(concurrent_users: int = 10, requests_per_user: int = 5):
    print(f"=== Load Test: {concurrent_users} users × {requests_per_user} requests each ===")
    start = time.perf_counter()
    # Launch all users concurrently
    tasks = [simulate_user(uid, requests_per_user) for uid in range(concurrent_users)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_elapsed = time.perf_counter() - start
    # Flatten latencies and filter out failures
    all_latencies = []
    for r in results:
        if isinstance(r, Exception):
            print(f"User simulation failed: {r}")
            continue
        all_latencies.extend([t for t in r if t != float('inf')])
    total_requests = concurrent_users * requests_per_user
    success_count = len(all_latencies)
    failure_count = total_requests - success_count
    if all_latencies:
        print(f"Total time: {total_elapsed:.2f}s")
        print(f"Requests: {success_count}/{total_requests} succeeded ({failure_count} failures)")
        print(f"Avg latency: {mean(all_latencies):.4f}s")
        print(f"Median latency: {median(all_latencies):.4f}s")
        print(f"Min/Max latency: {min(all_latencies):.4f}s / {max(all_latencies):.4f}s")
        print(f"Throughput: {success_count / total_elapsed:.2f} req/s")
    else:
        print("No successful requests.")
    # Cache stats
    cache = get_default_cache()
    print(f"Cache hit rate: {cache.get_hit_rate():.2%}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load test for OpenAI-backed Glimpse sampler")
    parser.add_argument("-u", "--users", type=int, default=12, help="Number of concurrent users")
    parser.add_argument("-r", "--requests", type=int, default=8, help="Requests per user")
    args = parser.parse_args()
    asyncio.run(main(concurrent_users=args.users, requests_per_user=args.requests))
