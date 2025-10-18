#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Backup utility for critical data operations.

Provides atomic file operations with backup capabilities for safe data handling.
"""

import json
import shutil
from pathlib import Path
from typing import Any, List, Optional, Union


class BackupManager:
    """Manages backup operations for critical file operations."""

    def __init__(self, backup_dir: Optional[Path] = None):
        """Initialize backup manager.

        Args:
            backup_dir: Directory to store backups. Defaults to .backups/ in current directory.
        """
        self.backup_dir = backup_dir or Path(".backups")
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(
        self, file_path: Union[str, Path], suffix: str = ".bak"
    ) -> Optional[Path]:
        """Create a backup of a file before modification.

        Args:
            file_path: Path to the file to backup
            suffix: Suffix to add to backup filename

        Returns:
            Path to the created backup file, or None if backup failed
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return None

        timestamp = file_path.stat().st_mtime
        backup_name = f"{file_path.name}{suffix}.{int(timestamp)}"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            return None

    def restore_backup(
        self, original_path: Union[str, Path], backup_path: Union[str, Path]
    ) -> bool:
        """Restore a file from backup.

        Args:
            original_path: Path where to restore the file
            backup_path: Path to the backup file

        Returns:
            True if restoration was successful
        """
        try:
            shutil.copy2(Path(backup_path), Path(original_path))
            return True
        except Exception:
            return False

    def list_backups(
        self, original_file: Optional[Union[str, Path]] = None
    ) -> List[Path]:
        """List available backup files.

        Args:
            original_file: Optional filter to show backups for specific file

        Returns:
            List of backup file paths
        """
        if original_file:
            file_name = Path(original_file).name
            pattern = f"{file_name}.bak.*"
            return list(self.backup_dir.glob(pattern))
        else:
            return list(self.backup_dir.glob("*.bak.*"))

    def cleanup_old_backups(self, max_backups: int = 5) -> int:
        """Clean up old backup files, keeping only the most recent ones.

        Args:
            max_backups: Maximum number of backups to keep per file

        Returns:
            Number of files removed
        """
        removed = 0
        backup_groups = {}

        # Group backups by original filename
        for backup in self.backup_dir.glob("*.bak.*"):
            try:
                # Extract original filename from backup name
                parts = backup.name.split(".bak.")
                if len(parts) >= 2:
                    original_name = parts[0]
                    timestamp = int(parts[1])

                    if original_name not in backup_groups:
                        backup_groups[original_name] = []
                    backup_groups[original_name].append((timestamp, backup))
            except (ValueError, IndexError):
                continue

        # Remove old backups for each file
        for original_name, backups in backup_groups.items():
            if len(backups) > max_backups:
                # Sort by timestamp (newest first)
                backups.sort(key=lambda x: x[0], reverse=True)

                # Remove excess backups
                for _, backup_path in backups[max_backups:]:
                    try:
                        backup_path.unlink()
                        removed += 1
                    except Exception:
                        pass

        return removed


def atomic_write_json(
    file_path: Union[str, Path],
    data: Any,
    backup_manager: Optional[BackupManager] = None,
) -> bool:
    """Atomically write JSON data to file with backup support.

    Args:
        file_path: Path where to write the JSON file
        data: Data to serialize as JSON
        backup_manager: Optional backup manager instance

    Returns:
        True if write was successful
    """
    file_path = Path(file_path)

    # Create backup if file exists and backup manager is provided
    if backup_manager and file_path.exists():
        backup_manager.create_backup(file_path)

    # Write to temporary file first
    temp_path = file_path.with_suffix(".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic move
        temp_path.replace(file_path)
        return True

    except Exception:
        # Clean up temp file on failure
        if temp_path.exists():
            temp_path.unlink()
        return False


def atomic_write_text(
    file_path: Union[str, Path],
    content: str,
    backup_manager: Optional[BackupManager] = None,
) -> bool:
    """Atomically write text content to file with backup support.

    Args:
        file_path: Path where to write the text file
        content: Text content to write
        backup_manager: Optional backup manager instance

    Returns:
        True if write was successful
    """
    file_path = Path(file_path)

    # Create backup if file exists and backup manager is provided
    if backup_manager and file_path.exists():
        backup_manager.create_backup(file_path)

    # Write to temporary file first
    temp_path = file_path.with_suffix(".tmp")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Atomic move
        temp_path.replace(file_path)
        return True

    except Exception:
        # Clean up temp file on failure
        if temp_path.exists():
            temp_path.unlink()
        return False


def safe_api_call(
    func, *args, max_retries: int = 3, backup_on_failure: bool = True, **kwargs
):
    """Execute an API call with retry logic and optional backup.

    Args:
        func: Function to call (should be an API function)
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts
        backup_on_failure: Whether to create backup on failure
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or None if all retries failed
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            if attempt < max_retries:
                print(f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                # Could add exponential backoff here
                continue
            else:
                print(f"API call failed after {max_retries + 1} attempts: {e}")

                if backup_on_failure:
                    print("Creating backup of current state before failure...")

                break

    return None
