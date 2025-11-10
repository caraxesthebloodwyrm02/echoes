#!/usr/bin/env python3
"""
Module Import Updater for Echoes Project

This script updates import statements to reflect the new agent_* module names.
It automatically detects renamed modules by scanning for agent_*.py files.
"""
import re
from pathlib import Path

# Directories to scan for Python files
SOURCE_DIRS = ["core", "echoes", "tests", "app", "scripts"]

# Files or directories to skip
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist"}
SKIP_FILES = {"__init__.py", "__main__.py"}


def find_renamed_modules(root_dir: Path) -> dict[str, str]:
    """
    Find all agent_*.py files and build a mapping of original to new module names.
    Returns a dictionary mapping original names to agent_* names.
    """
    rename_map = {}

    for py_file in root_dir.rglob("agent_*.py"):
        # Skip files in directories we want to ignore
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue

        if py_file.name in SKIP_FILES:
            continue

        # Get the original module name (without agent_ prefix and .py extension)
        original_name = py_file.stem[6:]  # Remove 'agent_' prefix

        # Only add if the original name is not empty and not already in the map
        if original_name and original_name not in rename_map:
            rename_map[original_name] = py_file.stem

    return rename_map


def update_imports_in_file(filepath: Path, rename_map: dict[str, str]) -> bool:
    """
    Update imports in a single file.
    Returns True if changes were made, False otherwise.
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"Skipping non-text file: {filepath}")
        return False

    updated = content
    changes_made = False

    for old_name, new_name in rename_map.items():
        # Skip if the names are the same (shouldn't happen with our mapping)
        if old_name == new_name:
            continue

        # Pattern to match "import X" or "from X import"
        pattern = rf"(?<!\w)(import\s+){old_name}(?!\w)"
        replacement = f"\\1{new_name}"
        new_content, num_subs = re.subn(pattern, replacement, updated)

        if num_subs > 0:
            updated = new_content
            changes_made = True
            print(f"  - Replaced 'import {old_name}' with 'import {new_name}'")

        # Handle from X import Y
        pattern = rf"(?<!\w)(from\s+){old_name}(?=\s+import\s+)"
        replacement = f"\\1{new_name}"
        new_content, num_subs = re.subn(pattern, replacement, updated)

        if num_subs > 0:
            updated = new_content
            changes_made = True
            print(
                f"  - Replaced 'from {old_name} import' with 'from {new_name} import'"
            )

    if changes_made:
        # Create a backup before modifying the file
        backup_path = filepath.with_suffix(filepath.suffix + ".bak")
        if not backup_path.exists():
            filepath.rename(backup_path)

        # Write the updated content
        filepath.write_text(updated, encoding="utf-8")
        return True

    return False


def main():
    print("🔍 Scanning for renamed agent_* modules...")
    root_dir = Path(__file__).parent
    rename_map = find_renamed_modules(root_dir)

    if not rename_map:
        print("No agent_*.py modules found. Nothing to update.")
        return

    print(f"\n📋 Found {len(rename_map)} renamed modules:")
    max_len = max(len(k) for k in rename_map)
    for old, new in sorted(rename_map.items()):
        print(f"  {old.ljust(max_len)}  →  {new}")

    print("\n🔄 Updating imports in source files...")
    updated_files = 0

    for source_dir in SOURCE_DIRS:
        source_path = root_dir / source_dir
        if not source_path.exists():
            print(rf"\⚠️  Directory not found: {source_path}")
            continue

        print(f"\n📂 Processing {source_path}...")
        for py_file in source_path.rglob("*.py"):
            # Skip agent_*.py files and other special cases
            if (
                any(skip in py_file.parts for skip in SKIP_DIRS)
                or py_file.name in SKIP_FILES
                or py_file.name.startswith("agent_")
                or py_file.suffix != ".py"
            ):
                continue

            print(f"\n📄 Checking {py_file.relative_to(root_dir)}")
            if update_imports_in_file(py_file, rename_map):
                updated_files += 1

    print(f"\n✅ Done! Updated imports in {updated_files} files.")
    print("\nNext steps:")
    print("1. Run your test suite: pytest -v --tb=short")
    print("2. Check for any remaining import errors")
    print("3. If everything looks good, you can remove the .bak files")


if __name__ == "__main__":
    main()
