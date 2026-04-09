"""Directory analysis mixin for EchoesAssistantV2.

Extracted from assistant_v2_core.py (lines 2752–2993) as part of the
god-module decomposition.  Provides codebase / directory structure analysis
driven by an LLM call.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class DirectoryAnalysisMixin:
    """Directory structure scanning, stats collection and LLM-driven analysis."""

    # -- Attribute stubs for type checkers (set by the host class) -----------
    client: Any  # OpenAI client
    model: str
    enable_status: bool

    # -- Public API ----------------------------------------------------------

    def analyze_directory(
        self,
        directory_path: str,
        output_file: str | None = None,
        max_depth: int = 10,
        exclude_dirs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Analyse a directory tree and generate an LLM-driven report."""
        # Lazy imports of module-level helpers defined in the host file
        from assistant_v2_core import (
            STATUS_COMPLETE,
            STATUS_WORKING,
            EnhancedStatusIndicator,
            load_prompt,
        )

        exclude_dirs = exclude_dirs or [
            ".git",
            "__pycache__",
            "node_modules",
            "venv",
            ".venv",
            "env",
        ]
        directory_path = Path(directory_path).resolve()
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Directory not found: {directory_path}")

        system_prompt = load_prompt("directory_analyst")
        if not system_prompt:
            system_prompt = (
                "You are an expert codebase analyst. Analyze the directory structure and provide:\n"
                "1. Project structure overview\n"
                "2. Key components and their relationships\n"
                "3. Technology stack\n"
                "4. Potential issues and improvements\n"
                "5. Recommendations for better organization"
            )

        structure = self._get_directory_structure(directory_path, max_depth, exclude_dirs)
        stats = self._collect_file_stats(structure)

        file_types = sorted(stats["file_types"].items(), key=lambda item: item[1], reverse=True)
        top_file_types = file_types[:20]
        if len(file_types) > 20:
            remaining = sum(count for _, count in file_types[20:])
            top_file_types.append(("other", remaining))
        file_type_summary = ", ".join(f"{ext or 'no-ext'}: {count}" for ext, count in top_file_types) or "None"

        analysis = {
            "directory": str(directory_path),
            "timestamp": datetime.now(UTC).isoformat(),
            "file_count": stats["file_count"],
            "dir_count": stats["dir_count"],
            "file_types": stats["file_types"],
            "structure": structure,
            "analysis": None,
        }

        directory_summary = self._format_directory_structure(structure, max_lines=400)
        top_directories_summary = self._summarize_top_directories(structure, max_entries=20)
        analysis_prompt = (
            f"Analyze this directory structure and provide a comprehensive report:\n\n"
            f"Directory: {directory_path}\n"
            f"Total Files: {analysis['file_count']}\n"
            f"Total Directories: {analysis['dir_count']}\n"
            f"File Types: {file_type_summary}\n\n"
            f"Top Directories:\n{top_directories_summary}\n\n"
            f"Directory Structure:\n{directory_summary}\n\n"
            "Please provide a detailed analysis including:\n"
            "1. Project structure overview\n"
            "2. Key components and their relationships\n"
            "3. Technology stack identification\n"
            "4. Potential issues and improvements\n"
            "5. Recommendations for better organization"
        )

        status = EnhancedStatusIndicator(enabled=self.enable_status)
        try:
            status.start_phase(f"{STATUS_WORKING} Preparing directory summary")
            status.complete_phase("Directory summary ready")
            status.start_phase(f"{STATUS_WORKING} Generating analysis")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_prompt},
                ],
                temperature=0.3,
                max_completion_tokens=3000 if "o3" in self.model else None,
                max_tokens=3000 if "o3" not in self.model else None,
            )
            analysis["analysis"] = response.choices[0].message.content
            status.complete_phase("Analysis complete")

            if output_file:
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, indent=2)
                print(f"{STATUS_COMPLETE} Analysis saved to {output_path}")

            return analysis
        except Exception as e:
            status.error(str(e))
            raise

    # -- Private helpers -----------------------------------------------------

    def _get_directory_structure(self, root_path: Path, max_depth: int, exclude_dirs: list[str]) -> dict[str, Any]:
        root_path = root_path.resolve()
        structure = {
            "name": root_path.name,
            "type": "directory",
            "path": str(root_path),
            "size": 0,
            "file_count": 0,
            "dir_count": 0,
            "children": [],
        }

        if max_depth < 0:
            return structure

        try:
            for item in root_path.iterdir():
                if item.is_symlink():
                    continue
                if item.name in exclude_dirs or any(item.match(pattern) for pattern in exclude_dirs):
                    continue

                if item.is_file():
                    try:
                        size = item.stat().st_size
                    except (OSError, PermissionError):
                        size = 0
                    structure["size"] += size
                    structure["file_count"] += 1
                    structure["children"].append(
                        {
                            "name": item.name,
                            "type": "file",
                            "path": str(item),
                            "size": size,
                            "extension": item.suffix.lower(),
                        }
                    )
                elif item.is_dir():
                    child_structure = self._get_directory_structure(item, max_depth - 1, exclude_dirs)
                    structure["size"] += child_structure.get("size", 0)
                    structure["file_count"] += child_structure.get("file_count", 0)
                    structure["dir_count"] += 1 + child_structure.get("dir_count", 0)
                    structure["children"].append(child_structure)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not access {root_path}: {e}")

        return structure

    def _collect_file_stats(self, structure: dict[str, Any]) -> dict[str, Any]:
        stats = {"file_count": 0, "dir_count": 0, "file_types": {}}

        def _walk(node: dict[str, Any]):
            node_type = node.get("type")
            if node_type == "file":
                stats["file_count"] += 1
                ext = node.get("extension", "")
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
            elif node_type == "directory":
                stats["dir_count"] += 1
                for child in node.get("children", []):
                    _walk(child)

        _walk(structure)
        return stats

    def _format_directory_structure(self, structure: dict[str, Any], indent: int = 0, max_lines: int = 400) -> str:
        lines: list[str] = []
        truncated = False

        def _walk(node: dict[str, Any], depth: int) -> None:
            nonlocal truncated
            if truncated:
                return

            prefix = "  " * depth
            if node.get("type") == "file":
                size_mb = node.get("size", 0) / (1024 * 1024)
                line = f"{prefix}📄 {node.get('name')} ({size_mb:.2f} MB)"
                lines.append(line)
            else:
                file_count = node.get("file_count", 0)
                dir_count = node.get("dir_count", 0)
                line = f"{prefix}📁 {node.get('name')}/"
                if file_count or dir_count:
                    line += f" ({file_count} files, {dir_count} dirs)"
                lines.append(line)
                for child in node.get("children", []):
                    if len(lines) >= max_lines:
                        truncated = True
                        return
                    _walk(child, depth + 1)

            if len(lines) >= max_lines:
                truncated = True

        _walk(structure, indent)

        if truncated:
            lines = lines[:max_lines]
            lines.append(f"... (truncated after {max_lines} lines)")

        return "\n".join(lines)

    def _summarize_top_directories(self, structure: dict[str, Any], max_entries: int = 20) -> str:
        entries: list[dict[str, Any]] = []

        def _collect(node: dict[str, Any]) -> None:
            if node.get("type") != "directory":
                return
            entries.append(
                {
                    "path": node.get("path"),
                    "name": node.get("name"),
                    "file_count": node.get("file_count", 0),
                    "dir_count": node.get("dir_count", 0),
                    "size": node.get("size", 0),
                }
            )
            for child in node.get("children", []):
                if child.get("type") == "directory":
                    _collect(child)

        _collect(structure)

        entries.sort(key=lambda item: item["file_count"], reverse=True)
        top_entries = entries[:max_entries]

        if not top_entries:
            return "(no directories found)"

        lines = []
        for idx, item in enumerate(top_entries, start=1):
            size_mb = item["size"] / (1024 * 1024)
            lines.append(
                f"{idx}. {item['path']} — files: {item['file_count']}, dirs: {item['dir_count']}, size: {size_mb:.2f} MB"
            )

        if len(entries) > max_entries:
            remaining = len(entries) - max_entries
            lines.append(f"... ({remaining} more directories)")

        return "\n".join(lines)
