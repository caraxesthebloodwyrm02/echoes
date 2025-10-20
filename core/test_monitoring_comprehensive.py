# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Comprehensive tests for echoe-monitoring package."""

import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from monitoring.alerts import Alert, AlertManager
from monitoring.ci import CIBuild, CIMonitor
from monitoring.health import HealthCheck, HealthChecker
from monitoring.metrics import MetricsCollector, SystemMetrics

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestMetricsCollector:
    """Test system metrics collection."""

    def test_metrics_collector_initialization(self):
        """Test metrics collector can be initialized."""
        collector = MetricsCollector()
        assert collector is not None
        assert hasattr(collector, "logger")

    def test_collect_system_metrics(self):
        """Test collecting system metrics."""
        collector = MetricsCollector()
        metrics = collector.collect_system_metrics()

        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.disk_percent >= 0
        assert metrics.process_count > 0

    def test_system_metrics_dataclass(self):
        """Test SystemMetrics dataclass."""
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=45.5,
            memory_percent=60.2,
            disk_percent=70.0,
            network_bytes_sent=1000000,
            network_bytes_recv=2000000,
            process_count=150,
        )

        assert metrics.cpu_percent == 45.5
        assert metrics.memory_percent == 60.2
        assert metrics.process_count == 150

    def test_collect_metrics_multiple_times(self):
        """Test collecting metrics multiple times."""
        collector = MetricsCollector()

        metrics1 = collector.collect_system_metrics()
        time.sleep(0.1)
        metrics2 = collector.collect_system_metrics()

        assert metrics1.timestamp < metrics2.timestamp

    def test_collect_application_metrics_python(self):
        """Test collecting metrics for Python processes."""
        collector = MetricsCollector()
        metrics = collector.collect_application_metrics("python")

        assert "app_name" in metrics
        assert "timestamp" in metrics
        assert "process_count" in metrics
        assert metrics["app_name"] == "python"
        assert metrics["process_count"] >= 0

    def test_collect_application_metrics_nonexistent(self):
        """Test collecting metrics for nonexistent application."""
        collector = MetricsCollector()
        metrics = collector.collect_application_metrics("nonexistent_app_xyz")

        assert metrics["process_count"] == 0
        assert metrics["total_cpu_percent"] == 0.0

    def test_save_metrics_to_file(self):
        """Test saving metrics to file."""
        collector = MetricsCollector()
        metrics = collector.collect_system_metrics()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "metrics.json"
            collector.save_metrics(metrics, output_file)

            assert output_file.exists()

            import json

            with open(output_file) as f:
                data = json.load(f)

            assert "cpu_percent" in data
            assert "memory_percent" in data
            assert data["cpu_percent"] == metrics.cpu_percent

    def test_save_metrics_creates_directory(self):
        """Test that save_metrics creates parent directories."""
        collector = MetricsCollector()
        metrics = collector.collect_system_metrics()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "subdir" / "nested" / "metrics.json"
            collector.save_metrics(metrics, output_file)

            assert output_file.exists()

    def test_metrics_under_load(self):
        """Test metrics collection under simulated load."""
        collector = MetricsCollector()

        # Collect metrics multiple times quickly
        metrics_list = []
        for _ in range(10):
            metrics = collector.collect_system_metrics()
            metrics_list.append(metrics)

        assert len(metrics_list) == 10
        assert all(m.cpu_percent >= 0 for m in metrics_list)


