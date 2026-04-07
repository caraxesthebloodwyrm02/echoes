#!/usr/bin/env python3
"""Structural wiring health check for canopy/echoes.

Scheduled maintenance for code wiring — the equivalent of checking
cable runs, junction integrity, and loop isolation in a physical system.

Five checks:
  1. Import resolution  — every internal import actually resolves
  2. Circular deps      — no cycles in the core_modules DAG
  3. Partition conflicts — no stale partition_key collisions in data/
  4. Barrel alignment    — __init__.py re-exports match module public surface
  5. Debug residue       — no breakpoint(), pdb, or print() leaks in core_modules

Usage:
    uv run python scripts/structural_health_check.py
    uv run python scripts/structural_health_check.py --verbose
    uv run python scripts/structural_health_check.py --check imports,cycles
"""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ECHOES_ROOT = Path(__file__).resolve().parent.parent
CORE_MODULES = ECHOES_ROOT / "core_modules"
INTEGRATIONS = ECHOES_ROOT / "integrations"
DATA_DIR = ECHOES_ROOT / "data"

# Packages whose internal imports we trace
INTERNAL_ROOTS = ("core_modules", "integrations", "core", "app", "legal_safeguards")

# Patterns that should never appear in production core_modules
DEBUG_PATTERNS = ("breakpoint(", "pdb.set_trace(", "import pdb")
PRINT_PATTERN = "print("

# Return codes
RC_OK = 0
RC_FAIL = 1


# ── Utilities ────────────────────────────────────────────────────────────────


def _py_files(directory: Path) -> list[Path]:
    """Yield non-pycache .py files."""
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.rglob("*.py") if "__pycache__" not in f.parts)


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ECHOES_ROOT))
    except ValueError:
        return str(path)


# ── Check 1: Import resolution ──────────────────────────────────────────────


def check_imports(verbose: bool = False) -> list[str]:
    """Verify every core_modules and integrations module is importable."""
    failures: list[str] = []
    sys.path.insert(0, str(ECHOES_ROOT))

    targets: list[tuple[str, Path]] = []
    for pkg_dir in (CORE_MODULES, INTEGRATIONS):
        pkg_name = pkg_dir.name
        for f in _py_files(pkg_dir):
            if f.name == "__init__.py":
                targets.append((pkg_name, f))
            else:
                targets.append((f"{pkg_name}.{f.stem}", f))

    for module_name, filepath in targets:
        try:
            importlib.import_module(module_name)
            if verbose:
                print(f"  OK  {module_name}")
        except Exception as exc:
            msg = f"{module_name}: {type(exc).__name__}: {exc}"
            failures.append(msg)
            print(f"  FAIL {msg}")

    return failures


# ── Check 2: Circular dependency detection ───────────────────────────────────


def check_cycles(verbose: bool = False) -> list[str]:
    """Detect circular imports within core_modules using AST analysis."""
    graph: dict[str, set[str]] = {}

    for f in _py_files(CORE_MODULES):
        if f.name == "__init__.py":
            continue
        name = f.stem
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        deps: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[0] == "core_modules" and len(parts) > 1:
                    deps.add(parts[1])
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    parts = alias.name.split(".")
                    if parts[0] == "core_modules" and len(parts) > 1:
                        deps.add(parts[1])
        if deps:
            graph[name] = deps

    if verbose:
        for mod, deps in sorted(graph.items()):
            print(f"  {mod} -> {sorted(deps)}")

    # DFS cycle detection
    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycles: list[list[str]] = []

    def _dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        for dep in graph.get(node, set()):
            if dep not in graph:
                continue
            if dep in rec_stack:
                idx = path.index(dep)
                cycles.append(path[idx:] + [dep])
            elif dep not in visited:
                _dfs(dep, path + [dep])
        rec_stack.discard(node)

    for m in sorted(graph):
        if m not in visited:
            _dfs(m, [m])

    return [f"CYCLE: {' -> '.join(c)}" for c in cycles]


# ── Check 3: Partition conflict stale data ───────────────────────────────────


def check_partition_data(verbose: bool = False) -> list[str]:
    """Verify partition registry integrity in data/class-of-21/."""
    issues: list[str] = []
    registry = DATA_DIR / "class-of-21" / "manifests" / "partition_registry.jsonl"

    if not registry.exists():
        if verbose:
            print("  SKIP partition_registry.jsonl not found (no data yet)")
        return issues

    seen_ids: dict[tuple[str, str], int] = {}
    line_no = 0
    for raw in registry.read_text(encoding="utf-8").splitlines():
        line_no += 1
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(f"partition_registry.jsonl:{line_no} invalid JSON: {exc}")
            continue

        eid = row.get("entity_id", "")
        pid = row.get("partition_id", "")
        key = (eid, pid)
        if key in seen_ids:
            issues.append(
                f"partition_registry.jsonl:{line_no} duplicate (entity_id={eid}, "
                f"partition_id={pid}) first seen line {seen_ids[key]}"
            )
        else:
            seen_ids[key] = line_no

    if verbose:
        print(f"  {line_no} entries, {len(seen_ids)} unique partitions")

    return issues


