"""
Metrics System for Echoes Assistant
Tracks performance metrics, usage statistics, and system health
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time"""
    timestamp: datetime
    metrics: Dict[str, Any]
    tags: Dict[str, str] = field(default_factory=dict)

class ModelMetrics:
    """
    Tracks performance metrics for the Echoes assistant system.
    Monitors response times, error rates, usage patterns, and system health.
    """

    def __init__(self):
        self.metrics: Dict[str, Any] = defaultdict(int)
        self.snapshots: List[MetricSnapshot] = []
        self.logger = logging.getLogger(__name__)

    def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter metric

        Args:
            metric_name: Name of the metric
            value: Value to increment by
            tags: Optional tags for categorization
        """
        self.metrics[metric_name] += value
        self.logger.debug(f"Incremented {metric_name} by {value}")

    def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge metric (current value)

        Args:
            metric_name: Name of the metric
            value: Current value
            tags: Optional tags for categorization
        """
        self.metrics[metric_name] = value
        self.logger.debug(f"Set gauge {metric_name} to {value}")

    def timing(self, metric_name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a timing metric

        Args:
            metric_name: Name of the metric
            duration: Duration in seconds
            tags: Optional tags for categorization
        """
        self.metrics[f"{metric_name}_total"] += duration
        self.metrics[f"{metric_name}_count"] += 1

        # Calculate average
        total = self.metrics[f"{metric_name}_total"]
        count = self.metrics[f"{metric_name}_count"]
        self.metrics[f"{metric_name}_avg"] = total / count

        self.logger.debug(f"Recorded timing {metric_name}: {duration:.3f}s")

    def snapshot(self, tags: Optional[Dict[str, str]] = None) -> MetricSnapshot:
        """
        Take a snapshot of current metrics

        Args:
            tags: Optional tags for the snapshot

        Returns:
            MetricSnapshot object
        """
        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            metrics=dict(self.metrics),
            tags=tags or {}
        )
        self.snapshots.append(snapshot)
        self.logger.debug("Created metrics snapshot")
        return snapshot

    def get_metric(self, metric_name: str) -> Any:
        """
        Get the value of a specific metric

        Args:
            metric_name: Name of the metric

        Returns:
            Metric value
        """
        return self.metrics.get(metric_name, 0)

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all current metrics

        Returns:
            Dictionary of all metrics
        """
        return dict(self.metrics)

    def reset_metric(self, metric_name: str):
        """
        Reset a specific metric to zero

        Args:
            metric_name: Name of the metric to reset
        """
        if metric_name in self.metrics:
            self.metrics[metric_name] = 0
            self.logger.debug(f"Reset metric: {metric_name}")

    def reset_all(self):
        """Reset all metrics to zero"""
        self.metrics.clear()
        self.logger.debug("Reset all metrics")

    def get_recent_snapshots(self, count: int = 5) -> List[MetricSnapshot]:
        """
        Get recent metric snapshots

        Args:
            count: Number of recent snapshots to return

        Returns:
            List of recent snapshots
        """
        return self.snapshots[-count:] if self.snapshots else []

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of performance metrics

        Returns:
            Dictionary with performance summary
        """
        summary = {
            "total_requests": self.get_metric("requests_total"),
            "error_rate": 0.0,
            "avg_response_time": self.get_metric("response_time_avg"),
            "cache_hit_rate": 0.0,
            "uptime_seconds": self.get_metric("uptime_seconds")
        }

        # Calculate error rate
        total_errors = self.get_metric("errors_total")
        total_requests = self.get_metric("requests_total")
        if total_requests > 0:
            summary["error_rate"] = total_errors / total_requests

        # Calculate cache hit rate
        cache_hits = self.get_metric("cache_hits")
        cache_misses = self.get_metric("cache_misses")
        total_cache = cache_hits + cache_misses
        if total_cache > 0:
            summary["cache_hit_rate"] = cache_hits / total_cache

        return summary

# Global instance for easy access
model_metrics = ModelMetrics()

# Convenience functions for timing
def start_timer():
    """Start a timer for performance measurement"""
    return time.time()

def end_timer(start_time: float, metric_name: str = "operation"):
    """End a timer and record the duration"""
    duration = time.time() - start_time
    model_metrics.timing(metric_name, duration)
    return duration
