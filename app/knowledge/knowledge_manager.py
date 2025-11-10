"""
Knowledge Manager for EchoesAssistantV2

Handles knowledge gathering, storage, retrieval, and context building.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class KnowledgeEntry:
    """Knowledge entry with metadata."""

    id: str
    content: str
    source: str
    category: str
    timestamp: str
    metadata: Dict[str, Any]
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "KnowledgeEntry":
        return KnowledgeEntry(**data)


class KnowledgeManager:
    """Manages knowledge gathering, storage, and retrieval."""

    def __init__(self, storage_path: Optional[str] = None):
        """Initialize the knowledge manager."""
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path("data/knowledge")

        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.knowledge_file = self.storage_path / "knowledge_base.json"
        self.context_file = self.storage_path / "context.json"

        self.knowledge: Dict[str, KnowledgeEntry] = {}
        self.context: Dict[str, Any] = {}

        self._load_knowledge()
        self._load_context()

    def _load_knowledge(self):
        """Load knowledge from storage."""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.knowledge = {
                        k: KnowledgeEntry.from_dict(v) for k, v in data.items()
                    }
            except Exception:
                self.knowledge = {}

    def _save_knowledge(self):
        """Save knowledge to storage."""
        data = {k: v.to_dict() for k, v in self.knowledge.items()}
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_context(self):
        """Load context from storage."""
        if self.context_file.exists():
            try:
                with open(self.context_file, "r", encoding="utf-8") as f:
                    self.context = json.load(f)
            except Exception:
                self.context = {}

    def _save_context(self):
        """Save context to storage."""
        with open(self.context_file, "w", encoding="utf-8") as f:
            json.dump(self.context, f, indent=2)

    def add_knowledge(
        self,
        content: str,
        source: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add knowledge entry."""

        # Like good code structure:
        def handle_user_request(request):
            # Phase 1: Analysis
            understand_request(request)

            # Phase 2: Planning
            plan_approach(request)

            # Phase 3: Execution
            execute_plan()

        # Phase 1: Input Processing
        import hashlib

        # Generate ID
        entry_id = hashlib.md5(
            f"{content}{source}{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:12]

        entry = KnowledgeEntry(
            id=entry_id,
            content=content,
            source=source,
            category=category,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
            tags=tags or [],
        )

        self.knowledge[entry_id] = entry
        self._save_knowledge()

        return entry_id

    def get_knowledge(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get knowledge entry by ID."""
        return self.knowledge.get(entry_id)

    def search_knowledge(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[KnowledgeEntry]:
        """Search knowledge entries."""
        results = list(self.knowledge.values())

        # Filter by category
        if category:
            results = [e for e in results if e.category == category]

        # Filter by tags
        if tags:
            results = [e for e in results if any(t in e.tags for t in tags)]

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                e
                for e in results
                if query_lower in e.content.lower() or query_lower in e.source.lower()
            ]

        # Sort by timestamp (newest first)
        results.sort(key=lambda e: e.timestamp, reverse=True)

        return results[:limit]

    def update_context(self, key: str, value: Any):
        """Update context."""
        self.context[key] = value
        self._save_context()

    def get_context(self, key: Optional[str] = None) -> Any:
        """Get context."""
        if key:
            return self.context.get(key)
        return self.context

    def build_context_summary(self) -> str:
        """Build context summary for assistant."""
        summary_parts = []

        # Recent knowledge
        recent = self.search_knowledge(limit=5)
        if recent:
            summary_parts.append("Recent Knowledge:")
            for entry in recent:
                summary_parts.append(f"- [{entry.category}] {entry.content[:100]}...")

        # Active context
        if self.context:
            summary_parts.append("\nActive Context:")
            for key, value in list(self.context.items())[:5]:
                summary_parts.append(f"- {key}: {str(value)[:50]}")

        return "\n".join(summary_parts) if summary_parts else "No context available"

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge statistics."""
        categories = {}
        for entry in self.knowledge.values():
            categories[entry.category] = categories.get(entry.category, 0) + 1

        return {
            "total_entries": len(self.knowledge),
            "categories": categories,
            "context_keys": len(self.context),
            "storage_path": str(self.storage_path),
        }

    def store_roi_analysis(
        self, roi_results: Dict[str, Any], analysis_id: Optional[str] = None
    ) -> str:
        """Store ROI analysis results in knowledge base."""
        if not analysis_id:
            import hashlib

            timestamp = roi_results.get("timestamp", "")
            institution = roi_results.get("stakeholder_config", {}).get(
                "institution_name", "unknown"
            )
            analysis_id = hashlib.md5(
                f"roi_{institution}_{timestamp}".encode()
            ).hexdigest()[:12]

        content = f"ROI Analysis for {roi_results.get('stakeholder_config', {}).get('institution_name', 'Unknown Institution')}\n"
        content += f"Business Type: {roi_results.get('business_type', 'unknown')}\n"
        content += f"Monthly Investment: ${roi_results.get('roi_metrics', {}).get('monthly_investment', 0):,.0f}\n"
        content += f"Monthly Savings: ${roi_results.get('roi_metrics', {}).get('monthly_savings', 0):,.0f}\n"
        content += f"Payback Period: {roi_results.get('roi_metrics', {}).get('payback_days', 0):.0f} days\n"
        content += (
            f"ROI: {roi_results.get('roi_metrics', {}).get('roi_percentage', 0):.0f}%\n"
        )

        # Add file organization info
        file_org = roi_results.get("file_organization", {})
        if file_org.get("success"):
            content += (
                f"Files organized in: {file_org.get('institution_directory', '')}\n"
            )

        self.add_knowledge(
            content=content,
            source=f"ROI Analysis Tool - {analysis_id}",
            category="roi_analysis",
            tags=[
                "roi",
                "analysis",
                roi_results.get("business_type", "unknown"),
                "financial",
            ],
            metadata={
                "analysis_id": analysis_id,
                "roi_metrics": roi_results.get("roi_metrics", {}),
                "stakeholder_config": roi_results.get("stakeholder_config", {}),
                "file_organization": roi_results.get("file_organization", {}),
                "generated_files": list(roi_results.get("generated_files", {}).keys()),
            },
        )

        return analysis_id

    def search_roi_analyses(
        self,
        institution: Optional[str] = None,
        business_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[KnowledgeEntry]:
        """Search ROI analyses by institution or business type."""
        query = "ROI Analysis"
        tags = ["roi"]
        if business_type:
            tags.append(business_type)

        results = self.search_knowledge(
            query=query, category="roi_analysis", tags=tags, limit=limit
        )

        if institution:
            # Filter by institution in content
            results = [r for r in results if institution.lower() in r.content.lower()]

        return results

    def get_roi_summary(self) -> Dict[str, Any]:
        """Get summary of all ROI analyses."""
        roi_entries = self.search_knowledge(category="roi_analysis", limit=1000)

        total_analyses = len(roi_entries)
        business_types = {}
        total_investment = 0
        total_savings = 0
        institutions = set()

        for entry in roi_entries:
            # Extract business type from tags
            for tag in entry.tags:
                if tag != "roi" and tag != "analysis" and tag != "financial":
                    business_types[tag] = business_types.get(tag, 0) + 1

            # Extract metrics from metadata
            metrics = entry.metadata.get("roi_metrics", {})
            total_investment += metrics.get("monthly_investment", 0)
            total_savings += metrics.get("monthly_savings", 0)

            # Extract institution
            stakeholder_config = entry.metadata.get("stakeholder_config", {})
            institution = stakeholder_config.get("institution_name", "")
            if institution:
                institutions.add(institution)

        return {
            "total_analyses": total_analyses,
            "business_types": business_types,
            "institutions_analyzed": list(institutions),
            "total_monthly_investment": total_investment,
            "total_monthly_savings": total_savings,
            "average_roi": (
                (total_savings / total_investment * 100) if total_investment > 0 else 0
            ),
        }