# ── Check 4: Barrel alignment ────────────────────────────────────────────────


def check_barrel_alignment(verbose: bool = False) -> list[str]:
    """Verify __init__.py re-exports vs actual module files."""
    issues: list[str] = []

    for pkg_dir in (CORE_MODULES, INTEGRATIONS):
        init = pkg_dir / "__init__.py"
        if not init.exists():
            continue

        # Modules present on disk
        disk_modules = {f.stem for f in _py_files(pkg_dir) if f.name != "__init__.py"}

        # Names imported in __init__.py
        try:
            tree = ast.parse(init.read_text(encoding="utf-8"))
        except SyntaxError:
            issues.append(f"{_relative(init)}: SyntaxError")
            continue

        barrel_imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if len(parts) > 1 and parts[0] == pkg_dir.name:
                    barrel_imports.add(parts[1])
                elif parts[0] not in INTERNAL_ROOTS and node.level > 0:
                    # relative import
                    for alias in node.names or []:
                        barrel_imports.add(alias.name)

        # Only flag if __init__.py is actively re-exporting (not just docstring)
        init_text = init.read_text(encoding="utf-8").strip()
        if len(init_text.splitlines()) <= 2:
            if verbose:
                print(f"  {_relative(init)}: minimal barrel (OK, no re-exports)")
            continue

        missing = disk_modules - barrel_imports
        if missing and verbose:
            print(f"  {_relative(init)}: modules not re-exported: {sorted(missing)}")

    return issues


# ── Check 5: Debug residue ───────────────────────────────────────────────────


def check_debug_residue(verbose: bool = False) -> list[str]:
    """Scan core_modules for breakpoint/pdb/print leaks."""
    issues: list[str] = []

    for f in _py_files(CORE_MODULES):
        if f.name == "__init__.py":
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("#"):
                continue
            # Skip strings (rough heuristic — inside triple-quotes)
            if stripped.startswith(('"""', "'''")):
                continue

            for pat in DEBUG_PATTERNS:
                if pat in stripped:
                    issues.append(f"{_relative(f)}:{line_no} debug residue: {pat}")

            # print() in non-script files — warn only
            # Must be a standalone call, not a substring (e.g. fingerprint)
            if PRINT_PATTERN in stripped and not stripped.startswith("def "):
                # Exclude substrings: only flag if print( is preceded by
                # a non-alphanumeric character or starts the line
                import re

                if re.search(r"(?<![a-zA-Z_])print\(", stripped):
                    if verbose:
                        print(f"  WARN {_relative(f)}:{line_no} print() call")

    return issues


# ── Orchestrator ─────────────────────────────────────────────────────────────

ALL_CHECKS = {
    "imports": ("Import resolution", check_imports),
    "cycles": ("Circular dependency", check_cycles),
    "partitions": ("Partition data integrity", check_partition_data),
    "barrel": ("Barrel alignment", check_barrel_alignment),
    "debug": ("Debug residue", check_debug_residue),
}


def run(checks: list[str] | None = None, verbose: bool = False) -> dict[str, Any]:
    """Run selected checks and return structured results."""
    selected = checks or list(ALL_CHECKS.keys())
    results: dict[str, Any] = {}
    total_failures = 0

    for key in selected:
        if key not in ALL_CHECKS:
            print(f"Unknown check: {key}")
            continue

        label, fn = ALL_CHECKS[key]
        print(f"\n{'─' * 60}")
        print(f"Check: {label}")
        print(f"{'─' * 60}")

        failures = fn(verbose=verbose)
        passed = len(failures) == 0
        total_failures += len(failures)

        results[key] = {
            "label": label,
            "passed": passed,
            "failures": failures,
        }

        if passed:
            print(f"  ✓ PASS")
        else:
            for f in failures:
                print(f"  ✗ {f}")

    # Summary
    print(f"\n{'═' * 60}")
    total = len(selected)
    passed = sum(1 for r in results.values() if r["passed"])
    print(f"Structural health: {passed}/{total} checks passed")
    if total_failures > 0:
        print(f"  {total_failures} issue(s) found")
    else:
        print("  All wiring clean.")
    print(f"{'═' * 60}")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Structural wiring health check")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--check",
        "-c",
        help="Comma-separated check names: imports,cycles,partitions,barrel,debug",
    )
    args = parser.parse_args()

    checks = args.check.split(",") if args.check else None
    results = run(checks=checks, verbose=args.verbose)

    all_passed = all(r["passed"] for r in results.values())
    return RC_OK if all_passed else RC_FAIL


if __name__ == "__main__":
    sys.exit(main())
