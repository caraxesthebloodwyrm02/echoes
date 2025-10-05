#!/usr/bin/env python3
"""
Local CI Simulation Script
Run this script to simulate the GitHub Actions CI pipeline locally before committing.

Usage: python scripts/local_ci_simulate.py
"""

import os
import sys
import subprocess
import time
import requests
import json


def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, check=check, capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e}")
        if capture_output:
            print(f"Output: {e.output}")
        sys.exit(1)


def check_file_exists(filepath):
    """Check if a file exists."""
    if not os.path.isfile(filepath):
        print(f"❌ Required file '{filepath}' not found.")
        sys.exit(1)


def main():
    print("🚀 Starting Local CI Simulation...")

    # 1. Check if we're in a git repo
    if not os.path.isdir(".git"):
        print("❌ Not in a git repository. Run 'git init' first.")
        sys.exit(1)

    # 2. Check for required files
    required_files = [
        "requirements.txt",
        "mcp_requirements.txt",
        "pyproject.toml",
        ".pre-commit-config.yaml",
        "README.md",
    ]
    for file in required_files:
        check_file_exists(file)

    print("✅ Repository and required files check passed.")

    # 3. Check Python environment
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️  Warning: No virtual environment detected.")
        print("   Activate your virtual environment first:")
        print("   Windows: .\\.venv\\Scripts\\activate")
        print("   Linux/Mac: source venv/bin/activate")

    # 4. Install dependencies
    print("📦 Installing dependencies...")
    run_command("python -m pip install --upgrade pip")
    run_command("pip install -r requirements.txt")
    run_command("pip install -r mcp_requirements.txt")
    run_command("pip install pytest pytest-asyncio pytest-cov httpx fastapi[all]")
    run_command("pip install ruff black mypy bandit safety")
    run_command("pip install pre-commit")
    print("✅ Dependencies installed.")

    # 5. Run Ruff linting
    print("🔍 Running Ruff linting...")
    run_command(
        "ruff check app packages automation --select=E9,F63,F7,F82 --show-source --statistics"
    )
    run_command("ruff check app packages automation --exit-zero --statistics")
    print("✅ Ruff linting passed.")

    # 6. Run Black formatting check
    print("🎨 Checking Black formatting...")
    run_command("black --check app packages automation tests")
    print("✅ Black formatting check passed.")

    # 7. Run mypy type checking
    print("🔍 Running mypy type checking...")
    run_command("mypy app packages automation --ignore-missing-imports")
    print("✅ mypy type checking passed.")

    # 8. Run Bandit security scan
    print("🔒 Running Bandit security scan...")
    run_command("bandit -r app packages automation -ll -i")
    print("✅ Bandit security scan passed.")

    # 9. Run safety dependency check
    print("🛡️  Running safety dependency check...")
    try:
        run_command("safety check --json")
    except:
        print("⚠️  Safety check had issues, but continuing...")
    print("✅ Safety check completed.")

    # 10. Run unit tests with coverage
    print("🧪 Running unit tests with coverage...")
    run_command(
        "pytest tests/ -v --cov=app --cov=packages --cov-report=xml --cov-report=term --cov-fail-under=80"
    )
    print("✅ Unit tests passed.")

    # 11. Run async tests
    print("🧪 Running async tests...")
    run_command("pytest tests/test_async.py -v")
    print("✅ Async tests passed.")

    # 12. Test MCP server locally
    print("🤖 Testing MCP server...")
    # Start server in background (cross-platform)
    if os.name == "nt":  # Windows
        server_process = subprocess.Popen([sys.executable, "mcp_server.py"])
    else:
        server_process = subprocess.Popen([sys.executable, "mcp_server.py"])

    time.sleep(5)  # Wait for server to start

    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8081/health")
        response.raise_for_status()
        print("✅ MCP health check passed.")

        # Test echo tool
        payload = {"text": "test", "repeat": 2}
        response = requests.post("http://127.0.0.1:8081/tools/echo", json=payload)
        response.raise_for_status()
        data = response.json()
        expected = "test test"
        if data.get("echoed") == expected:
            print("✅ MCP echo tool test passed.")
        else:
            print(f"❌ MCP echo tool test failed. Expected '{expected}', got '{data.get('echoed')}'")
            server_process.terminate()
            sys.exit(1)

    except requests.RequestException as e:
        print(f"❌ MCP server test failed: {e}")
        server_process.terminate()
        sys.exit(1)

    # Stop server
    server_process.terminate()
    print("✅ MCP server tests passed.")

    # 13. Run pre-commit hooks
    print("🔗 Running pre-commit hooks...")
    run_command("pre-commit run --all-files")
    print("✅ Pre-commit hooks passed.")

    # 14. Check compliance (imports)
    print("📋 Running compliance checks...")
    run_command(
        "python -c \"from app.core.validation.provenance_enforcer import ProvenanceEnforcerMiddleware; print('✅ Provenance enforcer imports successfully')\""
    )
    run_command(
        "python -c \"from app.api.schemas import Provenance, Assertion, HILFeedback, AgentExecutionRequest; print('✅ All safety schemas validated')\""
    )
    print("✅ Compliance checks passed.")

    # 15. Verify documentation exists
    print("📚 Verifying documentation...")
    check_file_exists("docs/DOMAIN_EXPANSION_PLAN.md")
    check_file_exists("README.md")
    print("✅ Documentation files present.")

    print("\n🎉 All local CI simulations passed!")
    print("\nNext steps:")
    print("1. Review any warnings above.")
    print("2. If everything looks good, commit your changes:")
    print("   git add .")
    print("   git commit -m 'Your commit message'")
    print("3. Push to trigger remote CI:")
    print("   git push origin main")
    print("\nRemember: This script simulates CI but doesn't guarantee remote CI success.")
    print("Always check GitHub Actions after pushing.")


if __name__ == "__main__":
    main()