class TestHealthChecker:
    """Test health checking functionality."""

    def test_health_checker_initialization(self):
        """Test health checker initialization."""
        health = HealthChecker()
        assert health is not None
        assert hasattr(health, "checks")

    def test_health_check_dataclass(self):
        """Test HealthCheck dataclass."""
        check = HealthCheck(
            name="test_check",
            status="healthy",
            message="All systems operational",
            timestamp=datetime.now(),
            response_time_ms=150.5,
        )

        assert check.name == "test_check"
        assert check.status == "healthy"
        assert check.response_time_ms == 150.5

    def test_register_check(self):
        """Test registering a health check."""
        health = HealthChecker()

        def custom_check():
            return HealthCheck(name="custom", status="healthy", message="OK", timestamp=datetime.now())

        health.register_check("custom", custom_check)
        assert "custom" in health.checks

    def test_check_url_unreachable(self):
        """Test checking unreachable URL."""
        health = HealthChecker()
        result = health.check_url("unreachable", "http://localhost:99999", timeout=1)

        assert result.name == "unreachable"
        assert result.status == "unhealthy"
        assert result.timestamp is not None

    def test_check_url_invalid(self):
        """Test checking invalid URL."""
        health = HealthChecker()
        result = health.check_url("invalid", "not-a-valid-url", timeout=1)

        assert result.status == "unhealthy"

    def test_check_disk_space(self):
        """Test disk space checking."""
        health = HealthChecker()
        result = health.check_disk_space("/", threshold_percent=95.0)

        assert result.name == "disk_space_/"
        assert result.status in ["healthy", "warning", "unhealthy"]
        assert "usage" in result.message.lower()

    def test_check_disk_space_high_threshold(self):
        """Test disk space with very high threshold."""
        health = HealthChecker()
        result = health.check_disk_space("/", threshold_percent=10.0)

        # Should warn/fail if disk is more than 10% used
        assert result.status in ["warning", "unhealthy"]

    def test_check_disk_space_low_threshold(self):
        """Test disk space with very low threshold."""
        health = HealthChecker()
        result = health.check_disk_space("/", threshold_percent=99.9)

        # Should be healthy unless disk is >99.9% full
        assert result.status in ["healthy", "warning"]

    def test_run_all_checks_empty(self):
        """Test running checks when none registered."""
        health = HealthChecker()
        results = health.run_all_checks()

        assert isinstance(results, list)
        assert len(results) == 0

    def test_run_all_checks_multiple(self):
        """Test running multiple registered checks."""
        health = HealthChecker()

        def check1():
            return HealthCheck("check1", "healthy", "OK", datetime.now())

        def check2():
            return HealthCheck("check2", "warning", "Slow", datetime.now())

        health.register_check("check1", check1)
        health.register_check("check2", check2)

        results = health.run_all_checks()

        assert len(results) == 2
        assert any(r.name == "check1" for r in results)
        assert any(r.name == "check2" for r in results)

    def test_run_checks_with_failure(self):
        """Test running checks when one fails."""
        health = HealthChecker()

        def failing_check():
            raise Exception("Check failed")

        def working_check():
            return HealthCheck("working", "healthy", "OK", datetime.now())

        health.register_check("failing", failing_check)
        health.register_check("working", working_check)

        results = health.run_all_checks()

        assert len(results) == 2
        failing_result = next(r for r in results if r.name == "failing")
        assert failing_result.status == "unhealthy"
        assert "error" in failing_result.message.lower()


