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
Weekly Planning Task

Integrates with the weekly planning system to provide automated planning features.
"""

from typing import Optional

from automation.core.context import Context
from automation.core.logger import AutomationLogger
from automation.core.weekly_plan import PlanStatus, WeeklyPlan
from automation.notifications.notify import Notifier


class WeeklyPlanningTask:
    """Task for managing weekly planning workflow."""

    def __init__(self, context: Optional[Context] = None):
        self.ctx = context or Context()
        self.log = AutomationLogger()
        self.plan = WeeklyPlan(context)

    def run(self):
        """Run the weekly planning task."""
        if self.ctx.extra_data.get("action") == "review":
            return self._generate_review()
        elif self.ctx.extra_data.get("remind"):
            return self._send_reminders()
        else:
            return self._show_status()

    def _generate_review(self) -> str:
        """Generate and return the weekly review."""
        review = self.plan.weekly_review()

        # Notify about the review
        Notifier.notify(
            "Weekly Review Ready",
            "Your weekly review is ready. Check the logs for details.",
        )

        return review

    def _send_reminders(self) -> str:
        """Send reminders for pending items."""
        pending = [i for i in self.plan.plan["focus_areas"] if i["status"] == PlanStatus.PENDING.value]

        if not pending:
            return "No pending items to remind about."

        message = "Pending Focus Areas:\n"
        for item in pending:
            message += f"- [{item['id']}] {item['area']}: {', '.join(item['key_outcomes'][:2])}\n"

        Notifier.notify(
            "Weekly Priorities Reminder",
            f"You have {len(pending)} pending focus areas this week.",
        )

        return message

    def _show_status(self) -> str:
        """Show the current status of the weekly plan."""
        plan = self.plan.plan
        completed = len(plan["completed_items"])
        pending = len([i for i in plan["focus_areas"] if i["status"] != PlanStatus.COMPLETED.value])

        status = f"Weekly Plan - {plan['week_start']}\n" f"✓ Completed: {completed} | ⏳ Pending: {pending}\n"

        if pending > 0:
            status += "\nCurrent Focus Areas:\n"
            for item in plan["focus_areas"]:
                if item["status"] != PlanStatus.COMPLETED.value:
                    status += f"- [{item['id']}] {item['area']}\n" f"  → {', '.join(item['key_outcomes'][:2])}\n"

        if plan["constraints"]:
            status += "\nConstraints:\n"
            for c in plan["constraints"][-3:]:  # Show only 3 most recent
                status += f"- {c['constraint']}\n"

        return status


def register_tasks():
    """Register tasks with the task registry."""
    from automation.core.task_registry import TaskRegistry

    def plan_weekly(ctx):
        task = WeeklyPlanningTask(ctx)
        return task.run()

    TaskRegistry.register("weekly_plan", plan_weekly)


# Register tasks when module is imported
register_tasks()
