"""Tests for discover_issues.py."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from automation.tasks.discover_issues import find_code_patterns, run_code_quality_tools


@pytest.fixture
def test_files(tmp_path):
    """Create test files with various patterns."""
    patterns = {
        "todo.py": "# TODO: Fix this later\ndef foo(): pass",
        "fixme.py": "# FIXME: This is broken\ndef bar(): pass",
        "tech_debt.py": "# Technical Debt: Needs refactoring\ndef baz(): pass",
        "temp.py": "# Temporary: Quick fix\ndef qux(): pass",
        "unused.py": "import os\ndef main(): pass",
        "except.py": "try:\n    pass\nexcept:\n    pass",
        "mutable.py": "def func(x=[]):\n    pass",
    }

    for filename, content in patterns.items():
        file_path = tmp_path / filename
        file_path.write_text(content)

    return tmp_path


def test_find_code_patterns_successful(test_files):
    """Test finding code patterns in files."""

    def mock_grep(args, **kwargs):
        pattern = args[4]  # The pattern is the 5th argument
        matches = {
            r"TODO[ :].*": ("todo.py:1:# TODO: Fix this later"),
            r"FIXME[ :].*": ("fixme.py:1:# FIXME: This is broken"),
            r"(?i)(technical[ -]debt|refactor[ -]needed|needs[ -]improvement).*": (
                "tech_debt.py:1:# Technical Debt: Needs refactoring"
            ),
            r"(?i)(temporary|interim|provisional|workaround|stopgap)[ :].*": (
                "temp.py:1:# Temporary: Quick fix"
            ),
            r"^import \w+(?:\s*,\s*\w+)*(?:\s+as\s+\w+)?\s*(?:#.*)?$": ("unused.py:1:import os"),
            r"except\s*:": ("except.py:3:except:"),
            r"=\s*(\[|\{|\(|dict\(|list\(|set\()": ("mutable.py:1:def func(x=[]): pass"),
        }

        if pattern in matches:
            return Mock(returncode=0, stdout=matches[pattern], stderr="")

        # No match found
        return Mock(returncode=1, stdout="", stderr="")

    with patch("subprocess.run", side_effect=mock_grep):
        results = find_code_patterns(test_files)

        assert "todo" in results
        assert "fixme" in results
        assert "technical_debt" in results
        assert "interim_solution" in results
        assert "unused_import" in results
        assert "bare_except" in results
        assert "mutable_default" in results

        # Verify that matches were found for each pattern
        assert len(results["todo"]) == 1
        assert len(results["fixme"]) == 1
        assert len(results["technical_debt"]) == 1
        assert len(results["interim_solution"]) == 1
        assert len(results["unused_import"]) == 1
        assert len(results["bare_except"]) == 1
        assert len(results["mutable_default"]) == 1

        # Verify the structure of matches
        for name, matches in results.items():
            for match in matches:
                assert "file" in match
                assert "line" in match
                assert isinstance(match["line"], int)
                assert "content" in match


def test_find_code_patterns_grep_error():
    """Test handling of grep command failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(2, "grep", stderr="Error")
        results = find_code_patterns(Path("/nonexistent"))
        assert results == {}


def test_run_code_quality_tools_successful(tmp_path):
    """Test running code quality tools successfully."""

    def mock_tool_run(*args, **kwargs):
        # Mock successful execution for any tool
        return Mock(
            returncode=0,
            stdout="Success",
            stderr="",
            check=lambda: None,  # Add check method that succeeds
        )

    with patch("subprocess.run", side_effect=mock_tool_run):
        results = run_code_quality_tools(tmp_path)

        assert "ruff" in results
        assert results["ruff"]["success"]
        assert "mypy" in results
        assert results["mypy"]["success"]
        assert "pytest" in results
        assert results["pytest"]["success"]


