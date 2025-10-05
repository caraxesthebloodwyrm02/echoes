"""
Module: automation.tasks.sanitize_codebase

This module provides a simple function to sanitize a codebase by removing temporary files
and optionally formatting the code.

The function `sanitize_codebase` accepts a target directory and a list of rules. The
supported rules are:

- ``remove_temp_files``: Delete files with common temporary extensions such as
  ``.tmp``, ``.temp`` and ``.bak``.
- ``format_code``: Run the ``black`` formatter on the target directory if it is
  available. If ``black`` is not installed, the function will simply skip
  formatting.
- ``sort_imports``: Run the ``isort`` import sorter on the target directory if it is
  available. If ``isort`` is not installed, the function will simply skip
  import sorting.

The module can also be executed directly from the command line for quick
sanitization.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

__all__ = ["sanitize_codebase"]


def _remove_temp_files(target: Path) -> None:
    """Recursively delete temporary files from *target*.

    Temporary files are identified by the extensions ``.tmp``, ``.temp`` and
    ``.bak``. Hidden files and directories are ignored.
    """
    temp_extensions = {".tmp", ".temp", ".bak"}
    for root, dirs, files in os.walk(target, topdown=True):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if Path(file).suffix.lower() in temp_extensions:
                file_path = Path(root) / file
                try:
                    file_path.unlink()
                    print(f"Removed temp file: {file_path}")
                except Exception as exc:  # pragma: no cover - defensive
                    print(f"Failed to remove {file_path}: {exc}", file=sys.stderr)


def _format_code(target: Path) -> None:
    """Format the code in *target* using ``black`` if available.

    The function attempts to run ``black`` via the command line. If ``black`` is not
    installed, a warning is printed and the function returns.
    """
    try:
        subprocess.run(["black", str(target)], check=True)
        print("Formatted code with black.")
    except Exception:  # pragma: no cover - defensive
        print("Black formatter not available. Skipping formatting.", file=sys.stderr)


def _sort_imports(target: Path) -> None:
    """Sort imports in *target* using ``isort`` if available.

    The function attempts to run ``isort`` via the command line. If ``isort`` is not
    installed, a warning is printed and the function returns.
    """
    try:
        subprocess.run(["isort", str(target)], check=True)
        print("Sorted imports with isort.")
    except Exception:  # pragma: no cover - defensive
        print("Isort not available. Skipping import sorting.", file=sys.stderr)


def sanitize_codebase(context) -> None:
    """Sanitize the codebase according to the context parameters.

    Parameters
    ----------
    context:
        Context object containing dry_run flag and extra_data with target_directory and rules.
    """
    from automation.core.logger import AutomationLogger

    log = AutomationLogger()

    target_directory = context.extra_data.get("target_directory", "/src")
    rules = context.extra_data.get("rules", ["remove_temp_files"])

    log.info(f"Sanitizing codebase at {target_directory} with rules: {rules}")

    if context.dry_run:
        log.info("Dry-run mode: skipping actual sanitization")
        return

    target = Path(target_directory).expanduser().resolve()
    if not target.is_dir():
        raise ValueError(f"Target directory does not exist: {target}")

    for rule in rules:
        if rule == "remove_temp_files":
            _remove_temp_files(target)
        elif rule == "format_code":
            _format_code(target)
        elif rule == "sort_imports":
            _sort_imports(target)
        else:
            log.error(f"Unknown rule '{rule}'. Skipping.")


if __name__ == "__main__":  # pragma: no cover - CLI helper
    import argparse

    parser = argparse.ArgumentParser(description="Sanitize a codebase.")
    parser.add_argument("target", help="Target directory to sanitize.")
    parser.add_argument(
        "--rules",
        nargs="+",
        default=["remove_temp_files", "format_code"],
        help="Rules to apply. Supported: remove_temp_files, format_code, sort_imports.",
    )
    args = parser.parse_args()
    try:
        sanitize_codebase(args.target, args.rules)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
