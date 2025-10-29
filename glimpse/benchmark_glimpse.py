import asyncio
import time
from statistics import mean
from glimpse.engine import GlimpseEngine, Draft

async def run_once():
    engine = GlimpseEngine()
    draft = Draft(
        "Analyze system logs for anomalies",
        "summarize logs",
        "focus on errors",
    )
    start = time.perf_counter()
    await engine.glimpse(draft)
    return time.perf_counter() - start

async def main(iterations=10):
    samples = [await run_once() for _ in range(iterations)]
    print("Samples:", [round(s, 4) for s in samples])
    print(f"Average: {mean(samples):.4f}s")
    print(f"Min: {min(samples):.4f}s, Max: {max(samples):.4f}s")

if __name__ == "__main__":
    asyncio.run(main())