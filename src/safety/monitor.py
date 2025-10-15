#!/usr/bin/env python3
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

"""
Safety Monitoring Dashboard for real-time visibility.

Provides real-time monitoring of safety operations including:
- Live audit event streaming
- Safety statistics dashboard
- Rate limiting metrics
- Circuit breaker status
- Security event alerts
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.safety.audit import AuditLogger
from src.safety.guards import CircuitBreaker
from src.safety.limiter import TokenBucket


@dataclass
class SafetyMetrics:
    """Real-time safety metrics snapshot."""

    timestamp: str
    total_evaluations: int
    safety_events_24h: int
    rate_limited_requests: int
    blocked_injections: int
    circuit_breaker_trips: int
    active_users: int
    avg_response_time: float
    system_health: str  # "healthy", "warning", "critical"


class SafetyMonitor:
    """
    Real-time safety monitoring dashboard.

    Provides live visibility into safety operations and system health.
    """

    def __init__(
        self, audit_logger: AuditLogger, rate_limiter: Optional[TokenBucket] = None
    ):
        self.audit = audit_logger
        self.rate_limiter = rate_limiter
        self.circuit_breaker = None  # Will be set if available
        self._alert_thresholds = {
            "rate_limit_percent": 10,  # Alert if >10% requests rate limited
            "injection_block_percent": 5,  # Alert if >5% requests blocked
            "circuit_breaker_trips": 3,  # Alert if >3 circuit breaker trips in 24h
        }

    def set_circuit_breaker(self, cb: CircuitBreaker) -> None:
        """Set circuit breaker for monitoring."""
        self.circuit_breaker = cb

    def get_live_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive safety dashboard data."""
        now = datetime.utcnow()

        # Get recent events (last 24 hours)
        recent_events = self.audit.get_recent_events(1000)

        # Calculate metrics
        metrics = self._calculate_metrics(recent_events, now)

        # Get rate limiter stats
        rate_stats = self.rate_limiter.get_stats() if self.rate_limiter else {}

        # Get circuit breaker status
        cb_status = self._get_circuit_breaker_status()

        # Generate alerts
        alerts = self._generate_alerts(metrics)

        return {
            "timestamp": now.isoformat(),
            "metrics": metrics,
            "rate_limiter": rate_stats,
            "circuit_breaker": cb_status,
            "alerts": alerts,
            "recent_events": recent_events[-10:],  # Last 10 events
            "system_health": self._assess_system_health(metrics, alerts),
        }

    def get_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate detailed security report."""
        stats = self.audit.get_security_stats(hours)

        # Enhanced analysis
        threat_analysis = self._analyze_threats(stats)

        return {
            "time_range": stats["time_range"],
            "summary": stats,
            "threat_analysis": threat_analysis,
            "recommendations": self._generate_security_recommendations(threat_analysis),
        }

    def stream_events(self, callback: callable, poll_interval: float = 5.0):
        """Stream new audit events in real-time."""
        last_event_count = 0

        while True:
            try:
                events = self.audit.get_recent_events(100)
                if len(events) > last_event_count:
                    new_events = events[last_event_count:]
                    for event in new_events:
                        callback(event)
                    last_event_count = len(events)

                time.sleep(poll_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Monitoring stream error: {e}")
                time.sleep(poll_interval)

    def _calculate_metrics(self, events: List[Dict], now: datetime) -> SafetyMetrics:
        """Calculate comprehensive safety metrics."""
        # Time windows
        last_24h = now - timedelta(hours=24)
        last_1h = now - timedelta(hours=1)

        # Filter events by time
        events_24h = [
            e
            for e in events
            if datetime.fromisoformat(e.get("timestamp") or e.get("ts", "")) > last_24h
        ]
        events_1h = [
            e
            for e in events
            if datetime.fromisoformat(e.get("timestamp") or e.get("ts", "")) > last_1h
        ]

        # Calculate metrics
        total_evaluations = len(
            [e for e in events_24h if e["operation"] == "bias_evaluation"]
        )
        safety_events = len(
            [
                e
                for e in events_24h
                if e["safety_status"]
                in ["rate_limited", "input_blocked", "circuit_breaker"]
            ]
        )
        rate_limited = len(
            [e for e in events_24h if e["safety_status"] == "rate_limited"]
        )
        blocked_injections = len(
            [e for e in events_24h if e["safety_status"] == "input_blocked"]
        )
        cb_trips = len(
            [e for e in events_24h if e["safety_status"] == "circuit_breaker"]
        )

        # Calculate active users (unique user hashes in last 24h)
        active_users = len(set(e["user_id"] for e in events_24h))

        # Mock response time (would need actual timing data)
        avg_response_time = 1.2  # seconds

        return SafetyMetrics(
            timestamp=now.isoformat(),
            total_evaluations=total_evaluations,
            safety_events_24h=safety_events,
            rate_limited_requests=rate_limited,
            blocked_injections=blocked_injections,
            circuit_breaker_trips=cb_trips,
            active_users=active_users,
            avg_response_time=avg_response_time,
            system_health="unknown",  # Will be set by _assess_system_health
        )

    def _get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker current status."""
        if not self.circuit_breaker:
            return {"status": "not_monitored"}

        # This is a simplified status - real implementation would need CB introspection
        return {
            "status": "active",
            "failures": getattr(self.circuit_breaker, "count", 0),
            "timeout_remaining": 0,  # Would need CB internal state
        }

    def _generate_alerts(self, metrics: SafetyMetrics) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics and thresholds."""
        alerts = []

        # Rate limiting alert
        if metrics.total_evaluations > 0:
            rate_limit_percent = (
                metrics.rate_limited_requests / metrics.total_evaluations
            ) * 100
            if rate_limit_percent > self._alert_thresholds["rate_limit_percent"]:
                alerts.append(
                    {
                        "level": "warning",
                        "type": "rate_limiting",
                        "message": f"High rate limiting: {rate_limit_percent:.1f}% of requests blocked",
                        "value": rate_limit_percent,
                        "threshold": self._alert_thresholds["rate_limit_percent"],
                    }
                )

        # Injection blocking alert
        if metrics.total_evaluations > 0:
            injection_percent = (
                metrics.blocked_injections / metrics.total_evaluations
            ) * 100
            if injection_percent > self._alert_thresholds["injection_block_percent"]:
                alerts.append(
                    {
                        "level": "warning",
                        "type": "injection_attempts",
                        "message": f"Elevated injection attempts: {injection_percent:.1f}% blocked",
                        "value": injection_percent,
                        "threshold": self._alert_thresholds["injection_block_percent"],
                    }
                )

        # Circuit breaker alert
        if (
            metrics.circuit_breaker_trips
            > self._alert_thresholds["circuit_breaker_trips"]
        ):
            alerts.append(
                {
                    "level": "critical",
                    "type": "circuit_breaker",
                    "message": f"Excessive circuit breaker trips: {metrics.circuit_breaker_trips}",
                    "value": metrics.circuit_breaker_trips,
                    "threshold": self._alert_thresholds["circuit_breaker_trips"],
                }
            )

        return alerts

    def _assess_system_health(self, metrics: SafetyMetrics, alerts: List[Dict]) -> str:
        """Assess overall system health."""
        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        warning_alerts = [a for a in alerts if a["level"] == "warning"]

        if critical_alerts:
            return "critical"
        elif warning_alerts:
            return "warning"
        else:
            return "healthy"

    def _analyze_threats(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security threats from statistics."""
        total = stats["total_events"]

        if total == 0:
            return {"threat_level": "none", "analysis": "No events to analyze"}

        rate_limited_percent = (stats["rate_limited"] / total) * 100
        blocked_percent = (stats["blocked_injections"] / total) * 100

        threat_level = "low"
        if rate_limited_percent > 20 or blocked_percent > 10:
            threat_level = "high"
        elif rate_limited_percent > 10 or blocked_percent > 5:
            threat_level = "medium"

        return {
            "threat_level": threat_level,
            "rate_limited_percent": round(rate_limited_percent, 2),
            "blocked_injections_percent": round(blocked_percent, 2),
            "analysis": self._generate_threat_analysis(
                threat_level, rate_limited_percent, blocked_percent
            ),
        }

    def _generate_threat_analysis(
        self, level: str, rate_limited: float, blocked: float
    ) -> str:
        """Generate human-readable threat analysis."""
        if level == "high":
            return f"High threat activity detected. {rate_limited:.1f}% rate limiting and {blocked:.1f}% injection blocks suggest active abuse attempts."
        elif level == "medium":
            return f"Moderate threat activity. Monitor rate limiting ({rate_limited:.1f}%) and injection blocks ({blocked:.1f}%)."
        else:
            return f"Normal activity levels. Rate limiting: {rate_limited:.1f}%, Injection blocks: {blocked:.1f}%."

    def _generate_security_recommendations(self, threat_analysis: Dict) -> List[str]:
        """Generate security recommendations based on threat analysis."""
        recommendations = []

        level = threat_analysis["threat_level"]
        rate_limited = threat_analysis["rate_limited_percent"]
        blocked = threat_analysis["blocked_injections_percent"]

        if level == "high":
            recommendations.extend(
                [
                    "Implement stricter rate limiting",
                    "Consider IP-based blocking for high-frequency offenders",
                    "Review and enhance prompt injection detection patterns",
                    "Enable real-time alerting for security team",
                ]
            )
        elif level == "medium":
            recommendations.extend(
                [
                    "Monitor rate limiting trends closely",
                    "Review blocked injection patterns for new attack vectors",
                    "Consider increasing rate limits if legitimate traffic is affected",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Maintain current security posture",
                    "Regular review of security logs",
                    "Keep security patterns updated",
                ]
            )

        return recommendations


# Global monitor instance for easy access
_monitor_instance = None


def get_safety_monitor(
    audit_logger: AuditLogger = None, rate_limiter: TokenBucket = None
) -> SafetyMonitor:
    """Get or create global safety monitor instance."""
    global _monitor_instance

    if _monitor_instance is None:
        if audit_logger is None:
            audit_logger = AuditLogger()
        _monitor_instance = SafetyMonitor(audit_logger, rate_limiter)

    return _monitor_instance


def quick_status() -> Dict[str, Any]:
    """Get quick safety status overview."""
    monitor = get_safety_monitor()
    dashboard = monitor.get_live_dashboard()

    return {
        "health": dashboard["system_health"],
        "evaluations_24h": dashboard["metrics"].total_evaluations,
        "safety_events": dashboard["metrics"].safety_events_24h,
        "active_users": dashboard["metrics"].active_users,
        "alerts_count": len(dashboard["alerts"]),
    }
