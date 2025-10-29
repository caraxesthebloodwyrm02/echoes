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
Task: automation.tasks.foreign_dependency_sanitize

Scans the repository for non-Python (foreign) dependencies with emphasis on
JavaScript/Node.js artifacts, produces a structured JSON report, and
optionally applies guardrail remediations:
- Replace Node-based markdown linting in CI with Python-native linting
- Ensure .gitignore protects against node_modules/
- Prune commented Node tool references from pre-commit config
- Optionally remove Node-specific configs (e.g., .markdownlint.json)

Use via automation runner:
  python -m automation.scripts.run_automation --task "Foreign Dependency Sanitize"

Parameters (context.extra_data):
- apply_changes: bool (default False)  -> actually modify files
- delete_node_configs: bool (default False) -> remove Node-specific config files
- assume_yes: bool (default False) -> skip confirmations for deletions/patches
- report_file: str (default automation/reports/foreign_dependency_report.json)

All destructive changes require confirmation unless dry_run=True.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from automation.core.logger import AutomationLogger

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "htmlcov",
}

NODE_MANIFESTS = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}

FOREIGN_MANIFESTS = NODE_MANIFESTS | {
    "Gemfile",
    "Gemfile.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "composer.json",
    "composer.lock",
    "build.gradle",
    "pom.xml",
    "mix.exs",
    "mix.lock",
}

FOREIGN_SOURCE_EXTS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".rb",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".scala",
    ".php",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".swift",
    ".m",
    ".sh",
    ".ps1",
}

WORKFLOW_FOREIGN_KEYS = [
    "node",
    "npm",
    "npx",
    "yarn",
    "pnpm",
    "deno",
    "bun",
]

PRECOMMIT_NODE_HINTS = [
    "markdownlint",
    "prettier",
]


def _is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    return any(part in IGNORED_DIRS for part in parts)


def _scan_files(root: Path) -> Dict[str, Any]:
    manifests: List[str] = []
    foreign_sources: List[str] = []

    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in IGNORED_DIRS:
                # prune walk by skipping ignored dirs
                # rglob cannot prune, but we simply ignore their contents by check above
                pass
            continue
        if _is_ignored(p):
            continue
        name = p.name
        if name in FOREIGN_MANIFESTS:
            manifests.append(str(p.resolve()))
        else:
            if p.suffix.lower() in FOREIGN_SOURCE_EXTS:
                foreign_sources.append(str(p.resolve()))

    return {
        "manifests": sorted(manifests),
        "foreign_sources": sorted(foreign_sources),
    }


def _scan_workflows(root: Path) -> Dict[str, Any]:
    workflows_dir = root / ".github" / "workflows"
    results: List[Dict[str, Any]] = []
    if workflows_dir.is_dir():
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        for wf in workflow_files:
            try:
                text = wf.read_text(encoding="utf-8")
            except Exception:
                continue
            hits = []
            for key in WORKFLOW_FOREIGN_KEYS:
                if re.search(rf"\b{re.escape(key)}\b", text):
                    hits.append(key)
            if hits:
                results.append(
                    {
                        "path": str(wf.resolve()),
                        "keys": sorted(set(hits)),
                    }
                )
    return {"workflows_with_foreign_keys": results}


def _scan_precommit(root: Path) -> Dict[str, Any]:
    file = root / ".pre-commit-config.yaml"
    status = {"path": str(file.resolve()), "node_hints": [], "has_file": file.exists()}
    if not file.exists():
        return status
    try:
        text = file.read_text(encoding="utf-8")
    except Exception:
        return status
    hints: List[str] = []
    for hint in PRECOMMIT_NODE_HINTS:
        if hint in text:
            hints.append(hint)
    status["node_hints"] = hints
    return status


def _scan_node_configs(root: Path) -> Dict[str, Any]:
    hits: List[str] = []
    for name in [
        ".markdownlint.json",
        ".pnp.cjs",
        ".pnp.js",
        ".yarnrc",
        ".npmrc",
        ".nvmrc",
        ".node-version",
    ]:
        p = root / name
        if p.exists():
            hits.append(str(p.resolve()))
    # node_modules directories
    node_modules_dirs = [str(p.resolve()) for p in root.rglob("node_modules") if p.is_dir() and not _is_ignored(p)]
    return {"node_configs": sorted(hits), "node_modules": sorted(node_modules_dirs)}


def _write_report(report: Dict[str, Any], out_path: Path, log: AutomationLogger) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    log.info(f"Wrote foreign dependency report: {out_path}")


def _replace_in_file(path: Path, replacements: List[tuple[str, str]], log: AutomationLogger) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        log.error(f"Cannot read {path}: {e}")
        return False
    new_text = text
    for old, new in replacements:
        new_text = new_text.replace(old, new)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        log.info(f"Patched file: {path}")
        return True
    return False


def _ensure_gitignore_node_modules(root: Path, log: AutomationLogger) -> bool:
    gi = root / ".gitignore"
    if not gi.exists():
        return False
    content = gi.read_text(encoding="utf-8")
    if re.search(r"^node_modules/\s*$", content, flags=re.MULTILINE):
        return False
    content = content.rstrip() + "\n\n# Node\nnode_modules/\n"
    gi.write_text(content, encoding="utf-8")
    log.info("Appended node_modules/ to .gitignore")
    return True


