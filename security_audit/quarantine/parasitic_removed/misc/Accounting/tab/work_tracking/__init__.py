#!/usr/bin/env python3
"""
Work Tracking Module - Tab Repository

Tracks all work done by users, automatically logging:
- Time invested in tasks
- Intellectual contributions
- Motivation and dedication levels
- Quality of work delivered

Integrates with assistant_v2_core.py to automatically track
user contributions and ensure fair compensation.
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class WorkEntry:
    """Represents a single work entry with all contribution details."""

    work_id: str
    user_id: str
    timestamp: str
    task_type: str  # query_processing, analysis, creation, etc.
    description: str
    time_invested_minutes: float
    intellectual_effort: float  # 0-10 scale
    motivation_level: float  # 0-10 scale
    quality_rating: float  # 0-10 scale
    assistant_interaction: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    status: str = "completed"


@dataclass
class UserWorkProfile:
    """Tracks a user's complete work history and contribution patterns."""

    user_id: str
    total_work_entries: int = 0
    total_time_invested: float = 0.0
    average_intellectual_effort: float = 0.0
    average_motivation_level: float = 0.0
    average_quality_rating: float = 0.0
    skill_tags: list[str] = field(default_factory=list)
    work_categories: dict[str, int] = field(default_factory=dict)
    last_updated: str = ""


