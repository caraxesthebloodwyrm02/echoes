#!/usr/bin/env python3
"""
Formatting helper: run black/isort/autoflake, then best-effort split of long
single-line string literals and f-strings to satisfy E501 without changing
semantics.

Usage examples:
  python tools/format_all.py --files examples/Untitled-1.py ubi_simulator/models/ubi_model.py
  python tools/format_all.py  # runs on a sensible default set

Notes:
- Long-string splitting is conservative: it skips triple-quoted strings and
  lines that look complex (multiple quote types or mixed tokens). It focuses on
  single-line literals and f-strings.
- Always review diffs after running.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FILES = [
    "examples/Untitled-1.py",
    "ubi_simulator/models/ubi_model.py",
    "examples/agentic_assistant_demo.py",
    "examples/assistant_automation_integration.py",
    "examples/assistant_basic_usage.py",
    "examples/lumina_demo.py",
    "examples/natural_language_demo.py",
    "examples/orchestrator_demo.py",
    "examples/quickstart.py",
    "examples/stick_shift_demo.py",
    "maintenance/reorganization_summary.py",
    "ubi_simulator/dashboard/app.py",
]

TRIPLE_QUOTE_PATTERN = re.compile(r"'''|\"\"\"")
SIMPLE_STRING_LINE = re.compile(
    r"^\s*(?P<prefix>[rubfRUBF]{0,2})?(?P<quote>['\"])\s*.*\s*(?P=quote)\s*(#.*)?$"
)


def run(cmd: List[str]) -> int:
    try:
        print("$", " ".join(cmd))
        return subprocess.call(cmd, cwd=str(REPO_ROOT))
    except FileNotFoundError:
        print(f"[WARN] Command not found: {cmd[0]}")
        return 127


def chunk_text(text: str, max_len: int) -> List[str]:
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_len)
        chunks.append(text[start:end])
        start = end
    return chunks


def split_long_strings(path: Path, max_len: int = 88) -> bool:
    """Split long one-line string or f-string literals using implicit concatenation.

    Returns True if file was modified.
    """
    try:
        original = path.read_text(encoding="utf-8")
    except Exception:
        return False

    lines = original.splitlines(keepends=False)
    changed = False

    new_lines: List[str] = []
    for line in lines:
        if len(line) <= max_len:
            new_lines.append(line)
            continue

        # Skip triple-quoted or complex lines
        if TRIPLE_QUOTE_PATTERN.search(line):
            new_lines.append(line)
            continue

        # Heuristic: only operate on lines that look like a single literal (possibly f-prefixed)
        # and avoid multiple quote types in one line
        quote_counts = (line.count('"') > 0) + (line.count("'") > 0)
        if quote_counts != 1:
            new_lines.append(line)
            continue

        m = SIMPLE_STRING_LINE.match(line.strip())
        if not m:
            new_lines.append(line)
            continue

        prefix = (m.group("prefix") or "").lower()
        is_f = "f" in prefix
        quote = m.group("quote")

        # Extract content inside the outermost quotes conservatively
        try:
            first = line.index(quote)
            last = line.rindex(quote)
            inner = line[first + 1 : last]
        except ValueError:
            new_lines.append(line)
            continue

        indent = line[: len(line) - len(line.lstrip())]

        # Build parenthesized concatenation pieces
        max_inner = max(8, max_len - len(indent) - 3)  # keep margin
        parts = chunk_text(inner, max_inner)

        # For f-strings, each piece should be an f-string
        prefix_out = "f" if is_f else ""
        pieces = [f"{prefix_out}{quote}{p}{quote}" for p in parts]

        split_block = indent + "(" + (" \n" + indent).join(pieces) + ")"

        if len(split_block) < len(line):
            new_lines.append(split_block)
            changed = True
        else:
            new_lines.append(line)

    if changed:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return changed


def files_from_args(items: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    for it in items:
        p = (REPO_ROOT / it).resolve()
        if p.exists():
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Format repo and split long strings")
    ap.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Target files. If omitted, a default curated set is used.",
    )
    ap.add_argument("--max-len", type=int, default=88, help="Max line length")
    ap.add_argument(
        "--no-autoflake",
        action="store_true",
        help="Do not run autoflake to remove unused imports/variables",
    )
    ap.add_argument(
        "--stage",
        action="store_true",
        help="git add changed files after formatting",
    )
    args = ap.parse_args()

    targets = (
        files_from_args(args.files) if args.files else files_from_args(DEFAULT_FILES)
    )
    if not targets:
        print("[INFO] No targets found. Nothing to do.")
        return 0

    rels = [str(p.relative_to(REPO_ROOT)) for p in targets]

    # Run formatters
    run(["black", *rels])
    run(["isort", *rels])
    if not args.no_autoflake:
        run(
            [
                "autoflake",
                "--in-place",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "-r",
                *rels,
            ]
        )

    # Best-effort long-string splitting
    changed_any = False
    for p in targets:
        if split_long_strings(p, max_len=args.max_len):
            print(f"[CHANGED] Split long strings: {p}")
            changed_any = True

    if args.stage and changed_any:
        run(["git", "add", *rels])

    print("[DONE] Formatting complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