def test_run_code_quality_tools_failure(tmp_path):
    """Test handling of tool execution failures."""

    def mock_tool_failure(*args, **kwargs):
        tool = args[0][1]
        return Mock(returncode=1, stdout=f"Error in {tool}", stderr=f"Failed to run {tool}")

    with patch("subprocess.run", side_effect=mock_tool_failure):
        results = run_code_quality_tools(tmp_path)

        assert "ruff" in results
        assert not results["ruff"]["success"]
        assert "mypy" in results
        assert not results["mypy"]["success"]
        assert "pytest" in results
        assert not results["pytest"]["success"]


def test_run_code_quality_tools_timeout(tmp_path):
    """Test handling of tool execution timeout."""
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 300)):
        results = run_code_quality_tools(tmp_path)
        # Verify that all tools are marked as failed
        assert all(not result["success"] for result in results.values())
        # Verify that timeout errors are reported correctly
        assert all("timed out" in result.get("error", "") for result in results.values())


def test_run_code_quality_tools_file_not_found(tmp_path):
    """Test handling of missing tool executables."""
    with patch("subprocess.run", side_effect=FileNotFoundError("No such file")):
        results = run_code_quality_tools(tmp_path)
        # Verify that all tools are marked as failed
        assert all(not result["success"] for result in results.values())
        # Verify that tool not found errors are reported correctly
        for result in results.values():
            assert "Tool not installed" in result.get("error", "") or "No such file" in result.get(
                "error", ""
            )


def test_run_code_quality_tools_generic_error(tmp_path):
    """Test handling of generic exceptions during tool execution."""
    with patch("subprocess.run", side_effect=Exception("Unexpected error")):
        results = run_code_quality_tools(tmp_path)
        # Verify that all tools are marked as failed
        assert all(not result["success"] for result in results.values())
        # Verify that error messages are captured
        assert all("Unexpected error" in result.get("error", "") for result in results.values())


def test_run_code_quality_tools_coverage_parsing(tmp_path):
    """Test parsing of coverage report and low coverage detection."""
    coverage_output = """Name                              Stmts   Miss  Cover
-----------------------------------------------------
module1.py                            50     10    80%
module2.py                            30     20    33%
module3.py                            20      2    90%
-----------------------------------------------------
TOTAL                               100     32    68%
"""

    def mock_coverage_run(*args, **kwargs):
        if "run" in args[0]:
            return Mock(returncode=0, stdout="Tests passed", stderr="")
        elif "report" in args[0]:
            return Mock(returncode=0, stdout=coverage_output, stderr="")
        return Mock(returncode=0, stdout="", stderr="")

    with patch("subprocess.run", side_effect=mock_coverage_run):
        results = run_code_quality_tools(tmp_path)

        assert "coverage" in results
        assert results["coverage"]["success"]
        assert "report" in results["coverage"]
        assert results["coverage"]["report"] == coverage_output

        # Verify low coverage module detection
        assert "low_coverage_modules" in results["coverage"]
        low_coverage = results["coverage"]["low_coverage_modules"]
        assert len(low_coverage) == 1
        assert low_coverage[0]["module"] == "module2.py"
        assert low_coverage[0]["coverage"] == 33.0


def test_find_code_patterns_broad_except(test_files):
    """Test detection of broad except clauses."""
    code = """try:
    something()
except Exception:
    pass
"""
    (test_files / "broad_except.py").write_text(code)

    def mock_grep(args, **kwargs):
        pattern = args[4]  # The pattern is the 5th argument
        if pattern == r"except\s+Exception\s*:":
            return Mock(returncode=0, stdout="broad_except.py:2:except Exception:", stderr="")
        return Mock(returncode=1, stdout="", stderr="")

    with patch("subprocess.run", side_effect=mock_grep):
        results = find_code_patterns(test_files)
        assert "broad_except" in results
        assert len(results["broad_except"]) == 1
        match = results["broad_except"][0]
        assert match["file"] == "broad_except.py"
        assert match["line"] == 2
        assert "except Exception:" in match["content"]
