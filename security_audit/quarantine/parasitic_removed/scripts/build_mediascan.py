"""
Build script for MediaScan PyPI package.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None


def main():
    """Build the MediaScan package."""
    print("🚀 Building MediaScan package for PyPI")
    print("=" * 50)

    # Ensure we're in the right directory
    project_root = Path(__file__).parent

    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    for dist_dir in ["dist", "build", "*.egg-info"]:
        run_command(f"rm -rf {dist_dir}", f"Removing {dist_dir}")

    # Install build dependencies
    run_command("pip install --upgrade build twine", "Installing build dependencies")

    # Build the package
    if run_command("python -m build", "Building package") is None:
        print("\n❌ Build failed. Please check the errors above.")
        sys.exit(1)

    # Check the package
    if run_command("python -m twine check dist/*", "Checking package") is None:
        print("\n❌ Package check failed.")
        sys.exit(1)

    print("\n📦 Package built successfully!")
    print("\nTo upload to PyPI:")
    print("1. Test upload: python -m twine upload --repository testpypi dist/*")
    print("2. Production upload: python -m twine upload dist/*")
    print("\nTo install locally:")
    print("pip install dist/mediascan-0.1.0-py3-none-any.whl")

    # List built files
    print("\n📋 Built files:")
    dist_files = list(Path("dist").glob("*"))
    for file in dist_files:
        size = file.stat().st_size / 1024  # Size in KB
        print(f"  - {file.name} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
