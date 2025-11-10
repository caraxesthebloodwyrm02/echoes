#!/usr/bin/env python3
"""
Echoes AI PyPI Publishing Script

This script automates the process of building and publishing the Echoes AI package to PyPI.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(
    cmd: list, cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, cwd=cwd or Path.cwd(), check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def clean_build_dirs(project_root: Path):
    """Clean build directories."""
    print("🧹 Cleaning build directories...")

    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in project_root.glob(pattern):
            if path.is_dir():
                print(f"Removing directory: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing file: {path}")
                path.unlink()


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")

    required_packages = ["build", "twine", "wheel"]
    missing_packages = []

    for package in required_packages:
        try:
            run_command([sys.executable, "-c", f"import {package}"])
            print(f"✅ {package} is installed")
        except:
            missing_packages.append(package)
            print(f"❌ {package} is missing")

    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        run_command([sys.executable, "-m", "pip", "install"] + missing_packages)


def run_tests(project_root: Path):
    """Run tests to ensure package quality."""
    print("🧪 Running tests...")

    # Check if pytest is available
    try:
        run_command([sys.executable, "-c", "import pytest"])
        run_command([sys.executable, "-m", "pytest", "tests/", "-v"], cwd=project_root)
        print("✅ Tests passed")
    except:
        print("⚠️  pytest not found, skipping tests")


def run_linting(project_root: Path):
    """Run linting to ensure code quality."""
    print("🔍 Running linting...")

    # Check if ruff is available
    try:
        run_command([sys.executable, "-c", "import ruff"])
        run_command([sys.executable, "-m", "ruff", "check", "."], cwd=project_root)
        print("✅ Linting passed")
    except:
        print("⚠️  ruff not found, skipping linting")


def build_package(project_root: Path):
    """Build the package."""
    print("📦 Building package...")

    # Clean first
    clean_build_dirs(project_root)

    # Build the package
    run_command([sys.executable, "-m", "build"], cwd=project_root)

    # Check if build was successful
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        print("❌ Build failed - no dist directory found")
        sys.exit(1)

    built_files = list(dist_dir.glob("*"))
    if not built_files:
        print("❌ Build failed - no files in dist directory")
        sys.exit(1)

    print("✅ Package built successfully:")
    for file in built_files:
        print(f"  - {file.name}")


def check_package(project_root: Path):
    """Check the built package."""
    print("🔍 Checking package...")

    project_root / "dist"
    run_command([sys.executable, "-m", "twine", "check", "dist/*"], cwd=project_root)
    print("✅ Package check passed")


def upload_to_testpypi(project_root: Path):
    """Upload package to Test PyPI."""
    print("🚀 Uploading to Test PyPI...")

    # Check for Test PyPI token
    testpypi_token = os.getenv("TEST_PYPI_TOKEN")
    if not testpypi_token:
        print("⚠️  TEST_PYPI_TOKEN environment variable not set")
        print("You can set it or upload manually:")
        print("  twine upload --repository testpypi dist/*")
        return False

    # Upload to Test PyPI
    run_command(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--repository",
            "testpypi",
            "--username",
            "__token__",
            "--password",
            testpypi_token,
            "dist/*",
        ],
        cwd=project_root,
    )

    print("✅ Uploaded to Test PyPI successfully")
    return True


def upload_to_pypi(project_root: Path):
    """Upload package to PyPI."""
    print("🚀 Uploading to PyPI...")

    # Check for PyPI token
    pypi_token = os.getenv("PYPI_TOKEN")
    if not pypi_token:
        print("⚠️  PYPI_TOKEN environment variable not set")
        print("You can set it or upload manually:")
        print("  twine upload --repository pypi dist/*")
        return False

    # Upload to PyPI
    run_command(
        [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--repository",
            "pypi",
            "--username",
            "__token__",
            "--password",
            pypi_token,
            "dist/*",
        ],
        cwd=project_root,
    )

    print("✅ Uploaded to PyPI successfully")
    return True


def main():
    """Main publishing function."""
    parser = argparse.ArgumentParser(description="Publish Echoes AI to PyPI")
    parser.add_argument(
        "--repository",
        "-r",
        choices=["testpypi", "pypi", "both"],
        default="testpypi",
        help="Repository to publish to (default: testpypi)",
    )
    parser.add_argument(
        "--skip-tests", "-t", action="store_true", help="Skip running tests"
    )
    parser.add_argument(
        "--skip-linting", "-l", action="store_true", help="Skip running linting"
    )
    parser.add_argument(
        "--dry-run", "-d", action="store_true", help="Build package but don't upload"
    )

    args = parser.parse_args()

    # Get project root
    project_root = Path(__file__).parent.parent

    print("🎯 Echoes AI PyPI Publishing")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print(f"Repository: {args.repository}")
    print(f"Skip tests: {args.skip_tests}")
    print(f"Skip linting: {args.skip_linting}")
    print(f"Dry run: {args.dry_run}")
    print()

    try:
        # Check dependencies
        check_dependencies()

        # Run tests
        if not args.skip_tests:
            run_tests(project_root)

        # Run linting
        if not args.skip_linting:
            run_linting(project_root)

        # Build package
        build_package(project_root)

        # Check package
        check_package(project_root)

        # Upload if not dry run
        if not args.dry_run:
            if args.repository in ["testpypi", "both"]:
                upload_to_testpypi(project_root)

            if args.repository in ["pypi", "both"]:
                # Ask for confirmation before uploading to production PyPI
                if args.repository == "both":
                    response = input("Upload to production PyPI? (y/N): ")
                    if response.lower() != "y":
                        print("Skipping production PyPI upload")
                    else:
                        upload_to_pypi(project_root)
                else:
                    upload_to_pypi(project_root)
        else:
            print("🏁 Dry run completed - package built but not uploaded")

        print("\n🎉 Publishing process completed successfully!")

        # Show installation instructions
        if not args.dry_run and args.repository in ["pypi", "both"]:
            print("\n📦 Installation instructions:")
            print("  pip install echoes-ai")
            print("  pip install echoes-ai[dev]    # Development dependencies")
            print("  pip install echoes-ai[all]    # All dependencies")

        if not args.dry_run and args.repository in ["testpypi", "both"]:
            print("\n📦 Test PyPI installation:")
            print("  pip install --index-url https://test.pypi.org/simple/ echoes-ai")

    except KeyboardInterrupt:
        print("\n❌ Publishing process cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Publishing process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
