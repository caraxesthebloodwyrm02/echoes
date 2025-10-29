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

"""Continuous monitoring system for codebase health and performance benchmarks.

Implements monitoring tools that track performance against established benchmarks,
following trajectory log patterns for ecosystem monitoring and detector validation.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from detectors import DetectorManager
from Q4.drucker_management import EcosystemManager


@dataclass
class BenchmarkResult:
    """Result of a benchmark measurement."""

    metric_name: str
    value: float
    timestamp: datetime
    threshold: Optional[float] = None
    status: str = "ok"  # ok, warning, critical
    details: Optional[Dict[str, Any]] = None


@dataclass
class MonitoringReport:
    """Comprehensive monitoring report."""

    timestamp: datetime
    ecosystem_health: Dict[str, Any]
    detector_metrics: Dict[str, Any]
    benchmark_results: List[BenchmarkResult]
    recommendations: List[str]


class ContinuousMonitor:
    """Continuous monitoring system tracking performance against trajectory benchmarks."""

    def __init__(self, root_path: str = ".", log_path: str = "logs/monitoring.log"):
        self.root_path = Path(root_path)
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(exist_ok=True)

        # Initialize components
        self.ecosystem_manager = EcosystemManager(root_path)
        self.detector_manager = DetectorManager()

        # Setup logging
        self.logger = logging.getLogger("continuous_monitor")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_path)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

        # Benchmark thresholds (established from trajectory analysis)
        self.benchmarks = {
            "complexity_score": {"warning": 10.0, "critical": 20.0},
            "communication_issues": {"warning": 1, "critical": 3},
            "detector_false_positives": {"warning": 0.1, "critical": 0.3},
            "gate_failures": {"warning": 1, "critical": 3},
            "test_coverage": {"warning": 80.0, "critical": 70.0},
        }

    def run_monitoring_cycle(self) -> MonitoringReport:
        """Run a complete monitoring cycle."""

        self.logger.info("Starting monitoring cycle")

        # Gather ecosystem health
        ecosystem_health = self._assess_ecosystem_health()

        # Gather detector metrics
        detector_metrics = self._assess_detector_performance()

        # Run benchmark checks
        benchmark_results = self._run_benchmarks()

        # Generate recommendations
        recommendations = self._generate_recommendations(ecosystem_health, detector_metrics, benchmark_results)

        report = MonitoringReport(
            timestamp=datetime.now(),
            ecosystem_health=ecosystem_health,
            detector_metrics=detector_metrics,
            benchmark_results=benchmark_results,
            recommendations=recommendations,
        )

        self.logger.info(f"Monitoring cycle complete. Status: {self._overall_status(benchmark_results)}")

        return report

    def _assess_ecosystem_health(self) -> Dict[str, Any]:
        """Assess overall ecosystem health using trajectory patterns."""

        # Track terraforming
        terraforming = self.ecosystem_manager.track_terraforming()

        # Validate communications
        communications = self.ecosystem_manager.validate_communication_wirings()

        # Check GATE status
        gate_status = self.ecosystem_manager.operate_gate()

        # Check endpoint vulnerabilities
        vulnerabilities = self.ecosystem_manager._check_endpoint_vulnerabilities()

        return {
            "terraforming": {
                "roots": terraforming.roots,
                "branches": terraforming.branches,
                "leaves": terraforming.leaves,
                "complexity_score": terraforming.complexity_score,
                "timestamp": terraforming.timestamp.isoformat(),
            },
            "communications": communications,
            "gate_status": gate_status,
            "vulnerabilities": vulnerabilities,
            "overall_health": self._calculate_ecosystem_score(
                terraforming, communications, gate_status, vulnerabilities
            ),
        }

    def _assess_detector_performance(self) -> Dict[str, Any]:
        """Assess detector system performance."""

        all_metrics = self.detector_manager.get_all_metrics()

        # Aggregate metrics across all detectors
        aggregated = {
            "total_detectors": len(all_metrics),
            "active_detectors": sum(1 for m in all_metrics.values() if m.get("total_detections", 0) > 0),
            "total_detections": sum(m.get("total_detections", 0) for m in all_metrics.values()),
            "shadow_mode_detectors": sum(1 for m in all_metrics.values() if m.get("shadow_mode_active", False)),
            "by_tier": {},
            "false_positive_rate": 0.0,  # Would need manual labeling
            "average_confidence": 0.0,
        }

        # Aggregate by tier
        all_tiers = {}
        total_confidence = 0
        confidence_count = 0

        for detector_metrics in all_metrics.values():
            for tier, count in detector_metrics.get("by_tier", {}).items():
                all_tiers[tier] = all_tiers.get(tier, 0) + count

            # Calculate average confidence (simplified)
            detections = detector_metrics.get("total_detections", 0)
            if detections > 0:
                # Estimate confidence - in practice would track actual values
                total_confidence += 0.8 * detections  # Placeholder
                confidence_count += detections

        aggregated["by_tier"] = all_tiers
        if confidence_count > 0:
            aggregated["average_confidence"] = total_confidence / confidence_count

        return aggregated

    def _run_benchmarks(self) -> List[BenchmarkResult]:
        """Run benchmark checks against established thresholds."""

        results = []

        # Complexity benchmark
        ecosystem = self._assess_ecosystem_health()
        complexity = ecosystem["terraforming"]["complexity_score"]
        results.append(self._check_benchmark("complexity_score", complexity, self.benchmarks["complexity_score"]))

        # Communication issues benchmark
        comm_issues = len(ecosystem["communications"].get("issues", []))
        results.append(
            self._check_benchmark(
                "communication_issues",
                comm_issues,
                self.benchmarks["communication_issues"],
            )
        )

        # GATE failures benchmark
        gate_failures = 1 if ecosystem["gate_status"]["gate_status"] == "closed" else 0
        results.append(self._check_benchmark("gate_failures", gate_failures, self.benchmarks["gate_failures"]))

        # Detector false positives (placeholder - would need real labeling)
        detector_metrics = self._assess_detector_performance()
        fp_rate = detector_metrics.get("false_positive_rate", 0.05)  # Placeholder
        results.append(
            self._check_benchmark(
                "detector_false_positives",
                fp_rate,
                self.benchmarks["detector_false_positives"],
            )
        )

        # Test coverage (placeholder - would integrate with coverage tools)
        coverage = self._estimate_test_coverage()
        results.append(self._check_benchmark("test_coverage", coverage, self.benchmarks["test_coverage"]))

        return results

    def _check_benchmark(self, metric_name: str, value: float, thresholds: Dict[str, float]) -> BenchmarkResult:
        """Check a metric against its thresholds."""

        if value >= thresholds.get("critical", float("inf")):
            status = "critical"
        elif value >= thresholds.get("warning", float("inf")):
            status = "warning"
        else:
            status = "ok"

        return BenchmarkResult(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            threshold=thresholds.get("warning"),
            status=status,
        )

    def _generate_recommendations(
        self, ecosystem: Dict, detectors: Dict, benchmarks: List[BenchmarkResult]
    ) -> List[str]:
        """Generate recommendations based on monitoring results."""

        recommendations = []

        # Ecosystem recommendations
        if ecosystem["terraforming"]["complexity_score"] > 15:
            recommendations.append("High code complexity detected. Consider refactoring complex modules.")

        if not ecosystem["communications"]["healthy"]:
            recommendations.append("Communication issues found. Review import dependencies and API coherence.")

        if ecosystem["gate_status"]["gate_status"] == "closed":
            recommendations.append("GATE validation failed. Address security, quality, or dependency issues.")

        # Detector recommendations
        if detectors["total_detections"] == 0:
            recommendations.append("No detector activity detected. Verify detector configuration and inputs.")

        shadow_count = detectors.get("shadow_mode_detectors", 0)
        if shadow_count > 0:
            recommendations.append(
                f"{shadow_count} detectors in shadow mode. Monitor performance before enabling live mode."
            )

        # Benchmark recommendations
        critical_benchmarks = [b for b in benchmarks if b.status == "critical"]
        if critical_benchmarks:
            recommendations.append(
                f"Critical benchmark failures: {', '.join(b.metric_name for b in critical_benchmarks)}"
            )

        warning_benchmarks = [b for b in benchmarks if b.status == "warning"]
        if warning_benchmarks:
            recommendations.append(
                f"Warning benchmark thresholds exceeded: {', '.join(b.metric_name for b in warning_benchmarks)}"
            )

        if not recommendations:
            recommendations.append("All systems operating within normal parameters. Continue monitoring.")

        return recommendations

    def _calculate_ecosystem_score(self, terraforming, communications, gate_status, vulnerabilities) -> float:
        """Calculate overall ecosystem health score (0-100)."""

        score = 100.0

        # Complexity penalty
        if terraforming.complexity_score > 10:
            score -= min(20, (terraforming.complexity_score - 10) * 2)

        # Communication penalty
        if not communications["healthy"]:
            score -= 15

        # GATE penalty
        if gate_status["gate_status"] == "closed":
            score -= 25

        # Vulnerability penalty
        if not vulnerabilities["passed"]:
            score -= 10

        return max(0, score)

    def _estimate_test_coverage(self) -> float:
        """Estimate test coverage (placeholder - would integrate with coverage tools)."""
        # In practice, this would read from coverage.xml or similar
        # For now, return a placeholder based on test file count
        test_files = list(self.root_path.glob("tests/test_*.py"))
        total_files = list(self.root_path.glob("**/*.py"))
        total_files = [f for f in total_files if not str(f).startswith(str(self.root_path / "tests"))]

        if not total_files:
            return 0.0

        # Rough estimate: assume each test file covers ~5 source files
        estimated_coverage = min(95.0, (len(test_files) * 5 / len(total_files)) * 100)
        return estimated_coverage

    def _overall_status(self, benchmarks: List[BenchmarkResult]) -> str:
        """Determine overall system status from benchmarks."""

        if any(b.status == "critical" for b in benchmarks):
            return "critical"
        elif any(b.status == "warning" for b in benchmarks):
            return "warning"
        else:
            return "healthy"

    def start_continuous_monitoring(self, interval_minutes: int = 60):
        """Start continuous monitoring with specified interval."""

        self.logger.info(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")

        while True:
            try:
                report = self.run_monitoring_cycle()

                # Log summary
                status = self._overall_status(report.benchmark_results)
                self.logger.info(f"Monitoring cycle complete - Status: {status}")

                # Save detailed report
                self._save_report(report)

            except Exception as e:
                self.logger.error(f"Monitoring cycle failed: {e}")

            # Wait for next cycle
            time.sleep(interval_minutes * 60)

    def _save_report(self, report: MonitoringReport):
        """Save monitoring report to file."""

        report_path = self.log_path.parent / f"monitoring_report_{report.timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        report_data = {
            "timestamp": report.timestamp.isoformat(),
            "ecosystem_health": report.ecosystem_health,
            "detector_metrics": report.detector_metrics,
            "benchmark_results": [
                {
                    "metric_name": b.metric_name,
                    "value": b.value,
                    "status": b.status,
                    "threshold": b.threshold,
                    "timestamp": b.timestamp.isoformat(),
                    "details": b.details,
                }
                for b in report.benchmark_results
            ],
            "recommendations": report.recommendations,
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        self.logger.info(f"Report saved to {report_path}")


# Convenience functions for external use
def run_monitoring_cycle(root_path: str = ".") -> MonitoringReport:
    """Run a single monitoring cycle."""
    monitor = ContinuousMonitor(root_path)
    return monitor.run_monitoring_cycle()


def start_continuous_monitoring(root_path: str = ".", interval_minutes: int = 60):
    """Start continuous monitoring."""
    monitor = ContinuousMonitor(root_path)
    monitor.start_continuous_monitoring(interval_minutes)
