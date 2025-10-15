# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Path resolution utilities for consistent file path handling."""

from pathlib import Path
from typing import Optional


class PathResolver:
    """Utility class for resolving and managing file paths safely."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize path resolver with a base directory."""
        self.base_dir = base_dir or Path(__file__).parent.parent

    def resolve_path(self, relative_path: str) -> Path:
        """Resolve relative paths safely from the base directory."""
        try:
            resolved = (self.base_dir / relative_path).resolve()
            # Ensure the resolved path is within the base directory for security
            resolved.relative_to(self.base_dir)
            return resolved
        except (ValueError, OSError) as e:
            raise ValueError(f"Invalid path resolution for '{relative_path}': {e}")

    def ensure_directory(self, path: Path) -> Path:
        """Ensure a directory exists, creating it if necessary."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except OSError as e:
            raise OSError(f"Failed to create directory '{path}': {e}")

    def safe_write(self, path: Path, content: str, encoding: str = "utf-8") -> None:
        """Safely write content to a file with error handling."""
        try:
            # Ensure parent directory exists
            self.ensure_directory(path.parent)

            # Write with temporary file for atomic operation
            temp_path = path.with_suffix(".tmp")
            with open(temp_path, "w", encoding=encoding) as f:
                f.write(content)

            # Atomic move to final location
            temp_path.replace(path)

        except OSError as e:
            raise OSError(f"Failed to write file '{path}': {e}")

    def safe_read(self, path: Path, encoding: str = "utf-8") -> str:
        """Safely read content from a file with error handling."""
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except (OSError, UnicodeDecodeError) as e:
            raise OSError(f"Failed to read file '{path}': {e}")


# Global path resolver instance
path_resolver = PathResolver()


def resolve_path(relative_path: str) -> Path:
    """Global function for path resolution."""
    return path_resolver.resolve_path(relative_path)


def get_project_root() -> Path:
    """Get the project root directory."""
    return path_resolver.base_dir


def get_config_path(filename: str) -> Path:
    """Get path for configuration files."""
    return resolve_path(f"config/{filename}")


def get_data_path(filename: str) -> Path:
    """Get path for data files."""
    return resolve_path(f"data/{filename}")


def get_logs_path(filename: str) -> Path:
    """Get path for log files."""
    return resolve_path(f"logs/{filename}")
