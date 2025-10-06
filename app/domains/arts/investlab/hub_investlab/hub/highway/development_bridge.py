#!/usr/bin/env python3
"""
Highway Development Bridge - Integration with E:\projects\development
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from highway import Highway, DataType


class HighwayDevelopmentBridge:
    """Bridge between Unified Hub and E:\projects\development"""

    def __init__(self):
        self.external_path = None  # E:\ integration disabled for optimization
        self.internal_path = "D:\\hub\\hub"
        self.sync_log = []
        self.adaptation_rules = {}
        self.learning_cache = {}

        # Skip external path setup (E:\ integration disabled)
        self._initialize_adaptation_rules()

    def _ensure_external_path(self):
        """Ensure the external development path exists"""
        os.makedirs(self.external_path, exist_ok=True)
        os.makedirs(os.path.join(self.external_path, "highway_sync"), exist_ok=True)
        os.makedirs(os.path.join(self.external_path, "insights_cache"), exist_ok=True)
        os.makedirs(os.path.join(self.external_path, "code_advancements"), exist_ok=True)

    def _initialize_adaptation_rules(self):
        """Initialize rules for adapting external code to internal modules"""
        self.adaptation_rules = {
            "ai_models": {
                "source": "research",
                "target": "external",
                "adaptation": self._adapt_ai_models,
            },
            "financial_strategies": {
                "source": "finance",
                "target": "external",
                "adaptation": self._adapt_financial_strategies,
            },
            "content_templates": {
                "source": "content",
                "target": "external",
                "adaptation": self._adapt_content_templates,
            },
            "research_insights": {
                "source": "external",
                "target": "research",
                "adaptation": self._adapt_research_insights,
            },
            "development_patterns": {
                "source": "external",
                "target": "insights",
                "adaptation": self._adapt_development_patterns,
            },
        }

    def sync_with_external_projects(self) -> Dict[str, Any]:
        """Sync with external development projects"""
        sync_result = {
            "timestamp": datetime.now().isoformat(),
            "projects_found": 0,
            "files_synced": 0,
            "insights_generated": 0,
            "advancements_applied": 0,
        }

        try:
            # Scan external projects
            projects = self._scan_external_projects()
            sync_result["projects_found"] = len(projects)

            for project in projects:
                project_data = self._analyze_project(project)
                sync_result["files_synced"] += project_data["files_processed"]

                # Generate insights from project
                insights = self._generate_project_insights(project_data)
                sync_result["insights_generated"] += len(insights)

                # Apply advancements to internal modules
                advancements = self._apply_project_advancements(project_data)
                sync_result["advancements_applied"] += len(advancements)

            # Send sync results via highway
            self._send_sync_results(sync_result)

        except Exception as e:
            logger.error(f"External sync failed: {str(e)}")
            sync_result["error"] = str(e)

        return sync_result

    def _scan_external_projects(self) -> List[Dict[str, Any]]:
        """Scan external development projects"""
        projects = []

        if not os.path.exists(self.external_path):
            return projects

        for item in os.listdir(self.external_path):
            item_path = os.path.join(self.external_path, item)
            if os.path.isdir(item_path) and not item.startswith("."):
                project_info = {
                    "name": item,
                    "path": item_path,
                    "files": [],
                    "insights": {},
                    "last_modified": datetime.fromtimestamp(os.path.getmtime(item_path)),
                }

                # Scan project files
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if file.endswith((".py", ".js", ".ts", ".md", ".json")):
                            file_path = os.path.join(root, file)
                            file_info = {
                                "name": file,
                                "path": file_path,
                                "size": os.path.getsize(file_path),
                                "last_modified": datetime.fromtimestamp(
                                    os.path.getmtime(file_path)
                                ),
                            }
                            project_info["files"].append(file_info)

                projects.append(project_info)

        return projects

    def _analyze_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a project for insights and patterns"""
        analysis = {
            "project_name": project["name"],
            "total_files": len(project["files"]),
            "code_patterns": {},
            "ai_applications": [],
            "financial_implications": [],
            "content_opportunities": [],
            "files_processed": 0,
        }

        for file_info in project["files"]:
            try:
                with open(file_info["path"], "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # Analyze for AI patterns
                    if "ai" in content.lower() or "ml" in content.lower():
                        analysis["ai_applications"].append(file_info["name"])

                    # Analyze for financial patterns
                    if any(
                        word in content.lower() for word in ["finance", "money", "budget", "invest"]
                    ):
                        analysis["financial_implications"].append(file_info["name"])

                    # Analyze for content opportunities
                    if any(
                        word in content.lower()
                        for word in ["content", "media", "publish", "create"]
                    ):
                        analysis["content_opportunities"].append(file_info["name"])

                    # Extract code patterns
                    patterns = self._extract_code_patterns(content, file_info["name"])
                    analysis["code_patterns"].update(patterns)

                    analysis["files_processed"] += 1
            except Exception as e:
                logger.warning(f"Could not analyze file {file_info['name']}: {str(e)}")

        return analysis

    def _extract_code_patterns(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract useful code patterns and insights"""
        patterns = {"functions": [], "classes": [], "libraries": [], "algorithms": []}

        # Simple pattern extraction (can be enhanced with AST parsing)
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("def "):
                patterns["functions"].append(line.split("def ")[1].split("(")[0])
            elif line.startswith("class "):
                patterns["classes"].append(line.split("class ")[1].split("(")[0].split(":")[0])
            elif "import " in line:
                patterns["libraries"].append(line.strip())

        return patterns

    def _generate_project_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable insights from project analysis"""
        insights = []

        # AI insights
        if analysis["ai_applications"]:
            insights.append(
                {
                    "type": "ai_insight",
                    "category": "research",
                    "description": f"Project {analysis['project_name']} uses AI in {len(analysis['ai_applications'])} files",
                    "files": analysis["ai_applications"],
                    "suggested_action": "integrate_with_research_module",
                }
            )

        # Financial insights
        if analysis["financial_implications"]:
            insights.append(
                {
                    "type": "financial_insight",
                    "category": "finance",
                    "description": f"Project {analysis['project_name']} has financial implications in {len(analysis['financial_implications'])} files",
                    "files": analysis["financial_implications"],
                    "suggested_action": "analyze_financial_impact",
                }
            )

        # Content insights
        if analysis["content_opportunities"]:
            insights.append(
                {
                    "type": "content_insight",
                    "category": "content",
                    "description": f"Project {analysis['project_name']} has content opportunities in {len(analysis['content_opportunities'])} files",
                    "files": analysis["content_opportunities"],
                    "suggested_action": "create_content_from_code",
                }
            )

        return insights

    def _apply_project_advancements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply project advancements to internal modules"""
        advancements = []

        for insight in self._generate_project_insights(analysis):
            advancement = self._create_advancement_from_insight(insight)
            if advancement:
                advancements.append(advancement)

        return advancements

    def _create_advancement_from_insight(self, insight: Dict[str, Any]) -> Dict[str, Any]:
        """Create an advancement from an insight"""
        advancement = {
            "source": "external_project",
            "category": insight["category"],
            "insight": insight,
            "timestamp": datetime.now().isoformat(),
            "applied": False,
        }

        # Route advancement to appropriate module via highway
        if insight["category"] == "research":
            advancement["packet_id"] = self._send_advancement_to_research(insight)
        elif insight["category"] == "finance":
            advancement["packet_id"] = self._send_advancement_to_finance(insight)
        elif insight["category"] == "content":
            advancement["packet_id"] = self._send_advancement_to_content(insight)

        return advancement

    def _send_advancement_to_research(self, insight: Dict[str, Any]) -> str:
        """Send advancement to research module"""
        packet = {
            "type": "external_advancement",
            "category": "research",
            "insight": insight,
            "files": insight.get("files", []),
            "timestamp": datetime.now().isoformat(),
        }

        from highway import get_highway

        return get_highway().send_to_research(packet, "external")

    def _send_advancement_to_finance(self, insight: Dict[str, Any]) -> str:
        """Send advancement to finance module"""
        packet = {
            "type": "external_advancement",
            "category": "finance",
            "insight": insight,
            "files": insight.get("files", []),
            "timestamp": datetime.now().isoformat(),
        }

        from highway import get_highway

        return get_highway().send_to_finance(packet, "external")

    def _send_advancement_to_content(self, insight: Dict[str, Any]) -> str:
        """Send advancement to content module"""
        packet = {
            "type": "external_advancement",
            "category": "content",
            "insight": insight,
            "files": insight.get("files", []),
            "timestamp": datetime.now().isoformat(),
        }

        from highway import get_highway

        return get_highway().send_to_content(packet, "external")

    def _send_sync_results(self, sync_result: Dict[str, Any]):
        """Send sync results via highway"""
        packet = {
            "type": "external_sync_result",
            "sync_data": sync_result,
            "timestamp": datetime.now().isoformat(),
        }

        # Send to all modules
        from highway import get_highway

        get_highway().send_to_research(packet, "external")
        get_highway().send_to_insights(packet, "external")
        get_highway().send_to_finance(packet, "external")

    def _adapt_ai_models(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt external AI models for internal use"""
        return {
            "adapted_models": [],
            "integration_notes": "External AI models adapted for research module",
            "timestamp": datetime.now().isoformat(),
        }

    def _adapt_financial_strategies(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt external financial strategies for internal use"""
        return {
            "adapted_strategies": [],
            "integration_notes": "External financial strategies adapted for finance module",
            "timestamp": datetime.now().isoformat(),
        }

    def _adapt_content_templates(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt external content templates for internal use"""
        return {
            "adapted_templates": [],
            "integration_notes": "External content templates adapted for content module",
            "timestamp": datetime.now().isoformat(),
        }

    def _adapt_research_insights(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt external research insights for internal use"""
        return {
            "adapted_insights": [],
            "integration_notes": "External research insights adapted for research module",
            "timestamp": datetime.now().isoformat(),
        }

    def _adapt_development_patterns(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt external development patterns for internal use"""
        return {
            "adapted_patterns": [],
            "integration_notes": "External development patterns adapted for insights module",
            "timestamp": datetime.now().isoformat(),
        }

    def create_development_bridge(
        self, source_module: str, target_module: str, data: Dict[str, Any]
    ) -> str:
        """Create a bridge between development and internal modules"""
        packet = {
            "source_module": source_module,
            "target_module": target_module,
            "bridge_data": data,
            "timestamp": datetime.now().isoformat(),
            "type": "development_bridge",
        }

        # Route through appropriate highway endpoint
        if target_module == "research":
            return self.highway.send_to_research(packet, source_module)
        elif target_module == "finance":
            return self.highway.send_to_finance(packet, source_module)
        elif target_module == "content":
            return self.highway.send_to_content(packet, source_module)
        elif target_module == "insights":
            return self.highway.send_to_insights(packet, source_module)
        elif target_module == "entertainment":
            return self.highway.send_to_entertainment(packet, source_module)
        elif target_module == "media":
            return self.highway.send_to_media(packet, source_module)
        elif target_module == "brainstorming":
            return self.highway.send_to_brainstorming(packet, source_module)
        elif target_module == "external":
            return self.highway.send_to_external(packet, source_module)

    def get_bridge_status(self) -> Dict[str, Any]:
        """Get the current status of the development bridge"""
        return {
            "external_path": self.external_projects_path,
            "sync_log_length": len(self.sync_log),
            "adaptation_rules": len(self.adaptation_rules),
            "learning_cache_size": len(self.learning_cache),
            "last_sync": datetime.now().isoformat(),
        }

    def monitor_development_learnings(self) -> Dict[str, Any]:
        """Monitor how development projects contribute to module learning"""
        return {
            "code_patterns_learned": len(self.learning_cache.get("code_patterns", {})),
            "ai_advancements": len(self.learning_cache.get("ai_advancements", {})),
            "financial_strategies": len(self.learning_cache.get("financial_strategies", {})),
            "content_templates": len(self.learning_cache.get("content_templates", {})),
            "last_update": datetime.now().isoformat(),
        }


# Global development bridge instance
development_bridge = HighwayDevelopmentBridge()


def get_development_bridge() -> HighwayDevelopmentBridge:
    """Get the global development bridge instance"""
    return development_bridge


# Convenience functions
def sync_with_development() -> Dict[str, Any]:
    """Sync with external development projects"""
    return development_bridge.sync_with_external_projects()


def create_dev_bridge(source: str, target: str, data: Dict[str, Any]) -> str:
    """Create a development bridge"""
    return development_bridge.create_development_bridge(source, target, data)


def route_dev_to_research(data: Dict[str, Any]) -> str:
    """Route development insights to research"""
    return development_bridge.route_development_to_research(data)


def route_research_to_dev(data: Dict[str, Any]) -> str:
    """Route research insights to development"""
    return development_bridge.route_research_to_development(data)
