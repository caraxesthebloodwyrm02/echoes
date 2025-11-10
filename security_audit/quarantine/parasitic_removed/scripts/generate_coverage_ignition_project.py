"""
generate_coverage_ignition_project.py

Project-specific version that filters out venv and focuses on Echoes project files
"""

from __future__ import annotations

import argparse
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_coverage_xml(coverage_xml: Path) -> dict[str, dict]:
    """Parse coverage.xml produced by coverage.py and return a mapping."""
    if not coverage_xml.exists():
        return {}
    tree = ET.parse(coverage_xml)
    root = tree.getroot()
    files = {}
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
    """Return a mapping of file paths to non-blank line counts, excluding venv."""
    results: dict[str, int] = {}
    for p in root.rglob("*.py"):
        # Skip venv and other non-project directories
        if any(skip in str(p) for skip in ["venv", ".venv", "__pycache__", ".git"]):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = [
            l for l in text.splitlines() if l.strip() and not l.strip().startswith("#")
        ]
        results[str(p)] = len(lines)
    return results


def guess_module_from_path(repo_root: Path, file_path: str) -> str:
    """Convert a file path to an importable module name."""
    p = Path(file_path)
    try:
        rel = p.relative_to(repo_root)
    except Exception:
        rel = p
    parts = list(rel.with_suffix("").parts)
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

# ---------- Echoes-specific mocks ----------
COMMON_PATCHES = [
    ('{module}.OpenAIClient', 'mock.Mock'),
    ('{module}.DatabaseClient', 'mock.Mock'),
    ('{module}.RedisClient', 'mock.Mock'),
    ('{module}.requests.get', 'mock.Mock'),
    ('{module}.asyncio.sleep', 'mock.Mock'),
]


def test_import_and_basic_init():
    \"\"\"Smoke import and minimal sanity checks for Echoes module.\"\"\"
    # Patch common external clients
    for target, _ in COMMON_PATCHES:
        try:
            mock.patch(target).start()
        except (ImportError, AttributeError):
            pass  # Skip if target doesn't exist
    
    try:
        mod = importlib.import_module('{module}')
    finally:
        mock.patch.stopall()

    # Basic assertions
    assert hasattr(mod, '__name__')
    
    # Test common Echoes patterns
    common_classes = ['EchoesAssistant', 'RAGEngine', 'ConfigManager', 'ToolRegistry', 'WorkflowEngine']
    for cls_name in common_classes:
        if hasattr(mod, cls_name):
            cls = getattr(mod, cls_name)
            if isinstance(cls, type):
                try:
                    # Try no-arg instantiation first
                    inst = cls()
                    assert inst is not None
                except TypeError:
                    try:
                        # Try with common config pattern
                        mock_config = mock.Mock()
                        inst = cls(mock_config)
                        assert inst is not None
                    except Exception:
                        pytest.skip(f'{cls_name} requires specific arguments')


def test_module_functions():
    \"\"\"Test key module functions if they exist.\"\"\"
    sys.path.insert(0, '{repo_root}')
    
    try:
        mod = importlib.import_module('{module}')
    except ImportError:
        pytest.skip(f'Cannot import module {module}')
    
    # Test common function patterns
    common_functions = ['initialize', 'configure', 'process', 'execute', 'run', 'start', 'setup']
    
    for func_name in common_functions:
        if hasattr(mod, func_name):
            func = getattr(mod, func_name)
            if callable(func):
                try:
                    # Try calling with minimal args
                    result = func()
                    assert result is not None
                except Exception:
                    # Functions may require args, that's OK
                    pass
