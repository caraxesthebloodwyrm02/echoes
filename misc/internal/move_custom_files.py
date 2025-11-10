#!/usr/bin/env python3
import os
import shutil
from pathlib import Path


def is_custom_file(filepath):
    """Check if a file is a custom Echoes file vs installed package file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(1000)  # Read first 1000 chars

        # Custom indicators
        custom_indicators = [
            "Echoes",
            "echoes",
            "agent_",
            "MIT License",
            "# Copyright (c) 2024 Echoes Project",
        ]

        for indicator in custom_indicators:
            if indicator in content:
                return True

        # Check filename patterns
        filename = os.path.basename(filepath)
        if filename.startswith("agent_") or filename.startswith("echoes_"):
            return True

    except:
        pass

    return False


def move_custom_files():
    source_dir = Path(r"e:\Projects\Echoes\echoes_core")
    target_dir = Path(r"e:\Projects\Echoes\echoes_modules")

    if not target_dir.exists():
        target_dir.mkdir()

    moved_files = []

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                rel_path = filepath.relative_to(source_dir)
                target_path = target_dir / rel_path

                if is_custom_file(filepath):
                    # Create target directory if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Move file
                    shutil.move(filepath, target_path)
                    moved_files.append(str(rel_path))
                    print(f"Moved: {rel_path}")

    print(f"\nMoved {len(moved_files)} custom files to echoes_modules/")
    return moved_files


if __name__ == "__main__":
    move_custom_files()
