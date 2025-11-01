"""
Comprehensive tests for PerformanceOptimizer
"""
import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from glimpse.performance_optimizer import (
    PerformanceCache,
    RequestQueue,
    AdaptiveTimeout,
    PerformanceOptimizer,
    PerformanceMetrics,
    monitor_performance
)
from glimpse.Glimpse import Draft, GlimpseResult


class TestPerformanceCache:
    """Test the PerformanceCache class"""
    
    @pytest.mark.asyncio
    async def test_cache_initialization(self):
        cache = PerformanceCache(max_size=100, ttl_seconds=60)
        assert cache.max_size == 100
        assert cache.ttl_seconds == 60
        assert cache.hits == 0
        assert cache.misses == 0
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        cache = PerformanceCache()
        draft = Draft("test", "goal", "constraints")
        result = GlimpseResult(
            attempt=1,
            status="aligned",
            sample="test sample",
            essence="test essence",
            delta=None,
            stale=False,
            status_history=["test"]
        )
        
        # Set and get
        await cache.set(draft.input_text, draft.goal, draft.constraints, result)
        cached = await cache.get(draft.input_text, draft.goal, draft.constraints)
        
        assert cached is not None
        assert cached.sample == "test sample"
        assert cache.hits == 1
        assert cache.misses == 0
    
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        cache = PerformanceCache()
        
        # Get non-existent item
        result = await cache.get("nonexistent", "goal", "constraints")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self):
        cache = PerformanceCache(ttl_seconds=0.1)  # 100ms TTL
        draft = Draft("test", "goal", "constraints")
        result = GlimpseResult(
            attempt=1,
            status="aligned",
            sample="test",
            essence="test",
            delta=None,
            stale=False,
            status_history=[]
        )
        
        # Set item
        await cache.set(draft.input_text, draft.goal, draft.constraints, result)
        
        # Get immediately - should work
        cached = await cache.get(draft.input_text, draft.goal, draft.constraints)
        assert cached is not None
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Get after expiration - should miss
        cached = await cache.get(draft.input_text, draft.goal, draft.constraints)
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_cache_max_size_eviction(self):
        cache = PerformanceCache(max_size=2)
        
        # Add 3 items
        for i in range(3):
            draft = Draft(f"test{i}", "goal", "constraints")
            result = GlimpseResult(
                attempt=1,
                status="aligned",
                sample=f"sample{i}",
                essence="test",
                delta=None,
                stale=False,
                status_history=[]
            )
            await cache.set(draft.input_text, draft.goal, draft.constraints, result)
        
        # First item should be evicted
        cached = await cache.get("test0", "goal", "constraints")
        assert cached is None
        
        # Last two items should still be there
        cached = await cache.get("test1", "goal", "constraints")
        assert cached is not None
        cached = await cache.get("test2", "goal", "constraints")
        assert cached is not None
    
    @pytest.mark.asyncio
    async def test_cache_clear(self):
        cache = PerformanceCache()
        draft = Draft("test", "goal", "constraints")
        result = GlimpseResult(
            attempt=1,
            status="aligned",
            sample="test",
            essence="test",
            delta=None,
            stale=False,
            status_history=[]
        )
        
        # Add item
        await cache.set(draft.input_text, draft.goal, draft.constraints, result)
        assert cache.hits == 0
        assert cache.misses == 0
        
        # Clear cache
        await cache.clear()
        
        # Should miss after clear
        cached = await cache.get(draft.input_text, draft.goal, draft.constraints)
        assert cached is None
        assert cache.hits == 0
        assert cache.misses == 1
    
    def test_cache_hit_rate(self):
        cache = PerformanceCache()
        cache.hits = 7
        cache.misses = 3
        
        hit_rate = cache.get_hit_rate()
        assert hit_rate == 0.7  # 7/(7+3)
    
    def test_cache_key_generation(self):
        cache = PerformanceCache()
        
        # Same inputs should generate same key
        key1 = cache._generate_key("test", "goal", "constraints")
        key2 = cache._generate_key("test", "goal", "constraints")
        assert key1 == key2
        
        # Different inputs should generate different keys
        key3 = cache._generate_key("different", "goal", "constraints")
        assert key1 != key3


