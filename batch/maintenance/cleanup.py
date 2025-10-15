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

"""Maintenance scripts for batch operations."""

import argparse
import logging
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict

from config.settings import get_settings
from utils.path_resolver import PathResolver

logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Manager for various maintenance operations."""

    def __init__(self):
        self.settings = get_settings()
        self.path_resolver = PathResolver()

    def cleanup_temp_files(self, max_age_days: int = 7) -> Dict[str, Any]:
        """Clean up temporary files older than specified days."""
        temp_dir = self.settings.temp_dir
        if not temp_dir.exists():
            return {"files_cleaned": 0, "message": "Temp directory does not exist"}

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        cleaned_files = []

        try:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_date:
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                        logger.info(f"Cleaned up old temp file: {file_path}")

            return {
                "files_cleaned": len(cleaned_files),
                "files_list": cleaned_files,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
            return {"error": str(e), "success": False}

    def cleanup_logs(
        self, max_age_days: int = 30, max_size_mb: int = 100
    ) -> Dict[str, Any]:
        """Clean up old log files and manage log size."""
        logs_dir = self.settings.logs_dir
        if not logs_dir.exists():
            return {"files_cleaned": 0, "message": "Logs directory does not exist"}

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        max_size_bytes = max_size_mb * 1024 * 1024
        cleaned_files = []
        archived_files = []

        try:
            for file_path in logs_dir.glob("*.log*"):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    file_size = file_path.stat().st_size

                    # Remove old files
                    if file_age < cutoff_date:
                        file_path.unlink()
                        cleaned_files.append(str(file_path))
                        logger.info(f"Removed old log file: {file_path}")

                    # Archive large files
                    elif file_size > max_size_bytes:
                        archive_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d')}.archive{file_path.suffix}"
                        archive_path = logs_dir / archive_name
                        shutil.move(str(file_path), str(archive_path))
                        archived_files.append(str(archive_path))
                        logger.info(f"Archived large log file: {archive_path}")

            return {
                "files_cleaned": len(cleaned_files),
                "files_archived": len(archived_files),
                "cleaned_list": cleaned_files,
                "archived_list": archived_files,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")
            return {"error": str(e), "success": False}

    def optimize_data_directory(self) -> Dict[str, Any]:
        """Optimize data directory structure."""
        data_dir = self.settings.data_dir
        if not data_dir.exists():
            return {"message": "Data directory does not exist"}

        try:
            # Create subdirectories for better organization
            subdirs = ["raw", "processed", "cache", "exports"]
            created_dirs = []

            for subdir in subdirs:
                subdir_path = data_dir / subdir
                if not subdir_path.exists():
                    subdir_path.mkdir(parents=True)
                    created_dirs.append(str(subdir_path))

            # Move loose files into appropriate subdirectories
            moved_files = []
            for file_path in data_dir.glob("*"):
                if file_path.is_file() and file_path.name != ".gitkeep":
                    if file_path.suffix.lower() in [".txt", ".md", ".json"]:
                        target_dir = data_dir / "raw"
                    elif file_path.suffix.lower() in [".csv", ".xlsx"]:
                        target_dir = data_dir / "processed"
                    else:
                        target_dir = data_dir / "cache"

                    target_path = target_dir / file_path.name
                    shutil.move(str(file_path), str(target_path))
                    moved_files.append(f"{file_path} -> {target_path}")

            return {
                "directories_created": created_dirs,
                "files_moved": moved_files,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error during data directory optimization: {e}")
            return {"error": str(e), "success": False}

    def run_full_maintenance(self) -> Dict[str, Any]:
        """Run complete maintenance suite."""
        logger.info("Starting full maintenance routine")

        results = {"timestamp": datetime.now().isoformat(), "operations": {}}

        # Temp file cleanup
        results["operations"]["temp_cleanup"] = self.cleanup_temp_files()

        # Log cleanup
        results["operations"]["log_cleanup"] = self.cleanup_logs()

        # Data directory optimization
        results["operations"]["data_optimization"] = self.optimize_data_directory()

        # Summary
        successful_ops = sum(
            1 for op in results["operations"].values() if op.get("success", False)
        )
        total_ops = len(results["operations"])

        results["summary"] = {
            "total_operations": total_ops,
            "successful_operations": successful_ops,
            "overall_success": successful_ops == total_ops,
        }

        logger.info(
            f"Maintenance complete: {successful_ops}/{total_ops} operations successful"
        )
        return results


def main():
    """Main entry point for maintenance scripts."""
    parser = argparse.ArgumentParser(description="Project maintenance utilities")
    parser.add_argument(
        "operation",
        choices=["temp", "logs", "data", "full"],
        help="Maintenance operation to perform",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=7,
        help="Maximum age in days for cleanup operations",
    )
    parser.add_argument(
        "--max-size-mb", type=int, default=100, help="Maximum size in MB for log files"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Run maintenance
    manager = MaintenanceManager()

    if args.operation == "temp":
        result = manager.cleanup_temp_files(args.max_age_days)
    elif args.operation == "logs":
        result = manager.cleanup_logs(args.max_age_days, args.max_size_mb)
    elif args.operation == "data":
        result = manager.optimize_data_directory()
    elif args.operation == "full":
        result = manager.run_full_maintenance()

    # Output result
    if result.get("success", False):
        print(f"✓ Operation '{args.operation}' completed successfully")
        if "files_cleaned" in result:
            print(f"  Files cleaned: {result['files_cleaned']}")
        if "files_archived" in result:
            print(f"  Files archived: {result['files_archived']}")
        if "directories_created" in result:
            print(f"  Directories created: {len(result['directories_created'])}")
    else:
        print(f"✗ Operation '{args.operation}' failed")
        if "error" in result:
            print(f"  Error: {result['error']}")
        exit(1)


if __name__ == "__main__":
    main()