class TestAlertManager:
    """Test alert management system."""

    def test_alert_manager_initialization(self):
        """Test alert manager initialization."""
        manager = AlertManager()
        assert manager is not None
        assert len(manager.alerts) == 0

    def test_alert_dataclass(self):
        """Test Alert dataclass."""
        alert = Alert(
            name="test_alert",
            severity="warning",
            message="Test message",
            timestamp=datetime.now(),
            metadata={"key": "value"},
        )

        assert alert.name == "test_alert"
        assert alert.severity == "warning"
        assert alert.metadata["key"] == "value"

    def test_create_alert(self):
        """Test creating and sending alert."""
        manager = AlertManager()

        alert = manager.create_alert(
            name="test",
            severity="info",
            message="Test alert",
            metadata={"source": "test"},
        )

        assert alert.name == "test"
        assert len(manager.alerts) == 1
        assert manager.alerts[0] == alert

    def test_create_multiple_alerts(self):
        """Test creating multiple alerts."""
        manager = AlertManager()

        for i in range(5):
            manager.create_alert(name=f"alert_{i}", severity="info", message=f"Message {i}")

        assert len(manager.alerts) == 5

    def test_register_handler(self):
        """Test registering alert handler."""
        manager = AlertManager()

        handled_alerts = []

        def handler(alert: Alert):
            handled_alerts.append(alert)

        manager.register_handler("test_handler", handler)

        manager.create_alert("test", "info", "Test")

        assert len(handled_alerts) == 1
        assert handled_alerts[0].name == "test"

    def test_multiple_handlers(self):
        """Test multiple alert handlers."""
        manager = AlertManager()

        handler1_calls = []
        handler2_calls = []

        manager.register_handler("handler1", lambda a: handler1_calls.append(a))
        manager.register_handler("handler2", lambda a: handler2_calls.append(a))

        manager.create_alert("test", "warning", "Test")

        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1

    def test_handler_failure_isolation(self):
        """Test that handler failures don't affect others."""
        manager = AlertManager()

        def failing_handler(alert):
            raise Exception("Handler failed")

        successful_calls = []

        def successful_handler(alert):
            successful_calls.append(alert)

        manager.register_handler("failing", failing_handler)
        manager.register_handler("successful", successful_handler)

        manager.create_alert("test", "error", "Test")

        # Successful handler should still run
        assert len(successful_calls) == 1

    def test_get_alerts_all(self):
        """Test getting all alerts."""
        manager = AlertManager()

        manager.create_alert("a1", "info", "Info alert")
        manager.create_alert("a2", "warning", "Warning alert")
        manager.create_alert("a3", "critical", "Critical alert")

        all_alerts = manager.get_alerts()
        assert len(all_alerts) == 3

    def test_get_alerts_by_severity(self):
        """Test filtering alerts by severity."""
        manager = AlertManager()

        manager.create_alert("a1", "info", "Info 1")
        manager.create_alert("a2", "warning", "Warning 1")
        manager.create_alert("a3", "info", "Info 2")
        manager.create_alert("a4", "critical", "Critical 1")

        info_alerts = manager.get_alerts(severity="info")
        warning_alerts = manager.get_alerts(severity="warning")
        critical_alerts = manager.get_alerts(severity="critical")

        assert len(info_alerts) == 2
        assert len(warning_alerts) == 1
        assert len(critical_alerts) == 1

    def test_alert_with_complex_metadata(self):
        """Test alerts with complex metadata."""
        manager = AlertManager()

        metadata = {
            "server": "web-01",
            "metrics": {"cpu": 95.5, "memory": 80.2},
            "tags": ["production", "critical"],
        }

        alert = manager.create_alert("high_load", "critical", "High system load", metadata=metadata)

        assert alert.metadata["server"] == "web-01"
        assert alert.metadata["metrics"]["cpu"] == 95.5
        assert "production" in alert.metadata["tags"]


class TestCIMonitor:
    """Test CI/CD monitoring."""

    def test_ci_monitor_initialization(self):
        """Test CI monitor initialization."""
        monitor = CIMonitor()
        assert monitor is not None
        assert len(monitor.builds) == 0

    def test_ci_build_dataclass(self):
        """Test CIBuild dataclass."""
        build = CIBuild(
            build_id="build-123",
            status="success",
            branch="main",
            commit="abc123",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_seconds=120.5,
        )

        assert build.build_id == "build-123"
        assert build.status == "success"
        assert build.duration_seconds == 120.5

    def test_add_build(self):
        """Test adding a build to monitoring."""
        monitor = CIMonitor()

        build = CIBuild(
            build_id="b1",
            status="running",
            branch="feature/test",
            commit="xyz789",
            started_at=datetime.now(),
            completed_at=None,
            duration_seconds=None,
        )

        monitor.add_build(build)
        assert len(monitor.builds) == 1
        assert monitor.builds[0].build_id == "b1"

    def test_add_multiple_builds(self):
        """Test adding multiple builds."""
        monitor = CIMonitor()

        for i in range(10):
            build = CIBuild(
                build_id=f"build-{i}",
                status="success" if i % 2 == 0 else "failed",
                branch="main",
                commit=f"commit{i}",
                started_at=datetime.now() - timedelta(hours=i),
                completed_at=datetime.now() - timedelta(hours=i, minutes=-5),
                duration_seconds=300.0,
            )
            monitor.add_build(build)

        assert len(monitor.builds) == 10


