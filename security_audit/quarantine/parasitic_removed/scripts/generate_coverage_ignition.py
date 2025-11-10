"""
generate_coverage_ignition.py

Utility for you (IDE agents and developers) to identify the "elephant" files that drag down project coverage
and to produce drop-in smoke test templates that you can quickly use to exercise large modules (high leverage).

Usage:
    python generate_coverage_ignition.py --root /path/to/repo --out tests/generated

Features:
- Reads coverage.xml (if present) to compute file-level statistics.
- Falls back to scanning .py files and counting source lines.
- Ranks files by size (lines) and uncovered statements (if coverage.xml is available).
- Generates smoke-test templates for the top-N heavy modules (module path -> test file).
- Generates a short report (JSON + human-readable) summarizing recommended targets.

Notes:
- The generated tests are intentionally conservative: they import the module under mocks,
  stub common external dependencies, and instantiate core classes if found.
- We should review and tweak import names (e.g., OpenAIClient) to match your actual code.

"""

from __future__ import annotations

import argparse
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_coverage_xml(coverage_xml: Path) -> dict[str, dict]:
    """Parse coverage.xml produced by coverage.py and return a mapping:
    { "path/to/file.py": {"lines": int, "covered": int, "missing": int, "percent": float} }
    """
    if not coverage_xml.exists():
        return {}
    tree = ET.parse(coverage_xml)
    root = tree.getroot()
    files = {}
    # coverage.py XML structure: packages/package/classes/class/lines/line ...
    # The top-level `<packages>` -> `<package>` -> `<classes>` -> `<class filename=...` is common.
    for cls in root.findall(".//class"):
        filename = cls.attrib.get("filename")
        if not filename:
            continue
        filename = os.path.normpath(filename)
        lines_total = 0
        lines_covered = 0
        for line in cls.findall(".//lines/line"):
            lines_total += 1
            if line.attrib.get("hits") and int(line.attrib.get("hits")) > 0:
                lines_covered += 1
        missing = lines_total - lines_covered
        percent = (lines_covered / lines_total * 100.0) if lines_total else 0.0
        files[filename] = {
            "lines": lines_total,
            "covered": lines_covered,
            "missing": missing,
            "percent": percent,
        }
    return files


