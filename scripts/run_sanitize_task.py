"""
Run the sanitize_codebase task defined in automation.tasks.sanitize_codebase.

This script imports the task module and executes the `sanitize_codebase` function
with the parameters specified in the user request.
"""

import os

# Ensure the current directory is on sys.path so that the 'automation' package can be imported
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the task function (ignore import error for static analysis)
from automation.tasks.sanitize_codebase import sanitize_codebase  # type: ignore

if __name__ == "__main__":
    # Define the target directory and rules as per the user request
    target_directory = Path("src")
    rules = ["remove_temp_files", "format_code", "sort_imports"]

    try:
        sanitize_codebase(target_directory, rules)
    except Exception as exc:  # pragma: no cover - defensive
        import sys

        print(f"Error running sanitize_codebase: {exc}", file=sys.stderr)
        sys.exit(1)
