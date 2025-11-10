#!/usr/bin/env python3
"""
Test the OpenAI client with patterns from real user interactions.
"""
import asyncio
import random
import time
from typing import Dict, Any

from core.ai.openai_client import OpenAIClient

# Common patterns observed in the logs
COMMON_PATTERNS = [
    # Short greetings - using gpt-4-1106-preview which we saw in logs
    {"messages": [{"role": "user", "content": "Hello"}], "model": "gpt-4-1106-preview"},
    # Common questions - using gpt-3.5-turbo-1106 which is more cost-effective
    {"messages": [{"role": "user", "content": "What's the weather?"}], "model": "gpt-3.5-turbo-1106"},
    # Code-related questions
    {"messages": [{"role": "user", "content": "How do I fix this error?"}], "model": "gpt-4-1106-preview"},
    # General knowledge
    {"messages": [{"role": "user", "content": "Tell me about the capital of France"}], "model": "gpt-3.5-turbo-1106"},
    # System status
    {"messages": [{"role": "user", "content": "Are you working?"}], "model": "gpt-3.5-turbo-1106"},
]

class PatternTester:
    def __init__(self):
        self.client = OpenAIClient()
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "total_time": 0.0,
            "response_lengths": [],
            "response_times": [],
        }

    async def test_pattern(self, pattern: Dict[str, Any]) -> None:
        """Test a single conversation pattern."""
        start_time = time.time()
        
        try:
            # Make the API call
            _ = self.client.chat_completion(
                messages=pattern["messages"],
                model=pattern.get("model", "gpt-3.5-turbo-1106")
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update stats
            self.stats["total_requests"] += 1
            self.stats["total_time"] += response_time
            self.stats["response_times"].append(response_time)
            
            # Get cache stats
            cache_stats = self.client.get_cache_stats()
            self.stats["cache_hits"] = cache_stats["cache_hits"]
            
            # Log the result
            print(f"✅ Request {self.stats['total_requests']} - "
                  f"Time: {response_time:.3f}s - "
                  f"Cache: {'HIT' if cache_stats['cache_hits'] > self.stats['cache_hits'] - 1 else 'MISS'}")
            
        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f"❌ Error in pattern {pattern}: {str(e)}")

    def print_summary(self) -> None:
        """Print test summary."""
        print("\n📊 Test Summary")
        print("-" * 40)
        print(f"Total Requests: {self.stats['total_requests']}")
        print(f"Cache Hits: {self.stats['cache_hits']}")
        
        if self.stats['total_requests'] > 0:
            hit_rate = (self.stats['cache_hits'] / self.stats['total_requests']) * 100
            avg_time = self.stats['total_time'] / self.stats['total_requests']
            
            print(f"Cache Hit Rate: {hit_rate:.1f}%")
            print(f"Average Response Time: {avg_time:.3f}s")
            
            if self.stats['response_times']:
                sorted_times = sorted(self.stats['response_times'])
                p90 = sorted_times[int(len(sorted_times) * 0.9)]
                print(f"90th Percentile: {p90:.3f}s")
                print(f"Max Response Time: {max(self.stats['response_times']):.3f}s")

async def main():
    print("🚀 Testing with Real User Patterns\n")
    
    # Initialize tester
    tester = PatternTester()
    
    # Run multiple test iterations
    test_iterations = 10  # Test each pattern 10 times
    
    for i in range(test_iterations):
        print(f"\n🔄 Test Iteration {i + 1}/{test_iterations}")
        print("-" * 30)
        
        # Shuffle patterns to simulate random user behavior
        random.shuffle(COMMON_PATTERNS)
        
        # Test each pattern
        for pattern in COMMON_PATTERNS:
            await tester.test_pattern(pattern)
            
            # Small delay between requests to simulate real user behavior
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    # Print final summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
