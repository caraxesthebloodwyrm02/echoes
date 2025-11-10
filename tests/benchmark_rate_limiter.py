"""
Benchmark script for testing the adaptive rate limiter under load.
"""
import asyncio
import os
import random
import statistics
import sys
import time
from typing import Any

try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

from datetime import datetime

# Add the parent directory to the path so we can import glimpse modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glimpse.rate_limiter import AdaptiveRateLimiter


class RateLimiterBenchmark:
    """Benchmark class for testing rate limiter performance."""

    def __init__(
        self, initial_rpm: int = 60, num_workers: int = 10, duration: int = 60
    ):
        """Initialize the benchmark."""
        self.rate_limiter = AdaptiveRateLimiter(
            initial_rpm=initial_rpm,
            initial_tpm=initial_rpm * 100,  # Rough estimate: 100 tokens per request
            min_rpm=10,
            max_rpm=120,
            min_tpm=1000,
            max_tpm=12000,
            burst_multiplier=1.5,
            adjustment_interval=5.0,  # Adjust more frequently for testing
            success_rate_target=0.95,
            history_size=20,
        )
        self.num_workers = num_workers
        self.duration = duration
        self.results = []
        self.metrics = {
            "successful_requests": 0,
            "rate_limited_requests": 0,
            "total_requests": 0,
            "response_times": [],
            "success_rates": [],
            "rpm_history": [],
            "timestamps": [],
        }

    async def worker(self, worker_id: int, stop_event: asyncio.Event):
        """Worker that makes requests to the rate limiter."""
        while not stop_event.is_set():
            start_time = time.time()

            # Simulate token usage (rough estimate: 100 tokens per request)
            token_count = random.randint(50, 150)

            # Try to acquire a token
            acquired, wait_time = await self.rate_limiter.acquire(
                endpoint="benchmark", token_count=token_count
            )

            if acquired:
                # Simulate API call with random latency (50-150ms)
                await asyncio.sleep(random.uniform(0.05, 0.15))

                # Randomly fail 5% of requests to test error handling
                if random.random() < 0.05:
                    await self.rate_limiter.record_error("benchmark")
                else:
                    await self.rate_limiter.record_success(
                        "benchmark", token_count=token_count
                    )

                # Record metrics
                self.metrics["successful_requests"] += 1
                self.metrics["response_times"].append(time.time() - start_time)

                # Record success rate and RPM every 10 successful requests
                if self.metrics["successful_requests"] % 10 == 0:
                    self._record_metrics()
            else:
                # Request was rate limited
                self.metrics["rate_limited_requests"] += 1
                await asyncio.sleep(wait_time)  # Wait before retrying

            self.metrics["total_requests"] += 1

            # Small sleep to prevent tight loops
            await asyncio.sleep(0.01)

    def _record_metrics(self):
        """Record current metrics."""
        status = self.rate_limiter.get_status()
        self.metrics["success_rates"].append(status["success_rate"])
        self.metrics["rpm_history"].append(self.rate_limiter.current_rpm)
        self.metrics["timestamps"].append(time.time())

    async def run(self):
        """Run the benchmark."""
        print(
            f"Starting benchmark with {self.num_workers} workers for {self.duration} seconds..."
        )
        start_time = time.time()
        stop_event = asyncio.Event()

        # Start workers
        workers = [
            asyncio.create_task(self.worker(i, stop_event))
            for i in range(self.num_workers)
        ]

        # Run for specified duration
        try:
            await asyncio.sleep(self.duration)
        finally:
            stop_event.set()
            await asyncio.gather(*workers, return_exceptions=True)

        # Final metrics
        end_time = time.time()
        total_time = end_time - start_time

        # Calculate statistics
        stats = {
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "rate_limited_requests": self.metrics["rate_limited_requests"],
            "request_rate": self.metrics["total_requests"] / total_time,
            "success_rate": (
                self.metrics["successful_requests"]
                / (
                    self.metrics["successful_requests"]
                    + self.metrics["rate_limited_requests"]
                )
                if (
                    self.metrics["successful_requests"]
                    + self.metrics["rate_limited_requests"]
                )
                > 0
                else 0
            ),
            "avg_response_time": (
                statistics.mean(self.metrics["response_times"])
                if self.metrics["response_times"]
                else 0
            ),
            "p95_response_time": (
                statistics.quantiles(self.metrics["response_times"], n=20)[-1]
                if len(self.metrics["response_times"]) > 1
                else 0
            ),
            "final_rpm": self.rate_limiter.current_rpm,
            "max_rpm": max(self.metrics["rpm_history"])
            if self.metrics["rpm_history"]
            else 0,
            "min_rpm": min(self.metrics["rpm_history"])
            if self.metrics["rpm_history"]
            else 0,
        }

        return stats, self.metrics

    def plot_results(self, metrics: dict[str, Any], output_file: str = None):
        """Plot benchmark results."""
        if not metrics["timestamps"]:
            print("No metrics to plot")
            return

        # Normalize timestamps to start from 0
        start_time = metrics["timestamps"][0]
        x = [t - start_time for t in metrics["timestamps"]]

        # Create figure with 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
        fig.suptitle("Rate Limiter Performance")

        # Plot 1: Requests per minute and success rate
        ax1.plot(x, metrics["rpm_history"], "b-", label="RPM")
        ax1.set_ylabel("Requests per Minute")
        ax1.set_ylim(0, max(metrics["rpm_history"] or [0]) * 1.2)
        ax1.grid(True)

        # Add success rate on secondary y-axis
        ax1b = ax1.twinx()
        ax1b.plot(x, metrics["success_rates"], "r--", label="Success Rate")
        ax1b.set_ylabel("Success Rate", color="r")
        ax1b.tick_params(axis="y", labelcolor="r")
        ax1b.set_ylim(0, 1.1)

        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1b.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        # Plot 2: Response times (moving average)
        if len(metrics["response_times"]) > 10:
            window_size = max(5, len(metrics["response_times"]) // 20)
            moving_avg = [
                statistics.mean(
                    metrics["response_times"][max(0, i - window_size) : i + 1]
                )
                for i in range(len(metrics["response_times"]))
            ]
            ax2.plot(moving_avg, "g-", label=f"Moving Avg (window={window_size})")

        ax2.set_xlabel("Request Number")
        ax2.set_ylabel("Response Time (s)")
        ax2.set_title("Response Times")
        ax2.grid(True)
        ax2.legend()

        # Plot 3: Request rate over time (rolling window)
        if x:
            window_seconds = 5  # 5-second window for request rate
            request_rates = []
            for t in x:
                # Count requests in the last window_seconds
                count = sum(1 for req_t in x if t - window_seconds <= req_t <= t)
                request_rates.append(count / window_seconds)  # requests per second

            ax3.plot(
                x, request_rates, "m-", label=f"Requests/s (rolling {window_seconds}s)"
            )
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel("Request Rate (req/s)")
            ax3.set_title("Request Rate Over Time")
            ax3.grid(True)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
            print(f"Plot saved to {output_file}")
        else:
            plt.show()


async def main():
    """Run the benchmark and display results."""
    # Run benchmark
    benchmark = RateLimiterBenchmark(
        initial_rpm=60,  # Start with 1 request per second
        num_workers=20,  # Number of concurrent workers
        duration=300,  # Run for 5 minutes
    )

    stats, metrics = await benchmark.run()

    # Print summary
    print("\n=== Benchmark Results ===")
    print(f"Duration:           {benchmark.duration:.1f} seconds")
    print(f"Total Requests:     {stats['total_requests']}")
    print(
        f"Successful:         {stats['successful_requests']} ({stats['success_rate']:.1%})"
    )
    print(f"Rate Limited:       {stats['rate_limited_requests']}")
    print(f"Request Rate:       {stats['request_rate']:.1f} req/s")
    print(f"Avg Response Time:  {stats['avg_response_time']*1000:.1f} ms")
    print(f"P95 Response Time:  {stats['p95_response_time']*1000:.1f} ms")
    print(f"Final RPM:          {stats['final_rpm']:.1f}")
    print(f"Min/Max RPM:        {stats['min_rpm']:.1f} / {stats['max_rpm']:.1f}")

    # Plot results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"rate_limiter_benchmark_{timestamp}.png"
    benchmark.plot_results(metrics, output_file)


if __name__ == "__main__":
    asyncio.run(main())
