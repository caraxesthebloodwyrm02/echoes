#!/usr/bin/env python3
"""
Terminology Update Script

This script updates terminology across the codebase based on the new naming conventions:
- 'glimpse' → 'glimpse' (for protocol)
- 'Glimpse Bridge' → 'Glimpse'
- Other related terminology updates
"""

import re
from pathlib import Path

# Define terminology mappings
TERMINOLOGY_MAP = {
    # Protocol naming
    r"\bSandstorm\b": "glimpse",
    r"\bsandstorm\b": "glimpse",
    # Bridging/Glimpse
    r"\bGlimpseBridge\b": "SmartVisionBridge",
    r"\bglimpse_bridge\b": "glimpse_bridge",
    r"\bGlimpse Glimpse\b": "Glimpse",
    # File patterns
    r"sandstorm_([^\s.]+)\.py": r"glimpse_\1.py",
    r"sandstorm_([^\s.]+)\.(md|yaml|yml|json)": r"glimpse_\1.\2",
}

# Files to exclude from renaming
EXCLUDE_FILES = {
    ".git",
    "__pycache__",
    "venv",
    "node_modules",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "*.log",
}

# File extensions to process
TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".rst",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
}


def should_process_file(filepath: Path) -> bool:
    """Check if a file should be processed."""
    if filepath.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    return not any(filepath.match(pattern) for pattern in EXCLUDE_FILES)


def update_file_content(
    content: str, patterns: dict[str, str]
) -> tuple[str, list[tuple[str, str]]]:
    """Update content with new terminology."""
    changes = []
    updated_content = content

    for pattern, replacement in patterns.items():
        new_content, count = re.subn(
            pattern, replacement, updated_content, flags=re.IGNORECASE
        )
        if count > 0 and new_content != updated_content:
            changes.append((pattern, replacement, count))
            updated_content = new_content

    return updated_content, changes


def process_file(
    filepath: Path, patterns: dict[str, str]
) -> list[tuple[str, str, int]]:
    """Process a single file and return changes made."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        updated_content, changes = update_file_content(content, patterns)

        if updated_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return changes
        return []
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return []


def find_and_rename_files(root_dir: Path, patterns: dict[str, str]) -> None:
    """Find and rename files based on patterns."""
    for filepath in root_dir.rglob("*"):
        if not filepath.is_file() or not should_process_file(filepath):
            continue

        # Check if filename needs to be updated
        old_name = filepath.name
        new_name = old_name

        for pattern, replacement in patterns.items():
            if re.search(pattern, old_name, re.IGNORECASE):
                new_name = re.sub(pattern, replacement, old_name, flags=re.IGNORECASE)
                if new_name != old_name:
                    new_path = filepath.parent / new_name
                    try:
                        filepath.rename(new_path)
                        print(f"Renamed: {filepath} → {new_path}")
                        filepath = new_path  # Update reference for content processing
                    except Exception as e:
                        print(f"Error renaming {filepath}: {str(e)}")
                break

        # Process file content
        changes = process_file(filepath, patterns)
        if changes:
            print(f"\nUpdated {filepath}:")
            for pattern, replacement, count in changes:
                print(f"  - Replaced '{pattern}' with '{replacement}' ({count} times)")


def main():
    """Main function to update terminology."""
    root_dir = Path(__file__).parent.parent  # Project root
    print(f"Updating terminology in: {root_dir}")

    # First pass: Rename files
    print("\n=== Renaming Files ===")
    find_and_rename_files(
        root_dir,
        {
            r"^sandstorm_([^\s.]+)\.py$": r"glimpse_\1.py",
            r"^sandstorm_([^\s.]+)\.(md|yaml|yml|json)$": r"glimpse_\1.\2",
        },
    )

    # Second pass: Update file contents
    print("\n=== Updating File Contents ===")
    find_and_rename_files(root_dir, TERMINOLOGY_MAP)

    print("\nTerminology update complete!")


if __name__ == "__main__":
    main()
