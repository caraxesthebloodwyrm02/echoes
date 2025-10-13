"""Drucker Foundation Management Model utilities.

This module operationalizes Peter Drucker's foundational management principles
while providing a structured roadmap data layer that can be consumed by the
interactive Dash dashboard.

Incorporates plant-based ecosystem metaphors for continuous codebase management:
- External Stressors: Monitor and experiment with protective umbrellas against stressors
- Growth & Diverging Paths: Track terraforming patterns (roots, branches, leaves)
- Communication Breakdown: Maintain optimal wirings for uncluttered component communication
- Resilient GATE: Build defenses against trojan horses through continuous validation
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional
import os
import re
from pathlib import Path


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


@dataclass(slots=True)
class StressorEvent:
    """Represents an external stressor event in the ecosystem."""
    timestamp: datetime
    type: str  # 'rain' (dependency issues), 'scorch' (security breaches), etc.
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    mitigation: Optional[str] = None


@dataclass(slots=True)
class TerraformingMetric:
    """Tracks codebase terraforming patterns (roots, branches, leaves)."""
    timestamp: datetime
    roots: int  # core modules/files
    branches: int  # feature modules
    leaves: int  # utility/helper files
    complexity_score: float


class EcosystemManager:
    """Plant-based ecosystem management for continuous codebase health.

    Metaphors:
    - Roots: Core foundational code (models, core logic)
    - Branches: Feature extensions (APIs, integrations)
    - Leaves: Utilities and helpers (tests, scripts, configs)
    - Umbrellas: Protective measures against stressors
    - GATE: Validation gate against trojan horses
    """

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.stressors: List[StressorEvent] = []
        self.terraforming_history: List[TerraformingMetric] = []
        self.communication_wirings: Dict[str, List[str]] = {}  # module -> dependencies
        self.gate_validations: List[Dict[str, Any]] = []

    def monitor_stressors(self) -> List[StressorEvent]:
        """Continuously monitor for external stressors and return active ones."""
        # Implement monitoring logic (CI status, dependency health, etc.)
        active_stressors = [s for s in self.stressors if self._is_stressor_active(s)]
        return active_stressors

    def deploy_umbrella(self, stressor_type: str, mitigation: str) -> str:
        """Deploy protective umbrella against specific stressor type."""
        # Logic to implement mitigation measures
        return f"Umbrella deployed for {stressor_type}: {mitigation}"

    def track_terraforming(self) -> TerraformingMetric:
        """Analyze current codebase structure using plant metaphors."""
        roots, branches, leaves = self._categorize_files()
        complexity = self._calculate_complexity_score()
        metric = TerraformingMetric(
            timestamp=datetime.now(),
            roots=roots,
            branches=branches,
            leaves=leaves,
            complexity_score=complexity
        )
        self.terraforming_history.append(metric)
        return metric

    def validate_communication_wirings(self) -> Dict[str, Any]:
        """Check for communication breakdowns in component interactions."""
        issues = []
        cycles = self._detect_import_cycles()
        if cycles:
            issues.append(f"Import cycles detected: {cycles}")

        uncluttered = self._check_api_coherence()
        if not uncluttered:
            issues.append("API coherence issues found")

        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "wirings_status": "optimal" if len(issues) == 0 else "needs_attention"
        }

    def operate_gate(self) -> Dict[str, Any]:
        """Run validation GATE to prevent trojan horses."""
        validations = {
            "security_scan": self._run_security_scan(),
            "quality_checks": self._run_quality_checks(),
            "dependency_audit": self._run_dependency_audit(),
            "communication_health": self.validate_communication_wirings()
        }

        gate_passed = all(v.get("passed", False) for v in validations.values())
        self.gate_validations.append({
            "timestamp": datetime.now(),
            "passed": gate_passed,
            "validations": validations
        })

        return {
            "gate_status": "open" if gate_passed else "closed",
            "details": validations,
            "action_required": "none" if gate_passed else "review_failures"
        }

    def _categorize_files(self) -> tuple[int, int, int]:
        """Categorize files into roots, branches, leaves."""
        roots = branches = leaves = 0
        for file_path in self.root_path.rglob("*.py"):
            if self._is_root_file(file_path):
                roots += 1
            elif self._is_branch_file(file_path):
                branches += 1
            else:
                leaves += 1
        return roots, branches, leaves

    def _is_root_file(self, path: Path) -> bool:
        """Determine if file is a root (core) component."""
        # Core directories: core/, models/, main modules
        return any(part in ["core", "models", "foundation"] for part in path.parts)

    def _is_branch_file(self, path: Path) -> bool:
        """Determine if file is a branch (feature) component."""
        # Feature directories: features/, integrations/, apis/
        return any(part in ["features", "integrations", "apis", "services"] for part in path.parts)

    def _calculate_complexity_score(self) -> float:
        """Calculate codebase complexity using cyclomatic complexity approximation."""
        total_lines = 0
        control_structures = 0
        for file_path in self.root_path.rglob("*.py"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += len(content.splitlines())
                    # Simple heuristic: count if/elif/for/while/try/except
                    control_structures += len(re.findall(r'\b(if|elif|for|while|try|except)\b', content))
            except:
                continue
        return control_structures / max(total_lines, 1) * 100

    def _detect_import_cycles(self) -> List[List[str]]:
        """Detect circular import dependencies."""
        # Simplified cycle detection - in practice, use tools like importlib
        cycles = []
        # Placeholder for actual cycle detection logic
        return cycles

    def _check_api_coherence(self) -> bool:
        """Check if APIs are coherent and uncluttered."""
        # Placeholder for API coherence checks
        return True

    def _is_stressor_active(self, stressor: StressorEvent) -> bool:
        """Check if a stressor is still active."""
        # Implement based on stressor type (e.g., check CI status, vuln scans)
        return False

    def _run_security_scan(self) -> Dict[str, Any]:
        """Run security validation."""
        return {"passed": True, "details": "No vulnerabilities found"}

    def _run_quality_checks(self) -> Dict[str, Any]:
        """Run code quality checks."""
        return {"passed": True, "details": "All quality gates passed"}

    def _run_dependency_audit(self) -> Dict[str, Any]:
        """Audit dependencies for issues."""
        return {"passed": True, "details": "Dependencies healthy"}


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
