#!/usr/bin/env python3
import os
import re
import sys


def update_imports_in_file(filepath):
    """Update core imports to echoes_core in a single file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace from echoes_core. with from echoes_core.
        updated = re.sub(r"from core\.", r"from echoes_core.", content)
        # Replace import echoes_core. with import echoes_core.
        updated = re.sub(r"import core\.", r"import echoes_core.", updated)

        if content != updated:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(updated)
            return True
        return False
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False


def main():
    root_dir = r"e:\Projects\Echoes"
    updated_files = 0

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                if update_imports_in_file(filepath):
                    print(f"Updated: {filepath}")
                    updated_files += 1

    print(f"Total files updated: {updated_files}")


if __name__ == "__main__":
    main()