def _prune_precommit_node_blocks(root: Path, log: AutomationLogger) -> bool:
    pc = root / ".pre-commit-config.yaml"
    if not pc.exists():
        return False
    lines = pc.read_text(encoding="utf-8").splitlines()
    out: List[str] = []
    skip = False
    removed = False
    for line in lines:
        # Remove commented markdownlint-cli block
        if line.startswith("#  - repo: https://github.com/igorshubovych/markdownlint-cli"):
            skip = True
            removed = True
            continue
        if line.startswith("#  - repo: https://github.com/pre-commit/mirrors-prettier"):
            skip = True
            removed = True
            continue
        if skip:
            # stop skipping when leaving a commented block (next non-comment or blank less indented)
            if line.strip() and not line.strip().startswith("#"):
                skip = False
                out.append(line)
            else:
                # continue skipping commented block
                continue
        else:
            out.append(line)
    if removed:
        pc.write_text("\n".join(out) + "\n", encoding="utf-8")
        log.info("Pruned Node-related commented hooks from .pre-commit-config.yaml")
    return removed


def _add_precommit_guard_hook(root: Path, log: AutomationLogger) -> bool:
    pc = root / ".pre-commit-config.yaml"
    if not pc.exists():
        return False
    text = pc.read_text(encoding="utf-8")
    guard_snippet = (
        "    - id: foreign-deps-guard\n"
        "      name: Foreign dependency guard (scan only)\n"
        '      entry: python -m automation.scripts.run_automation --task "Foreign Dependency Sanitize" --dry-run\n'
        "      language: system\n"
        "      pass_filenames: false\n"
    )
    if "id: foreign-deps-guard" in text:
        return False
    # Insert into local repo hooks section (after existing local hooks)
    new_text = text
    if "- repo: local" in text and "hooks:" in text:
        new_text = re.sub(
            r"(- repo: local\s*\n\s*hooks:\s*\n)",
            r"\1" + guard_snippet,
            text,
            count=1,
        )
    if new_text != text:
        pc.write_text(new_text, encoding="utf-8")
        log.info("Added pre-commit guard hook for foreign dependency scan")
        return True
    return False


def _delete_node_configs(paths: List[str], ctx, log: AutomationLogger, assume_yes: bool = False) -> List[str]:
    removed: List[str] = []
    for p_str in paths:
        p = Path(p_str)
        if not p.exists():
            continue
        if ctx.dry_run:
            log.info(f"[DRY-RUN] Would delete {p}")
            removed.append(str(p))
            continue
        if assume_yes or ctx.require_confirmation(f"Delete Node-specific config '{p.name}' at {p}?"):
            try:
                p.unlink()
                removed.append(str(p))
                log.info(f"Deleted {p}")
            except Exception as e:
                log.error(f"Failed to delete {p}: {e}")
    return removed


def foreign_dependency_sanitize(context) -> None:
    log = AutomationLogger()
    root = Path(".").resolve()

    apply_changes = bool(context.extra_data.get("apply_changes", False))
    delete_node_configs = bool(context.extra_data.get("delete_node_configs", False))
    report_file = context.extra_data.get("report_file", "automation/reports/foreign_dependency_report.json")
    assume_yes = bool(context.extra_data.get("assume_yes", False))

    log.info("Scanning repository for foreign dependencies...")

    report: Dict[str, Any] = {
        "root": str(root),
    }

    files_info = _scan_files(root)
    report.update(files_info)

    workflow_info = _scan_workflows(root)
    report.update(workflow_info)

    precommit_info = _scan_precommit(root)
    report["precommit"] = precommit_info

    node_cfg_info = _scan_node_configs(root)
    report.update(node_cfg_info)

    # Classify priorities
    critical: List[Dict[str, Any]] = []
    moderate: List[Dict[str, Any]] = []
    informational: List[Dict[str, Any]] = []

    # Critical: Node usage in workflows
    for wf in workflow_info.get("workflows_with_foreign_keys", []):
        if any(k in {"npm", "node", "yarn", "pnpm"} for k in wf.get("keys", [])):
            critical.append({"type": "workflow_node_usage", **wf})

    # Moderate: Shell scripts and PowerShell scripts in repo
    for p in files_info.get("foreign_sources", []):
        if Path(p).suffix.lower() in {".sh"}:
            moderate.append({"type": "bash_script", "path": p})
        if Path(p).suffix.lower() in {".ps1"}:  # unlikely here due to ext set, but keep
            moderate.append({"type": "powershell_script", "path": p})

    # Informational: Node config files present
    for p in node_cfg_info.get("node_configs", []):
        informational.append({"type": "node_config", "path": p})

    report["classification"] = {
        "critical": critical,
        "moderate": moderate,
        "informational": informational,
    }

    _write_report(report, Path(report_file), log)

    if not apply_changes:
        log.info("apply_changes is False: reporting only.")
        return

    # Guardrail remediations
    # 1) Patch CI workflow to remove npm markdownlint-cli2
    ai_ci = root / ".github" / "workflows" / "ai_advisor_ci.yml"
    if ai_ci.exists():
        _replace_in_file(
            ai_ci,
            [
                ("npm install -g markdownlint-cli2", "pip install pymarkdownlnt"),
                (
                    r'markdownlint-cli2"\*\*/\*.md" --config .markdownlint.json',
                    'pymarkdown scan "**/*.md"',
                ),
                (
                    'markdownlint-cli2 "**/*.md" --config .markdownlint.json',
                    'pymarkdown scan "**/*.md"',
                ),
            ],
            log,
        )

    # 2) Ensure node_modules/ ignored
    _ensure_gitignore_node_modules(root, log)

    # 3) Prune commented Node blocks from pre-commit and add guard hook
    _prune_precommit_node_blocks(root, log)
    _add_precommit_guard_hook(root, log)

    # 4) Optionally remove Node-specific config files
    if delete_node_configs and node_cfg_info.get("node_configs"):
        _delete_node_configs(node_cfg_info["node_configs"], context, log, assume_yes=assume_yes)

    log.info("Foreign dependency sanitation completed.")
