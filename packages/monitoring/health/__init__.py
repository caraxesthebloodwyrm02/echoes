"""Health checking and status monitoring."""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

import requests

from packages.core import get_logger

logger = get_logger("monitoring.health")


@dataclass
class HealthCheck:
    """Health check result."""

    name: str
    status: str  # "healthy", "unhealthy", "warning"
    message: str
    timestamp: datetime
    response_time_ms: Optional[float] = None


class HealthChecker:
    """Performs health checks on system components."""

    def __init__(self) -> None:
        self.logger = logger
        self.checks: Dict[str, Callable[[], HealthCheck]] = {}

    def register_check(self, name: str, check_func: Callable[[], HealthCheck]) -> None:
        """
        Register a health check function.

        Args:
            name: Name of the health check
            check_func: Function that returns HealthCheck result
        """
        self.checks[name] = check_func
        self.logger.info(f"Registered health check: {name}")

    def check_url(self, name: str, url: str, timeout: int = 10) -> HealthCheck:
        """
        Check if a URL is accessible.

        Args:
            name: Name for this check
            url: URL to check
            timeout: Request timeout in seconds

        Returns:
            HealthCheck result
        """
        start_time = datetime.now()

        try:
            response = requests.get(url, timeout=timeout)
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return HealthCheck(
                    name=name,
                    status="healthy",
                    message=f"URL accessible (status: {response.status_code})",
                    timestamp=end_time,
                    response_time_ms=response_time,
                )
            else:
                return HealthCheck(
                    name=name,
                    status="warning",
                    message=f"URL returned status: {response.status_code}",
                    timestamp=end_time,
                    response_time_ms=response_time,
                )

        except requests.RequestException as e:
            return HealthCheck(
                name=name,
                status="unhealthy",
                message=f"URL not accessible: {str(e)}",
                timestamp=datetime.now(),
            )

    def check_service(self, name: str, service_name: str) -> HealthCheck:
        """
        Check if a system service is running.

        Args:
            name: Name for this check
            service_name: Name of the service to check

        Returns:
            HealthCheck result
        """
        try:
            # Try Windows service check first
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and "RUNNING" in result.stdout:
                return HealthCheck(
                    name=name,
                    status="healthy",
                    message=f"Service {service_name} is running",
                    timestamp=datetime.now(),
                )
            else:
                return HealthCheck(
                    name=name,
                    status="unhealthy",
                    message=f"Service {service_name} is not running",
                    timestamp=datetime.now(),
                )

        except (subprocess.SubprocessError, FileNotFoundError):
            # Try systemd (Linux) as fallback
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service_name],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0 and result.stdout.strip() == "active":
                    return HealthCheck(
                        name=name,
                        status="healthy",
                        message=f"Service {service_name} is active",
                        timestamp=datetime.now(),
                    )
                else:
                    return HealthCheck(
                        name=name,
                        status="unhealthy",
                        message=f"Service {service_name} is not active",
                        timestamp=datetime.now(),
                    )

            except (subprocess.SubprocessError, FileNotFoundError):
                return HealthCheck(
                    name=name,
                    status="warning",
                    message=f"Unable to check service {service_name} (no service manager found)",
                    timestamp=datetime.now(),
                )

    def check_disk_space(self, path: str, threshold_percent: float = 90.0) -> HealthCheck:
        """
        Check disk space usage.

        Args:
            path: Path to check disk usage for
            threshold_percent: Alert threshold percentage

        Returns:
            HealthCheck result
        """
        try:
            import shutil

            total, used, free = shutil.disk_usage(path)
            usage_percent = (used / total) * 100

            if usage_percent < threshold_percent:
                status = "healthy"
                message = (
                    f"Disk usage at {usage_percent:.1f}% (below {threshold_percent}% threshold)"
                )
            else:
                status = "warning" if usage_percent < 95.0 else "unhealthy"
                message = (
                    f"Disk usage at {usage_percent:.1f}% (above {threshold_percent}% threshold)"
                )

            return HealthCheck(
                name=f"disk_space_{path}", status=status, message=message, timestamp=datetime.now()
            )

        except Exception as e:
            return HealthCheck(
                name=f"disk_space_{path}",
                status="unhealthy",
                message=f"Failed to check disk space: {str(e)}",
                timestamp=datetime.now(),
            )

    def run_all_checks(self) -> List[HealthCheck]:
        """
        Run all registered health checks.

        Returns:
            List of HealthCheck results
        """
        results = []

        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results.append(result)
                self.logger.info(f"Health check '{name}': {result.status}")
            except Exception as e:
                error_result = HealthCheck(
                    name=name,
                    status="unhealthy",
                    message=f"Check failed with error: {str(e)}",
                    timestamp=datetime.now(),
                )
                results.append(error_result)
                self.logger.error(f"Health check '{name}' failed: {e}")

        return results


__all__ = ["HealthCheck", "HealthChecker"]