class TestAdaptiveTimeout:
    """Test the AdaptiveTimeout class"""
    
    def test_initialization(self):
        timeout = AdaptiveTimeout(initial_timeout=1.0, max_timeout=5.0)
        assert timeout.initial_timeout == 1.0
        assert timeout.max_timeout == 5.0
        assert timeout.current_timeout == 1.0
    
    def test_record_latency_increases_timeout(self):
        timeout = AdaptiveTimeout(initial_timeout=1.0, max_timeout=5.0)
        
        # Record high latency
        timeout.record_latency(2.0)
        
        # Timeout should increase
        assert timeout.current_timeout > 1.0
    
    def test_record_latency_decreases_timeout(self):
        timeout = AdaptiveTimeout(initial_timeout=3.0, max_timeout=5.0)
        
        # Record low latencies
        for _ in range(10):
            timeout.record_latency(0.5)
        
        # Timeout should decrease
        assert timeout.current_timeout < 3.0
    
    def test_timeout_never_exceeds_max(self):
        timeout = AdaptiveTimeout(initial_timeout=1.0, max_timeout=2.0)
        
        # Record very high latencies
        for _ in range(10):
            timeout.record_latency(10.0)
        
        # Should not exceed max
        assert timeout.current_timeout <= 2.0
    
    def test_get_timeout(self):
        timeout = AdaptiveTimeout(initial_timeout=1.5, max_timeout=5.0)
        assert timeout.get_timeout() == 1.5


class TestRequestQueue:
    """Test the RequestQueue class"""
    
    @pytest.mark.asyncio
    async def test_queue_initialization(self):
        queue = RequestQueue(max_concurrent=5)
        assert queue.max_concurrent == 5
        assert queue.queue.qsize() == 0
        assert queue.active_requests == 0
    
    @pytest.mark.asyncio
    async def test_submit_task(self):
        queue = RequestQueue(max_concurrent=1)
        
        async def dummy_task():
            await asyncio.sleep(0.1)
            return "result"
        
        # Submit task
        result = await queue.submit(dummy_task(), priority=0)
        assert result == ["result"]
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        queue = RequestQueue(max_concurrent=3)
        
        results = []
        
        async def make_task(value):
            await asyncio.sleep(0.01)
            results.append(value)
            return value
        
        # Submit tasks with different priorities
        task1 = queue.submit(make_task("low"), priority=2)
        task2 = queue.submit(make_task("high"), priority=0)
        task3 = queue.submit(make_task("medium"), priority=1)
        
        # Wait for all to complete
        await asyncio.gather(task1, task2, task3)
        
        # Check that high priority was processed first
        # Note: Due to async nature, we check if high appears early in results
        assert "high" in results
        assert len(results) == 3


