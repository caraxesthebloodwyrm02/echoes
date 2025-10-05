#!/usr/bin/env python3
"""
Automated Deployment Script for Semantic Resonance Engine
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command, shell=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def deploy_to_environment(environment="staging"):
    """Deploy to specified environment"""
    print(f"🚀 Deploying to {environment}...")

    # Build the package
    print("📦 Building package...")
    success, stdout, stderr = run_command("python -m build")
    if not success:
        print(f"❌ Build failed: {stderr}")
        return False

    # Install the package
    print("🔧 Installing package...")
    success, stdout, stderr = run_command("pip install dist/*.whl")
    if not success:
        print(f"❌ Installation failed: {stderr}")
        return False

    # Run health checks
    print("🏥 Running health checks...")
    success, stdout, stderr = run_command(
        "python -c \"from semantic_resonance import SmartSearchEngine; print('✅ Import successful')\""
    )
    if not success:
        print(f"❌ Health check failed: {stderr}")
        return False

    # Run tests
    print("🧪 Running tests...")
    success, stdout, stderr = run_command("python run_tests.py all")
    if not success:
        print(f"❌ Tests failed: {stderr}")
        return False

    print(f"✅ Deployment to {environment} successful!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy Semantic Resonance Engine")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="staging",
        help="Target environment",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deployed without actually doing it",
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 Dry run mode - showing deployment steps...")
        print(f"Would deploy to: {args.env}")
        print("Steps:")
        print("1. Build package with 'python -m build'")
        print("2. Install package from dist/")
        print("3. Run health checks")
        print("4. Run test suite")
        return

    success = deploy_to_environment(args.env)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
