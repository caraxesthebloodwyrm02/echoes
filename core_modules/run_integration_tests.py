#!/usr/bin/env python
"""
Clean test runner for cross-platform integration tests
Avoids pytest cache issues by disabling cache provider
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run integration tests with clean configuration"""
    test_file = Path(__file__).parent / "tests" / "test_cross_platform_integration.py"

    # Run pytest with cache disabled
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "-p",
        "no:cacheprovider",  # Disable cache to avoid file descriptor issues
        "--tb=short",
    ]

    print("Running cross-platform integration tests...")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
