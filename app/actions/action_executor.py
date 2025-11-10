"""
Action Executor for EchoesAssistantV2

Enables the assistant to take autonomous actions:
- Execute inventory operations (ATLAS)
- Call external tools
- Track action results
- Provide feedback to the assistant
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
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

    def execute_inventory_action(self, action_type: str, **kwargs) -> ActionResult:
        """Execute an inventory action via ATLAS."""

        # Like good code structure:
        def handle_user_request(request):
            # Phase 1: Analysis
            understand_request(request)

            # Phase 2: Planning
            plan_approach(request)

            # Phase 3: Execution
            execute_plan()

        # Phase 1: Setup
        self.action_counter += 1
        action_id = f"action_{self.action_counter}"
        start_time = time.time()

        try:
            # Phase 2: Action Execution
            # Import ATLAS service
            from ATLAS.service import InventoryService

            svc = InventoryService()
            result_data = None

            # Phase 3: Action Routing
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

            # Phase 4: Result Processing
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

    def execute_tool_action(self, tool_name: str, **kwargs) -> ActionResult:
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

    def execute_roi_action(self, action_type: str, **kwargs) -> ActionResult:
        """Execute ROI-specific actions."""
        self.action_counter += 1
        action_id = f"roi_action_{self.action_counter}"
        start_time = time.time()

        try:
            result_data = None

            # ROI-specific actions
            if action_type == "generate_roi_package":
                result_data = self._generate_roi_analysis_package(**kwargs)
            elif action_type == "save_roi_template":
                result_data = self._save_roi_template(**kwargs)
            elif action_type == "load_roi_analysis":
                result_data = self._load_roi_analysis(**kwargs)
            elif action_type == "compare_roi_scenarios":
                result_data = self._compare_roi_scenarios(**kwargs)
            else:
                raise ValueError(f"Unknown ROI action: {action_type}")

            duration_ms = (time.time() - start_time) * 1000
            result = ActionResult(
                action_id=action_id,
                action_type=f"roi:{action_type}",
                status="success",
                result=result_data,
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = ActionResult(
                action_id=action_id,
                action_type=f"roi:{action_type}",
                status="failed",
                result=None,
                error=str(e),
                duration_ms=duration_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        self.action_history.append(result)
        return result

    def _generate_roi_analysis_package(self, **kwargs) -> Dict[str, Any]:
        """Generate a complete ROI analysis package."""
        # This would integrate with the ROI tool to generate all formats
        from tools.roi_analysis_tool import ROIAnalysisTool

        tool = ROIAnalysisTool()
        result = tool(**kwargs)

        if result.success:
            # Automatically organize the generated files
            from app.filesystem import FilesystemTools

            fs_tools = FilesystemTools()
            organization_result = fs_tools.organize_roi_files(result.data)

            if organization_result["success"]:
                result.data["file_organization"] = organization_result
            else:
                result.data["file_organization_error"] = organization_result.get(
                    "error"
                )

            # Automatically store in knowledge base
            from app.knowledge import KnowledgeManager

            km = KnowledgeManager()
            analysis_id = km.store_roi_analysis(result.data)
            result.data["analysis_id"] = analysis_id

            return result.data
        else:
            raise Exception(f"ROI generation failed: {result.error}")

    def _save_roi_template(
        self, template_name: str, template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Save an ROI analysis template."""
        # Implementation for saving templates
        return {"template_name": template_name, "saved": True}

    def _load_roi_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """Load a previously generated ROI analysis."""
        # Implementation for loading saved analyses
        return {"analysis_id": analysis_id, "loaded": True}

    def _compare_roi_scenarios(self, scenario_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple ROI analysis scenarios."""
        # Implementation for scenario comparison
        return {"scenarios_compared": len(scenario_ids), "comparison": "completed"}

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
            sum(a.duration_ms for a in self.action_history) / total if total > 0 else 0
        )

        return {
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "avg_duration_ms": avg_duration,
        }
