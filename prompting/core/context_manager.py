"""
ContextManager - Maintains state, cross-session memory, and codebase metadata
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextManager:
    """Manages execution context, memory, and codebase metadata"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "data/context")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Current session context
        self.session_context = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now(),
            "project_root": None,
            "current_file": None,
            "working_directory": os.getcwd(),
            "user_profile": {},
            "conversation_history": [],
            "active_tasks": {},
            "mode_preferences": {},
        }

        # Persistent memory
        self.memory = self._load_memory()

        # Codebase metadata cache
        self.codebase_metadata = {}

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def set_project_context(self, project_root: str):
        """Set the current project context"""
        self.session_context["project_root"] = os.path.abspath(project_root)
        self.session_context["working_directory"] = os.path.abspath(project_root)

        # Load or create codebase metadata
        self._load_codebase_metadata(project_root)

    def set_current_file(self, file_path: str):
        """Set the currently active file"""
        self.session_context["current_file"] = os.path.abspath(file_path)

    def add_conversation_entry(self, role: str, content: str, mode: str = None):
        """Add entry to conversation history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "mode": mode,
        }
        self.session_context["conversation_history"].append(entry)

        # Keep only last 100 entries to manage memory
        if len(self.session_context["conversation_history"]) > 100:
            self.session_context["conversation_history"] = self.session_context["conversation_history"][-100:]

    def get_context_for_mode(self, mode: str) -> Dict[str, Any]:
        """Get relevant context for a specific mode"""
        base_context = {
            "session_id": self.session_context["session_id"],
            "project_root": self.session_context["project_root"],
            "current_file": self.session_context["current_file"],
            "working_directory": self.session_context["working_directory"],
        }

        # Add mode-specific context
        if mode == "ide":
            base_context.update(
                {
                    "codebase_structure": self.codebase_metadata.get("structure", {}),
                    "recent_files": self._get_recent_files(),
                    "dependencies": self.codebase_metadata.get("dependencies", []),
                    "test_files": self.codebase_metadata.get("test_files", []),
                }
            )
        elif mode == "business":
            base_context.update(
                {
                    "project_metrics": self.memory.get("project_metrics", {}),
                    "kpis": self.memory.get("kpis", {}),
                    "business_context": self.memory.get("business_context", {}),
                }
            )
        elif mode == "conversational":
            base_context.update(
                {
                    "recent_conversation": self.session_context["conversation_history"][-5:],
                    "user_preferences": self.session_context["user_profile"],
                }
            )

        return base_context

    def _load_codebase_metadata(self, project_root: str):
        """Load or generate codebase metadata"""
        metadata_file = self.storage_path / f"codebase_{hash(project_root)}.json"

        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                self.codebase_metadata = json.load(f)
        else:
            # Generate new metadata
            self.codebase_metadata = self._analyze_codebase(project_root)
            self._save_codebase_metadata(metadata_file)

    def _analyze_codebase(self, project_root: str) -> Dict[str, Any]:
        """Analyze codebase structure and generate metadata"""
        metadata = {
            "project_root": project_root,
            "last_analyzed": datetime.now().isoformat(),
            "structure": {},
            "file_types": {},
            "dependencies": [],
            "test_files": [],
            "config_files": [],
        }

        try:
            for root, dirs, files in os.walk(project_root):
                # Skip common ignore directories
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules"]]

                rel_root = os.path.relpath(root, project_root)
                if rel_root == ".":
                    rel_root = ""

                for file in files:
                    if file.startswith("."):
                        continue

                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_root)

                    # Track file types
                    ext = os.path.splitext(file)[1]
                    metadata["file_types"][ext] = metadata["file_types"].get(ext, 0) + 1

                    # Identify special files
                    if "test" in file.lower() or file.startswith("test_"):
                        metadata["test_files"].append(rel_path)
                    elif file in [
                        "requirements.txt",
                        "package.json",
                        "pyproject.toml",
                        "setup.py",
                    ]:
                        metadata["config_files"].append(rel_path)

                    # Build structure
                    if rel_root not in metadata["structure"]:
                        metadata["structure"][rel_root] = []
                    metadata["structure"][rel_root].append(file)

        except Exception as e:
            print(f"Error analyzing codebase: {e}")

        return metadata

    def _save_codebase_metadata(self, metadata_file: Path):
        """Save codebase metadata to file"""
        try:
            with open(metadata_file, "w") as f:
                json.dump(self.codebase_metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving codebase metadata: {e}")

    def _get_recent_files(self) -> List[str]:
        """Get list of recently accessed files"""
        # This would typically track file access, for now return empty
        return []

    def _load_memory(self) -> Dict[str, Any]:
        """Load persistent memory from storage"""
        memory_file = self.storage_path / "memory.json"

        if memory_file.exists():
            try:
                with open(memory_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")

        return {
            "insights": [],
            "learned_patterns": {},
            "user_preferences": {},
            "project_metrics": {},
            "successful_strategies": [],
        }

    def save_memory(self):
        """Save current memory to persistent storage"""
        memory_file = self.storage_path / "memory.json"

        try:
            with open(memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def add_insight(self, insight: str, category: str = "general", confidence: float = 1.0):
        """Add a learned insight to memory"""
        insight_entry = {
            "content": insight,
            "category": category,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_context["session_id"],
        }

        self.memory["insights"].append(insight_entry)

        # Keep only last 1000 insights
        if len(self.memory["insights"]) > 1000:
            self.memory["insights"] = self.memory["insights"][-1000:]

    def get_relevant_insights(self, query: str, category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get insights relevant to a query"""
        # Simple keyword matching - could be enhanced with embeddings
        query_lower = query.lower()
        relevant = []

        for insight in self.memory["insights"]:
            if category and insight["category"] != category:
                continue

            if any(word in insight["content"].lower() for word in query_lower.split()):
                relevant.append(insight)

        # Sort by confidence and recency
        relevant.sort(key=lambda x: (x["confidence"], x["timestamp"]), reverse=True)
        return relevant[:limit]

    def update_user_preference(self, key: str, value: Any):
        """Update user preference"""
        self.session_context["user_profile"][key] = value
        self.memory["user_preferences"][key] = value

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_context["session_id"],
            "duration": (datetime.now() - self.session_context["start_time"]).total_seconds(),
            "conversation_entries": len(self.session_context["conversation_history"]),
            "active_tasks": len(self.session_context["active_tasks"]),
            "project_context": bool(self.session_context["project_root"]),
            "insights_generated": len(
                [i for i in self.memory["insights"] if i["session_id"] == self.session_context["session_id"]]
            ),
        }
