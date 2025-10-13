#!/usr/bin/env python3
"""
Setup script for codebase metrics collection and visualization.
Ensures all required tools are installed and properly configured.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return (success, output)."""
    try:
        result = subprocess.run(cmd, cwd=cwd or os.getcwd(), check=True, shell=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Command failed with code {e.returncode}: {e.stderr}"


def main():
    print("Setting up codebase metrics tools...")

    # Create metrics directory if it doesn't exist
    metrics_dir = Path("metrics")
    metrics_dir.mkdir(exist_ok=True)
    (metrics_dir / "plots").mkdir(exist_ok=True)

    # Check and install required packages
    required = ["flake8", "pytest", "pytest-cov", "radon", "matplotlib"]
    print(f"Checking required packages: {', '.join(required)}")

    for pkg in required:
        print(f"Checking {pkg}...")
        success, _ = run_command(f"pip show {pkg}")
        if not success:
            print(f"Installing {pkg}...")
            success, output = run_command(f"pip install {pkg}")
            if not success:
                print(f"Failed to install {pkg}: {output}")
                return 1

    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Run: flake8 --format=json > flake8_report.json")
    print("2. Run: coverage run -m pytest")
    print("3. Run: coverage json -o coverage.json")
    print("4. Run: python metrics/codebase_visualizer.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
