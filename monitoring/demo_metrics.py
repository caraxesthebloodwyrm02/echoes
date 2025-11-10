#!/usr/bin/env python3
"""
Demo script showing optimized CacheMetrics integration
"""
import time
import random
from typing import Dict, List, Optional
from .cache_metrics import CacheMetrics

def demo_metrics():
    """Demonstrate optimized CacheMetrics functionality with realistic load testing."""
    print("🚀 Optimized CacheMetrics Demo")
    print("=" * 40)
    
    # Initialize metrics with custom configuration
    metrics = CacheMetrics(
        max_samples=5000,          # Keep last 5000 response times
        memory_sample_rate=0.01    # Sample 1% of operations for memory
    )
    
    print("Simulating cache operations under load...")
    start_time = time.time()
    
    # Simulate a more realistic load pattern
    total_operations = 10_000
    hit_ratio = 0.7  # 70% cache hit rate
    
    for i in range(total_operations):
        if random.random() < hit_ratio:
            # Simulate cache hit (faster response)
            metrics.record_hit(random.uniform(0.0001, 0.005))  # 0.1ms to 5ms
        else:
            # Simulate cache miss (slower API call)
            metrics.record_miss(random.uniform(0.1, 3.0))  # 100ms to 3000ms
            
        # Show progress
        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1:,} operations...")
    
    duration = time.time() - start_time
    ops_per_sec = total_operations / duration

    # Get and display stats
    stats = metrics.get_stats()
    
    print("\n📊 Performance Summary:")
    print(f"  Total Operations: {total_operations:,}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Throughput: {ops_per_sec:,.0f} ops/sec")
    print("\n📈 Cache Metrics:")
    print(f"  Hits: {metrics.hits:,}")
    print(f"  Misses: {metrics.misses:,}")
    print(f"  Hit Rate: {stats['hit_rate']:.1%}")
    print("\n⏱️  Response Times:")
    print(f"  Average: {stats['avg_response_time']*1000:.2f} ms")
    print(f"  90th Percentile: {stats['p90_response_time']*1000:.2f} ms")
    
    # Calculate and display cache vs API performance
    if stats['hit_rate'] > 0 and stats['hit_rate'] < 1.0:
        # Get all response times and separate hits/misses
        all_times = metrics.response_times
        split_idx = int(len(all_times) * (1 - stats['hit_rate']))
        
        if split_idx > 0 and split_idx < len(all_times):
            api_times = all_times[:split_idx]  # First part is misses
            cache_times = all_times[split_idx:]  # Second part is hits
            
            if api_times and cache_times:
                avg_api = sum(api_times) / len(api_times)
                avg_cache = sum(cache_times) / len(cache_times)
                speedup = avg_api / avg_cache if avg_cache > 0 else 0
                
                print("\n🚀 Performance Improvement:")
                print(f"  - Cache hits are {speedup:,.0f}x faster than API calls")
                print(f"  - API avg: {avg_api*1000:.2f} ms")
                print(f"  - Cache avg: {avg_cache*1000:.3f} ms")
    
    # Memory usage
    print("\n💾 Memory Usage:")
    print(f"  Samples: {len(metrics.memory_usage)}/{metrics.max_samples}")
    if metrics.memory_usage:
        print(f"  Current: {metrics.memory_usage[-1]:.1f} MB")
    
    print(f"\n🏁 Test completed in {duration:.2f} seconds")

if __name__ == "__main__":
    demo_metrics()
