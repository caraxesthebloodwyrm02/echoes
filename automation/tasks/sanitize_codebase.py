"""Task to clean up and sanitize the codebase."""

import os
import shutil
from pathlib import Path
from typing import List, Set, Optional

from automation.core.context import Context
from automation.core.logger import log


def _remove_directory(directory: Path, dry_run: bool = False) -> None:
    """Remove a directory if it exists.

    Args:
        directory: Directory to remove
        dry_run: If True, only log what would be done
    """
    if not directory.exists():
        return

    if dry_run:
        log.info(f"[DRY RUN] Would remove directory: {directory}")
        return

    try:
        shutil.rmtree(directory)
        log.info(f"Removed directory: {directory}")
    except Exception as e:
        log.error(f"Failed to remove directory {directory}: {e}")


def _get_project_root(context: Context) -> Path:
    """Get the project root directory from context or use current directory."""
    project_root = context.extra.get("project_root")
    if project_root:
        return Path(project_root).resolve()
    return Path.cwd()


def _get_directories_to_clean() -> Set[str]:
    """Get a set of directory names to clean."""
    return {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
        "*.egg-info",
        "node_modules",
        ".tox",
        ".venv",
        "venv",
        "env",
        ".env",
        ".eggs",
        ".cache",
        "coverage",
        ".coverage",
        "htmlcov",
        ".mypy_cache",
        ".ruff_cache",
        ".hypothesis",
        ".ipynb_checkpoints",
    }


def run(context: Context) -> None:
    """Run the codebase sanitization task.

    Args:
        context: Execution context
    """
    project_root = _get_project_root(context)
    log.info(f"Sanitizing codebase in: {project_root}")

    directories_to_clean = _get_directories_to_clean()

    for dir_pattern in directories_to_clean:
        # Handle patterns like '*.egg-info'
        if "*" in dir_pattern:
            for path in project_root.glob("**/" + dir_pattern):
                if path.is_dir():
                    _remove_directory(path, context.dry_run)
        else:
            # Handle exact directory names
            for path in project_root.rglob(dir_pattern):
                if path.is_dir() and path.name == dir_pattern:
                    _remove_directory(path, context.dry_run)

    log.success("Codebase sanitization complete")
