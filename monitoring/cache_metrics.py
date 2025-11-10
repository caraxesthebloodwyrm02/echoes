"""
Optimized Cache Metrics Module

This module provides a high-performance CacheMetrics class for tracking and reporting
cache performance metrics with minimal overhead.
"""
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Deque, Optional
import threading
import time
import psutil
import platform
import random

@dataclass
class CacheMetrics:
    """
    High-performance cache metrics tracker with bounded memory usage and thread safety.
    
    Features:
    - Bounded memory usage with fixed-size deques
    - Thread-safe operations
    - Efficient percentile calculation
    - Configurable sampling rate for memory usage
    - Optimized for high-throughput scenarios
    
    Args:
        max_samples: Maximum number of samples to keep in memory
        memory_sample_rate: Fraction of operations to sample memory (0.0 to 1.0)
    """
    max_samples: int = 1000
    memory_sample_rate: float = 0.1  # Sample 10% of operations
    
    def __post_init__(self):
        """Initialize thread-safe data structures and counters."""
        self.hits: int = 0
        self.misses: int = 0
        self.total_requests: int = 0
        self._response_times: Deque[float] = deque(maxlen=self.max_samples)
        self._memory_samples: Deque[float] = deque(maxlen=100)  # Fixed size for memory stats
        self._lock = threading.RLock()
        self._last_memory_sample: float = 0.0
        
    def record_hit(self, response_time: float):
        """
        Record a cache hit with the given response time.
        Thread-safe and memory-efficient.
        
        Args:
            response_time: Response time in seconds
        """
        with self._lock:
            self.hits += 1
            self.total_requests += 1
            self._record_response_time(response_time)
            self._maybe_sample_memory()
    
    def record_miss(self, response_time: float):
        """
        Record a cache miss with the given response time.
        Thread-safe and memory-efficient.
        
        Args:
            response_time: Response time in seconds
        """
        with self._lock:
            self.misses += 1
            self.total_requests += 1
            self._record_response_time(response_time)
            self._maybe_sample_memory()
    
    def _record_response_time(self, response_time: float):
        """Record response time in a thread-safe manner."""
        with self._lock:
            self._response_times.append(response_time)
    
    def _maybe_sample_memory(self):
        """Sample memory usage based on configured rate."""
        if random.random() < self.memory_sample_rate:
            self._sample_memory()
    
    def _sample_memory(self):
        """Record current memory usage in MB."""
        try:
            process = psutil.Process()
            with self._lock:
                self._memory_samples.append(process.memory_info().rss / 1024 / 1024)
                self._last_memory_sample = time.time()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # Handle cases where process info is not available
    
    def get_stats(self) -> Dict:
        """
        Get current cache statistics in a thread-safe manner.
        
        Returns:
            Dictionary containing:
            - hit_rate: Cache hit rate (0.0 to 1.0)
            - avg_response_time: Average response time in seconds
            - p90_response_time: 90th percentile response time
            - current_memory_mb: Last sampled memory usage in MB
            - system: System hostname
            - sample_count: Number of response time samples
        """
        with self._lock:
            response_times = list(self._response_times)
            memory_samples = list(self._memory_samples)
            hit_rate = self.hits / max(1, self.total_requests)
            
            # Calculate response time statistics
            if response_times:
                sorted_times = sorted(response_times)
                avg_time = sum(response_times) / len(response_times)
                p90_index = min(int(len(sorted_times) * 0.9), len(sorted_times) - 1)
                p90_time = sorted_times[p90_index]
            else:
                avg_time = 0.0
                p90_time = 0.0
            
            # Get latest memory sample or 0 if none available
            current_mem = memory_samples[-1] if memory_samples else 0.0
            
            return {
                "hit_rate": hit_rate,
                "avg_response_time": avg_time,
                "p90_response_time": p90_time,
                "current_memory_mb": current_mem,
                "system": platform.node(),
                "sample_count": len(response_times)
            }
    
    def reset(self):
        """Reset all metrics to initial state."""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.total_requests = 0
            self._response_times.clear()
            self._memory_samples.clear()
    
    @property
    def response_times(self) -> List[float]:
        """Thread-safe access to response times (copy)."""
        with self._lock:
            return list(self._response_times)
    
    @property
    def memory_usage(self) -> List[float]:
        """Thread-safe access to memory samples (copy)."""
        with self._lock:
            return list(self._memory_samples)
