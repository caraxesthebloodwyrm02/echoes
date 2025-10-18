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
Weekly Planning System based on System Thinking Principles

Implements a minimal-viable planning system focused on high-leverage actions
and automated progress tracking.
"""

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from automation.core.context import Context
from automation.core.logger import AutomationLogger
from automation.notifications.notify import Notifier

PLAN_FILE = Path("automation/cache/weekly_plan.json")
PLAN_FILE.parent.mkdir(parents=True, exist_ok=True)


class PlanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"


class WeeklyPlan:
    """Minimal planning system focused on high-leverage actions."""

    def __init__(self, context: Optional[Context] = None):
        self.ctx = context or Context()
        self.log = AutomationLogger()
        self.plan = self._load_plan()

    def _load_plan(self) -> Dict:
        """Load existing plan or create a new one."""
        if PLAN_FILE.exists():
            with open(PLAN_FILE, "r") as f:
                return json.load(f)
        return self._create_new_plan()

    def _create_new_plan(self) -> Dict:
        """Create a new weekly plan template."""
        return {
            "created_at": datetime.utcnow().isoformat(),
            "week_start": (
                datetime.now() - timedelta(days=datetime.now().weekday())
            ).strftime("%Y-%m-%d"),
            "focus_areas": [],
            "completed_items": [],
            "constraints": [],
            "review_notes": "",
        }

    def add_focus_area(
        self,
        area: str,
        key_outcomes: List[str],
        status: PlanStatus = PlanStatus.PENDING,
    ) -> None:
        """Add a focus area with key outcomes."""
        self.plan["focus_areas"].append(
            {
                "id": len(self.plan["focus_areas"]) + 1,
                "area": area,
                "key_outcomes": key_outcomes,
                "status": status.value,
                "created_at": datetime.utcnow().isoformat(),
            }
        )
        self._save_plan()

    def add_constraint(self, constraint: str) -> None:
        """Add a constraint to work within."""
        self.plan["constraints"].append(
            {"constraint": constraint, "added_at": datetime.utcnow().isoformat()}
        )
        self._save_plan()

    def mark_complete(self, item_id: int, notes: str = "") -> None:
        """Mark a focus area as completed."""
        for item in self.plan["focus_areas"]:
            if item["id"] == item_id:
                item["status"] = PlanStatus.COMPLETED.value
                item["completed_at"] = datetime.utcnow().isoformat()
                item["notes"] = notes

                # Move to completed
                self.plan["completed_items"].append(item)
                self.plan["focus_areas"] = [
                    i for i in self.plan["focus_areas"] if i["id"] != item_id
                ]

                # Send completion notification
                Notifier.notify("Task Completed", f"✓ {item['area']} - {notes}")
                break
        self._save_plan()

    def weekly_review(self) -> str:
        """Generate a weekly review and prepare for next week."""
        completed = len(self.plan["completed_items"])
        pending = len(
            [i for i in self.plan["focus_areas"] if i["status"] != PlanStatus.COMPLETED]
        )

        review = (
            f"Weekly Review - {self.plan['week_start']}\n"
            f"Completed: {completed} | Pending: {pending}\n"
            "\nKey Learnings:\n"
            f"{self.plan.get('review_notes', 'No notes added.')}"
        )

        # Archive current plan
        archive_file = f"automation/cache/plans/review_{self.plan['week_start']}.json"
        Path(archive_file).parent.mkdir(exist_ok=True)
        with open(archive_file, "w") as f:
            json.dump(self.plan, f, indent=2)

        # Start fresh
        self.plan = self._create_new_plan()
        self._save_plan()

        return review

    def _save_plan(self) -> None:
        """Save the current plan to disk."""
        with open(PLAN_FILE, "w") as f:
            json.dump(self.plan, f, indent=2)


# CLI Interface
def cli():
    """Command-line interface for weekly planning."""
    import argparse

    parser = argparse.ArgumentParser(description="Weekly Planning System")
    subparsers = parser.add_subparsers(dest="command")

    # Add focus area
    add_parser = subparsers.add_parser("add", help="Add a focus area")
    add_parser.add_argument("area", help="Name of focus area")
    add_parser.add_argument("--outcomes", nargs="+", help="Key outcomes", required=True)

    # Complete item
    complete_parser = subparsers.add_parser("complete", help="Mark item as complete")
    complete_parser.add_argument("item_id", type=int, help="ID of item to complete")
    complete_parser.add_argument("--notes", help="Completion notes", default="")

    # Weekly review
    subparsers.add_parser("review", help="Generate weekly review")

    args = parser.parse_args()
    plan = WeeklyPlan()

    if args.command == "add":
        plan.add_focus_area(args.area, args.outcomes)
        print(f"✓ Added focus area: {args.area}")
    elif args.command == "complete":
        plan.mark_complete(args.item_id, args.notes)
        print(f"✓ Marked item {args.item_id} as complete")
    elif args.command == "review":
        print(plan.weekly_review())
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()
