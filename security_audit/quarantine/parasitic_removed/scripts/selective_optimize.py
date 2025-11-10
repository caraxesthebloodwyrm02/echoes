#!/usr/bin/env python3
"""
Selective Attention Optimizer - Repository Scanner

- Scans a repository for .py files
- Runs the i_o.smart_optimizer.SelectiveAttentionOptimizer on each file
- Aggregates results into a consolidated summary

Usage:
  python scripts/selective_optimize.py --root . --limit 100

Notes:
- Non-destructive and read-only. Prints a human-friendly report to stdout.
- You can redirect output to a file if desired.
"""
from __future__ import annotations

import argparse
import os
import sys

# Import optimizer from i_o package
try:
    from i_o.smart_optimizer import SelectiveAttentionOptimizer
except Exception as exc:
    print(
        "⚠️ Failed to import i_o.smart_optimizer. Ensure i_o/smart_optimizer.py exists and is importable."
    )
    print("Error:", exc)
    sys.exit(1)


def iter_python_files(root: str, max_files: int | None = None) -> list[str]:
    collected: list[str] = []
    for base, _dirs, files in os.walk(root):
        # Skip common heavy or virtualenv dirs
        if any(
            skip in base
            for skip in (
                os.sep + ".git",
                os.sep + "venv",
                os.sep + ".venv",
                os.sep + "__pycache__",
            )
        ):
            continue
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(base, name)
            collected.append(path)
            if max_files and len(collected) >= max_files:
                return collected
    return collected


def scan_file(path: str, optimizer: SelectiveAttentionOptimizer) -> tuple[str, object]:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        report = optimizer.optimize_text(content)
        return path, report
    except Exception as exc:

        class _Err:
            def __init__(self, e):
                self.pretty = f"ERROR: {e}"

        return path, _Err(exc)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run Selective Attention Optimizer across a repository"
    )
    ap.add_argument("--root", default=".", help="Root directory to scan (default: .)")
    ap.add_argument(
        "--limit", type=int, default=200, help="Max files to scan (default: 200)"
    )
    ap.add_argument(
        "--focus",
        default="auto",
        choices=["auto", "high_value", "low_complexity", "urgent"],
        help="Attention focus mode",
    )
    args = ap.parse_args()

    optimizer = SelectiveAttentionOptimizer(attention_focus=args.focus)

    files = iter_python_files(args.root, max_files=args.limit)
    if not files:
        print("No Python files found.")
        return 0

    # Per-file reports
    all_jargon = {}
    all_redundancies = 0
    top_hotspots: list[tuple[str, float]] = []

    print(
        f"🔎 Scanning {len(files)} Python files under {os.path.abspath(args.root)} ...\n"
    )

    for path in files:
        p, report = scan_file(path, optimizer)
        if hasattr(report, "pretty_print"):
            jargon_terms = {hit.term for hit in report.jargon_hits}
            for term in jargon_terms:
                all_jargon[term] = all_jargon.get(term, 0) + 1
            all_redundancies += sum(c.frequency for c in report.redundancies)

            # Use first gravity score as a quick hotspot indicator if present
            if report.gravity_ranking:
                top_hotspots.append((p, report.gravity_ranking[0][1]))
        else:
            print(f"⚠️ Skipping {p}: {getattr(report, 'pretty', 'Unknown error')}")

    top_hotspots.sort(key=lambda t: t[1], reverse=True)

    print("📊 Consolidated Optimization Summary")
    print("=" * 34)
    print(f"Files scanned: {len(files)}")
    print(
        f"Unique jargon terms detected: {len(all_jargon)} -> {', '.join(sorted(all_jargon)) if all_jargon else 'None'}"
    )
    print(f"Total redundancy signals (approx.): {all_redundancies}")
    print("")

    if top_hotspots:
        print("Top 10 hotspots (by gravity score):")
        for path, score in top_hotspots[:10]:
            print(f"  - {path}  (gravity={score:.2f})")
    else:
        print("No hotspots detected.")

    print("\n✅ Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
