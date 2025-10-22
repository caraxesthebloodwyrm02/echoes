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

"""Feedback mechanism system for gathering insights on refactoring effectiveness.

Implements feedback loops that analyze monitoring data, user input, and performance
metrics to provide continuous improvement recommendations based on trajectory patterns.
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from monitoring.continuous_monitor import BenchmarkResult, MonitoringReport


@dataclass
class FeedbackEntry:
    """Individual feedback entry from monitoring or user input."""

    timestamp: datetime
    source: str  # "monitoring", "user", "test_failure", etc.
    category: str  # "performance", "reliability", "usability", etc.
    severity: str  # "low", "medium", "high", "critical"
    title: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class FeedbackAnalysis:
    """Analysis of feedback patterns and trends."""

    period_start: datetime
    period_end: datetime
    total_entries: int
    entries_by_category: Dict[str, int]
    entries_by_severity: Dict[str, int]
    resolution_rate: float
    top_issues: List[Dict[str, Any]]
    improvement_trends: List[str]
    recommendations: List[str]


class FeedbackMechanism:
    """Feedback system for continuous improvement based on trajectory insights."""

    def __init__(
        self,
        feedback_path: str = "data/feedback.json",
        monitoring_path: str = "logs/monitoring.log",
    ):
        self.feedback_path = Path(feedback_path)
        self.monitoring_path = Path(monitoring_path)

        # Ensure directories exist
        self.feedback_path.parent.mkdir(parents=True, exist_ok=True)
        self.monitoring_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize feedback storage
        self.feedback_entries: List[FeedbackEntry] = []
        self._load_feedback()

        # Setup logging
        self.logger = logging.getLogger("feedback_mechanism")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler("logs/feedback.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

    def collect_monitoring_feedback(self, report: MonitoringReport):
        """Collect feedback from monitoring reports."""

        # Analyze benchmark results
        for benchmark in report.benchmark_results:
            if benchmark.status in ["warning", "critical"]:
                entry = FeedbackEntry(
                    timestamp=benchmark.timestamp,
                    source="monitoring",
                    category="performance",
                    severity=benchmark.status,
                    title=f"Benchmark threshold exceeded: {benchmark.metric_name}",
                    description=f"Metric {benchmark.metric_name} value {benchmark.value:.2f} exceeds threshold",
                    metrics={
                        "metric_name": benchmark.metric_name,
                        "value": benchmark.value,
                        "threshold": benchmark.threshold,
                        "status": benchmark.status,
                    },
                    recommendations=self._generate_benchmark_recommendations(benchmark),
                )
                self._add_feedback_entry(entry)

        # Analyze ecosystem health
        ecosystem_issues = self._analyze_ecosystem_health(report.ecosystem_health)
        for issue in ecosystem_issues:
            entry = FeedbackEntry(
                timestamp=report.timestamp,
                source="monitoring",
                category="architecture",
                severity=issue["severity"],
                title=issue["title"],
                description=issue["description"],
                metrics=issue.get("metrics", {}),
                recommendations=issue.get("recommendations", []),
            )
            self._add_feedback_entry(entry)

        # Analyze detector metrics
        detector_issues = self._analyze_detector_metrics(report.detector_metrics)
        for issue in detector_issues:
            entry = FeedbackEntry(
                timestamp=report.timestamp,
                source="monitoring",
                category="security",
                severity=issue["severity"],
                title=issue["title"],
                description=issue["description"],
                metrics=issue.get("metrics", {}),
                recommendations=issue.get("recommendations", []),
            )
            self._add_feedback_entry(entry)

    def collect_user_feedback(
        self,
        title: str,
        description: str,
        category: str = "general",
        severity: str = "medium",
        user_context: Optional[Dict[str, Any]] = None,
    ):
        """Collect feedback from user input."""

        entry = FeedbackEntry(
            timestamp=datetime.now(),
            source="user",
            category=category,
            severity=severity,
            title=title,
            description=description,
            metrics=user_context or {},
            recommendations=[],
        )

        self._add_feedback_entry(entry)
        self.logger.info(f"User feedback collected: {title}")

    def collect_test_failure_feedback(self, test_name: str, error_message: str, stack_trace: Optional[str] = None):
        """Collect feedback from test failures."""

        entry = FeedbackEntry(
            timestamp=datetime.now(),
            source="test_failure",
            category="reliability",
            severity="high",
            title=f"Test failure: {test_name}",
            description=f"Test {test_name} failed: {error_message}",
            metrics={
                "test_name": test_name,
                "error_message": error_message,
                "stack_trace": stack_trace,
            },
            recommendations=[
                "Review test implementation",
                "Check for recent code changes affecting this test",
                "Verify test environment and dependencies",
            ],
        )

        self._add_feedback_entry(entry)
        self.logger.warning(f"Test failure feedback: {test_name}")

    def analyze_feedback_period(self, days: int = 30) -> FeedbackAnalysis:
        """Analyze feedback patterns over a time period."""

        period_end = datetime.now()
        period_start = period_end - timedelta(days=days)

        # Filter entries in period
        period_entries = [entry for entry in self.feedback_entries if period_start <= entry.timestamp <= period_end]

        # Calculate statistics
        total_entries = len(period_entries)
        entries_by_category = defaultdict(int)
        entries_by_severity = defaultdict(int)
        resolved_entries = [e for e in period_entries if e.resolved]

        for entry in period_entries:
            entries_by_category[entry.category] += 1
            entries_by_severity[entry.severity] += 1

        resolution_rate = len(resolved_entries) / total_entries if total_entries > 0 else 0

        # Identify top issues
        top_issues = self._identify_top_issues(period_entries)

        # Analyze improvement trends
        improvement_trends = self._analyze_improvement_trends(period_entries)

        # Generate recommendations
        recommendations = self._generate_period_recommendations(
            entries_by_category, entries_by_severity, improvement_trends
        )

        return FeedbackAnalysis(
            period_start=period_start,
            period_end=period_end,
            total_entries=total_entries,
            entries_by_category=dict(entries_by_category),
            entries_by_severity=dict(entries_by_severity),
            resolution_rate=resolution_rate,
            top_issues=top_issues,
            improvement_trends=improvement_trends,
            recommendations=recommendations,
        )

    def resolve_feedback_entry(self, entry_index: int, resolution_notes: str):
        """Mark a feedback entry as resolved."""

        if 0 <= entry_index < len(self.feedback_entries):
            entry = self.feedback_entries[entry_index]
            entry.resolved = True
            entry.resolved_at = datetime.now()
            entry.resolution_notes = resolution_notes
            self._save_feedback()
            self.logger.info(f"Feedback entry resolved: {entry.title}")
        else:
            raise ValueError(f"Invalid entry index: {entry_index}")

    def get_unresolved_feedback(
        self, category: Optional[str] = None, severity: Optional[str] = None
    ) -> List[FeedbackEntry]:
        """Get unresolved feedback entries, optionally filtered."""

        unresolved = [entry for entry in self.feedback_entries if not entry.resolved]

        if category:
            unresolved = [e for e in unresolved if e.category == category]

        if severity:
            unresolved = [e for e in unresolved if e.severity == severity]

        return unresolved

    def export_feedback_report(self, output_path: str, days: int = 30):
        """Export feedback analysis report."""

        analysis = self.analyze_feedback_period(days)

        report = {
            "generated_at": datetime.now().isoformat(),
            "analysis_period": {
                "start": analysis.period_start.isoformat(),
                "end": analysis.period_end.isoformat(),
                "days": days,
            },
            "summary": {
                "total_entries": analysis.total_entries,
                "resolution_rate": analysis.resolution_rate,
                "entries_by_category": analysis.entries_by_category,
                "entries_by_severity": analysis.entries_by_severity,
            },
            "top_issues": analysis.top_issues,
            "improvement_trends": analysis.improvement_trends,
            "recommendations": analysis.recommendations,
            "unresolved_entries": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "category": entry.category,
                    "severity": entry.severity,
                    "title": entry.title,
                    "description": entry.description,
                    "source": entry.source,
                }
                for entry in self.get_unresolved_feedback()
            ],
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Feedback report exported to {output_path}")

    def _add_feedback_entry(self, entry: FeedbackEntry):
        """Add a feedback entry and save."""

        self.feedback_entries.append(entry)
        self._save_feedback()
        self.logger.debug(f"Feedback entry added: {entry.title}")

    def _generate_benchmark_recommendations(self, benchmark: BenchmarkResult) -> List[str]:
        """Generate recommendations for benchmark issues."""

        recommendations = []

        if benchmark.metric_name == "complexity_score":
            recommendations.extend(
                [
                    "Refactor complex functions into smaller, focused methods",
                    "Extract utility classes for common operations",
                    "Consider breaking down large modules into smaller packages",
                ]
            )
        elif benchmark.metric_name == "communication_issues":
            recommendations.extend(
                [
                    "Review import dependencies for circular references",
                    "Standardize API interfaces between modules",
                    "Implement proper abstraction layers",
                ]
            )
        elif benchmark.metric_name == "gate_failures":
            recommendations.extend(
                [
                    "Address security scan findings",
                    "Fix code quality issues flagged by linters",
                    "Update outdated dependencies",
                ]
            )
        elif benchmark.metric_name == "detector_false_positives":
            recommendations.extend(
                [
                    "Adjust detector confidence thresholds",
                    "Review and refine detection rules",
                    "Implement better feature engineering",
                ]
            )
        elif benchmark.metric_name == "test_coverage":
            recommendations.extend(
                [
                    "Add unit tests for uncovered functions",
                    "Implement integration tests for critical paths",
                    "Review and expand test scenarios",
                ]
            )

        return recommendations

    def _analyze_ecosystem_health(self, ecosystem_health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze ecosystem health for feedback issues."""

        issues = []

        # Check complexity
        complexity = ecosystem_health["terraforming"]["complexity_score"]
        if complexity > 20:
            issues.append(
                {
                    "severity": "critical",
                    "title": "Critical code complexity detected",
                    "description": f"Complexity score of {complexity:.1f} exceeds safe threshold",
                    "metrics": {"complexity_score": complexity},
                    "recommendations": [
                        "Immediate refactoring required",
                        "Break down complex modules",
                    ],
                }
            )
        elif complexity > 10:
            issues.append(
                {
                    "severity": "warning",
                    "title": "High code complexity",
                    "description": f"Complexity score of {complexity:.1f} is elevated",
                    "metrics": {"complexity_score": complexity},
                    "recommendations": ["Consider refactoring complex functions"],
                }
            )

        # Check communication health
        if not ecosystem_health["communications"]["healthy"]:
            issues.append(
                {
                    "severity": "high",
                    "title": "Communication issues detected",
                    "description": f"Found {len(ecosystem_health['communications']['issues'])} communication problems",
                    "metrics": {"issues_count": len(ecosystem_health["communications"]["issues"])},
                    "recommendations": ecosystem_health["communications"]["issues"],
                }
            )

        # Check GATE status
        if ecosystem_health["gate_status"]["gate_status"] == "closed":
            issues.append(
                {
                    "severity": "critical",
                    "title": "GATE validation failed",
                    "description": "Quality gate is closed due to validation failures",
                    "metrics": ecosystem_health["gate_status"]["details"],
                    "recommendations": ["Review and fix validation failures before proceeding"],
                }
            )

        return issues

    def _analyze_detector_metrics(self, detector_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze detector metrics for feedback issues."""

        issues = []

        # Check for inactive detectors
        if detector_metrics.get("active_detectors", 0) == 0:
            issues.append(
                {
                    "severity": "medium",
                    "title": "No active detectors",
                    "description": "Detector system shows no activity",
                    "metrics": detector_metrics,
                    "recommendations": [
                        "Verify detector configuration",
                        "Check input data sources",
                    ],
                }
            )

        # Check shadow mode
        shadow_count = detector_metrics.get("shadow_mode_detectors", 0)
        if shadow_count > 0:
            issues.append(
                {
                    "severity": "low",
                    "title": f"{shadow_count} detectors in shadow mode",
                    "description": "Some detectors are running in evaluation mode",
                    "metrics": {"shadow_mode_count": shadow_count},
                    "recommendations": [
                        "Monitor shadow mode performance",
                        "Consider enabling live mode when confident",
                    ],
                }
            )

        return issues

    def _identify_top_issues(self, entries: List[FeedbackEntry]) -> List[Dict[str, Any]]:
        """Identify the most common issues."""

        issue_counts = defaultdict(int)
        issue_details = {}

        for entry in entries:
            key = f"{entry.category}:{entry.title}"
            issue_counts[key] += 1
            if key not in issue_details:
                issue_details[key] = {
                    "category": entry.category,
                    "title": entry.title,
                    "count": 0,
                    "severities": set(),
                }
            issue_details[key]["count"] += 1
            issue_details[key]["severities"].add(entry.severity)

        # Sort by frequency
        top_issues = sorted(issue_details.values(), key=lambda x: x["count"], reverse=True)
        return top_issues[:10]  # Top 10 issues

    def _analyze_improvement_trends(self, entries: List[FeedbackEntry]) -> List[str]:
        """Analyze trends in feedback data."""

        trends = []

        if not entries:
            return ["No feedback data available for trend analysis"]

        # Sort entries by time
        sorted_entries = sorted(entries, key=lambda x: x.timestamp)

        # Check resolution trends
        recent_entries = [e for e in sorted_entries if e.timestamp > datetime.now() - timedelta(days=7)]
        older_entries = [e for e in sorted_entries if e.timestamp <= datetime.now() - timedelta(days=7)]

        recent_resolved = sum(1 for e in recent_entries if e.resolved)
        older_resolved = sum(1 for e in older_entries if e.resolved)

        if len(recent_entries) > 0 and len(older_entries) > 0:
            recent_rate = recent_resolved / len(recent_entries)
            older_rate = older_resolved / len(older_entries)

            if recent_rate > older_rate:
                trends.append("Resolution rate is improving")
            elif recent_rate < older_rate:
                trends.append("Resolution rate is declining")

        # Check severity trends
        critical_recent = sum(1 for e in recent_entries if e.severity == "critical")
        critical_older = sum(1 for e in older_entries if e.severity == "critical")

        if critical_recent < critical_older and len(older_entries) > 0:
            trends.append("Fewer critical issues in recent period")
        elif critical_recent > critical_older:
            trends.append("More critical issues in recent period")

        if not trends:
            trends.append("No significant trends detected in feedback data")

        return trends

    def _generate_period_recommendations(
        self, categories: Dict[str, int], severities: Dict[str, int], trends: List[str]
    ) -> List[str]:
        """Generate recommendations based on period analysis."""

        recommendations = []

        # Category-based recommendations
        if categories.get("performance", 0) > categories.get("architecture", 0):
            recommendations.append("Focus on performance optimization initiatives")

        if categories.get("security", 0) > 3:
            recommendations.append("Prioritize security improvements and detector tuning")

        # Severity-based recommendations
        if severities.get("critical", 0) > 0:
            recommendations.append("Address critical issues immediately")

        # Trend-based recommendations
        for trend in trends:
            if "improving" in trend.lower():
                recommendations.append("Continue current improvement practices")
            elif "declining" in trend.lower():
                recommendations.append("Review and adjust current processes")

        if not recommendations:
            recommendations.append("Maintain current monitoring and improvement practices")

        return recommendations

    def _load_feedback(self):
        """Load feedback entries from file."""

        if self.feedback_path.exists():
            try:
                with open(self.feedback_path, "r") as f:
                    data = json.load(f)
                    self.feedback_entries = [FeedbackEntry(**entry) for entry in data]
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Error loading feedback: {e}")
                self.feedback_entries = []

    def _save_feedback(self):
        """Save feedback entries to file."""

        data = [
            {
                "timestamp": entry.timestamp.isoformat(),
                "source": entry.source,
                "category": entry.category,
                "severity": entry.severity,
                "title": entry.title,
                "description": entry.description,
                "metrics": entry.metrics,
                "recommendations": entry.recommendations,
                "resolved": entry.resolved,
                "resolved_at": entry.resolved_at.isoformat() if entry.resolved_at else None,
                "resolution_notes": entry.resolution_notes,
            }
            for entry in self.feedback_entries
        ]

        with open(self.feedback_path, "w") as f:
            json.dump(data, f, indent=2)


# Convenience functions
def collect_user_feedback(title: str, description: str, **kwargs):
    """Convenience function for user feedback collection."""
    mechanism = FeedbackMechanism()
    mechanism.collect_user_feedback(title, description, **kwargs)


def export_feedback_report(output_path: str = "reports/feedback_analysis.json", days: int = 30):
    """Convenience function for feedback report export."""
    mechanism = FeedbackMechanism()
    mechanism.export_feedback_report(output_path, days)
