"""Stub IMPACT_ANALYTICS connector: offline-safe, satisfies contract tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImpactMetrics:
    safety_score: float = 0.0
    bias_reduction_index: float = 0.0
    total_evaluations: int = 0
    recent_milestones: list[Any] = field(default_factory=list)
    error: str | None = None


class ImpactAnalyticsConnector:
    """Records evaluations when an external IMPACT server is unavailable."""

    def __init__(self) -> None:
        self.workflow_tracker: dict[str, Any] = {}
        self.connected: bool = False
        self._evaluations: int = 0

    def is_connected(self) -> bool:
        return self.connected

    def record_evaluation(
        self,
        prompt: str,
        response: str,
        safety_score: float,
        bias_analysis: dict[str, Any],
    ) -> bool:
        self._evaluations += 1
        self.workflow_tracker.setdefault("evaluations", []).append(
            {"prompt": prompt, "response": response, "safety_score": safety_score}
        )
        return True

    def record_milestone(
        self,
        name: str,
        score: float,
        milestone_type: str = "research",
        metadata: Any | None = None,
    ) -> bool:
        self.workflow_tracker.setdefault("milestones", []).append(
            {"name": name, "score": score, "type": milestone_type, "metadata": metadata}
        )
        return True

    def get_metrics(self) -> ImpactMetrics:
        return ImpactMetrics(
            safety_score=0.0,
            bias_reduction_index=0.0,
            total_evaluations=self._evaluations,
            recent_milestones=list(self.workflow_tracker.get("milestones", [])),
            error=None,
        )

    def generate_report(self) -> str | None:
        return None


impact_connector = ImpactAnalyticsConnector()


def record_ai_evaluation(
    prompt: str,
    response: str,
    safety_score: float,
    bias_analysis: dict[str, Any],
) -> bool:
    return impact_connector.record_evaluation(prompt, response, safety_score, bias_analysis)


def record_research_progress(milestone: str, score: float) -> bool:
    return impact_connector.record_milestone(milestone, score, "research", None)


def get_impact_status() -> ImpactMetrics:
    return impact_connector.get_metrics()


def generate_impact_report() -> str | None:
    return impact_connector.generate_report()
