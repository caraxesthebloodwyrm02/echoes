#!/usr/bin/env python3
"""
Performance Monitor for Model Evaluation

Monitors system resources and model performance during evaluation runs.
Provides real-time metrics and bottleneck detection.
"""

import time
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json
import logging
from collections import defaultdict
import GPUtil

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor system performance during model evaluation"""

    def __init__(self, output_file: Path, interval: float = 1.0):
        self.output_file = output_file
        self.interval = interval
        self.monitoring = False
        self.metrics: List[Dict[str, Any]] = []
        self.start_time = None
        self.thread = None
        self.lock = threading.Lock()

    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring and save results"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=2.0)

        # Save metrics
        self._save_metrics()
        logger.info(f"Performance monitoring stopped. Metrics saved to {self.output_file}")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                with self.lock:
                    self.metrics.append(metrics)
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                break

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system and GPU metrics"""
        timestamp = time.time()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()

        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk metrics
        disk = psutil.disk_usage("/")

        # Network metrics
        network = psutil.net_io_counters()

        # GPU metrics (if available)
        gpu_metrics = {}
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                gpu_metrics = {
                    "gpu_load": gpu.load * 100,
                    "gpu_memory_used": gpu.memoryUsed,
                    "gpu_memory_total": gpu.memoryTotal,
                    "gpu_memory_free": gpu.memoryFree,
                    "gpu_temperature": gpu.temperature,
                }
        except Exception as e:
            logger.debug(f"GPU metrics unavailable: {e}")

        # Process metrics (Ollama if running)
        ollama_metrics = {}
        try:
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                if "ollama" in proc.info["name"].lower():
                    ollama_metrics = {
                        "pid": proc.info["pid"],
                        "cpu_percent": proc.info["cpu_percent"],
                        "memory_percent": proc.info["memory_percent"],
                    }
                    break
        except Exception as e:
            logger.debug(f"Ollama process metrics unavailable: {e}")

        return {
            "timestamp": timestamp,
            "elapsed_time": timestamp - self.start_time,
            "cpu": {"percent": cpu_percent, "frequency": cpu_freq.current if cpu_freq else None},
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
            },
            "swap": {"total": swap.total, "used": swap.used, "percent": swap.percent},
            "disk": {"total": disk.total, "used": disk.used, "free": disk.free, "percent": disk.percent},
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
            "gpu": gpu_metrics,
            "ollama_process": ollama_metrics,
        }

    def _save_metrics(self):
        """Save collected metrics to file"""
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "monitoring_start": self.start_time,
                        "monitoring_duration": time.time() - self.start_time,
                        "interval_seconds": self.interval,
                        "total_samples": len(self.metrics),
                        "metrics": self.metrics,
                    },
                    f,
                    indent=2,
                    default=str,
                )

        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from collected metrics"""
        if not self.metrics:
            return {}

        with self.lock:
            metrics = self.metrics.copy()

        # Calculate averages and peaks
        summary = {
            "total_samples": len(metrics),
            "duration": metrics[-1]["elapsed_time"] - metrics[0]["elapsed_time"] if metrics else 0,
            "cpu": {
                "avg_percent": sum(m["cpu"]["percent"] for m in metrics) / len(metrics),
                "max_percent": max(m["cpu"]["percent"] for m in metrics),
            },
            "memory": {
                "avg_percent": sum(m["memory"]["percent"] for m in metrics) / len(metrics),
                "max_percent": max(m["memory"]["percent"] for m in metrics),
            },
            "gpu": {},
        }

        # GPU stats if available
        gpu_loads = [m["gpu"].get("gpu_load", 0) for m in metrics if m["gpu"]]
        if gpu_loads:
            summary["gpu"] = {"avg_load": sum(gpu_loads) / len(gpu_loads), "max_load": max(gpu_loads)}

        return summary


class ModelPerformanceTracker:
    """Track model-specific performance metrics"""

    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.model_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.lock = threading.Lock()

    def record_request(
        self,
        model: str,
        prompt_length: int,
        response_length: int,
        response_time: float,
        success: bool,
        error: str = None,
    ):
        """Record a model request"""
        with self.lock:
            self.model_metrics[model].append(
                {
                    "timestamp": time.time(),
                    "prompt_length": prompt_length,
                    "response_length": response_length,
                    "response_time": response_time,
                    "success": success,
                    "error": error,
                    "tokens_per_second": response_length / response_time if response_time > 0 else 0,
                }
            )

    def save_metrics(self):
        """Save model performance metrics"""
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

            # Calculate summary stats per model
            summary = {}
            for model, metrics in self.model_metrics.items():
                if metrics:
                    successful = [m for m in metrics if m["success"]]
                    summary[model] = {
                        "total_requests": len(metrics),
                        "successful_requests": len(successful),
                        "success_rate": len(successful) / len(metrics),
                        "avg_response_time": (
                            sum(m["response_time"] for m in successful) / len(successful) if successful else 0
                        ),
                        "avg_tokens_per_second": (
                            sum(m["tokens_per_second"] for m in successful) / len(successful) if successful else 0
                        ),
                        "total_tokens_generated": sum(m["response_length"] for m in successful),
                        "requests": metrics,
                    }

            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"Model performance metrics saved to {self.output_file}")

        except Exception as e:
            logger.error(f"Failed to save model metrics: {e}")


def monitor_evaluation_run(evaluation_script: str, *args):
    """Monitor a complete evaluation run"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Setup monitoring
    system_metrics_file = Path(f"performance_metrics_{timestamp}.json")
    model_metrics_file = Path(f"model_performance_{timestamp}.json")

    system_monitor = PerformanceMonitor(system_metrics_file, interval=2.0)
    model_tracker = ModelPerformanceTracker(model_metrics_file)

    try:
        # Start monitoring
        system_monitor.start_monitoring()
        logger.info("🚀 Starting monitored evaluation run")

        # Run the evaluation (this would need to be integrated with the actual evaluation)
        # For now, just simulate monitoring
        time.sleep(10)  # Simulate evaluation time

        # Stop monitoring
        system_monitor.stop_monitoring()
        model_tracker.save_metrics()

        # Print summary
        summary = system_monitor.get_summary_stats()
        print("\n📊 Performance Summary:")
        print(f"Duration: {summary.get('duration', 0):.1f}s")
        print(f"Samples: {summary.get('total_samples', 0)}")
        print(
            f"CPU Avg/Max: {summary.get('cpu', {}).get('avg_percent', 0):.1f}% / {summary.get('cpu', {}).get('max_percent', 0):.1f}%"
        )
        print(
            f"Memory Avg/Max: {summary.get('memory', {}).get('avg_percent', 0):.1f}% / {summary.get('memory', {}).get('max_percent', 0):.1f}%"
        )

        if summary.get("gpu"):
            print(
                f"GPU Avg/Max Load: {summary['gpu'].get('avg_load', 0):.1f}% / {summary['gpu'].get('max_load', 0):.1f}%"
            )

    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
        system_monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        system_monitor.stop_monitoring()
        raise


if __name__ == "__main__":
    # Example usage
    monitor_evaluation_run("expanded_evaluation_suite.py")
