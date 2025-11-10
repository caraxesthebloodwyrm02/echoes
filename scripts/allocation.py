import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("file_organizer.log"), logging.StreamHandler()],
)


class FileOrganizer:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.logger = logging.getLogger(__name__)

        # Define target directories and their associated keywords
        self.target_dirs = {
            "glimpse": {
                "dir": self.root_dir / "glimpse",
                "keywords": [
                    "glimpse",
                    "nexus",
                    "smartvision",
                    "analysis",
                    "insight",
                    "diagnostic",
                ],
                "extensions": {".py", ".md", ".yaml", ".yml", ".json"},
            },
            "tests": {
                "dir": self.root_dir / "tests",
                "keywords": ["test", "spec", "fixture", "mock"],
                "extensions": {".py", ".md", ".json"},
            },
            "docs": {
                "dir": self.root_dir / "docs",
                "keywords": ["readme", "doc", "guide", "tutorial", "manual"],
                "extensions": {".md", ".txt", ".rst", ".pdf"},
            },
            "scripts": {
                "dir": self.root_dir / "scripts",
                "keywords": ["script", "util", "tool", "helper"],
                "extensions": {".py", ".sh", ".bat", ".ps1"},
            },
            "config": {
                "dir": self.root_dir / "config",
                "keywords": ["config", "settings", "conf", "setup"],
                "extensions": {".yaml", ".yml", ".json", ".ini", ".cfg", ".env"},
            },
        }

        # Create target directories if they don't exist
        for config in self.target_dirs.values():
            config["dir"].mkdir(exist_ok=True)

    def get_file_keywords(self, filepath: Path) -> Set[str]:
        """Extract potential keywords from filename and content."""
        keywords = set()

        # Add filename parts as keywords (lowercase, no extension)
        name_parts = filepath.stem.lower().replace("_", " ").replace("-", " ").split()
        keywords.update(name_parts)

        # Read file content for additional keywords
        try:
            if filepath.suffix.lower() in {
                ".py",
                ".md",
                ".txt",
                ".yaml",
                ".yml",
                ".json",
            }:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(4096).lower()  # Read first 4KB for efficiency
                    # Add words that match our target keywords
                    for word in re.findall(r"\b\w{4,}\b", content):
                        if any(
                            kw in word
                            for kw in ["glimpse", "test", "doc", "script", "config"]
                        ):
                            keywords.add(word)
        except Exception as e:
            self.logger.warning(f"Could not read {filepath}: {e}")

        return keywords

    def get_best_match_dir(self, filepath: Path) -> Optional[Path]:
        """Determine the best target directory for a file."""
        keywords = self.get_file_keywords(filepath)
        best_match = None
        best_score = 0

        for name, config in self.target_dirs.items():
            if filepath.suffix.lower() not in config["extensions"]:
                continue

            # Calculate match score
            score = sum(
                1 for kw in keywords if any(k in kw for k in config["keywords"])
            )

            # Special case for test files
            if "test" in keywords and name == "tests":
                score += 2

            if score > best_score:
                best_score = score
                best_match = config["dir"]

        return best_match if best_score > 0 else None

    def organize_files(self, dry_run: bool = True) -> Dict[str, List[str]]:
        """Organize files based on their content and naming."""
        results = {"moved": [], "skipped": [], "errors": []}

        for filepath in self.root_dir.glob("*"):
            # Skip directories and hidden files
            if filepath.is_dir() or filepath.name.startswith("."):
                continue

            # Skip files already in target directories
            if any(
                str(filepath).startswith(str(config["dir"]))
                for config in self.target_dirs.values()
            ):
                continue

            target_dir = self.get_best_match_dir(filepath)
            if not target_dir:
                results["skipped"].append(str(filepath))
                continue

            target_path = target_dir / filepath.name

            try:
                if dry_run:
                    self.logger.info(f"Would move: {filepath} -> {target_path}")
                else:
                    shutil.move(str(filepath), str(target_path))
                    self.logger.info(f"Moved: {filepath} -> {target_path}")
                results["moved"].append(f"{filepath} -> {target_path}")
            except Exception as e:
                error_msg = f"Error moving {filepath}: {e}"
                self.logger.error(error_msg)
                results["errors"].append(error_msg)

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Organize files based on content and naming patterns."
    )
    parser.add_argument("--root-dir", default=".", help="Root directory to organize")
    parser.add_argument(
        "--apply", action="store_true", help="Actually move files (dry run by default)"
    )
    args = parser.parse_args()

    organizer = FileOrganizer(args.root_dir)
    results = organizer.organize_files(dry_run=not args.apply)

    print("\n=== Organization Results ===")
    print(f"Files moved: {len(results['moved'])}")
    print(f"Files skipped: {len(results['skipped'])}")
    print(f"Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\n=== Errors ===")
        for error in results["errors"]:
            print(f"- {error}")


if __name__ == "__main__":
    main()