def scan_py_files(root: Path) -> dict[str, int]:
    """Return a mapping of file paths to non-blank line counts (approximate statement weight)."""
    results: dict[str, int] = {}
    for p in root.rglob("*.py"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        # Simple: count non-empty, non-comment lines
        lines = [
            l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")
        ]
        results[str(p)] = len(lines)
    return results


def guess_module_from_path(repo_root: Path, file_path: str) -> str:
    """Convert a file path to an importable module name (best effort)."""
    p = Path(file_path)
    try:
        rel = p.relative_to(repo_root)
    except Exception:
        rel = p
    parts = list(rel.with_suffix("").parts)
    # Remove top-level 'src' or 'lib' if present
    if parts and parts[0] in ("src", "lib"):
        parts = parts[1:]
    return ".".join(parts)


SMOKE_TEST_TEMPLATE = """# Generated smoke test for {module}
import sys
import importlib
from unittest import mock
import pytest

# Ensure your repo root is on the path
sys.path.insert(0, '{repo_root}')

# ---------- Adjust these mocks to match our project's external clients ----------
COMMON_PATCHES = [
    # ('{module}.OpenAIClient', 'mock.Mock'),
    # ('{module}.SomeDBClient', 'mock.Mock'),
]


def test_import_and_basic_init():
    \"\"\"Smoke import and minimal sanity checks. Replace placeholder names as needed.\"\"\"
    # Patch common external clients to avoid network/IO during import
    for target, _ in COMMON_PATCHES:
        mock.patch(target).start()
    try:
        mod = importlib.import_module('{module}')
    finally:
        mock.patch.stopall()

    # Basic assertions that indicate that your module is present and exposes expected entry points
    assert hasattr(mod, '__name__')
    # If there's a central class, the generator will attempt to assert its presence (best effort)
    if hasattr(mod, 'AssistantCore'):
        cls = getattr(mod, 'AssistantCore')
        # Don't instantiate blindly — but try if it looks like a class
        if isinstance(cls, type):
            # Attempt a no-arg instantiation; if the constructor requires arguments, skip safely
            try:
                inst = cls()
                assert inst is not None
            except TypeError:
                pytest.skip('AssistantCore requires constructor arguments; please provide a custom test')


"""


def generate_smoke_test(repo_root: Path, module: str, out_dir: Path) -> Path:
    """Generate a smoke test file for your given module name (import path) into out_dir.
    Returns the path to the created file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = module.replace(".", "_")
    file_path = out_dir / f"test_smoke_{safe_name}.py"
    content = SMOKE_TEST_TEMPLATE.format(
        module=module, repo_root=str(repo_root).replace("\\", "\\\\")
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path


def recommend_targets(
    repo_root: Path,
    coverage_files: dict[str, dict],
    size_map: dict[str, int],
    top_n: int = 5,
) -> list[tuple[str, int, float | None]]:
    """Return a ranked list of (module_import_path, size_lines, percent_covered_or_None).
    Ranking criteria: missing coverage weight = size * (1 - percent/100) if percent is known; otherwise, size.
    """
    entries: list[tuple[str, int, float | None]] = []
    for fp, size in size_map.items():
        os.path.normpath(fp)
        cov = None
        # Try to match by filename ending
        for cfp, data in coverage_files.items():
            if os.path.normpath(cfp).endswith(os.path.normpath(fp)) or os.path.normpath(
                fp
            ).endswith(os.path.normpath(cfp)):
                cov = data.get("percent")
                break
        entries.append((fp, size, cov))

    def weight(e: tuple[str, int, float | None]) -> float:
        _, size, cov = e
        if cov is None:
            return float(size)
        return size * (1.0 - cov / 100.0)

    entries.sort(key=weight, reverse=True)
    # Map to module import path guesses
    result = []
    for fp, size, cov in entries[:top_n]:
        module = guess_module_from_path(repo_root, fp)
        result.append((module, size, cov))
    return result


def write_report(out: Path, report: dict):
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root", "-r", type=Path, default=Path("."), help="Your repository root"
    )
    ap.add_argument(
        "--coverage-xml",
        type=Path,
        default=Path("coverage.xml"),
        help="Path to your coverage.xml file",
    )
    ap.add_argument(
        "--out",
        "-o",
        type=Path,
        default=Path("tests/generated"),
        help="Output directory for generated tests",
    )
    ap.add_argument(
        "--top", type=int, default=5, help="Number of top targets you want to recommend"
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("tests/generated/coverage_ignition_report.json"),
    )
    args = ap.parse_args(argv)

    repo_root = args.root.resolve()
    cov_xml = args.coverage_xml

    print(f"Your repo root: {repo_root}")
    print(f"Looking for your coverage xml at: {cov_xml}")

    cov_files = parse_coverage_xml(cov_xml) if cov_xml.exists() else {}
    size_map = scan_py_files(repo_root)

    # Select top N by missing coverage weight
    targets = recommend_targets(repo_root, cov_files, size_map, top_n=args.top)
    print(
        "\\nTop targets (module, approximate non-blank lines, percent covered if known):"
    )
    for mod, size, cov in targets:
        print(f" - {mod}  | lines~{size} | covered%={cov}")

    generated = []
    for mod, size, cov in targets:
        path = generate_smoke_test(repo_root, mod, args.out)
        generated.append(
            {
                "module": mod,
                "size": size,
                "covered_percent": cov,
                "test_path": str(path),
            }
        )

    report = {
        "repo_root": str(repo_root),
        "coverage_xml_found": str(cov_xml.exists()),
        "top_targets": generated,
    }
    write_report(args.report, report)
    print(
        f"Generated {len(generated)} smoke tests into {args.out} and wrote your report to {args.report}"
    )


if __name__ == "__main__":
    main()
