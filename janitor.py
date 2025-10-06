"""
Janitor Script: Unified Codebase Maintenance & Hygiene

- Regularly collects garbage, clears cache, prunes temp files, and optimizes dependencies.
- Integrates bio-inspired logic from waste_management.py for adaptive, feedback-driven cleaning.
- Performs semantic analysis of automation tasks to unify working patterns for cleanup, security, and reporting.
- Keeps the codebase clean, safe, and ready for scale/presentation.

Usage:
    python janitor.py [--dry-run] [--optimize-deps] [--full]

Options:
    --dry-run       Only print actions, do not perform destructive changes
    --optimize-deps Run dependency cleanup/upgrade
    --full          Run all maintenance, security, and reporting tasks
"""
import argparse
import os
import shutil
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json
import glob
import fnmatch

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yaml = None

# --- Configurable targets ---
CLEAN_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "logs",
    "app/__pycache__",
    "automation/__pycache__",
    "tests/__pycache__",
]
CLEAN_FILES = ["*.pyc", "*.pyo", "*.tmp", "*.temp", "*.log", "*.bak"]
REPORT_DIRS = ["automation/reports", "logs"]


# --- Bio-inspired feedback loop (simplified) ---
def feedback_log(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[janitor][{now}] {msg}")


# --- Garbage/Cache Cleanup ---
def clean_garbage(dry_run=False):
    feedback_log("Cleaning cache/garbage/temp files...")
    for d in CLEAN_DIRS:
        p = Path(d)
        if p.exists() and p.is_dir():
            if dry_run:
                feedback_log(f"[DRY-RUN] Would remove directory: {p}")
            else:
                shutil.rmtree(p, ignore_errors=True)
                feedback_log(f"Removed directory: {p}")
    for pat in CLEAN_FILES:
        for f in Path(".").rglob(pat):
            if f.exists():
                if dry_run:
                    feedback_log(f"[DRY-RUN] Would remove file: {f}")
                else:
                    f.unlink()
                    feedback_log(f"Removed file: {f}")


# --- Dependency Optimization ---
def optimize_dependencies(dry_run=False):
    feedback_log("Optimizing Python dependencies (pip)...")
    if dry_run:
        feedback_log(
            "[DRY-RUN] Would run: pip cache purge && pip check && pip install -U -r requirements.txt"
        )
        return
    subprocess.run([sys.executable, "-m", "pip", "cache", "purge"])
    subprocess.run([sys.executable, "-m", "pip", "check"])
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"])
    feedback_log("Dependencies checked and updated.")


# --- Security & Maintenance Automation ---
def run_automation_tasks(dry_run=False):
    feedback_log("Running automation security/maintenance tasks...")
    tasks = [
        ("Foreign Dependency Sanitize", "--dry-run" if dry_run else ""),
        ("Security Monitoring", "--dry-run" if dry_run else ""),
        ("Semantic Guardrails", "--dry-run" if dry_run else ""),
    ]
    for task, flag in tasks:
        cmd = [sys.executable, "-m", "automation.scripts.run_automation", "--task", task]
        if flag:
            cmd.append(flag)
        feedback_log(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)


# --- Consolidation Support ---
def _load_manifest(path: Path | str) -> dict:
    """Load consolidation manifest YAML if available, else return {}."""
    p = Path(path)

    def add_contextual_cleanup(self):
        """Add contextual garbage collection based on project structure."""
        # Remove old logs older than 30 days
        log_dir = Path("automation/reports")
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < time.time() - 30 * 24 * 3600:
                    self.remove_item(log_file)
                    self.logger.info(f"Removed old log: {log_file}")

        # Remove large files in content/ if >10MB (archive instead)
        content_dir = Path("content")
        if content_dir.exists():
            for file in content_dir.rglob("*"):
                if file.is_file() and file.stat().st_size > 10 * 1024 * 1024:
                    archive_path = Path("archive/large_files") / file.name
                    archive_path.parent.mkdir(exist_ok=True)
                    file.rename(archive_path)
                    self.logger.info(f"Archived large file: {file} -> {archive_path}")


def _ensure_dir(path: Path, dry_run: bool) -> None:
    if dry_run:
        if not path.exists():
            feedback_log(f"[DRY-RUN] Would create directory: {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def _archive_file(src: Path, archive_root: Path, dry_run: bool, moved: list[str]) -> None:
    """Move file to archive, preserving relative path under archive root."""
    rel = src.as_posix()
    # store under a flat name to avoid deep trees but keep info
    target = archive_root / (src.as_posix().replace("/", "_").replace("\\", "_"))
    _ensure_dir(archive_root, dry_run)
    if dry_run:
        feedback_log(f"[DRY-RUN] Would archive: {src} -> {target}")
        moved.append(f"{src} -> {target}")
    else:
        try:
            shutil.move(str(src), str(target))
            feedback_log(f"Archived: {src} -> {target}")
            moved.append(f"{src} -> {target}")
        except Exception as e:
            feedback_log(f"Failed to archive {src}: {e}")


def _consolidate_group(group: dict, archive_root: Path, dry_run: bool, moved: list[str]) -> None:
    survivor = group.get("survivor")
    candidates = group.get("candidates", [])
    if not survivor:
        return
    survivor_path = Path(survivor)
    for c in candidates:
        cpath = Path(c)
        if cpath.resolve() == survivor_path.resolve():
            continue
        if cpath.exists():
            _archive_file(cpath, archive_root, dry_run, moved)


def consolidate_from_manifest(manifest: dict, dry_run: bool, moved: list[str]) -> None:
    if not manifest:
        return
    archive_dir = Path(manifest.get("archive_dir", "scripts/archive"))
    # Powershell groups
    for section in (manifest.get("powershell", {}) or {}).values():
        _consolidate_group(section, archive_dir, dry_run, moved)
    # Bash groups
    for section in (manifest.get("bash", {}) or {}).values():
        _consolidate_group(section, archive_dir, dry_run, moved)
    # Python groups
    for section in (manifest.get("python", {}) or {}).values():
        _consolidate_group(section, archive_dir, dry_run, moved)
    # Reports groups (e.g., bandit)
    for section in (manifest.get("reports", {}) or {}).values():
        _consolidate_group(section, archive_dir, dry_run, moved)


def _is_preserved(path: Path, preserve_patterns: list[str]) -> bool:
    posix = path.as_posix()
    for pat in preserve_patterns:
        # glob-style pattern matching for POSIX path strings
        if fnmatch.fnmatch(posix, pat):
            return True
    return False


def cleanup_from_manifest(manifest: dict, dry_run: bool, deleted: list[str]) -> None:
    cleanup = manifest.get("cleanup", {}) or {}
    patterns = cleanup.get("delete_patterns", [])
    preserve = cleanup.get("preserve_paths", [])
    # Add conservative defaults
    preserve = list(
        set(preserve + ["venv/**", ".git/**", "automation/reports/**", "docs/**", "configs/**"])
    )
    for pat in patterns:
        matches = glob.glob(pat, recursive=True)
        for m in matches:
            p = Path(m)
            # Skip directories under preserved paths
            if _is_preserved(p, preserve):
                continue
            if not p.exists():
                continue
            if dry_run:
                feedback_log(f"[DRY-RUN] Would remove: {p}")
                deleted.append(str(p))
            else:
                try:
                    if p.is_dir():
                        shutil.rmtree(p, ignore_errors=True)
                    else:
                        p.unlink()
                    feedback_log(f"Removed: {p}")
                    deleted.append(str(p))
                except Exception as e:
                    feedback_log(f"Failed to remove {p}: {e}")


# --- Main Janitor Routine ---
def main():
    parser = argparse.ArgumentParser(description="Janitor: Codebase Hygiene & Maintenance")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions, don't delete or change anything"
    )
    parser.add_argument("--optimize-deps", action="store_true", help="Optimize dependencies")
    parser.add_argument(
        "--full", action="store_true", help="Run all maintenance, security, and reporting tasks"
    )
    parser.add_argument(
        "--consolidate",
        action="store_true",
        help="Consolidate scripts/reports and clean transient files per manifest",
    )
    args = parser.parse_args()

    clean_garbage(dry_run=args.dry_run)
    if args.optimize_deps:
        optimize_dependencies(dry_run=args.dry_run)
    if args.full:
        run_automation_tasks(dry_run=args.dry_run)
    # Consolidation execution
    if args.consolidate:
        manifest = _load_manifest(Path("configs/maintenance/consolidation_manifest.yaml"))
        moved: list[str] = []
        deleted: list[str] = []
        consolidate_from_manifest(manifest, args.dry_run, moved)
        cleanup_from_manifest(manifest, args.dry_run, deleted)
        # Write summary report
        report_dir = Path("automation/reports")
        _ensure_dir(report_dir, args.dry_run)
        report_path = report_dir / "consolidation_report.json"
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "dry_run": args.dry_run,
            "moved": moved,
            "deleted": deleted,
        }
        if args.dry_run:
            feedback_log(f"[DRY-RUN] Would write consolidation report to: {report_path}")
        else:
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                feedback_log(f"Wrote consolidation report: {report_path}")
            except Exception as e:
                feedback_log(f"Failed to write consolidation report: {e}")
    feedback_log("Janitor run complete.")


if __name__ == "__main__":
    main()
