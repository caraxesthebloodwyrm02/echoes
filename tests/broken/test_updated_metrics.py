#!/usr/bin/env python3
"""
Test the updated CacheMetrics implementation with OpenAIClient
"""
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai.openai_client import OpenAIClient
from monitoring.cache_metrics import CacheMetrics

def test_metrics():
    """Test the updated metrics functionality"""
    print("🧪 Testing Updated CacheMetrics")
    print("=" * 50)

    # Initialize client
    client = OpenAIClient()
    
    # Test data
    test_messages = [
        [{"role": "user", "content": "Hello, how are you?"}],
        [{"role": "user", "content": "What's the weather today?"}],
        [{"role": "user", "content": "Hello, how are you?"}],  # Should be a cache hit
        [{"role": "user", "content": "Tell me a joke"}],
        [{"role": "user", "content": "Hello, how are you?"}],  # Another cache hit
    ]

    print("\n📡 Making test requests...")
    for i, messages in enumerate(test_messages, 1):
        try:
            start = time.perf_counter()
            response = client.chat_completion(
                messages=messages,
                model="gpt-3.5-turbo"
            )
            elapsed = time.perf_counter() - start
            print(f"  Request {i}: {messages[0]['content'][:30]}... | Time: {elapsed:.3f}s")
        except Exception as e:
            print(f"  ❌ Request {i} failed: {e}")
    
    # Get and display stats
    print("\n📊 Cache Statistics:")
    cache_stats = client.get_cache_stats()
    
    print(f"  Cache Hits: {cache_stats['cache_hits']}")
    print(f"  Cache Misses: {cache_stats['cache_misses']}")
    print(f"  Hit Rate: {cache_stats['performance']['hit_rate']:.1%}")
    print(f"  Avg Response Time: {cache_stats['performance']['avg_response_time']:.3f}s")
    print(f"  P90 Response Time: {cache_stats['performance']['p90_response_time']:.3f}s")
    print(f"  Memory Usage: {cache_stats['system']['current_memory_mb']:.1f} MB")
    
    # Verify metrics are being recorded
    assert cache_stats['cache_hits'] >= 2, "Expected at least 2 cache hits"
    assert cache_stats['cache_misses'] >= 2, "Expected at least 2 cache misses"
    assert cache_stats['performance']['avg_response_time'] > 0, "Response time should be positive"
    assert cache_stats['system']['current_memory_mb'] > 0, "Memory usage should be positive"
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_metrics()
