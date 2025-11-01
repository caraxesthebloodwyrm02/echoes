#!/usr/bin/env python3
"""
Replace 'glimpse' with 'glimpse' in all relevant files
"""

import os
import re
from pathlib import Path

# Define patterns to replace
REPLACEMENTS = {
    r'\bsandstorm\b': 'glimpse',
    r'\bSandstorm\b': 'Glimpse',
    r'\bSANDSTORM\b': 'GLIMPSE',
    
    # File patterns
    r'sandstorm_([^\s.]+)\.py': r'glimpse_\1.py',
    r'sandstorm_([^\s.]+)\.(md|yaml|yml|json)': r'glimpse_\1.\2',
}

# Directories to exclude
EXCLUDE_DIRS = {
    '.git',
    '__pycache__',
    'venv',
    'node_modules',
}

# File extensions to process
TEXT_EXTENSIONS = {
    '.py', '.md', '.yaml', '.yml', '.json',
    '.txt', '.rst', '.toml', '.ini', '.cfg', '.conf'
}

def should_process_file(filepath: Path) -> bool:
    """Check if a file should be processed."""
    if filepath.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    return not any(part in EXCLUDE_DIRS for part in filepath.parts)

def update_file_content(filepath: Path) -> bool:
    """Update file content with replacements."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated = False
        for pattern, replacement in REPLACEMENTS.items():
            new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
            if count > 0 and new_content != content:
                content = new_content
                updated = True
        
        if updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def rename_file(filepath: Path) -> bool:
    """Rename file if needed."""
    old_name = filepath.name
    new_name = old_name
    
    # Apply file name patterns
    for pattern, replacement in REPLACEMENTS.items():
        if re.search(r'^' + pattern.replace('\\b', '').replace('\\([^)]+\\)', '.*') + '$', old_name, re.IGNORECASE):
            new_name = re.sub(pattern, replacement, old_name, flags=re.IGNORECASE)
            if new_name != old_name:
                new_path = filepath.parent / new_name
                try:
                    filepath.rename(new_path)
                    print(f"Renamed: {filepath} → {new_path}")
                    return True
                except Exception as e:
                    print(f"Error renaming {filepath}: {e}")
                break
    return False

def main():
    root_dir = Path(__file__).parent.parent
    print(f"Replacing 'glimpse' with 'glimpse' in: {root_dir}")
    
    renamed_count = 0
    updated_count = 0
    
    # First pass: Rename files
    print("\n=== Renaming Files ===")
    for filepath in root_dir.rglob('*'):
        if filepath.is_file() and should_process_file(filepath):
            if rename_file(filepath):
                renamed_count += 1
    
    # Second pass: Update file contents
    print("\n=== Updating File Contents ===")
    for filepath in root_dir.rglob('*'):
        if filepath.is_file() and should_process_file(filepath):
            if update_file_content(filepath):
                print(f"Updated: {filepath}")
                updated_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Files renamed: {renamed_count}")
    print(f"Files updated: {updated_count}")
    print("\nReplacement complete!")

if __name__ == '__main__':
    main()
