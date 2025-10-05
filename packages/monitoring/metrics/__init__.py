"""System metrics collection and reporting."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import psutil

from packages.core import get_logger

logger = get_logger("monitoring.metrics")


@dataclass
class SystemMetrics:
    """System performance metrics."""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int


class MetricsCollector:
    """Collects system and application metrics."""

    def __init__(self) -> None:
        self.logger = logger
        self._baseline_network = psutil.net_io_counters()

    def collect_system_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics.

        Returns:
            SystemMetrics dataclass with current values
        """
        try:
            # Get current metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            network = psutil.net_io_counters()
            process_count = len(psutil.pids())

            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk.percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                process_count=process_count,
            )

            self.logger.debug(f"Collected metrics: CPU {cpu_percent}%, Memory {memory.percent}%")
            return metrics

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            # Return empty metrics on error
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                process_count=0,
            )

    def collect_application_metrics(self, app_name: str) -> Dict[str, Any]:
        """
        Collect application-specific metrics.

        Args:
            app_name: Name of the application to monitor

        Returns:
            Dictionary of application metrics
        """
        metrics = {
            "app_name": app_name,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Find processes matching app name
            matching_processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    if app_name.lower() in proc.info["name"].lower():
                        matching_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if matching_processes:
                total_cpu = sum(p["cpu_percent"] or 0 for p in matching_processes)
                total_memory = sum(p["memory_percent"] or 0 for p in matching_processes)

                metrics.update(
                    {
                        "process_count": len(matching_processes),
                        "total_cpu_percent": total_cpu,
                        "total_memory_percent": total_memory,
                        "processes": matching_processes,
                    }
                )
            else:
                metrics.update(
                    {
                        "process_count": 0,
                        "total_cpu_percent": 0.0,
                        "total_memory_percent": 0.0,
                        "processes": [],
                    }
                )

        except Exception as e:
            self.logger.error(f"Failed to collect app metrics for {app_name}: {e}")

        return metrics

    def save_metrics(self, metrics: SystemMetrics, output_file: Path) -> None:
        """
        Save metrics to file.

        Args:
            metrics: SystemMetrics to save
            output_file: Path to output file
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict for JSON serialization
            metrics_dict = {
                "timestamp": metrics.timestamp.isoformat(),
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "network_bytes_sent": metrics.network_bytes_sent,
                "network_bytes_recv": metrics.network_bytes_recv,
                "process_count": metrics.process_count,
            }

            import json

            with open(output_file, "w") as f:
                json.dump(metrics_dict, f, indent=2)

            self.logger.info(f"Metrics saved to {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")


__all__ = ["SystemMetrics", "MetricsCollector"]
