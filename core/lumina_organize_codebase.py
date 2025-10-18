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
Lumina Task: Intelligent Codebase Organization

This automation task uses Lumina to analyze and reorganize the codebase
intelligently, moving files to appropriate directories and improving structure.
"""

from pathlib import Path
from typing import Dict, List

from automation.core.context import Context
from automation.core.logger import AutomationLogger


def lumina_organize_codebase(context: Context):
    """
    Organize codebase intelligently using Lumina.

    This task:
    1. Analyzes current project structure
    2. Identifies misplaced files
    3. Suggests optimal organization
    4. Creates necessary directories
    5. Moves files (with dry-run support)
    """
    logger = AutomationLogger()

    logger.info("🗂️  Lumina: Intelligent Codebase Organization")

    # Get project root
    project_root = Path.cwd()

    # Define ideal structure
    ideal_structure = {
        "app/": {
            "description": "Main application code",
            "subdirs": ["core/", "api/", "cli/", "harmony/", "mcp/"],
        },
        "automation/": {
            "description": "Automation framework",
            "subdirs": ["core/", "tasks/", "scripts/"],
        },
        "tests/": {
            "description": "Test files",
            "pattern": "test_*.py",
        },
        "docs/": {
            "description": "Documentation",
            "extensions": [".md", ".rst", ".txt"],
        },
        "examples/": {
            "description": "Example scripts and demos",
            "extensions": [".py"],
        },
        "config/": {
            "description": "Configuration files",
            "extensions": [".yaml", ".yml", ".toml", ".ini", ".json"],
        },
        "scripts/": {
            "description": "Utility scripts",
            "extensions": [".py", ".sh", ".ps1"],
        },
        "packages/": {
            "description": "Internal packages",
            "subdirs": ["core/", "monitoring/", "security/"],
        },
    }

    logger.info(f"📁 Analyzing project: {project_root}")

    # Analyze current structure
    analysis = _analyze_structure(project_root, ideal_structure, logger)

    # Generate recommendations
    recommendations = _generate_recommendations(analysis, logger)

    # Display recommendations
    logger.info("\n📋 Organization Recommendations:")
    for rec in recommendations:
        logger.info(f"   • {rec['action']}: {rec['description']}")

    # Execute if not dry-run
    if not context.dry_run:
        if context.require_confirmation("Apply these changes?"):
            _apply_changes(recommendations, logger)
            logger.success("✅ Codebase reorganization completed!")
        else:
            logger.info("❌ Changes cancelled by user")
    else:
        logger.info("🔍 Dry-run mode: No changes made")

    logger.success("Task completed")


def _analyze_structure(
    project_root: Path,
    ideal: Dict,
    logger: AutomationLogger,
) -> Dict:
    """Analyze current project structure."""
    logger.info("🔍 Analyzing current structure...")

    analysis = {
        "existing_dirs": set(),
        "missing_dirs": set(),
        "misplaced_files": [],
        "duplicate_files": [],
        "empty_dirs": [],
    }

    # Find existing directories
    for item in project_root.rglob("*"):
        if item.is_dir() and not any(part.startswith(".") for part in item.parts):
            rel_path = item.relative_to(project_root)
            analysis["existing_dirs"].add(str(rel_path))

    # Check for missing ideal directories
    for ideal_dir in ideal:
        if ideal_dir not in analysis["existing_dirs"]:
            analysis["missing_dirs"].add(ideal_dir)

    # Find misplaced files (root level files that should be elsewhere)
    root_files = [f for f in project_root.iterdir() if f.is_file()]
    for file in root_files:
        if file.suffix == ".py" and file.name not in ["setup.py", "manage.py"]:
            # Python files should be in app/ or scripts/
            analysis["misplaced_files"].append(
                {
                    "file": str(file.name),
                    "current": "root",
                    "suggested": (
                        "scripts/" if "script" in file.name.lower() else "app/"
                    ),
                    "reason": "Python modules should be in organized directories",
                }
            )
        elif file.suffix in [".md", ".rst", ".txt"] and file.name not in [
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
        ]:
            # Docs should be in docs/
            analysis["misplaced_files"].append(
                {
                    "file": str(file.name),
                    "current": "root",
                    "suggested": "docs/",
                    "reason": "Documentation files belong in docs/",
                }
            )

    # Find empty directories
    for dir_path in analysis["existing_dirs"]:
        full_path = project_root / dir_path
        if full_path.is_dir() and not any(full_path.iterdir()):
            analysis["empty_dirs"].append(str(dir_path))

    logger.info(f"   Found: {len(analysis['existing_dirs'])} directories")
    logger.info(f"   Missing: {len(analysis['missing_dirs'])} ideal directories")
    logger.info(f"   Misplaced: {len(analysis['misplaced_files'])} files")
    logger.info(f"   Empty: {len(analysis['empty_dirs'])} directories")

    return analysis


def _generate_recommendations(analysis: Dict, logger: AutomationLogger) -> List[Dict]:
    """Generate organization recommendations."""
    logger.info("💡 Generating recommendations...")

    recommendations = []

    # Recommend creating missing directories
    for missing_dir in analysis["missing_dirs"]:
        recommendations.append(
            {
                "action": "CREATE_DIR",
                "description": f"Create directory: {missing_dir}",
                "target": missing_dir,
                "priority": "medium",
            }
        )

    # Recommend moving misplaced files
    for misplaced in analysis["misplaced_files"]:
        recommendations.append(
            {
                "action": "MOVE_FILE",
                "description": f"Move {misplaced['file']} from {misplaced['current']} to {misplaced['suggested']}",
                "source": misplaced["file"],
                "target": misplaced["suggested"],
                "reason": misplaced["reason"],
                "priority": "high",
            }
        )

    # Recommend removing empty directories
    for empty_dir in analysis["empty_dirs"]:
        if empty_dir not in ["logs", "data", "temp", "cache"]:  # Keep these
            recommendations.append(
                {
                    "action": "REMOVE_DIR",
                    "description": f"Remove empty directory: {empty_dir}",
                    "target": empty_dir,
                    "priority": "low",
                }
            )

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order[x["priority"]])

    return recommendations


def _apply_changes(recommendations: List[Dict], logger: AutomationLogger):
    """Apply organization changes."""
    logger.info("🔨 Applying changes...")

    project_root = Path.cwd()

    for rec in recommendations:
        action = rec["action"]

        try:
            if action == "CREATE_DIR":
                target = project_root / rec["target"]
                target.mkdir(parents=True, exist_ok=True)
                logger.info(f"   ✓ Created: {rec['target']}")

            elif action == "MOVE_FILE":
                source = project_root / rec["source"]
                target_dir = project_root / rec["target"]
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / source.name

                if source.exists():
                    source.rename(target)
                    logger.info(f"   ✓ Moved: {rec['source']} → {rec['target']}")

            elif action == "REMOVE_DIR":
                target = project_root / rec["target"]
                if target.exists() and target.is_dir():
                    target.rmdir()  # Only removes if empty
                    logger.info(f"   ✓ Removed: {rec['target']}")

        except Exception as e:
            logger.warning(f"   ✗ Failed: {rec['description']} - {e}")

    logger.success("Changes applied successfully")


# Make it callable as automation task
if __name__ == "__main__":
    from automation.core.context import Context

    context = Context(dry_run=True)
    lumina_organize_codebase(context)