class TestMonitoringIntegration:
    """Integration tests for monitoring package."""

    def test_metrics_and_health_integration(self):
        """Test integrating metrics collection with health checks."""
        collector = MetricsCollector()
        health = HealthChecker()

        # Collect metrics
        metrics = collector.collect_system_metrics()

        # Create health check based on metrics
        def cpu_check():
            if metrics.cpu_percent > 90:
                return HealthCheck(
                    "cpu_health",
                    "warning",
                    f"High CPU usage: {metrics.cpu_percent}%",
                    datetime.now(),
                )
            return HealthCheck(
                "cpu_health",
                "healthy",
                f"CPU usage normal: {metrics.cpu_percent}%",
                datetime.now(),
            )

        health.register_check("cpu", cpu_check)
        results = health.run_all_checks()

        assert len(results) == 1
        assert results[0].name == "cpu_health"

    def test_health_to_alerts_workflow(self):
        """Test workflow from health checks to alerts."""
        health = HealthChecker()
        alerts = AlertManager()

        # Register a health check
        def failing_check():
            return HealthCheck("service", "unhealthy", "Service is down", datetime.now())

        health.register_check("service", failing_check)

        # Run checks and create alerts for failures
        results = health.run_all_checks()

        for result in results:
            if result.status == "unhealthy":
                alerts.create_alert(
                    name=f"health_check_{result.name}",
                    severity="critical",
                    message=result.message,
                    metadata={"check": result.name},
                )

        assert len(alerts.alerts) == 1
        assert alerts.alerts[0].severity == "critical"

    def test_complete_monitoring_pipeline(self):
        """Test complete monitoring pipeline."""
        # Initialize all components
        collector = MetricsCollector()
        health = HealthChecker()
        alerts = AlertManager()
        ci = CIMonitor()

        # Collect system metrics
        metrics = collector.collect_system_metrics()
        assert metrics.cpu_percent >= 0

        # Run health checks
        health.register_check("disk", lambda: health.check_disk_space("/", threshold_percent=90))
        health_results = health.run_all_checks()
        assert len(health_results) > 0

        # Create alerts for unhealthy checks
        alert_count = 0
        for result in health_results:
            if result.status in ["unhealthy", "warning"]:
                alerts.create_alert(
                    name=result.name,
                    severity="warning" if result.status == "warning" else "critical",
                    message=result.message,
                )
                alert_count += 1

        # Track CI build
        build = CIBuild(
            build_id="test-build",
            status="success",
            branch="main",
            commit="abc123",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            duration_seconds=180.0,
        )
        ci.add_build(build)

        # Verify pipeline worked
        assert metrics is not None
        assert len(health_results) > 0
        assert len(ci.builds) == 1

    def test_monitoring_with_persistence(self):
        """Test monitoring with file persistence."""
        collector = MetricsCollector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Collect and save metrics over time
            for i in range(5):
                metrics = collector.collect_system_metrics()
                output_file = Path(tmpdir) / f"metrics_{i}.json"
                collector.save_metrics(metrics, output_file)
                time.sleep(0.1)

            # Verify all files created
            files = list(Path(tmpdir).glob("metrics_*.json"))
            assert len(files) == 5

            # Verify data in files
            import json

            for file in files:
                with open(file) as f:
                    data = json.load(f)
                assert "cpu_percent" in data
                assert "timestamp" in data


class TestMonitoringPerformance:
    """Performance tests for monitoring."""

    def test_rapid_metrics_collection(self):
        """Test collecting metrics rapidly."""
        collector = MetricsCollector()

        start = time.time()
        for _ in range(100):
            collector.collect_system_metrics()
        duration = time.time() - start

        # Should complete in reasonable time
        assert duration < 30.0  # 100 collections in < 30 seconds

    def test_many_health_checks(self):
        """Test running many health checks."""
        health = HealthChecker()

        # Register many checks
        for i in range(50):
            health.register_check(
                f"check_{i}",
                lambda i=i: HealthCheck(f"check_{i}", "healthy", "OK", datetime.now()),
            )

        start = time.time()
        results = health.run_all_checks()
        duration = time.time() - start

        assert len(results) == 50
        assert duration < 5.0  # Should complete quickly

    def test_alert_handler_performance(self):
        """Test alert handling performance."""
        manager = AlertManager()

        call_count = [0]

        def handler(alert):
            call_count[0] += 1

        manager.register_handler("perf_handler", handler)

        # Create many alerts
        start = time.time()
        for i in range(1000):
            manager.create_alert(f"alert_{i}", "info", f"Message {i}")
        duration = time.time() - start

        assert len(manager.alerts) == 1000
        assert call_count[0] == 1000
        assert duration < 2.0  # Should be fast


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
