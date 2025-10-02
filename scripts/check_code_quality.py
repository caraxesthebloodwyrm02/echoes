#!/usr/bin/env python3
"""
Run all code quality checks in sequence:
1. Black (code formatting)
2. isort (import sorting)
3. mypy (type checking)
"""
import subprocess
import sys
from pathlib import Path

def run_command(command: str, cwd: Path) -> bool:
    """Run a shell command and return True if successful."""
    print(f"\n\033[1mRunning: {command}\033[0m")
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        print("\033[92m✓ Success\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m✗ Failed with exit code {e.returncode}\033[0m")
        return False

def main() -> int:
    """Run all code quality checks."""
    root_dir = Path(__file__).parent.parent
    checks = [
        "python -m black --check automation tests",
        "python -m isort --check-only automation tests",
        "python -m mypy automation tests"
    ]
    
    print("\n\033[1;34m=== Running Code Quality Checks ===\033[0m")
    
    all_passed = True
    for check in checks:
        if not run_command(check, root_dir):
            all_passed = False
    
    if all_passed:
        print("\n\033[1;32m✓ All checks passed!\033[0m")
        return 0
    else:
        print("\n\033[1;31m✗ Some checks failed. Please fix the issues and try again.\033[0m")
        print("\nTo fix formatting and import sorting issues, run:")
        print("  python -m black automation tests")
        print("  python -m isort automation tests")
        return 1

if __name__ == "__main__":
    sys.exit(main())
