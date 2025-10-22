"""
Action Executor for EchoesAssistantV2

Enables the assistant to take autonomous actions:
- Execute inventory operations (ATLAS)
- Call external tools
- Track action results
- Provide feedback to the assistant
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ActionResult:
    """Result of an executed action."""
    action_id: str
    action_type: str
    status: str  # success, failed, pending
    result: Any
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ActionExecutor:
    """Executes actions on behalf of the assistant."""

    def __init__(self):
        self.action_history: List[ActionResult] = []
        self.action_counter = 0

    def execute_inventory_action(
        self,
        action_type: str,
        **kwargs
    ) -> ActionResult:
        """Execute an inventory action via ATLAS."""
        self.action_counter += 1
        action_id = f"action_{self.action_counter}"
        start_time = time.time()

        try:
            # Import ATLAS service
            from ATLAS.service import InventoryService

            svc = InventoryService()
            result_data = None

            # Execute based on action type
            if action_type == "add_item":
                result_data = svc.add_item(
                    sku=kwargs.get("sku"),
                    name=kwargs.get("name"),
                    category=kwargs.get("category"),
                    quantity=int(kwargs.get("quantity", 0)),
                    location=kwargs.get("location"),
                    min_stock=int(kwargs.get("min_stock", 0)),
                    max_stock=int(kwargs.get("max_stock", 0)),
                ).to_dict()

            elif action_type == "list_items":
                items = svc.list_items(
                    category=kwargs.get("category"),
                    location=kwargs.get("location"),
                )
                result_data = [i.to_dict() for i in items]

            elif action_type == "adjust_quantity":
                result_data = svc.adjust_quantity(
                    sku=kwargs.get("sku"),
                    delta=int(kwargs.get("delta", 0)),
                ).to_dict()

            elif action_type == "move_item":
                result_data = svc.move_item(
                    sku=kwargs.get("sku"),
                    new_location=kwargs.get("new_location"),
                ).to_dict()

            elif action_type == "report":
                result_data = svc.report(
                    report_type=kwargs.get("report_type", "summary")
                )

            else:
                raise ValueError(f"Unknown inventory action: {action_type}")

            duration_ms = (time.time() - start_time) * 1000
            result = ActionResult(
                action_id=action_id,
                action_type=action_type,
                status="success",
                result=result_data,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = ActionResult(
                action_id=action_id,
                action_type=action_type,
                status="failed",
                result=None,
                error=str(e),
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        self.action_history.append(result)
        return result

    def execute_tool_action(
        self,
        tool_name: str,
        **kwargs
    ) -> ActionResult:
        """Execute a tool action via the tool registry."""
        self.action_counter += 1
        action_id = f"action_{self.action_counter}"
        start_time = time.time()

        try:
            from tools.registry import get_registry

            registry = get_registry()
            if not registry.has_tool(tool_name):
                raise ValueError(f"Tool '{tool_name}' not found in registry")

            result_data = registry.execute(tool_name, **kwargs)

            duration_ms = (time.time() - start_time) * 1000
            result = ActionResult(
                action_id=action_id,
                action_type=f"tool:{tool_name}",
                status="success" if result_data.success else "failed",
                result=result_data.data if result_data.success else result_data.error,
                error=None if result_data.success else result_data.error,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = ActionResult(
                action_id=action_id,
                action_type=f"tool:{tool_name}",
                status="failed",
                result=None,
                error=str(e),
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        self.action_history.append(result)
        return result

    def get_action_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get action history."""
        history = self.action_history
        if limit:
            history = history[-limit:]
        return [a.to_dict() for a in history]

    def get_action_summary(self) -> Dict[str, Any]:
        """Get summary of actions executed."""
        total = len(self.action_history)
        successful = sum(1 for a in self.action_history if a.status == "success")
        failed = sum(1 for a in self.action_history if a.status == "failed")
        avg_duration = (
            sum(a.duration_ms for a in self.action_history) / total
            if total > 0
            else 0
        )

        return {
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "avg_duration_ms": avg_duration,
        }