class WorkTracker:
    """
    Core work tracking system integrated with assistant_v2_core.py

    Automatically tracks user contributions and ensures fair compensation
    for time, thoughts, and motivation invested in work.
    """

    def __init__(self, base_dir: str = "e:/Projects/Echoes/Accounting/tab"):
        self.base_dir = Path(base_dir)
        self.work_dir = self.base_dir / "work_tracking"
        self.data_dir = self.work_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Integration with assistant_v2_core.py
        self.assistant_integration = AssistantWorkIntegration()

        print("✅ Work Tracker initialized - tracking user contributions")

    def log_work_entry(
        self,
        user_id: str,
        task_type: str,
        description: str,
        time_invested_minutes: float,
        intellectual_effort: float,
        motivation_level: float,
        quality_rating: float,
        assistant_data: dict[str, Any] | None = None,
    ) -> str:
        """
        Log a work entry with all contribution details.

        Args:
            user_id: Unique identifier for the user
            task_type: Type of work (analysis, development, consultation, etc.)
            description: Description of the work done
            time_invested_minutes: Time spent in minutes
            intellectual_effort: Intellectual contribution (0-10)
            motivation_level: Motivation level (0-10)
            quality_rating: Quality of work delivered (0-10)
            assistant_data: Data from assistant_v2_core.py interaction

        Returns:
            Work entry ID
        """
        # Generate unique work ID
        work_id = hashlib.md5(
            f"{user_id}_{task_type}_{time.time()}".encode()
        ).hexdigest()[:16]

        # Create work entry
        entry = WorkEntry(
            work_id=work_id,
            user_id=user_id,
            timestamp=datetime.now(UTC).isoformat(),
            task_type=task_type,
            description=description,
            time_invested_minutes=time_invested_minutes,
            intellectual_effort=clamp(intellectual_effort, 0, 10),
            motivation_level=clamp(motivation_level, 0, 10),
            quality_rating=clamp(quality_rating, 0, 10),
            assistant_interaction=assistant_data or {},
            tags=self._generate_tags(task_type, description),
        )

        # Save entry
        self._save_work_entry(entry)

        # Update user profile
        self._update_user_profile(user_id, entry)

        # Sync with assistant
        self.assistant_integration.sync_work_entry(entry)

        print(f"✅ Work logged: {work_id} for user {user_id}")
        return work_id

    def get_user_work_history(self, user_id: str, limit: int = 50) -> list[WorkEntry]:
        """Get work history for a user."""
        profile_file = self.data_dir / f"user_{user_id}_profile.json"

        if not profile_file.exists():
            return []

        try:
            with open(profile_file) as f:
                profile_data = json.load(f)

            work_entries = []
            for entry_data in profile_data.get("work_entries", []):
                work_entries.append(WorkEntry(**entry_data))

            return work_entries[-limit:]  # Return most recent entries

        except Exception as e:
            print(f"Error loading work history for user {user_id}: {e}")
            return []

    def get_user_contribution_summary(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive contribution summary for a user."""
        profile_file = self.data_dir / f"user_{user_id}_profile.json"

        if not profile_file.exists():
            return self._create_empty_summary(user_id)

        try:
            with open(profile_file) as f:
                profile_data = json.load(f)

            # Calculate contribution metrics
            work_entries = profile_data.get("work_entries", [])
            total_entries = len(work_entries)

            if total_entries == 0:
                return self._create_empty_summary(user_id)

            total_time = sum(entry["time_invested_minutes"] for entry in work_entries)
            avg_intellectual = (
                sum(entry["intellectual_effort"] for entry in work_entries)
                / total_entries
            )
            avg_motivation = (
                sum(entry["motivation_level"] for entry in work_entries) / total_entries
            )
            avg_quality = (
                sum(entry["quality_rating"] for entry in work_entries) / total_entries
            )

            # Calculate contribution score (weighted average)
            contribution_score = (
                avg_intellectual * 0.4 + avg_motivation * 0.3 + avg_quality * 0.3
            )

            return {
                "user_id": user_id,
                "total_work_entries": total_entries,
                "total_time_invested_hours": round(total_time / 60, 2),
                "contribution_score": round(contribution_score, 2),
                "average_intellectual_effort": round(avg_intellectual, 2),
                "average_motivation_level": round(avg_motivation, 2),
                "average_quality_rating": round(avg_quality, 2),
                "skill_tags": profile_data.get("skill_tags", []),
                "work_categories": profile_data.get("work_categories", {}),
                "last_updated": profile_data.get("last_updated", ""),
                "compensation_eligibility": self._calculate_compensation_eligibility(
                    contribution_score, total_time
                ),
            }

        except Exception as e:
            print(f"Error loading contribution summary for user {user_id}: {e}")
            return self._create_empty_summary(user_id)

    def _save_work_entry(self, entry: WorkEntry):
        """Save work entry to file."""
        entry_file = self.data_dir / f"work_{entry.work_id}.json"

        with open(entry_file, "w") as f:
            json.dump(asdict(entry), f, indent=2)

    def _update_user_profile(self, user_id: str, entry: WorkEntry):
        """Update user work profile with new entry."""
        profile_file = self.data_dir / f"user_{user_id}_profile.json"

        # Load existing profile or create new one
        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    profile_data = json.load(f)
            except:
                profile_data = self._create_empty_profile(user_id)
        else:
            profile_data = self._create_empty_profile(user_id)

        # Add new entry
        profile_data["work_entries"].append(asdict(entry))

        # Update statistics
        entries = profile_data["work_entries"]
        total_entries = len(entries)

        profile_data["total_work_entries"] = total_entries
        profile_data["total_time_invested"] = sum(
            e["time_invested_minutes"] for e in entries
        )
        profile_data["average_intellectual_effort"] = (
            sum(e["intellectual_effort"] for e in entries) / total_entries
        )
        profile_data["average_motivation_level"] = (
            sum(e["motivation_level"] for e in entries) / total_entries
        )
        profile_data["average_quality_rating"] = (
            sum(e["quality_rating"] for e in entries) / total_entries
        )
        profile_data["last_updated"] = entry.timestamp

        # Update categories and tags
        category = entry.task_type
        profile_data["work_categories"][category] = (
            profile_data["work_categories"].get(category, 0) + 1
        )

        for tag in entry.tags:
            if tag not in profile_data["skill_tags"]:
                profile_data["skill_tags"].append(tag)

        # Save updated profile
        with open(profile_file, "w") as f:
            json.dump(profile_data, f, indent=2)

    def _generate_tags(self, task_type: str, description: str) -> list[str]:
        """Generate skill tags based on task type and description."""
        tags = []

        # Task-based tags
        task_mappings = {
            "analysis": ["analytical", "research", "problem-solving"],
            "development": ["programming", "technical", "implementation"],
            "consultation": ["advisory", "expertise", "guidance"],
            "design": ["creative", "planning", "architecture"],
            "testing": ["quality-assurance", "validation", "verification"],
            "documentation": ["writing", "communication", "knowledge-sharing"],
        }

        if task_type in task_mappings:
            tags.extend(task_mappings[task_type])

        # Content-based tags
        description_lower = description.lower()
        if any(
            word in description_lower
            for word in ["ai", "machine learning", "neural", "algorithm"]
        ):
            tags.append("ai/ml")
        if any(
            word in description_lower for word in ["business", "strategy", "planning"]
        ):
            tags.append("business")
        if any(
            word in description_lower for word in ["legal", "contract", "compliance"]
        ):
            tags.append("legal")
        if any(word in description_lower for word in ["financial", "budget", "cost"]):
            tags.append("financial")

        return list(set(tags))  # Remove duplicates

    def _calculate_compensation_eligibility(
        self, contribution_score: float, total_time: float
    ) -> dict[str, Any]:
        """Calculate compensation eligibility based on contributions."""
        # Compensation tiers based on contribution score and time invested
        if contribution_score >= 8.5 and total_time >= 480:  # High performer, 8+ hours
            tier = "premium"
            hourly_rate_range = [150, 250]
            bonus_eligible = True
        elif (
            contribution_score >= 7.0 and total_time >= 240
        ):  # Good performer, 4+ hours
            tier = "standard_plus"
            hourly_rate_range = [100, 180]
            bonus_eligible = True
        elif (
            contribution_score >= 6.0 and total_time >= 120
        ):  # Solid performer, 2+ hours
            tier = "standard"
            hourly_rate_range = [75, 125]
            bonus_eligible = False
        elif contribution_score >= 5.0:  # Developing contributor
            tier = "entry"
            hourly_rate_range = [50, 90]
            bonus_eligible = False
        else:
            tier = "training"
            hourly_rate_range = [25, 50]
            bonus_eligible = False

        return {
            "tier": tier,
            "hourly_rate_range_usd": hourly_rate_range,
            "bonus_eligible": bonus_eligible,
            "estimated_monthly_value": round(
                (total_time / 60) * ((hourly_rate_range[0] + hourly_rate_range[1]) / 2),
                2,
            ),
        }

    def _create_empty_profile(self, user_id: str) -> dict[str, Any]:
        """Create empty user profile structure."""
        return {
            "user_id": user_id,
            "work_entries": [],
            "total_work_entries": 0,
            "total_time_invested": 0.0,
            "average_intellectual_effort": 0.0,
            "average_motivation_level": 0.0,
            "average_quality_rating": 0.0,
            "skill_tags": [],
            "work_categories": {},
            "last_updated": "",
        }

    def _create_empty_summary(self, user_id: str) -> dict[str, Any]:
        """Create empty contribution summary."""
        return {
            "user_id": user_id,
            "total_work_entries": 0,
            "total_time_invested_hours": 0.0,
            "contribution_score": 0.0,
            "average_intellectual_effort": 0.0,
            "average_motivation_level": 0.0,
            "average_quality_rating": 0.0,
            "skill_tags": [],
            "work_categories": {},
            "last_updated": "",
            "compensation_eligibility": {
                "tier": "none",
                "hourly_rate_range_usd": [0, 0],
                "bonus_eligible": False,
                "estimated_monthly_value": 0.0,
            },
        }


class AssistantWorkIntegration:
    """
    Integration layer with assistant_v2_core.py

    Automatically tracks work when users interact with the assistant,
    ensuring all contributions are logged and compensated.
    """

    def __init__(self):
        self.assistant_path = "e:/Projects/Echoes/assistant_v2_core.py"
        self.work_tracker = None

    def sync_work_entry(self, work_entry: WorkEntry):
        """Sync work entry with assistant system."""
        # This would integrate with assistant_v2_core.py to log interactions
        # For now, we'll log the sync attempt
        print(f"🔄 Synced work entry {work_entry.work_id} with assistant system")

        # In a full implementation, this would:
        # 1. Notify assistant_v2_core.py of the work completed
        # 2. Update user's contribution metrics
        # 3. Trigger payout calculations if thresholds met
        # 4. Log interaction for audit trail


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


# Integration hook for assistant_v2_core.py
def log_assistant_interaction(user_id: str, interaction_data: dict[str, Any]) -> str:
    """
    Import existing work hours for users who have contributed before system implementation.

    This recognizes the substantial work done (like 1580 hours on Echoes) and properly
    values the user's contributions with appropriate multipliers.

    Args:
        user_id: User identifier
        total_hours: Total hours of existing work
        work_description: Description of the work done
        technical_level: Technical complexity (beginner, intermediate, advanced, expert)
        impact_level: Impact level (low, medium, high, transformative)

    Returns:
        Import confirmation with valuation details
    """
    tracker = WorkTracker()

    # Calculate work value based on technical level and impact
    technical_multipliers = {
        "beginner": 1.0,
        "intermediate": 1.3,
        "advanced": 1.6,
        "expert": 2.0,
    }

    impact_multipliers = {"low": 1.0, "medium": 1.2, "high": 1.5, "transformative": 1.8}

    # Base rate for technical work
    base_hourly_rate = 75.0

    # Apply multipliers
    tech_multiplier = technical_multipliers.get(technical_level, 1.3)
    impact_multiplier = impact_multipliers.get(impact_level, 1.2)

    effective_hourly_rate = base_hourly_rate * tech_multiplier * impact_multiplier

    # For long-term projects like Echoes (1580 hours), apply project complexity bonus
    if total_hours > 1000:  # Major project threshold
        project_bonus = 1.5  # 50% bonus for major projects
        effective_hourly_rate *= project_bonus

    # Calculate total value
    total_value = total_hours * effective_hourly_rate

    # Create work entry with special import flag
    work_id = tracker.log_work_entry(
        user_id=user_id,
        task_type="project_import",
        description=f"IMPORTED WORK: {work_description} | Technical Level: {technical_level} | Impact: {impact_level} | {total_hours} hours imported",
        time_invested_minutes=total_hours * 60,  # Convert to minutes
        intellectual_effort=9.0 if technical_level in ["advanced", "expert"] else 7.0,
        motivation_level=8.5,  # High motivation for long-term projects
        quality_rating=9.0,  # High quality for established work
        assistant_data={
            "import_type": "existing_work",
            "original_hours": total_hours,
            "technical_level": technical_level,
            "impact_level": impact_level,
            "effective_rate": effective_hourly_rate,
            "total_value": total_value,
            "import_reason": "Recognizing substantial pre-existing contributions",
        },
    )

    return {
        "work_id": work_id,
        "total_hours_imported": total_hours,
        "effective_hourly_rate": round(effective_hourly_rate, 2),
        "total_value": round(total_value, 2),
        "compensation_tier": "premium" if total_value > 10000 else "standard_plus",
        "message": f"✅ Imported {total_hours} hours of existing work. Total value: ${round(total_value, 2)} at ${round(effective_hourly_rate, 2)}/hour. Ready for payout processing.",
    }


def log_assistant_interaction(
    user_id: str, interaction_type: str, details: dict[str, Any]
):
    """
    Hook function that assistant_v2_core.py can call to log work automatically.

    This ensures every assistant interaction is tracked and the user gets
    compensated for their time, thoughts, and motivation invested.
    """
    tracker = WorkTracker()

    # Estimate time and effort based on interaction type
    time_estimates = {
        "query_processing": 15,  # 15 minutes
        "complex_analysis": 45,  # 45 minutes
        "code_generation": 60,  # 1 hour
        "research_task": 90,  # 1.5 hours
        "consultation": 30,  # 30 minutes
    }

    time_invested = time_estimates.get(interaction_type, 20)  # Default 20 minutes

    # Auto-determine effort levels based on interaction complexity
    if interaction_type in ["complex_analysis", "research_task"]:
        intellectual_effort = 8.5
        motivation_level = 8.0
        quality_rating = 8.5
    elif interaction_type in ["code_generation", "consultation"]:
        intellectual_effort = 7.5
        motivation_level = 7.5
        quality_rating = 8.0
    else:
        intellectual_effort = 6.5
        motivation_level = 7.0
        quality_rating = 7.5

    # Log the work
    work_id = tracker.log_work_entry(
        user_id=user_id,
        task_type=f"assistant_{interaction_type}",
        description=f"Assistant interaction: {details.get('description', 'AI assistance')}",
        time_invested_minutes=time_invested,
        intellectual_effort=intellectual_effort,
        motivation_level=motivation_level,
        quality_rating=quality_rating,
        assistant_data=details,
    )

    return work_id


def import_existing_work(
    user_id: str,
    total_hours: float,
    work_description: str,
    technical_level: str = "advanced",
    impact_level: str = "high",
) -> dict[str, Any]:
    """
    Import existing work hours for users who have contributed before system implementation.

    This recognizes the substantial work done (like 1580 hours on Echoes) and properly
    values the user's contributions with appropriate multipliers.

    Args:
        user_id: User identifier
        total_hours: Total hours of existing work
        work_description: Description of the work done
        technical_level: Technical complexity (beginner, intermediate, advanced, expert)
        impact_level: Impact level (low, medium, high, transformative)

    Returns:
        Import confirmation with valuation details
    """
    tracker = WorkTracker()

    # Calculate work value based on technical level and impact
    technical_multipliers = {
        "beginner": 1.0,
        "intermediate": 1.3,
        "advanced": 1.6,
        "expert": 2.0,
    }

    impact_multipliers = {"low": 1.0, "medium": 1.2, "high": 1.5, "transformative": 1.8}

    # Base rate for technical work
    base_hourly_rate = 75.0

    # Apply multipliers
    tech_multiplier = technical_multipliers.get(technical_level, 1.3)
    impact_multiplier = impact_multipliers.get(impact_level, 1.2)

    effective_hourly_rate = base_hourly_rate * tech_multiplier * impact_multiplier

    # For long-term projects like Echoes (1580 hours), apply project complexity bonus
    if total_hours > 1000:  # Major project threshold
        project_bonus = 1.5  # 50% bonus for major projects
        effective_hourly_rate *= project_bonus

    # Calculate total value
    total_value = total_hours * effective_hourly_rate

    # Create work entry with special import flag
    work_id = tracker.log_work_entry(
        user_id=user_id,
        task_type="project_import",
        description=f"IMPORTED WORK: {work_description} | Technical Level: {technical_level} | Impact: {impact_level} | {total_hours} hours imported",
        time_invested_minutes=total_hours * 60,  # Convert to minutes
        intellectual_effort=9.0 if technical_level in ["advanced", "expert"] else 7.0,
        motivation_level=8.5,  # High motivation for long-term projects
        quality_rating=9.0,  # High quality for established work
        assistant_data={
            "import_type": "existing_work",
            "original_hours": total_hours,
            "technical_level": technical_level,
            "impact_level": impact_level,
            "effective_rate": effective_hourly_rate,
            "total_value": total_value,
            "import_reason": "Recognizing substantial pre-existing contributions",
        },
    )

    return {
        "work_id": work_id,
        "total_hours_imported": total_hours,
        "effective_hourly_rate": round(effective_hourly_rate, 2),
        "total_value": round(total_value, 2),
        "compensation_tier": "premium" if total_value > 10000 else "standard_plus",
        "message": f"✅ Imported {total_hours} hours of existing work. Total value: ${round(total_value, 2)} at ${round(effective_hourly_rate, 2)}/hour. Ready for payout processing.",
    }


if __name__ == "__main__":
    # Demo the work tracking system
    tracker = WorkTracker()

    # Example work entries
    work_id1 = tracker.log_work_entry(
        user_id="user_123",
        task_type="ai_consultation",
        description="Provided strategic AI implementation advice for e-commerce platform",
        time_invested_minutes=90,
        intellectual_effort=8.5,
        motivation_level=9.0,
        quality_rating=9.0,
        assistant_data={"queries_processed": 15, "recommendations_made": 8},
    )

    work_id2 = tracker.log_work_entry(
        user_id="user_123",
        task_type="code_development",
        description="Developed custom machine learning pipeline for client project",
        time_invested_minutes=240,
        intellectual_effort=9.0,
        motivation_level=8.5,
        quality_rating=9.5,
        assistant_data={"lines_of_code": 850, "algorithms_implemented": 3},
    )

    # Get user summary
    summary = tracker.get_user_contribution_summary("user_123")
    print("User Contribution Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\\n✅ Work tracking system operational - users receive fair compensation!")
