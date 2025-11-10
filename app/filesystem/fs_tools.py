"""
Enhanced Filesystem Tools for EchoesAssistantV2

Safe filesystem operations with error handling and security.
"""

import os
from pathlib import Path
from typing import Any


class FilesystemTools:
    """Safe filesystem operations."""

    def __init__(
        self, root_dir: str | None = None, allowed_patterns: list[str] | None = None
    ):
        """Initialize filesystem tools."""
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.allowed_patterns = allowed_patterns or ["*"]

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe (within root and not sensitive)."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive = [".git", "__pycache__", ".env", "node_modules", ".venv", "venv"]
            path_parts = resolved.parts
            if any(s in path_parts for s in sensitive):
                return False

            return True
        except Exception:
            return False

    def list_directory(
        self, dirpath: str, pattern: str = "*", recursive: bool = False
    ) -> dict[str, Any]:
        """List directory contents safely."""

        # Like good code structure:
        def handle_user_request(request):
            # Phase 1: Analysis
            understand_request(request)

            # Phase 2: Planning
            plan_approach(request)

            # Phase 3: Execution
            execute_plan()

        # Phase 1: Path Validation
        try:
            path = Path(dirpath).resolve()

            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}

            if not path.exists():
                return {"success": False, "error": f"Directory not found: {dirpath}"}

            if not path.is_dir():
                return {"success": False, "error": f"Not a directory: {dirpath}"}

            # Phase 2: Directory Scanning
            files = []
            dirs = []

            if recursive:
                items = path.rglob(pattern)
            else:
                items = path.glob(pattern)

            for item in items:
                if self._is_safe_path(item):
                    rel_path = str(item.relative_to(self.root_dir))
                    if item.is_file():
                        files.append(
                            {
                                "path": rel_path,
                                "name": item.name,
                                "size": item.stat().st_size,
                                "modified": item.stat().st_mtime,
                            }
                        )
                    elif item.is_dir():
                        dirs.append({"path": rel_path, "name": item.name})

            # Phase 3: Result Compilation
            return {
                "success": True,
                "directory": dirpath,
                "files": files,
                "dirs": dirs,
                "total_files": len(files),
                "total_dirs": len(dirs),
            }

        except Exception as e:
            return {"success": False, "error": f"Error listing directory: {str(e)}"}

    def read_file(
        self,
        filepath: str,
        encoding: str = "utf-8",
        max_size: int = 1024 * 1024,  # 1MB default
    ) -> dict[str, Any]:
        """Read file contents safely."""

        # Like good code structure:
        def handle_user_request(request):
            # Phase 1: Analysis
            understand_request(request)

            # Phase 2: Planning
            plan_approach(request)

            # Phase 3: Execution
            execute_plan()

        # Phase 1: Path and Size Validation
        try:
            path = Path(filepath).resolve()

            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}

            if not path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}

            if not path.is_file():
                return {"success": False, "error": f"Not a file: {filepath}"}

            file_size = path.stat().st_size
            if file_size > max_size:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (max: {max_size})",
                }

            # Phase 2: File Reading
            with open(path, encoding=encoding) as f:
                content = f.read()

            # Phase 3: Result Compilation
            return {
                "success": True,
                "filepath": filepath,
                "content": content,
                "size": file_size,
                "encoding": encoding,
                "lines": len(content.splitlines()) if content else 0,
            }

        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}

    def write_file(
        self,
        filepath: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> dict[str, Any]:
        """Write file contents safely."""
        try:
            path = Path(filepath).resolve()

            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}

            # Create parent directories if needed
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path, "w", encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "filepath": filepath,
                "size": path.stat().st_size,
                "created": not path.exists(),
            }

        except Exception as e:
            return {"success": False, "error": f"Error writing file: {str(e)}"}

    def search_files(
        self,
        query: str,
        search_path: str | None = None,
        file_pattern: str = "*",
        max_results: int = 50,
    ) -> dict[str, Any]:
        """Search for files by name or content."""
        try:
            base_path = Path(search_path or self.root_dir).resolve()

            if not self._is_safe_path(base_path):
                return {"success": False, "error": "Access denied: path not allowed"}

            results = []
            query_lower = query.lower()

            for item in base_path.rglob(file_pattern):
                if not self._is_safe_path(item):
                    continue

                if len(results) >= max_results:
                    break

                # Search by filename
                if query_lower in item.name.lower():
                    results.append(
                        {
                            "path": str(item.relative_to(self.root_dir)),
                            "name": item.name,
                            "match_type": "filename",
                            "is_dir": item.is_dir(),
                        }
                    )

            return {
                "success": True,
                "query": query,
                "results": results,
                "total": len(results),
            }

        except Exception as e:
            return {"success": False, "error": f"Error searching files: {str(e)}"}

    def get_file_info(self, filepath: str) -> dict[str, Any]:
        """Get file metadata."""
        try:
            path = Path(filepath).resolve()

            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}

            if not path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}

            stat = path.stat()

            return {
                "success": True,
                "path": filepath,
                "name": path.name,
                "size": stat.st_size,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": path.suffix,
            }

        except Exception as e:
            return {"success": False, "error": f"Error getting file info: {str(e)}"}

    def get_directory_tree(
        self, dirpath: str, max_depth: int = 3, include_files: bool = True
    ) -> dict[str, Any]:
        """Get directory tree structure."""
        try:
            path = Path(dirpath).resolve()

            if not self._is_safe_path(path):
                return {"success": False, "error": "Access denied: path not allowed"}

            if not path.exists() or not path.is_dir():
                return {"success": False, "error": f"Directory not found: {dirpath}"}

            def build_tree(p: Path, depth: int) -> dict[str, Any]:
                if depth > max_depth:
                    return None

                node = {
                    "name": p.name,
                    "path": str(p.relative_to(self.root_dir)),
                    "is_dir": p.is_dir(),
                }

                if p.is_dir():
                    children = []
                    try:
                        for item in sorted(p.iterdir()):
                            if not self._is_safe_path(item):
                                continue
                            if item.is_dir() or (include_files and item.is_file()):
                                child = build_tree(item, depth + 1)
                                if child:
                                    children.append(child)
                        node["children"] = children
                    except PermissionError:
                        pass
                else:
                    node["size"] = p.stat().st_size

                return node

            tree = build_tree(path, 0)

            return {"success": True, "tree": tree}

        except Exception as e:
            return {"success": False, "error": f"Error building tree: {str(e)}"}

    def organize_roi_files(
        self, roi_results: dict[str, Any], base_dir: str = "roi_analysis"
    ) -> dict[str, Any]:
        """
        Organize ROI analysis files into a structured directory.

        Args:
            roi_results: Results from ROI analysis tool
            base_dir: Base directory name for organization

        Returns:
            Organization results
        """
        try:
            # Create base directory
            base_path = Path(base_dir)
            base_path.mkdir(parents=True, exist_ok=True)

            organized_files = {}
            institution_name = (
                roi_results.get("stakeholder_config", {})
                .get("institution_name", "unknown")
                .lower()
                .replace(" ", "_")
            )

            # Create institution-specific directory
            inst_dir = base_path / institution_name
            inst_dir.mkdir(exist_ok=True)

            # Create subdirectories
            configs_dir = inst_dir / "configs"
            data_dir = inst_dir / "data"
            reports_dir = inst_dir / "reports"

            for d in [configs_dir, data_dir, reports_dir]:
                d.mkdir(exist_ok=True)

            # Write files based on generated formats
            generated_files = roi_results.get("generated_files", {})

            if "yaml" in generated_files:
                yaml_data = generated_files["yaml"]
                yaml_path = configs_dir / yaml_data["filename"]
                with open(yaml_path, "w", encoding="utf-8") as f:
                    f.write(yaml_data["content"])
                organized_files["yaml_config"] = str(yaml_path)

            if "csv" in generated_files:
                csv_data = generated_files["csv"]
                csv_path = data_dir / csv_data["filename"]
                with open(csv_path, "w", encoding="utf-8") as f:
                    f.write(csv_data["content"])
                organized_files["csv_data"] = str(csv_path)

            if "spreadsheet" in generated_files:
                sheet_data = generated_files["spreadsheet"]
                sheet_path = data_dir / sheet_data["filename"]
                with open(sheet_path, "w", encoding="utf-8") as f:
                    f.write(sheet_data["content"])
                organized_files["spreadsheet"] = str(sheet_path)

            if "report" in generated_files:
                report_data = generated_files["report"]
                report_path = reports_dir / report_data["filename"]
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(report_data["content"])
                organized_files["executive_report"] = str(report_path)

            # Create metadata file
            metadata = {
                "institution": institution_name,
                "generated_at": roi_results.get("timestamp"),
                "business_type": roi_results.get("business_type"),
                "customization_level": roi_results.get("customization_level"),
                "roi_metrics": roi_results.get("roi_metrics"),
                "file_count": len(organized_files),
                "organized_files": organized_files,
            }

            metadata_path = inst_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            organized_files["metadata"] = str(metadata_path)

            return {
                "success": True,
                "base_directory": str(base_path),
                "institution_directory": str(inst_dir),
                "organized_files": organized_files,
                "total_files": len(organized_files),
            }

        except Exception as e:
            return {"success": False, "error": f"Error organizing ROI files: {str(e)}"}
