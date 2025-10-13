""
Weekly Planning Task

Integrates with the weekly planning system to provide automated planning features.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from automation.core.context import Context
from automation.core.logger import AutomationLogger
from automation.core.weekly_plan import WeeklyPlan, PlanStatus
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
            "Your weekly review is ready. Check the logs for details."
        )
        
        return review
    
    def _send_reminders(self) -> str:
        """Send reminders for pending items."""
        pending = [i for i in self.plan.plan["focus_areas"] 
                  if i["status"] == PlanStatus.PENDING.value]
        
        if not pending:
            return "No pending items to remind about."
        
        message = "Pending Focus Areas:\n"
        for item in pending:
            message += f"- [{item['id']}] {item['area']}: {', '.join(item['key_outcomes'][:2])}\n"
        
        Notifier.notify(
            "Weekly Priorities Reminder",
            f"You have {len(pending)} pending focus areas this week."
        )
        
        return message
    
    def _show_status(self) -> str:
        """Show the current status of the weekly plan."""
        plan = self.plan.plan
        completed = len(plan["completed_items"])
        pending = len([i for i in plan["focus_areas"] 
                      if i["status"] != PlanStatus.COMPLETED.value])
        
        status = (
            f"Weekly Plan - {plan['week_start']}\n"
            f"✓ Completed: {completed} | ⏳ Pending: {pending}\n"
        )
        
        if pending > 0:
            status += "\nCurrent Focus Areas:\n"
            for item in plan["focus_areas"]:
                if item["status"] != PlanStatus.COMPLETED.value:
                    status += (
                        f"- [{item['id']}] {item['area']}\n"
                        f"  → {', '.join(item['key_outcomes'][:2])}\n"
                    )
        
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
