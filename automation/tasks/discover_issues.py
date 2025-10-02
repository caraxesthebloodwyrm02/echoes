"""Search for common code patterns indicating issues."""

import subprocess
from pathlib import Path
from typing import Any

from automation.core.logger import log


def find_code_patterns(directory: Path) -> dict[str, list[dict[str, Any]]]:
    """Search for common code patterns indicating issues.

    Args:
        directory: Directory to search in

    Returns:
        Dictionary mapping pattern names to occurrences
    """
    patterns = {
        "todo": r"TODO[ :].*",
        "fixme": r"FIXME[ :].*",
        "technical_debt": (r"(?i)(technical[ -]debt|refactor[ -]needed|needs[ -]improvement).*"),
        "interim_solution": (
            r"(?i)(temporary|interim|provisional|workaround|stopgap)[ :].*"
        ),  # Enhanced from "temporary"
        "unused_import": (r"^import \w+(?:\s*,\s*\w+)*(?:\s+as\s+\w+)?\s*(?:#.*)?$"),
        "bare_except": r"except\s*:",
        "broad_except": r"except\s+Exception\s*:",
        "mutable_default": r"=\s*(\[|\{|\(|dict\(|list\(|set\()",
    }

    results = {}
    for pattern_name, pattern in patterns.items():
        log.info(f"Searching for {pattern_name} pattern")
        matches = []

        try:
            # Use grep for efficient pattern matching
            grep_result = subprocess.run(
                ["grep", "-r", "-n", "-P", pattern, str(directory)],
                capture_output=True,
                text=True,
                check=False,
            )

            if grep_result.returncode not in (0, 1):  # 1 means no matches
                log.error(f"Error searching for {pattern_name}: {grep_result.stderr}")
                continue

            for line in grep_result.stdout.splitlines():
                if line.strip():
                    file_path, line_num, content = line.split(":", 2)
                    matches.append(
                        {
                            "file": file_path,
                            "line": int(line_num),
                            "content": content.strip(),
                        }
                    )

        except subprocess.CalledProcessError as e:
            log.error(f"Error running grep for {pattern_name}: {e}")
            continue

        if matches:
            results[pattern_name] = matches

    return results


def run_code_quality_tools(project_root: Path) -> dict[str, Any]:
    """Run various code quality tools and collect results.

    Args:
        project_root: Root directory of the project

    Returns:
        Dictionary containing results from each tool
    """
    results = {}

    # Define tools and their commands
    tools = {
        "ruff": ["python", "-m", "ruff", "check", "."],
        "mypy": ["python", "-m", "mypy", "--ignore-missing-imports", "automation"],
        "pytest": ["python", "-m", "pytest", "-q"],
    }

    for tool_name, command in tools.items():
        try:
            log.info(f"Running {tool_name}...")
            result = subprocess.run(
                command,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            results[tool_name] = {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(command),
            }

            if result.returncode == 0:
                log.success(f"{tool_name} completed successfully")
            else:
                log.warning(f"{tool_name} found issues (exit code: {result.returncode})")

        except subprocess.TimeoutExpired:
            log.error(f"{tool_name} timed out")
            results[tool_name] = {
                "success": False,
                "error": "Tool timed out",
                "command": " ".join(command),
            }
        except FileNotFoundError:
            log.warning(f"{tool_name} not found, skipping")
            results[tool_name] = {
                "success": False,
                "error": "Tool not installed",
                "command": " ".join(command),
            }
        except Exception as e:
            log.error(f"Error running {tool_name}: {e}")
            results[tool_name] = {
                "success": False,
                "error": str(e),
                "command": " ".join(command),
            }

    # Run coverage separately
    try:
        log.info("Running coverage...")
        result = subprocess.run(
            ["coverage", "run", "-m", "pytest"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300,
        )

        coverage_result = {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

        if result.returncode == 0:
            # Generate coverage report
            report_result = subprocess.run(
                ["coverage", "report", "--format=text"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )

            coverage_result["report"] = report_result.stdout
            coverage_result["report_stderr"] = report_result.stderr

            # Parse coverage for modules below threshold
            low_coverage = []
            for line in report_result.stdout.splitlines():
                if "%" in line and "TOTAL" not in line and "-" not in line:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        try:
                            module = parts[0]
                            coverage_str = [p for p in parts if "%" in p][0]
                            coverage = float(coverage_str.rstrip("%"))
                            if coverage < 80:  # Configurable threshold
                                low_coverage.append({"module": module, "coverage": coverage})
                        except (ValueError, IndexError):
                            continue

            coverage_result["low_coverage_modules"] = low_coverage

        results["coverage"] = coverage_result

    except Exception as e:
        log.error(f"Error running coverage: {e}")
        results["coverage"] = {"success": False, "error": str(e)}

    return results