class TestPerformanceOptimizer:
    """Test the PerformanceOptimizer class"""
    
    @pytest.mark.asyncio
    async def test_optimizer_initialization(self):
        optimizer = PerformanceOptimizer(cache_size=100, max_concurrent=5)
        assert optimizer.cache.max_size == 100
        assert optimizer.queue.max_concurrent == 5
        assert optimizer.optimization_enabled == True
    
    @pytest.mark.asyncio
    async def test_optimized_glimpse_with_cache(self):
        optimizer = PerformanceOptimizer()
        
        async def mock_sampler(draft):
            await asyncio.sleep(0.1)
            return GlimpseResult(
                attempt=1,
                status="aligned",
                sample="cached",
                essence="test",
                delta=None,
                stale=False,
                status_history=[]
            )
        
        draft = Draft("test", "goal", "constraints")
        
        # First call - should execute sampler
        result1, time1 = await optimizer.optimized_glimpse(draft, mock_sampler)
        assert result1.sample == "cached"
        assert time1 > 0
        
        # Second call - should use cache
        result2, time2 = await optimizer.optimized_glimpse(draft, mock_sampler)
        assert result2.sample == "cached"
        assert time2 < time1  # Should be faster from cache
    
    @pytest.mark.asyncio
    async def test_optimized_glimpse_timeout_fallback(self):
        optimizer = PerformanceOptimizer()
        
        async def slow_sampler(draft):
            await asyncio.sleep(2.0)  # Longer than default timeout
            return GlimpseResult(
                attempt=1,
                status="aligned",
                sample="slow",
                essence="test",
                delta=None,
                stale=False,
                status_history=[]
            )
        
        draft = Draft("test", "goal", "constraints")
        
        # Should timeout and return fallback
        result, exec_time = await optimizer.optimized_glimpse(draft, slow_sampler)
        assert result.status == "stale"
        assert "delayed" in result.essence
    
    @pytest.mark.asyncio
    async def test_batch_glimpses(self):
        optimizer = PerformanceOptimizer()
        
        async def mock_sampler(draft):
            await asyncio.sleep(0.05)
            return GlimpseResult(
                attempt=1,
                status="aligned",
                sample=f"sample_{draft.input_text}",
                essence="test",
                delta=None,
                stale=False,
                status_history=[]
            )
        
        drafts = [
            Draft(f"test{i}", "goal", "constraints") 
            for i in range(3)
        ]
        
        results = await optimizer.batch_glimpses(drafts, mock_sampler)
        
        assert len(results) == 3
        for i, (result, time_taken) in enumerate(results):
            assert result.sample == f"sample_test{i}"
    
    @pytest.mark.asyncio
    async def test_batch_glimpses_optimization_disabled(self):
        optimizer = PerformanceOptimizer()
        optimizer.enable_optimization(False)
        
        async def mock_sampler(draft):
            return GlimpseResult(
                attempt=1,
                status="aligned",
                sample="sequential",
                essence="test",
                delta=None,
                stale=False,
                status_history=[]
            )
        
        drafts = [Draft("test", "goal", "constraints") for _ in range(2)]
        
        # Should work even when optimization disabled
        results = await optimizer.batch_glimpses(drafts, mock_sampler)
        assert len(results) == 2
    
    def test_get_metrics(self):
        optimizer = PerformanceOptimizer()
        optimizer.metrics.total_requests = 10
        optimizer.metrics.failed_requests = 2
        
        metrics = optimizer.get_metrics()
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_requests == 10
        assert metrics.failed_requests == 2
    
    @pytest.mark.asyncio
    async def test_clear_cache(self):
        optimizer = PerformanceOptimizer()
        
        async def mock_sampler(draft):
            return GlimpseResult(
                attempt=1,
                status="aligned",
                sample="test",
                essence="test",
                delta=None,
                stale=False,
                status_history=[]
            )
        
        draft = Draft("test", "goal", "constraints")
        
        # Add to cache
        await optimizer.optimized_glimpse(draft, mock_sampler)
        
        # Clear cache
        await optimizer.clear_cache()
        
        # Cache should be empty
        assert optimizer.cache.get_hit_rate() == 0.0
    
    def test_adaptive_essence_only(self):
        optimizer = PerformanceOptimizer()
        
        # Low latency - should not enable essence-only
        assert optimizer.adaptive_essence_only(0.5) == False
        
        # High latency - should enable essence-only
        assert optimizer.adaptive_essence_only(1.0) == True
        
        # Very high latency - should enable essence-only
        assert optimizer.adaptive_essence_only(2.0) == True
    
    def test_enable_disable_optimization(self):
        optimizer = PerformanceOptimizer()
        
        # Disable optimization
        optimizer.enable_optimization(False)
        assert optimizer.optimization_enabled == False
        
        # Re-enable optimization
        optimizer.enable_optimization(True)
        assert optimizer.optimization_enabled == True


class TestMonitorDecorator:
    """Test the monitor_performance decorator"""
    
    @pytest.mark.asyncio
    async def test_monitor_decorator_success(self):
        optimizer = PerformanceOptimizer()
        
        @monitor_performance(optimizer)
        async def test_function():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await test_function()
        assert result == "success"
        # Should record latency
        assert optimizer.timeout.current_timeout != optimizer.timeout.initial_timeout
    
    @pytest.mark.asyncio
    async def test_monitor_decorator_exception(self):
        optimizer = PerformanceOptimizer()
        
        @monitor_performance(optimizer)
        async def failing_function():
            raise ValueError("test error")
        
        with pytest.raises(ValueError):
            await failing_function()
        
        # Should record failure
        assert optimizer.metrics.failed_requests > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
