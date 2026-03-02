"""
Filesystem Tools for OpenAI Function Calling

Provides safe filesystem operations as OpenAI-compatible tools.
Based on OpenAI's function calling best practices.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class ReadFileTool(BaseTool):
    """Tool for safely reading file contents."""

    def __init__(self, root_dir: str | None = None):
        super().__init__(
            name="read_file",
            description="Read the contents of a text file. Supports various file types including code, configuration, and text files.",
        )
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.max_size = 1024 * 1024  # 1MB limit

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive_parts = [
                ".git",
                "__pycache__",
                ".env",
                "node_modules",
                ".venv",
                "venv",
                ".DS_Store",
                "Thumbs.db",
            ]
            if any(part in resolved.parts for part in sensitive_parts):
                return False

            # Avoid system directories on Windows
            if os.name == "nt":
                system_dirs = [
                    "Windows",
                    "Program Files",
                    "Program Files (x86)",
                    "System32",
                ]
                if any(part in resolved.parts for part in system_dirs):
                    return False

            return True
        except Exception:
            return False

    def __call__(self, filepath: str, encoding: str = "utf-8") -> ToolResult:
        """
        Read file contents.

        Args:
            filepath: Path to the file to read
            encoding: File encoding (default: utf-8)
        """
        try:
            path = Path(filepath).resolve()

            # Safety checks
            if not self._is_safe_path(path):
                return ToolResult(
                    success=False,
                    error="Access denied: Path not allowed or potentially dangerous",
                )

            if not path.exists():
                return ToolResult(success=False, error=f"File not found: {filepath}")

            if not path.is_file():
                return ToolResult(
                    success=False, error=f"Path is not a file: {filepath}"
                )

            # Size check
            file_size = path.stat().st_size
            if file_size > self.max_size:
                return ToolResult(
                    success=False,
                    error=f"File too large: {file_size:,} bytes (max: {self.max_size:,})",
                )

            # Determine if file is likely binary
            binary_extensions = {
                ".exe",
                ".dll",
                ".so",
                ".dylib",
                ".bin",
                ".img",
                ".iso",
                ".zip",
                ".tar",
                ".gz",
                ".rar",
                ".7z",
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".tiff",
                ".mp3",
                ".mp4",
                ".avi",
                ".mov",
            }

            if path.suffix.lower() in binary_extensions:
                return ToolResult(
                    success=False,
                    error=f"Binary file detected: {path.suffix}. This tool only reads text files.",
                )

            # Read file
            try:
                with open(path, encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                return ToolResult(
                    success=False,
                    error=f"Failed to decode file as {encoding}. File may be binary or use different encoding.",
                )

            # Prepare result
            line_count = content.count("\n") + 1 if content else 0

            # Truncate very long lines for display
            lines = content.split("\n")
            truncated_lines = []
            for line in lines:
                if len(line) > 1000:
                    truncated_lines.append(line[:1000] + "... (truncated)")
                else:
                    truncated_lines.append(line)

            truncated_content = "\n".join(truncated_lines)

            return ToolResult(
                success=True,
                data={
                    "filepath": str(path.relative_to(self.root_dir)),
                    "absolute_path": str(path),
                    "content": truncated_content,
                    "size": file_size,
                    "lines": line_count,
                    "encoding": encoding,
                    "extension": path.suffix,
                    "last_modified": datetime.fromtimestamp(
                        path.stat().st_mtime
                    ).isoformat(),
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error reading file: {str(e)}")

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to read (relative to current directory)",
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding to use",
                            "default": "utf-8",
                            "enum": ["utf-8", "ascii", "latin-1", "cp1252"],
                        },
                    },
                    "required": ["filepath"],
                },
            },
        }


class WriteFileTool(BaseTool):
    """Tool for safely writing file contents."""

    def __init__(self, root_dir: str | None = None):
        super().__init__(
            name="write_file",
            description="Write content to a text file. Creates directories if they don't exist. Overwrites existing files.",
        )
        self.root_dir = Path(root_dir or os.getcwd()).resolve()
        self.max_size = 10 * 1024 * 1024  # 10MB limit

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to write to."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive_parts = [
                ".git",
                "__pycache__",
                ".env",
                "node_modules",
                ".venv",
                "venv",
                ".DS_Store",
                "Thumbs.db",
            ]
            if any(part in resolved.parts for part in sensitive_parts):
                return False

            # Avoid system directories on Windows
            if os.name == "nt":
                system_dirs = [
                    "Windows",
                    "Program Files",
                    "Program Files (x86)",
                    "System32",
                ]
                if any(part in resolved.parts for part in system_dirs):
                    return False

            return True
        except Exception:
            return False

    def __call__(
        self,
        filepath: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
    ) -> ToolResult:
        """
        Write content to a file.

        Args:
            filepath: Path to the file to write
            content: Content to write to the file
            encoding: File encoding (default: utf-8)
            create_dirs: Create parent directories if they don't exist
        """
        try:
            path = Path(filepath).resolve()

            # Safety checks
            if not self._is_safe_path(path):
                return ToolResult(
                    success=False,
                    error="Access denied: Path not allowed or potentially dangerous",
                )

            # Size check
            content_size = len(content.encode(encoding))
            if content_size > self.max_size:
                return ToolResult(
                    success=False,
                    error=f"Content too large: {content_size:,} bytes (max: {self.max_size:,})",
                )

            # Create parent directories if needed
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Check if directory
            if path.exists() and path.is_dir():
                return ToolResult(
                    success=False, error=f"Path exists and is a directory: {filepath}"
                )

            # Write file
            with open(path, "w", encoding=encoding) as f:
                f.write(content)

            return ToolResult(
                success=True,
                data={
                    "filepath": str(path.relative_to(self.root_dir)),
                    "absolute_path": str(path),
                    "size": content_size,
                    "encoding": encoding,
                    "created": not path.exists(),
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error writing file: {str(e)}")

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to write (relative to current directory)",
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file",
                        },
                        "encoding": {
                            "type": "string",
                            "description": "File encoding to use",
                            "default": "utf-8",
                            "enum": ["utf-8", "ascii", "latin-1", "cp1252"],
                        },
                        "create_dirs": {
                            "type": "boolean",
                            "description": "Create parent directories if they don't exist",
                            "default": True,
                        },
                    },
                    "required": ["filepath", "content"],
                },
            },
        }


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""

    def __init__(self, root_dir: str | None = None):
        super().__init__(
            name="list_directory",
            description="List the contents of a directory, including files and subdirectories.",
        )
        self.root_dir = Path(root_dir or os.getcwd()).resolve()

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive_parts = [
                ".git",
                "__pycache__",
                ".env",
                "node_modules",
                ".venv",
                "venv",
                ".DS_Store",
                "Thumbs.db",
            ]
            if any(part in resolved.parts for part in sensitive_parts):
                return False

            return True
        except Exception:
            return False

    def __call__(
        self,
        dirpath: str,
        pattern: str = "*",
        recursive: bool = False,
        include_hidden: bool = False,
    ) -> ToolResult:
        """
        List directory contents.

        Args:
            dirpath: Path to the directory to list
            pattern: Glob pattern to filter files (default: *)
            recursive: List subdirectories recursively
            include_hidden: Include hidden files and directories
        """
        try:
            path = Path(dirpath).resolve()

            # Safety checks
            if not self._is_safe_path(path):
                return ToolResult(
                    success=False,
                    error="Access denied: Path not allowed or potentially dangerous",
                )

            if not path.exists():
                return ToolResult(
                    success=False, error=f"Directory not found: {dirpath}"
                )

            if not path.is_dir():
                return ToolResult(
                    success=False, error=f"Path is not a directory: {dirpath}"
                )

            # List contents
            files = []
            dirs = []

            if recursive:
                items = path.rglob(pattern)
            else:
                items = path.glob(pattern)

            for item in items:
                if not self._is_safe_path(item):
                    continue

                # Skip hidden files unless requested
                if not include_hidden and item.name.startswith("."):
                    continue

                rel_path = str(item.relative_to(self.root_dir))

                if item.is_file():
                    stat = item.stat()
                    files.append(
                        {
                            "name": item.name,
                            "path": rel_path,
                            "size": stat.st_size,
                            "extension": item.suffix,
                            "last_modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )
                elif item.is_dir():
                    dirs.append(
                        {
                            "name": item.name,
                            "path": rel_path,
                            "last_modified": datetime.fromtimestamp(
                                item.stat().st_mtime
                            ).isoformat(),
                        }
                    )

            return ToolResult(
                success=True,
                data={
                    "directory": str(path.relative_to(self.root_dir)),
                    "absolute_path": str(path),
                    "files": sorted(files, key=lambda x: x["name"]),
                    "directories": sorted(dirs, key=lambda x: x["name"]),
                    "total_files": len(files),
                    "total_directories": len(dirs),
                    "pattern": pattern,
                    "recursive": recursive,
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error listing directory: {str(e)}")

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dirpath": {
                            "type": "string",
                            "description": "Path to the directory to list (relative to current directory)",
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to filter files (e.g., '*.py', '*.txt')",
                            "default": "*",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "List subdirectories recursively",
                            "default": False,
                        },
                        "include_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories (starting with .)",
                            "default": False,
                        },
                    },
                    "required": ["dirpath"],
                },
            },
        }


class SearchFilesTool(BaseTool):
    """Tool for searching files by name or content."""

    def __init__(self, root_dir: str | None = None):
        super().__init__(
            name="search_files",
            description="Search for files by filename or content within files. Supports pattern matching.",
        )
        self.root_dir = Path(root_dir or os.getcwd()).resolve()

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive_parts = [
                ".git",
                "__pycache__",
                ".env",
                "node_modules",
                ".venv",
                "venv",
                ".DS_Store",
                "Thumbs.db",
            ]
            if any(part in resolved.parts for part in sensitive_parts):
                return False

            return True
        except Exception:
            return False

    def __call__(
        self,
        query: str,
        search_path: str | None = None,
        search_type: str = "filename",
        file_pattern: str = "*",
        max_results: int = 50,
        case_sensitive: bool = False,
    ) -> ToolResult:
        """
        Search for files.

        Args:
            query: Search query string
            search_path: Path to search in (default: current directory)
            search_type: Type of search ('filename' or 'content')
            file_pattern: Pattern to filter files (default: *)
            max_results: Maximum number of results to return
            case_sensitive: Whether the search should be case sensitive
        """
        try:
            base_path = Path(search_path or self.root_dir).resolve()

            # Safety checks
            if not self._is_safe_path(base_path):
                return ToolResult(
                    success=False,
                    error="Access denied: Path not allowed or potentially dangerous",
                )

            if not base_path.exists():
                return ToolResult(
                    success=False, error=f"Search path not found: {search_path}"
                )

            results = []
            search_query = query if case_sensitive else query.lower()

            # Search files
            for item in base_path.rglob(file_pattern):
                if not self._is_safe_path(item):
                    continue

                if len(results) >= max_results:
                    break

                # Skip directories for content search
                if search_type == "content" and not item.is_file():
                    continue

                # Filename search
                if search_type == "filename":
                    item_name = item.name if case_sensitive else item.name.lower()
                    if search_query in item_name:
                        stat = item.stat()
                        results.append(
                            {
                                "name": item.name,
                                "path": str(item.relative_to(self.root_dir)),
                                "match_type": "filename",
                                "is_directory": item.is_dir(),
                                "size": stat.st_size if item.is_file() else None,
                                "last_modified": datetime.fromtimestamp(
                                    stat.st_mtime
                                ).isoformat(),
                            }
                        )

                # Content search
                elif search_type == "content" and item.is_file():
                    try:
                        # Skip binary files
                        binary_extensions = {
                            ".exe",
                            ".dll",
                            ".so",
                            ".dylib",
                            ".bin",
                            ".img",
                            ".iso",
                            ".zip",
                            ".tar",
                            ".gz",
                            ".rar",
                            ".7z",
                            ".pdf",
                            ".doc",
                            ".docx",
                            ".xls",
                            ".xlsx",
                            ".ppt",
                            ".pptx",
                            ".jpg",
                            ".jpeg",
                            ".png",
                            ".gif",
                            ".bmp",
                            ".tiff",
                            ".mp3",
                            ".mp4",
                            ".avi",
                            ".mov",
                        }

                        if item.suffix.lower() in binary_extensions:
                            continue

                        # Read and search content
                        with open(item, encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            search_content = (
                                content if case_sensitive else content.lower()
                            )

                            if search_query in search_content:
                                # Find line numbers where query appears
                                lines = content.split("\n")
                                matching_lines = []
                                for i, line in enumerate(lines, 1):
                                    line_search = (
                                        line if case_sensitive else line.lower()
                                    )
                                    if search_query in line_search:
                                        matching_lines.append(i)
                                        if (
                                            len(matching_lines) >= 5
                                        ):  # Limit to first 5 matches
                                            break

                                stat = item.stat()
                                results.append(
                                    {
                                        "name": item.name,
                                        "path": str(item.relative_to(self.root_dir)),
                                        "match_type": "content",
                                        "size": stat.st_size,
                                        "matching_lines": matching_lines,
                                        "last_modified": datetime.fromtimestamp(
                                            stat.st_mtime
                                        ).isoformat(),
                                    }
                                )
                    except Exception:
                        # Skip files that can't be read
                        continue

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "search_path": str(base_path.relative_to(self.root_dir)),
                    "search_type": search_type,
                    "file_pattern": file_pattern,
                    "results": results,
                    "total_found": len(results),
                    "case_sensitive": case_sensitive,
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error searching files: {str(e)}")

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string",
                        },
                        "search_path": {
                            "type": "string",
                            "description": "Path to search in (relative to current directory)",
                            "default": ".",
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search to perform",
                            "enum": ["filename", "content"],
                            "default": "filename",
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "Pattern to filter files (e.g., '*.py', '*.txt')",
                            "default": "*",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 50,
                            "minimum": 1,
                            "maximum": 200,
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Whether the search should be case sensitive",
                            "default": False,
                        },
                    },
                    "required": ["query"],
                },
            },
        }


class CreateDirectoryTool(BaseTool):
    """Tool for creating directories."""

    def __init__(self, root_dir: str | None = None):
        super().__init__(
            name="create_directory",
            description="Create a new directory. Creates parent directories if they don't exist.",
        )
        self.root_dir = Path(root_dir or os.getcwd()).resolve()

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to create."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive_parts = [
                ".git",
                "__pycache__",
                ".env",
                "node_modules",
                ".venv",
                "venv",
                ".DS_Store",
                "Thumbs.db",
            ]
            if any(part in resolved.parts for part in sensitive_parts):
                return False

            # Avoid system directories on Windows
            if os.name == "nt":
                system_dirs = [
                    "Windows",
                    "Program Files",
                    "Program Files (x86)",
                    "System32",
                ]
                if any(part in resolved.parts for part in system_dirs):
                    return False

            return True
        except Exception:
            return False

    def __call__(
        self, dirpath: str, create_parents: bool = True, exist_ok: bool = False
    ) -> ToolResult:
        """
        Create a directory.

        Args:
            dirpath: Path to the directory to create
            create_parents: Create parent directories if they don't exist
            exist_ok: Don't raise error if directory already exists
        """
        try:
            path = Path(dirpath).resolve()

            # Safety checks
            if not self._is_safe_path(path):
                return ToolResult(
                    success=False,
                    error="Access denied: Path not allowed or potentially dangerous",
                )

            # Check if path exists
            if path.exists():
                if path.is_dir():
                    if exist_ok:
                        return ToolResult(
                            success=True,
                            data={
                                "directory": str(path.relative_to(self.root_dir)),
                                "absolute_path": str(path),
                                "already_existed": True,
                                "timestamp": datetime.now().isoformat(),
                            },
                        )
                    else:
                        return ToolResult(
                            success=False, error=f"Directory already exists: {dirpath}"
                        )
                else:
                    return ToolResult(
                        success=False,
                        error=f"Path exists but is not a directory: {dirpath}",
                    )

            # Create directory
            path.mkdir(parents=create_parents, exist_ok=exist_ok)

            return ToolResult(
                success=True,
                data={
                    "directory": str(path.relative_to(self.root_dir)),
                    "absolute_path": str(path),
                    "created": True,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            return ToolResult(
                success=False, error=f"Error creating directory: {str(e)}"
            )

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dirpath": {
                            "type": "string",
                            "description": "Path to the directory to create (relative to current directory)",
                        },
                        "create_parents": {
                            "type": "boolean",
                            "description": "Create parent directories if they don't exist",
                            "default": True,
                        },
                        "exist_ok": {
                            "type": "boolean",
                            "description": "Don't raise error if directory already exists",
                            "default": False,
                        },
                    },
                    "required": ["dirpath"],
                },
            },
        }


class GetFileInfoTool(BaseTool):
    """Tool for getting file metadata."""

    def __init__(self, root_dir: str | None = None):
        super().__init__(
            name="get_file_info",
            description="Get detailed metadata about a file or directory including size, creation date, and modification date.",
        )
        self.root_dir = Path(root_dir or os.getcwd()).resolve()

    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe to access."""
        try:
            resolved = path.resolve()
            # Must be within root directory
            if not str(resolved).startswith(str(self.root_dir)):
                return False

            # Avoid sensitive paths
            sensitive_parts = [
                ".git",
                "__pycache__",
                ".env",
                "node_modules",
                ".venv",
                "venv",
                ".DS_Store",
                "Thumbs.db",
            ]
            if any(part in resolved.parts for part in sensitive_parts):
                return False

            return True
        except Exception:
            return False

    def __call__(self, filepath: str) -> ToolResult:
        """
        Get file metadata.

        Args:
            filepath: Path to the file or directory
        """
        try:
            path = Path(filepath).resolve()

            # Safety checks
            if not self._is_safe_path(path):
                return ToolResult(
                    success=False,
                    error="Access denied: Path not allowed or potentially dangerous",
                )

            if not path.exists():
                return ToolResult(success=False, error=f"Path not found: {filepath}")

            stat = path.stat()

            # Get file type info
            if path.is_file():
                # Try to determine file type
                file_type = "unknown"
                if path.suffix:
                    file_type = path.suffix.lower().lstrip(".")

                # For text files, try to count lines
                line_count = None
                if file_type in [
                    "txt",
                    "py",
                    "js",
                    "html",
                    "css",
                    "json",
                    "yaml",
                    "yml",
                    "md",
                ]:
                    try:
                        with open(path, encoding="utf-8", errors="ignore") as f:
                            line_count = sum(1 for _ in f)
                    except Exception:
                        pass
            else:
                file_type = "directory"
                line_count = None

            return ToolResult(
                success=True,
                data={
                    "name": path.name,
                    "path": str(path.relative_to(self.root_dir)),
                    "absolute_path": str(path),
                    "type": file_type,
                    "is_file": path.is_file(),
                    "is_directory": path.is_dir(),
                    "size": stat.st_size,
                    "size_human": self._format_size(stat.st_size),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                    "extension": path.suffix,
                    "line_count": line_count,
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error getting file info: {str(e)}")

    def _format_size(self, size: int) -> str:
        """Format file size in human readable format."""
        for Glimpse in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {Glimpse}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file or directory (relative to current directory)",
                        }
                    },
                    "required": ["filepath"],
                },
            },
        }


# Initialize all filesystem tools
def create_filesystem_tools(root_dir: str | None = None) -> list[BaseTool]:
    """Create and return all filesystem tools."""
    return [
        ReadFileTool(root_dir),
        WriteFileTool(root_dir),
        ListDirectoryTool(root_dir),
        SearchFilesTool(root_dir),
        CreateDirectoryTool(root_dir),
        GetFileInfoTool(root_dir),
    ]