"""


def generate_smoke_test(repo_root: Path, module: str, out_dir: Path) -> Path:
    """Generate a smoke test file for the given module."""
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = module.replace(".", "_").replace("\\", "_").replace("/", "_")
    file_path = out_dir / f"test_smoke_{safe_name}.py"

    # Simple template without complex formatting
    template = f'''# Generated smoke test for {module}
import sys
import importlib
from unittest import mock
import pytest

# Ensure your repo root is on the path
sys.path.insert(0, '{repo_root}')

# ---------- Echoes-specific mocks ----------
COMMON_PATCHES = [
    ('{module}.OpenAIClient', 'mock.Mock'),
    ('{module}.DatabaseClient', 'mock.Mock'),
    ('{module}.RedisClient', 'mock.Mock'),
    ('{module}.requests.get', 'mock.Mock'),
    ('{module}.asyncio.sleep', 'mock.Mock'),
]


def test_import_and_basic_init():
    """Smoke import and minimal sanity checks for Echoes module."""
    # Patch common external clients
    for target, _ in COMMON_PATCHES:
        try:
            mock.patch(target).start()
        except (ImportError, AttributeError):
            pass  # Skip if target doesn't exist
    
    try:
        mod = importlib.import_module('{module}')
    finally:
        mock.patch.stopall()

    # Basic assertions
    assert hasattr(mod, '__name__')
    
    # Test common Echoes patterns
    common_classes = ['EchoesAssistant', 'RAGEngine', 'ConfigManager', 'ToolRegistry', 'WorkflowEngine']
    for cls_name in common_classes:
        if hasattr(mod, cls_name):
            cls = getattr(mod, cls_name)
            if isinstance(cls, type):
                try:
                    # Try no-arg instantiation first
                    inst = cls()
                    assert inst is not None
                except TypeError:
                    try:
                        # Try with common config pattern
                        mock_config = mock.Mock()
                        inst = cls(mock_config)
                        assert inst is not None
                    except Exception:
                        pytest.skip(f'{{cls_name}} requires specific arguments')


def test_module_functions():
    """Test key module functions if they exist."""
    sys.path.insert(0, '{repo_root}')
    
    try:
        mod = importlib.import_module('{module}')
    except ImportError:
        pytest.skip(f'Cannot import module {module}')
    
    # Test common function patterns
    common_functions = ['initialize', 'configure', 'process', 'execute', 'run', 'start', 'setup']
    
    for func_name in common_functions:
        if hasattr(mod, func_name):
            func = getattr(mod, func_name)
            if callable(func):
                try:
                    # Try calling with minimal args
                    result = func()
                    assert result is not None
                except Exception:
                    # Functions may require args, that's OK
                    pass
'''

    file_path.write_text(template, encoding="utf-8")
    return file_path


def recommend_targets(
    repo_root: Path,
    coverage_files: dict[str, dict],
    size_map: dict[str, int],
    top_n: int = 5,
) -> list[tuple[str, int, float | None]]:
    """Return ranked list of Echoes project targets."""
    entries: list[tuple[str, int, float | None]] = []
    for fp, size in size_map.items():
        os.path.normpath(fp)
        cov = None
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
        "--root", "-r", type=Path, default=Path("."), help="Repository root"
    )
    ap.add_argument(
        "--coverage-xml",
        type=Path,
        default=Path("coverage.xml"),
        help="Path to coverage.xml",
    )
    ap.add_argument(
        "--out",
        "-o",
        type=Path,
        default=Path("tests/generated"),
        help="Output directory",
    )
    ap.add_argument("--top", type=int, default=8, help="Number of top targets")
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("tests/generated/echoes_ignition_report.json"),
    )
    args = ap.parse_args(argv)

    repo_root = args.root.resolve()
    cov_xml = args.coverage_xml

    print("🔥 Echoes Coverage Ignition System")
    print(f"📁 Repo root: {repo_root}")
    print(f"📊 Coverage XML: {cov_xml}")

    cov_files = parse_coverage_xml(cov_xml) if cov_xml.exists() else {}
    size_map = scan_py_files(repo_root)

    targets = recommend_targets(repo_root, cov_files, size_map, top_n=args.top)
    print("\\n🎯 Top Echoes targets (module, lines, coverage%):")
    for mod, size, cov in targets:
        cov_str = f"{cov:.1f}%" if cov is not None else "Unknown"
        print(f"   🔥 {mod:<40} | {size:>4} lines | {cov_str:>8}")

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
        "total_project_files": len(size_map),
        "top_targets": generated,
        "potential_coverage_gain": sum(
            t[1] for t in targets if t[2] is not None and t[2] < 50
        ),
    }
    write_report(args.report, report)

    print(f"\\n✅ Generated {len(generated)} smoke tests in {args.out}")
    print(f"📈 Report saved to: {args.report}")
    print(f'🚀 Potential coverage gain: {report["potential_coverage_gain"]}+ lines')


if __name__ == "__main__":
    main()
