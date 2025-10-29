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
Evolution Mechanisms Module

Implements gradual evolution mechanisms for the ethics framework over a decade-long timeline.
Emphasizes distributed responsibility, transparency, and avoidance of power concentration.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class EvolutionPhase:
    def __init__(
        self,
        name: str,
        duration_years: int,
        focus_areas: List[str],
        milestones: List[str],
    ):
        self.name = name
        self.duration_years = duration_years
        self.focus_areas = focus_areas
        self.milestones = milestones
        self.start_date = None
        self.end_date = None

    def activate(self, start_date: datetime):
        """Activate this evolution phase."""
        self.start_date = start_date
        self.end_date = start_date + timedelta(days=self.duration_years * 365)

    def is_active(self, current_date: datetime) -> bool:
        """Check if this phase is currently active."""
        return self.start_date <= current_date <= self.end_date if self.start_date else False

    def get_progress(self, current_date: datetime) -> float:
        """Get completion progress of this phase (0.0 to 1.0)."""
        if not self.is_active(current_date):
            return 0.0 if current_date < self.start_date else 1.0
        total_duration = (self.end_date - self.start_date).days
        elapsed = (current_date - self.start_date).days
        return min(elapsed / total_duration, 1.0)


class DistributedResponsibilityManager:
    """Manages distributed responsibility to avoid power concentration."""

    def __init__(self):
        self.stakeholders = {}
        self.responsibility_matrix = {}

    def add_stakeholder(self, name: str, role: str, influence_level: float):
        """Add a stakeholder with defined role and influence."""
        self.stakeholders[name] = {
            "role": role,
            "influence_level": influence_level,
            "active_contributions": [],
        }

    def assign_responsibility(self, task: str, stakeholders: List[str], rotation_period_days: int = 90):
        """Assign responsibility for a task with rotation to distribute power."""
        self.responsibility_matrix[task] = {
            "stakeholders": stakeholders,
            "rotation_period": rotation_period_days,
            "current_holder": stakeholders[0] if stakeholders else None,
            "rotation_history": [],
        }

    def get_current_responsible_party(self, task: str) -> Optional[str]:
        """Get the currently responsible party for a task."""
        task_info = self.responsibility_matrix.get(task, {})
        return task_info.get("current_holder")

    def rotate_responsibility(self, task: str):
        """Rotate responsibility for a task."""
        task_info = self.responsibility_matrix.get(task, {})
        stakeholders = task_info.get("stakeholders", [])
        if not stakeholders:
            return

        current_index = stakeholders.index(task_info.get("current_holder", stakeholders[0]))
        next_index = (current_index + 1) % len(stakeholders)
        task_info["current_holder"] = stakeholders[next_index]
        task_info["rotation_history"].append(
            {
                "timestamp": datetime.now(),
                "previous_holder": stakeholders[current_index],
                "new_holder": stakeholders[next_index],
            }
        )


class TransparencyLedger:
    """Maintains a transparent ledger of all system changes and decisions."""

    def __init__(self, ledger_file: str = "transparency_ledger.json"):
        self.ledger_file = ledger_file
        self.entries = self._load_ledger()

    def _load_ledger(self) -> List[Dict]:
        """Load existing ledger entries."""
        try:
            with open(self.ledger_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_ledger(self):
        """Save ledger entries to file."""
        with open(self.ledger_file, "w") as f:
            json.dump(self.entries, f, indent=2, default=str)

    def log_decision(
        self,
        decision_type: str,
        description: str,
        rationale: str,
        stakeholders_involved: List[str],
    ):
        """Log an ethical decision or system change."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "description": description,
            "rationale": rationale,
            "stakeholders_involved": stakeholders_involved,
            "system_state": self._capture_system_state(),
        }
        self.entries.append(entry)
        self._save_ledger()

    def _capture_system_state(self) -> Dict:
        """Capture current system state for transparency."""
        return {
            "active_principles": list(CORE_PRINCIPLES.keys()),
            "evolution_phase": CURRENT_PHASE.name if CURRENT_PHASE else "None",
            "stakeholder_count": len(DISTRIBUTED_RESPONSIBILITY.stakeholders),
        }

    def get_audit_trail(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Retrieve audit trail for a date range."""
        filtered_entries = self.entries
        if start_date:
            filtered_entries = [e for e in filtered_entries if datetime.fromisoformat(e["timestamp"]) >= start_date]
        if end_date:
            filtered_entries = [e for e in filtered_entries if datetime.fromisoformat(e["timestamp"]) <= end_date]
        return filtered_entries


# Global instances
DISTRIBUTED_RESPONSIBILITY = DistributedResponsibilityManager()
TRANSPARENCY_LEDGER = TransparencyLedger()

# Define evolution phases (2025-2035, assuming start in 2025)
EVOLUTION_PHASES = [
    EvolutionPhase(
        "Foundation Building (2025-2027)",
        2,
        [
            "Establish core principles",
            "Build basic infrastructure",
            "Initial stakeholder engagement",
        ],
        [
            "Core principles documented",
            "Initial bias detection tools deployed",
            "Stakeholder council formed",
        ],
    ),
    EvolutionPhase(
        "Expansion and Refinement (2027-2030)",
        3,
        [
            "Expand capabilities",
            "Integrate societal models",
            "Enhance transparency mechanisms",
        ],
        [
            "Advanced bias detection algorithms",
            "Societal inspiration integration",
            "Public transparency reports",
        ],
    ),
    EvolutionPhase(
        "Maturation and Optimization (2030-2035)",
        5,
        [
            "Optimize for scale",
            "Deep societal integration",
            "Prepare for autonomous operation",
        ],
        [
            "System handles complex scenarios",
            "Full societal model adoption",
            "Autonomous ethical oversight",
        ],
    ),
]

CURRENT_PHASE = None


def initialize_evolution_framework(start_year: int = 2025):
    """Initialize the evolution framework with phases."""
    global CURRENT_PHASE
    start_date = datetime(start_year, 1, 1)
    for phase in EVOLUTION_PHASES:
        phase.activate(start_date)
        if phase.is_active(datetime.now()):
            CURRENT_PHASE = phase
            break
        start_date = phase.end_date


def get_current_phase() -> Optional[EvolutionPhase]:
    """Get the currently active evolution phase."""
    current_date = datetime.now()
    for phase in EVOLUTION_PHASES:
        if phase.is_active(current_date):
            return phase
    return None


def advance_to_next_phase():
    """Manually advance to the next evolution phase (for testing or acceleration)."""
    global CURRENT_PHASE
    current_date = datetime.now()
    for i, phase in enumerate(EVOLUTION_PHASES):
        if phase.is_active(current_date) and i + 1 < len(EVOLUTION_PHASES):
            CURRENT_PHASE = EVOLUTION_PHASES[i + 1]
            CURRENT_PHASE.activate(current_date)
            TRANSPARENCY_LEDGER.log_decision(
                "phase_advancement",
                f"Advanced to {CURRENT_PHASE.name}",
                "Manual or automatic phase progression based on milestones",
                ["system_administrator"],
            )
            break


# Initialize on import
initialize_evolution_framework()
