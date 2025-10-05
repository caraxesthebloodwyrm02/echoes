"""
automation/tasks/auto_fix_lint.py

Automation task module to run linting and auto-fix tools safely using the
repo's automation framework.

This module expects the repo to expose:
- automation.core.config.Config  (Config.get, Config.getitem)
- automation.core.context.Context (has attribute dry_run and require_confirmation helper)
- automation.core.logger.AutomationLogger (exposes .info, .warning, .success, .error)

Add to your orchestrator task list as a safe automated job. It respects
Config.dry_run and Context.require_confirmation where appropriate.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

try:
    from automation.core import config as config_mod
    from automation.core import context as context_mod
    from automation.core import logger as logger_mod
except Exception:  # pragma: no cover - defensive import fallback
    config_mod = None
    context_mod = None
    logger_mod = None

LOGGER = getattr(logger_mod, "log", None)

DEFAULT_TOOLS = [
    ("ruff", ["ruff", "--fix", "."]),
    ("isort", ["isort", "."]),
    ("black", ["black", "."]),
]


def _which_tools(tools: Iterable[str]) -> dict:
    found = {}
    for t in tools:
        found[t] = shutil.which(t) is not None
    return found


def _run_cmd(cmd: list[str], dry_run: bool) -> int:
    if dry_run:
        if LOGGER:
            LOGGER.info("[dry-run] would run: %s", " ".join(cmd))
        else:
            print("[dry-run] would run:", " ".join(cmd))
        return 0
    try:
        completed = subprocess.run(cmd, check=False)
        return completed.returncode
    except Exception as e:
        if LOGGER:
            LOGGER.error("command failed: %s -- %s", cmd, e)
        else:
            print("command failed:", cmd, e)
        return 2


def run(task_context=None):
    """Entrypoint used by the orchestrator.

    task_context is expected to be an instance of automation.core.context.Context
    or an object exposing at least:
      - dry_run: bool
      - require_confirmation(prompt) -> bool

    The task will:
      - check for presence of ruff/isort/black
      - run each available tool with their fix flags
      - log results and return non-zero on failures
    """
    ctx = task_context or getattr(context_mod, "Context", None)
    dry_run = False
    require_confirmation = lambda prompt: True

    if ctx is not None and hasattr(ctx, "dry_run"):
        dry_run = getattr(ctx, "dry_run")
    # if the context provides a require_confirmation helper use it
    if ctx is not None and hasattr(ctx, "require_confirmation"):
        require_confirmation = getattr(ctx, "require_confirmation")

    if LOGGER:
        LOGGER.info("Starting auto_fix_lint task. dry_run=%s", dry_run)

    # Locate tools
    tool_names = [name for name, _ in DEFAULT_TOOLS]
    tools_found = _which_tools(tool_names)

    if LOGGER:
        LOGGER.info("Tool availability: %s", tools_found)

    to_run = []
    for name, cmd in DEFAULT_TOOLS:
        if tools_found.get(name):
            to_run.append((name, cmd))
        else:
            if LOGGER:
                LOGGER.warning("Tool not found on PATH: %s. Skipping.", name)

    if not to_run:
        if LOGGER:
            LOGGER.warning(
                "No lint/format tools found. Install ruff/isort/black or update the task."
            )
        return 0

    # Confirm before making in-place fixes when not in dry-run
    if not dry_run:
        ok = require_confirmation("Run auto-fix for lint/format tools? (y/N)")
        if not ok:
            if LOGGER:
                LOGGER.info("User declined to run fixes. Exiting.")
            return 0

    repo_root = Path.cwd()

    failures = []
    for name, cmd in to_run:
        if LOGGER:
            LOGGER.info("Running %s: %s", name, cmd)
        rc = _run_cmd(cmd, dry_run=dry_run)
        if rc != 0:
            failures.append((name, rc))
            if LOGGER:
                LOGGER.error("%s returned nonzero exit code: %s", name, rc)

    if failures:
        if LOGGER:
            LOGGER.error("auto_fix_lint completed with failures: %s", failures)
        return 1

    if LOGGER:
        LOGGER.success("auto_fix_lint completed successfully.")
    return 0


if __name__ == "__main__":
    # Allow running the task directly for local testing
    # Build a minimal mock context if the framework is unavailable
    class _LocalCtx:
        dry_run = True

        @staticmethod
        def require_confirmation(prompt: str) -> bool:
            print(prompt)
            return False

    run(_LocalCtx())
