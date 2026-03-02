#!/usr/bin/env python3
"""
Replace Multiple Terms with Glimpse

This script finds and replaces multiple terms with "Glimpse" across the codebase.
Terms to replace: "Glimpse", "Glimpse", "Glimpse", "Glimpse" (in specific contexts)
"""

import re
from pathlib import Path

# Define comprehensive terminology mappings
TERMINOLOGY_MAP = {
    # Direct replacements
    r"\bNexus\b": "Glimpse",
    r"\bnexus\b": "glimpse",
    r"\bUnit\b": "Glimpse",
    r"\bunit\b": "glimpse",
    r"\bSmart Vision\b": "Glimpse",
    r"\bsmart vision\b": "glimpse",
    r"\bSmartVision\b": "Glimpse",
    r"\bsmart_vision\b": "glimpse",
    # Glimpse replacements (contextual - avoid replacing actual Glimpse components)
    r"\bEngine\b(?!.*=)": "Glimpse",  # Engine not followed by = (avoid variable assignments)
    r"\bengine\b(?!.*=)": "glimpse",  # engine not followed by = (avoid variable assignments)
    # Combined terms
    r"\bNexusProtocol\b": "Glimpse",
    r"\bNexus Protocol\b": "Glimpse",
    r"\bglimpse_Unit\b": "Glimpse",
    r"\bglimpse_Engine\b": "Glimpse",
    r"\bSmart Vision Glimpse\b": "Glimpse",
    # File patterns
    r"glimpse_([^\s.]+)": r"glimpse_\1",
    r"glimpse_([^\s.]+)": r"glimpse_\1",
    r"glimpse_([^\s.]+)": r"glimpse_\1",
    r"glimpse_([^\s.]+)": r"glimpse_\1",
}

# Files to exclude from processing
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
    "*.exe",
    "*.dll",
    "*.so",
    "*.dylib",
    "GLIMPSE_TERMINOLOGY.md",
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
) -> tuple[str, list[tuple[str, str, int]]]:
    """Update content with new terminology."""
    changes = []
    updated_content = content

    for pattern, replacement in patterns.items():
        # Skip if replacement is the same as pattern
        if pattern == replacement:
            continue

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
    total_files = 0
    total_changes = 0

    for filepath in root_dir.rglob("*"):
        if not filepath.is_file() or not should_process_file(filepath):
            continue

        total_files += 1

        # Check if filename needs to be updated
        old_name = filepath.name
        new_name = old_name

        # Apply file name patterns
        file_patterns = {
            r"^glimpse_([^\s.]+)": r"glimpse_\1",
            r"^glimpse_([^\s.]+)": r"glimpse_\1",
            r"^glimpse_([^\s.]+)": r"glimpse_\1",
            r"^glimpse_([^\s.]+)": r"glimpse_\1",
        }

        for pattern, replacement in file_patterns.items():
            if re.search(pattern, old_name, re.IGNORECASE):
                new_name = re.sub(pattern, replacement, old_name, flags=re.IGNORECASE)
                if new_name != old_name:
                    new_path = filepath.parent / new_name
                    try:
                        filepath.rename(new_path)
                        print(f"Renamed: {filepath.name} → {new_name}")
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
                total_changes += count

    print("\n=== Summary ===")
    print(f"Files processed: {total_files}")
    print(f"Total replacements: {total_changes}")


def main():
    """Main function to update terminology."""
    root_dir = Path(__file__).parent.parent  # Project root
    print(f"Updating terminology to 'Glimpse' in: {root_dir}")

    # First pass: Rename files
    print("\n=== Renaming Files ===")
    find_and_rename_files(root_dir, {})

    print("\n=== Updating File Contents ===")
    find_and_rename_files(root_dir, TERMINOLOGY_MAP)

    print("\nTerminology update complete!")


if __name__ == "__main__":
    main()
