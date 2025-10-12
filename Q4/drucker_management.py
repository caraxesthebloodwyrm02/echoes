"""Drucker Foundation Management Model utilities.

This module operationalizes Peter Drucker’s foundational management principles
while providing a structured roadmap data layer that can be consumed by the
interactive Dash dashboard.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional


@dataclass(slots=True)
class RoadmapItem:
    """A structured representation of a roadmap initiative."""

    id: int
    title: str
    phase: str
    status: str
    priority: str
    owner: str
    start_date: date
    due_date: date
    progress: int
    objective: Optional[str] = None
    notes: Optional[str] = None

    def to_record(self) -> Dict[str, Any]:
        """Return a serialisable dictionary suitable for Dash stores."""

        record = asdict(self)
        record["start_date"] = self.start_date.isoformat()
        record["due_date"] = self.due_date.isoformat()
        return record


class DruckerFoundationModel:
    """Encapsulates Drucker-style management and roadmap state."""

    def __init__(self, roadmap: Optional[Iterable[Dict[str, Any]]] = None):
        self.purpose: Optional[str] = None
        self.results: List[str] = []
        self.time_blocks: List[str] = []
        self.strengths: List[str] = []
        self.lessons: List[str] = []
        self.customers: List[str] = []
        self.human_engagements: List[str] = []
        self.roadmap: List[RoadmapItem] = []

        if roadmap:
            self.ingest_roadmap(roadmap)

    # 1. Define Purpose
    def define_purpose(self, objective: str) -> str:
        self.purpose = objective
        return f"Purpose set: {objective}"

    # 2. Focus on Results
    def log_result(self, result: str) -> str:
        self.results.append(result)
        return f"Result logged: {result}"

    # 3. Manage Time
    def allocate_time(self, block: str) -> str:
        self.time_blocks.append(block)
        return f"Time block added: {block}"

    # 4. Leverage Strengths
    def add_strength(self, strength: str) -> str:
        self.strengths.append(strength)
        return f"Strength recorded: {strength}"

    # 5. Continuous Learning
    def log_lesson(self, insight: str) -> str:
        self.lessons.append(insight)
        return f"Lesson captured: {insight}"

    # 6. Serve Customer Value
    def record_customer_feedback(self, feedback: str) -> str:
        self.customers.append(feedback)
        return f"Customer feedback logged: {feedback}"

    # 7. Maintain Human Balance
    def log_human_interaction(self, note: str) -> str:
        self.human_engagements.append(note)
        return f"Interaction noted: {note}"

    # Summary Output
    def summarize(self) -> Dict[str, Any]:
        return {
            "Purpose": self.purpose,
            "Results": self.results,
            "Time": self.time_blocks,
            "Strengths": self.strengths,
            "Learning": self.lessons,
            "Customer Value": self.customers,
            "Human Balance": self.human_engagements,
        }

    # Roadmap integration -------------------------------------------------
    def ingest_roadmap(self, items: Iterable[Dict[str, Any]]) -> int:
        """Replace the current roadmap with structured items."""

        self.roadmap = [self._coerce_item(index, raw) for index, raw in enumerate(items, start=1)]
        return len(self.roadmap)

    def add_roadmap_item(self, item: Dict[str, Any]) -> RoadmapItem:
        """Append a single roadmap item and return it."""

        next_id = max((entry.id for entry in self.roadmap), default=0) + 1
        roadmap_item = self._coerce_item(next_id, item, override_id=True)
        self.roadmap.append(roadmap_item)
        return roadmap_item

    def _coerce_item(self, index: int, raw: Dict[str, Any], override_id: bool = False) -> RoadmapItem:
        """Convert arbitrary dictionaries into `RoadmapItem` instances."""

        def _parse_date(value: Any) -> date:
            if isinstance(value, date):
                return value
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, str):
                return datetime.fromisoformat(value).date()
            raise ValueError(f"Unsupported date format: {value!r}")

        item_id = index if override_id or "id" not in raw else int(raw["id"])
        return RoadmapItem(
            id=item_id,
            title=str(raw["title"]),
            phase=str(raw.get("phase", "Unassigned")),
            status=str(raw.get("status", "Not Started")),
            priority=str(raw.get("priority", "Medium")),
            owner=str(raw.get("owner", "Unassigned")),
            start_date=_parse_date(raw.get("start_date")),
            due_date=_parse_date(raw.get("due_date")),
            progress=int(raw.get("progress", 0)),
            objective=raw.get("objective"),
            notes=raw.get("notes"),
        )

    def to_records(self) -> List[Dict[str, Any]]:
        """Return roadmap entries as serialisable dictionaries."""

        return [item.to_record() for item in self.roadmap]

    def status_counts(self) -> Dict[str, int]:
        """Aggregate roadmap items by status."""

        counts: Dict[str, int] = {}
        for item in self.roadmap:
            counts[item.status] = counts.get(item.status, 0) + 1
        return counts

    def phase_counts(self) -> Dict[str, int]:
        """Aggregate roadmap items by phase."""

        counts: Dict[str, int] = {}
        for item in self.roadmap:
            counts[item.phase] = counts.get(item.phase, 0) + 1
        return counts

    def metrics(self) -> Dict[str, Any]:
        """High-level metrics for dashboard hero cards."""

        status_counts = self.status_counts()
        return {
            "total": len(self.roadmap),
            "in_progress": status_counts.get("In Progress", 0),
            "completed": status_counts.get("Completed", 0),
            "on_hold": status_counts.get("On Hold", 0),
        }


DEFAULT_ROADMAP_ITEMS: List[Dict[str, Any]] = [
    {
        "title": "Biomedical Research Search Integration",
        "phase": "Execution",
        "status": "Not Started",
        "priority": "High",
        "owner": "Science Team",
        "start_date": "2024-10-01",
        "due_date": "2024-11-15",
        "progress": 0,
        "objective": "Implement PubMed API integration with peer-review validation",
    },
    {
        "title": "Employment Opportunity Matcher",
        "phase": "Execution",
        "status": "Completed",
        "priority": "High",
        "owner": "Commerce Team",
        "start_date": "2024-10-01",
        "due_date": "2024-11-15",
        "progress": 100,
        "objective": "Create semantic skill matching algorithm",
    },
    {
        "title": "Artisan Marketplace Connector",
        "phase": "Execution",
        "status": "Not Started",
        "priority": "High",
        "owner": "Commerce Team",
        "start_date": "2024-10-01",
        "due_date": "2024-11-15",
        "progress": 0,
        "objective": "Build MVP connector for creative marketplaces",
    },
    {
        "title": "Privacy Filters Implementation",
        "phase": "Execution",
        "status": "Not Started",
        "priority": "High",
        "owner": "Security Team",
        "start_date": "2024-10-01",
        "due_date": "2024-11-15",
        "progress": 0,
        "objective": "Deploy PII redaction and anonymization",
    },
    {
        "title": "Database Persistence Layer",
        "phase": "Execution",
        "status": "Not Started",
        "priority": "Medium",
        "owner": "Infrastructure Team",
        "start_date": "2024-10-01",
        "due_date": "2024-11-15",
        "progress": 0,
        "objective": "Set up PostgreSQL with data models",
    },
    {
        "title": "Provenance Enforcement Middleware",
        "phase": "Stabilisation",
        "status": "Completed",
        "priority": "High",
        "owner": "Security Team",
        "start_date": "2024-09-01",
        "due_date": "2024-09-30",
        "progress": 100,
        "objective": "Implement mandatory source validation",
    },
    {
        "title": "Human-in-the-Loop Feedback System",
        "phase": "Stabilisation",
        "status": "Completed",
        "priority": "High",
        "owner": "Product Team",
        "start_date": "2024-09-01",
        "due_date": "2024-09-30",
        "progress": 100,
        "objective": "Create feedback capture pipeline",
    },
    {
        "title": "Agent Safety Layer",
        "phase": "Stabilisation",
        "status": "Completed",
        "priority": "High",
        "owner": "Security Team",
        "start_date": "2024-09-01",
        "due_date": "2024-09-30",
        "progress": 100,
        "objective": "Implement dry-run and kill-switch controls",
    },
    {
        "title": "Cross-Domain Knowledge Fusion",
        "phase": "Discovery",
        "status": "Not Started",
        "priority": "High",
        "owner": "AI Team",
        "start_date": "2024-11-01",
        "due_date": "2024-12-15",
        "progress": 0,
        "objective": "Build unified ontology and fusion layer",
    },
    {
        "title": "Cost Metering & Quotas",
        "phase": "Discovery",
        "status": "Not Started",
        "priority": "Medium",
        "owner": "Infrastructure Team",
        "start_date": "2024-11-01",
        "due_date": "2024-12-15",
        "progress": 0,
        "objective": "Implement resource tracking and limits",
    },
    {
        "title": "UBI Simulation Engine",
        "phase": "Discovery",
        "status": "Completed",
        "priority": "Medium",
        "owner": "Commerce Team",
        "start_date": "2024-11-01",
        "due_date": "2024-12-15",
        "progress": 100,
        "objective": "Create economic modeling framework",
    },
    {
        "title": "Creative Intelligence Tools",
        "phase": "Discovery",
        "status": "Not Started",
        "priority": "Medium",
        "owner": "Arts Team",
        "start_date": "2024-11-01",
        "due_date": "2024-12-15",
        "progress": 0,
        "objective": "Develop attribution and originality scoring",
    },
    {
        "title": "Load Testing Suite",
        "phase": "Measurement",
        "status": "Not Started",
        "priority": "Medium",
        "owner": "QA Team",
        "start_date": "2024-12-01",
        "due_date": "2025-01-15",
        "progress": 0,
        "objective": "Implement comprehensive performance testing",
    },
    {
        "title": "Security Penetration Testing",
        "phase": "Measurement",
        "status": "Not Started",
        "priority": "High",
        "owner": "Security Team",
        "start_date": "2024-12-01",
        "due_date": "2025-01-15",
        "progress": 0,
        "objective": "Conduct thorough security audit",
    },
    {
        "title": "Compliance Audit Framework",
        "phase": "Measurement",
        "status": "Not Started",
        "priority": "High",
        "owner": "Legal Team",
        "start_date": "2024-12-01",
        "due_date": "2025-01-15",
        "progress": 0,
        "objective": "Build HIPAA/GDPR compliance verification",
    },
    {
        "title": "Deployment Automation",
        "phase": "Measurement",
        "status": "Not Started",
        "priority": "Medium",
        "owner": "DevOps Team",
        "start_date": "2024-12-01",
        "due_date": "2025-01-15",
        "progress": 0,
        "objective": "Create CI/CD pipeline and auto-deployment",
    },
]
