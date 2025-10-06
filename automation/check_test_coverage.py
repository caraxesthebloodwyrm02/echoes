#!/usr/bin/env python3
"""Check that new modules have corresponding tests.
Scans selected source directories and asserts presence of matching test files in tests/.
"""
from __future__ import annotations
from pathlib import Path
import sys

# Directories to scan for python modules
SRC_DIRS = [Path("app"), Path("packages")]
TESTS_DIR = Path("tests")


def candidate_modules():
    for src in SRC_DIRS:
        if not src.exists():
            continue
        for py in src.rglob("*.py"):
            if py.name == "__init__.py":
                continue
            yield py


def expected_test_file(py: Path) -> Path:
    # Simple heuristic: tests/test_<stem>.py
    return TESTS_DIR / f"test_{py.stem}.py"


def main() -> int:
    missing: list[tuple[Path, Path]] = []
    for mod in candidate_modules():
        t = expected_test_file(mod)
        if not t.exists():
            # Also allow any test file that mentions the module stem
            found = False
            if TESTS_DIR.exists():
                for tf in TESTS_DIR.glob("test_*.py"):
                    if mod.stem in tf.name:
                        found = True
                        break
            if not found:
                missing.append((mod, t))
    if missing:
        print("\n⚠️  Found modules without direct tests:")
        for m, t in missing[:50]:
            print(f"   {m} -> {t} (MISSING)")
        print("\n💡 Generate with: python automation/test_generator.py <source_file.py>")
        return 1
    print("✅ All modules appear to have matching tests (or indirect coverage)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
