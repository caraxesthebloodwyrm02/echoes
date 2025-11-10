"""
Performance Optimizer for Glimpse Preflight System
Optimizes performance for high-latency scenarios with caching, async processing, and batching
"""

import asyncio
import hashlib
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any


@dataclass
class PerformanceMetrics:
    """Track performance metrics"""

    avg_latency: float = 0.0
    cache_hit_rate: float = 0.0
    queue_depth: int = 0
    active_requests: int = 0
    total_requests: int = 0
    failed_requests: int = 0


class PerformanceCache:
    """High-performance cache with TTL and size limits"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, tuple[Any, float]] = {}
        self.access_times: dict[str, float] = {}
        self.lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, input_text: str, goal: str, constraints: str) -> str:
        """Generate cache key from input parameters"""
        content = f"{input_text}|{goal}|{constraints}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def get(self, input_text: str, goal: str, constraints: str) -> Any | None:
        """Get cached result if available and not expired"""
        key = self._generate_key(input_text, goal, constraints)

        async with self.lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    self.access_times[key] = time.time()
                    self.hits += 1
                    return result
                else:
                    # Expired - remove
                    del self.cache[key]
                    if key in self.access_times:
                        del self.access_times[key]

            self.misses += 1
            return None

    async def set(self, input_text: str, goal: str, constraints: str, result: Any):
        """Cache the result"""
        key = self._generate_key(input_text, goal, constraints)

        async with self.lock:
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size:
                oldest_key = min(
                    self.access_times.keys(), key=lambda k: self.access_times[k]
                )
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = (result, time.time())
            self.access_times[key] = time.time()

    def get_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    async def clear(self):
        """Clear all cached entries"""
        async with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hits = 0
            self.misses = 0


class RequestQueue:
    """Queue for managing concurrent requests with priority"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.queue = asyncio.Queue()
        self.active_requests = 0
        self.lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def submit(self, coro, priority: int = 0):
        """Submit a coroutine with optional priority"""
        await self.queue.put((priority, coro))
        return await self._process_queue()

    async def _process_queue(self):
        """Process the queue respecting priority"""
        # Get highest priority item
        items = []
        while not self.queue.empty() and len(items) < self.max_concurrent:
            items.append(await self.queue.get())

        # Sort by priority (lower number = higher priority)
        items.sort(key=lambda x: x[0])

        # Execute tasks
        tasks = []
        for _, coro in items:
            async with self.semaphore:
                task = asyncio.create_task(coro)
                tasks.append(task)

        if tasks:
            return await asyncio.gather(*tasks, return_exceptions=True)
        return None


class AdaptiveTimeout:
    """Adaptive timeout that adjusts based on historical performance"""

    def __init__(self, initial_timeout: float = 2.0, max_timeout: float = 10.0):
        self.initial_timeout = initial_timeout
        self.max_timeout = max_timeout
        self.current_timeout = initial_timeout
        self.recent_latencies = []
        self.max_history = 10

    def record_latency(self, latency: float):
        """Record actual latency and adjust timeout"""
        self.recent_latencies.append(latency)
        if len(self.recent_latencies) > self.max_history:
            self.recent_latencies.pop(0)

        # Calculate new timeout as 95th percentile of recent latencies
        sorted_latencies = sorted(self.recent_latencies)
        percentile_idx = int(0.95 * len(sorted_latencies))
        if percentile_idx < len(sorted_latencies):
            self.current_timeout = min(
                sorted_latencies[percentile_idx] * 1.5, self.max_timeout
            )

    def get_timeout(self) -> float:
        """Get current timeout value"""
        return self.current_timeout


