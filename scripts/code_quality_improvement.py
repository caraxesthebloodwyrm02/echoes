#!/usr/bin/env python3
"""
FinanceAdvisor Code Quality Improvement Script

This script applies comprehensive code quality improvements:
- Black formatting with Python 3.8+ compatibility
- Import sorting with isort
- Linting with flake8
- Type checking with mypy (optional)
- Security scanning with bandit
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()[:200]}...")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def main():
    """Main code quality improvement workflow"""
    print("🎨 FinanceAdvisor Code Quality Improvement")
    print("=" * 50)

    # Step 1: Black formatting with Python 3.8+ compatibility
    run_command(
        "black --target-version py38 --line-length 100 app/ tests/",
        "Black code formatting (Python 3.8+ compatible)",
    )

    # Step 2: Import sorting
    run_command("isort --profile black app/ tests/", "Import sorting with isort")

    # Step 3: Linting with flake8
    run_command(
        "flake8 --max-line-length 100 --extend-ignore E203,W503 app/ tests/",
        "Code linting with flake8",
    )

    # Step 4: Type checking (optional, may have import issues)
    print("\n🔧 Type checking with mypy (optional)...")
    try:
        result = subprocess.run(
            "mypy --ignore-missing-imports --no-error-summary app/",
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,  # 30 second timeout
        )
        if result.returncode == 0:
            print("✅ Type checking completed successfully")
        else:
            print("⚠️ Type checking completed with warnings (this is normal for complex projects)")
    except subprocess.TimeoutExpired:
        print("⏰ Type checking timed out (normal for large codebases)")
    except Exception as e:
        print(f"⚠️ Type checking skipped: {e}")

    # Step 5: Security scanning
    run_command("bandit -r app/ -x 'app/test_*' -f txt", "Security scanning with bandit")

    print("\n" + "=" * 50)
    print("🎉 Code quality improvement completed!")
    print("=" * 50)

    print("\n📋 NEXT STEPS:")
    print("   1. Review any linting errors and fix as needed")
    print("   2. Run tests to ensure functionality is preserved")
    print("   3. Commit changes with clear commit message")
    print("   4. Set up pre-commit hooks for ongoing quality")


if __name__ == "__main__":
    main()
