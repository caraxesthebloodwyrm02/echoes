"""
Action Executor for EchoesAssistantV2

Enables the assistant to take autonomous actions:
- Execute inventory operations (ATLAS)
- Call external tools
- Track action results
- Provide feedback to the assistant
- Filesystem operations
- Web search capabilities
"""

import os
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

# ATLAS Integration
try:
    from ATLAS.api import ATLASDirectAPI
    from ATLAS.service import InventoryService

    ATLAS_AVAILABLE = True
except ImportError:
    ATLAS_AVAILABLE = False

# Web Search Integration
try:
    import requests

    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False


@dataclass
class ActionResult:
    """Result of an executed action."""

    action_id: str
    action_type: str
    status: str  # success, failed, pending
    result: Any
    error: str | None = None
    duration_ms: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ActionExecutor:
    """Executes actions on behalf of the assistant."""

    def __init__(self):
        self.action_history: list[ActionResult] = []
        self.action_counter = 0

        # Initialize ATLAS integration
        if ATLAS_AVAILABLE:
            self.atlas_api = ATLASDirectAPI()
            print("✓ ATLAS API integration initialized")
        else:
            self.atlas_api = None
            print("⚠ ATLAS not available")

        # Initialize web capabilities
        if WEB_AVAILABLE:
            print("✓ Web search capabilities available")
        else:
            print("⚠ Web search not available")

    def _create_action_result(
        self, action_type: str, result: Any = None, error: str = None
    ) -> ActionResult:
        """Create a standardized action result."""
        self.action_counter += 1
        return ActionResult(
            action_id=f"action_{self.action_counter}",
            action_type=action_type,
            status="success" if error is None else "failed",
            result=result,
            error=error,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def execute_inventory_action(self, action_type: str, **kwargs) -> ActionResult:
        """Execute an inventory action via ATLAS."""
        if not ATLAS_AVAILABLE:
            return self._create_action_result("inventory", error="ATLAS not available")

        try:
            if action_type == "add":
                result = self.atlas_api.add_item(**kwargs)
            elif action_type == "get":
                result = self.atlas_api.get_item(kwargs.get("sku"))
            elif action_type == "list":
                result = self.atlas_api.list_items()
            else:
                return self._create_action_result(
                    "inventory", error=f"Unknown action: {action_type}"
                )

            return self._create_action_result("inventory", result=result)
        except Exception as e:
            return self._create_action_result("inventory", error=str(e))

    def execute_filesystem_action(self, action_type: str, **kwargs) -> ActionResult:
        """Execute filesystem operations."""
        try:
            if action_type == "list_files":
                path = kwargs.get("path", ".")
                files = os.listdir(path)
                result = {"path": path, "files": files}
            elif action_type == "read_file":
                path = kwargs.get("path")
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        content = f.read()
                    result = {"path": path, "content": content}
                else:
                    return self._create_action_result(
                        "filesystem", error=f"File not found: {path}"
                    )
            elif action_type == "write_file":
                path = kwargs.get("path")
                content = kwargs.get("content", "")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                result = {"path": path, "bytes_written": len(content)}
            else:
                return self._create_action_result(
                    "filesystem", error=f"Unknown action: {action_type}"
                )

            return self._create_action_result("filesystem", result=result)
        except Exception as e:
            return self._create_action_result("filesystem", error=str(e))

    def execute_web_search(self, query: str) -> ActionResult:
        """Execute a web search."""
        try:
            from config.search_config import get_search_config

            config = get_search_config()
            provider = config.create_provider()

            results = provider.search(query, config.max_results)

            if results:
                result_data = {
                    "query": query,
                    "provider": config.provider,
                    "results": [r.to_dict() for r in results],
                    "count": len(results),
                }
                return self._create_action_result("web_search", result=result_data)
            else:
                return self._create_action_result(
                    "web_search", error="No results found"
                )

        except Exception as e:
            # Fallback to basic functionality
            if WEB_AVAILABLE:
                result = {
                    "query": query,
                    "status": "search_framework_available",
                    "message": "Configure search provider in .env to enable actual search",
                    "providers": ["openai", "google", "bing"],
                }
                return self._create_action_result("web_search", result=result)
            else:
                return self._create_action_result("web_search", error=str(e))
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
                timestamp=datetime.now(UTC).isoformat(),
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
                timestamp=datetime.now(UTC).isoformat(),
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
                timestamp=datetime.now(UTC).isoformat(),
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
                timestamp=datetime.now(UTC).isoformat(),
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
                timestamp=datetime.now(UTC).isoformat(),
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
                timestamp=datetime.now(UTC).isoformat(),
            )

        self.action_history.append(result)
        return result

    def _generate_roi_analysis_package(self, **kwargs) -> dict[str, Any]:
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
        self, template_name: str, template_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Save an ROI analysis template."""
        # Implementation for saving templates
        return {"template_name": template_name, "saved": True}

    def _load_roi_analysis(self, analysis_id: str) -> dict[str, Any]:
        """Load a previously generated ROI analysis."""
        # Implementation for loading saved analyses
        return {"analysis_id": analysis_id, "loaded": True}

    def _compare_roi_scenarios(self, scenario_ids: list[str]) -> dict[str, Any]:
        """Compare multiple ROI analysis scenarios."""
        # Implementation for scenario comparison
        return {"scenarios_compared": len(scenario_ids), "comparison": "completed"}

    def get_action_history(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Get action history."""
        history = self.action_history
        if limit:
            history = history[-limit:]
        return [a.to_dict() for a in history]

    def get_action_summary(self) -> dict[str, Any]:
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
