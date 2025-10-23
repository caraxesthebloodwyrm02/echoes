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
                    self.knowledge = {k: KnowledgeEntry.from_dict(v) for k, v in data.items()}
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
        import hashlib

        # Generate ID
        entry_id = hashlib.md5(f"{content}{source}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]

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
            results = [e for e in results if query_lower in e.content.lower() or query_lower in e.source.lower()]

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