class PerformanceOptimizer:
    """Main performance optimizer coordinator"""

    def __init__(self, cache_size: int = 1000, max_concurrent: int = 10):
        self.cache = PerformanceCache(max_size=cache_size)
        self.queue = RequestQueue(max_concurrent=max_concurrent)
        self.timeout = AdaptiveTimeout()
        self.metrics = PerformanceMetrics()
        self.request_times = defaultdict(list)
        self.optimization_enabled = True

    def enable_optimization(self, enabled: bool = True):
        """Enable or disable performance optimizations"""
        self.optimization_enabled = enabled

    async def optimized_glimpse(
        self, draft, sampler_func: Callable
    ) -> tuple[Any, float]:
        """
        Execute glimpse with performance optimizations

        Args:
            draft: The input draft
            sampler_func: The sampler function to execute

        Returns:
            Tuple of (result, execution_time)
        """
        start_time = time.time()

        try:
            # Check cache first
            if self.optimization_enabled:
                cached_result = await self.cache.get(
                    draft.input_text, draft.goal, draft.constraints
                )
                if cached_result is not None:
                    execution_time = time.time() - start_time
                    self.timeout.record_latency(execution_time)
                    return cached_result, execution_time

            # Execute with timeout
            result = await asyncio.wait_for(
                sampler_func(draft), timeout=self.timeout.get_timeout()
            )

            execution_time = time.time() - start_time

            # Cache the result
            if self.optimization_enabled:
                await self.cache.set(
                    draft.input_text, draft.goal, draft.constraints, result
                )

            # Update metrics
            self.timeout.record_latency(execution_time)
            self.metrics.total_requests += 1

            return result, execution_time

        except TimeoutError:
            self.metrics.failed_requests += 1
            # Return a fallback result for high latency
            fallback_result = await self._create_fallback_result(draft)
            execution_time = time.time() - start_time
            return fallback_result, execution_time

    async def _create_fallback_result(self, draft):
        """Create a fallback result for high-latency scenarios"""
        from glimpse.Glimpse import GlimpseResult

        return GlimpseResult(
            attempt=1,
            status="stale",
            sample="",
            essence="Request processing delayed due to high latency. Please try again.",
            delta=None,
            stale=True,
            status_history=["High latency detected", "Using fallback response"],
        )

    async def batch_glimpses(
        self, drafts: list[Any], sampler_func: Callable
    ) -> list[tuple[Any, float]]:
        """
        Process multiple glimpse requests in batch for efficiency

        Args:
            drafts: List of drafts to process
            sampler_func: Sampler function to use

        Returns:
            List of (result, execution_time) tuples
        """
        if not self.optimization_enabled:
            # Process sequentially if optimization disabled
            results = []
            for draft in drafts:
                result = await sampler_func(draft)
                results.append((result, 0.0))
            return results

        # Process in parallel with queue management
        tasks = []
        for draft in drafts:
            task = self.optimized_glimpse(draft, sampler_func)
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        self.metrics.cache_hit_rate = self.cache.get_hit_rate()
        self.metrics.queue_depth = self.queue.queue.qsize()
        self.metrics.active_requests = self.queue.active_requests

        return self.metrics

    async def clear_cache(self):
        """Clear performance cache"""
        await self.cache.clear()

    def adaptive_essence_only(self, avg_latency: float) -> bool:
        """
        Determine if essence-only mode should be used based on latency

        Args:
            avg_latency: Average latency in seconds

        Returns:
            True if essence-only mode is recommended
        """
        # Enable essence-only for high latency scenarios
        return avg_latency > 0.8  # 800ms threshold


# Performance monitoring decorator
def monitor_performance(optimizer: PerformanceOptimizer):
    """Decorator to monitor function performance"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                optimizer.timeout.record_latency(execution_time)
                return result
            except Exception:
                optimizer.metrics.failed_requests += 1
                raise

        return wrapper

    return decorator


# Example usage
async def example_optimized_sampler(draft):
    """Example of an optimized sampler function"""
    # Simulate some processing time
    await asyncio.sleep(0.1)

    return GlimpseResult(
        attempt=1,
        status="aligned",
        sample=f"Sample for: {draft.input_text[:50]}...",
        essence=f"Essence: {draft.goal or 'process request'}",
        delta=None,
        stale=False,
        status_history=["Processing complete"],
    )


if __name__ == "__main__":

    async def demo():
        optimizer = PerformanceOptimizer()

        # Test single optimized glimpse
        from glimpse.Glimpse import Draft

        draft = Draft(
            input_text="Test input for optimization",
            goal="test performance",
            constraints="",
        )

        result, exec_time = await optimizer.optimized_glimpse(
            draft, example_optimized_sampler
        )

        print(f"Result: {result.status}")
        print(f"Execution time: {exec_time:.3f}s")
        print(f"Cache hit rate: {optimizer.get_metrics().cache_hit_rate:.2%}")

        # Test batch processing
        drafts = [draft for _ in range(5)]
        batch_results = await optimizer.batch_glimpses(
            drafts, example_optimized_sampler
        )

        print(f"Batch processed {len(batch_results)} requests")

    asyncio.run(demo())
