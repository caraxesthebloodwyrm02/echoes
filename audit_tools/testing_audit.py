"""
Testing Coverage & Quality Audit Tool for Echoes Project
Analyzes test coverage, test structure, and CI/CD integration.
"""

import json
import re
import subprocess
from pathlib import Path


class TestingAuditor:
    """Comprehensive testing auditor"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_files: list[Path] = []
        self.test_structure: dict = {}
        self.coverage_data: dict = {}
        self.ci_configs: list[Path] = []
        self.issues: list[dict] = []

    def find_test_files(self):
        """Find all test files"""
        print("Finding test files...")

        test_patterns = ["test_*.py", "*_test.py", "tests/*.py"]

        for pattern in test_patterns:
            if "*" in pattern:
                # Glob pattern
                for test_file in self.project_root.rglob(pattern):
                    if "__pycache__" not in test_file.parts:
                        self.test_files.append(test_file)
            else:
                # Directory pattern
                test_dir = self.project_root / pattern.replace("/*.py", "")
                if test_dir.exists():
                    for test_file in test_dir.rglob("*.py"):
                        if "__pycache__" not in test_file.parts:
                            self.test_files.append(test_file)

        # Remove duplicates
        self.test_files = list(set(self.test_files))
        print(f"Found {len(self.test_files)} test files")

    def analyze_test_structure(self):
        """Analyze test file structure"""
        print("Analyzing test structure...")

        test_metrics = {
            "total_tests": 0,
            "test_classes": 0,
            "test_functions": 0,
            "fixtures": 0,
            "mock_usage": 0,
            "integration_tests": 0,
            "unit_tests": 0,
        }

        test_categories = {"unit": [], "integration": [], "e2e": [], "other": []}

        for test_file in self.test_files:
            try:
                with open(test_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                rel_path = str(test_file.relative_to(self.project_root))

                # Count test functions
                test_funcs = len(re.findall(r"def\s+test_\w+", content))
                test_metrics["test_functions"] += test_funcs
                test_metrics["total_tests"] += test_funcs

                # Count test classes
                test_classes = len(re.findall(r"class\s+Test\w+", content))
                test_metrics["test_classes"] += test_classes

                # Count fixtures
                fixtures = len(re.findall(r"@pytest\.fixture|@fixture", content))
                test_metrics["fixtures"] += fixtures

                # Count mock usage
                mocks = len(re.findall(r"@patch|Mock\(|mock\.", content))
                test_metrics["mock_usage"] += mocks

                # Categorize tests
                content_lower = content.lower()
                if "integration" in content_lower or "e2e" in content_lower:
                    test_categories["integration"].append(rel_path)
                    test_metrics["integration_tests"] += test_funcs
                elif "unit" in content_lower:
                    test_categories["unit"].append(rel_path)
                    test_metrics["unit_tests"] += test_funcs
                elif "e2e" in content_lower or "end.to.end" in content_lower:
                    test_categories["e2e"].append(rel_path)
                else:
                    test_categories["other"].append(rel_path)

            except Exception as e:
                self.issues.append(
                    {
                        "type": "test_parse_error",
                        "file": str(test_file.relative_to(self.project_root)),
                        "error": str(e)[:100],
                    }
                )

        self.test_structure = {
            "metrics": test_metrics,
            "categories": test_categories,
            "test_files_count": len(self.test_files),
        }

    def check_test_coverage(self):
        """Check test coverage using pytest-cov"""
        print("Checking test coverage...")

        # Try to run coverage check
        try:
            # Check if pytest is available
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.project_root),
            )

            if result.returncode == 0:
                # Try to run coverage
                coverage_result = subprocess.run(
                    [
                        "python",
                        "-m",
                        "pytest",
                        "--cov=echoes",
                        "--cov=core_modules",
                        "--cov=app",
                        "--cov-report=json",
                        "--cov-report=term",
                        "tests/",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self.project_root),
                )

                # Try to parse coverage JSON
                coverage_json = self.project_root / ".coverage.json"
                if coverage_json.exists():
                    try:
                        with open(coverage_json) as f:
                            self.coverage_data = json.load(f)
                    except:
                        pass

                # Parse coverage from terminal output
                if coverage_result.stdout:
                    # Extract coverage percentage
                    coverage_match = re.search(
                        r"TOTAL\s+(\d+)\s+\d+\s+(\d+)%", coverage_result.stdout
                    )
                    if coverage_match:
                        self.coverage_data["total_lines"] = int(coverage_match.group(1))
                        self.coverage_data["coverage_percent"] = int(
                            coverage_match.group(2)
                        )
            else:
                self.coverage_data["status"] = "pytest_not_available"
                self.coverage_data["message"] = "pytest not found or not configured"

        except subprocess.TimeoutExpired:
            self.coverage_data["status"] = "timeout"
            self.coverage_data["message"] = "Coverage check timed out"
        except FileNotFoundError:
            self.coverage_data["status"] = "python_not_found"
            self.coverage_data["message"] = "Python not found in PATH"
        except Exception as e:
            self.coverage_data["status"] = "error"
            self.coverage_data["message"] = str(e)[:200]

    def check_ci_cd_config(self):
        """Check CI/CD configuration"""
        print("Checking CI/CD configuration...")

        ci_patterns = {
            ".github/workflows/*.yml": "GitHub Actions",
            ".github/workflows/*.yaml": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            ".circleci/config.yml": "CircleCI",
            "Jenkinsfile": "Jenkins",
            ".travis.yml": "Travis CI",
            "azure-pipelines.yml": "Azure Pipelines",
        }

        for pattern, ci_type in ci_patterns.items():
            if "*" in pattern:
                pattern.split("*")[0]
                for ci_file in self.project_root.rglob(pattern.replace("*", "*")):
                    self.ci_configs.append((ci_file, ci_type))
            else:
                ci_file = self.project_root / pattern
                if ci_file.exists():
                    self.ci_configs.append((ci_file, ci_type))

        # Check for pre-commit hooks
        precommit_file = self.project_root / ".pre-commit-config.yaml"
        if precommit_file.exists():
            self.ci_configs.append((precommit_file, "Pre-commit hooks"))

        # Check pytest.ini
        pytest_ini = self.project_root / "pytest.ini"
        if pytest_ini.exists():
            self.ci_configs.append((pytest_ini, "Pytest configuration"))

    def analyze_test_quality(self):
        """Analyze test quality metrics"""
        print("Analyzing test quality...")

        quality_issues = []

        # Check for common test quality issues
        for test_file in self.test_files:
            try:
                with open(test_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                rel_path = str(test_file.relative_to(self.project_root))
                file_issues = []

                # Check for long tests (more than 50 lines)
                if len(lines) > 50:
                    test_funcs = re.findall(r"def\s+(test_\w+)", content)
                    for func in test_funcs:
                        # Find function definition
                        func_match = re.search(rf"def\s+{func}[^:]*:", content)
                        if func_match:
                            # Find next function or end of file
                            next_func = re.search(
                                rf"def\s+(?!{func})", content[func_match.end() :]
                            )
                            func_end = func_match.end() + (
                                next_func.start()
                                if next_func
                                else len(content) - func_match.end()
                            )
                            func_lines = content[
                                func_match.start() : func_match.start() + func_end
                            ].count("\n")
                            if func_lines > 50:
                                file_issues.append(
                                    f"Long test function: {func} ({func_lines} lines)"
                                )

                # Check for missing docstrings
                test_funcs = re.findall(r"def\s+(test_\w+)", content)
                for func in test_funcs:
                    func_match = re.search(
                        rf'def\s+{func}[^:]*:\s*\n\s*"""[^"]*"""', content
                    )
                    if not func_match:
                        # Check if there's any docstring
                        func_def = re.search(rf"def\s+{func}[^:]*:", content)
                        if func_def:
                            next_line = content[func_def.end() : func_def.end() + 100]
                            if '"""' not in next_line and "'''" not in next_line:
                                file_issues.append(f"Missing docstring: {func}")

                # Check for hardcoded values
                if re.search(r'test[_-]?\w+\s*=\s*["\'][^"\']{20,}["\']', content):
                    file_issues.append("Possible hardcoded test data")

                # Check for proper assertions
                assertions = len(re.findall(r"assert\s+", content))
                if assertions == 0 and test_funcs:
                    file_issues.append("No assertions found in test file")

                if file_issues:
                    quality_issues.append({"file": rel_path, "issues": file_issues})

            except Exception:
                pass

        self.test_structure["quality_issues"] = quality_issues

    def check_test_organization(self):
        """Check test organization"""
        print("Checking test organization...")

        # Check if tests match source structure
        source_modules = {
            "echoes": list((self.project_root / "echoes").rglob("*.py"))
            if (self.project_root / "echoes").exists()
            else [],
            "core_modules": list((self.project_root / "core_modules").rglob("*.py"))
            if (self.project_root / "core_modules").exists()
            else [],
            "app": list((self.project_root / "app").rglob("*.py"))
            if (self.project_root / "app").exists()
            else [],
        }

        # Check for orphaned tests (tests without corresponding source)
        for test_file in self.test_files:
            test_name = test_file.stem.replace("test_", "").replace("_test", "")
            # Try to find corresponding source file
            found = False
            for module_name, source_files in source_modules.items():
                for source_file in source_files:
                    if test_name in source_file.name or source_file.stem in test_name:
                        found = True
                        break
                if found:
                    break

            # This is just a warning, not necessarily an issue
            # Some tests may test integration, not individual files

        self.test_structure["organization_notes"] = {
            "source_modules_checked": len(
                [f for files in source_modules.values() for f in files]
            ),
            "test_files": len(self.test_files),
        }

    def generate_report(self) -> dict:
        """Generate testing audit report"""
        print("\nGenerating testing report...")

        coverage_percent = self.coverage_data.get("coverage_percent", 0)

        report = {
            "summary": {
                "test_files_count": len(self.test_files),
                "total_tests": self.test_structure.get("metrics", {}).get(
                    "total_tests", 0
                ),
                "test_classes": self.test_structure.get("metrics", {}).get(
                    "test_classes", 0
                ),
                "test_functions": self.test_structure.get("metrics", {}).get(
                    "test_functions", 0
                ),
                "coverage_percent": coverage_percent,
                "ci_cd_configs": len(self.ci_configs),
                "quality_issues": len(self.test_structure.get("quality_issues", [])),
            },
            "test_structure": self.test_structure,
            "coverage": self.coverage_data,
            "ci_cd": {
                "configs_found": [
                    {"file": str(f.relative_to(self.project_root)), "type": t}
                    for f, t in self.ci_configs
                ]
            },
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> list[dict]:
        """Generate recommendations"""
        recommendations = []

        coverage_percent = self.coverage_data.get("coverage_percent", 0)
        if coverage_percent < 80:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Coverage",
                    "issue": f"Test coverage is {coverage_percent}% (target: 80%+)",
                    "recommendation": "Increase test coverage for core modules. Focus on critical paths and edge cases.",
                }
            )

        total_tests = self.test_structure.get("metrics", {}).get("total_tests", 0)
        test_files = len(self.test_files)

        if test_files == 0:
            recommendations.append(
                {
                    "priority": "CRITICAL",
                    "category": "Testing",
                    "issue": "No test files found",
                    "recommendation": "Create comprehensive test suite starting with critical modules",
                }
            )
        elif total_tests == 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Testing",
                    "issue": "Test files found but no test functions detected",
                    "recommendation": "Review test file structure and ensure tests are properly defined",
                }
            )

        quality_issues = len(self.test_structure.get("quality_issues", []))
        if quality_issues > 10:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Test Quality",
                    "issue": f"{quality_issues} test files have quality issues",
                    "recommendation": "Refactor tests for better structure, add docstrings, and reduce complexity",
                }
            )

        if len(self.ci_configs) == 0:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "CI/CD",
                    "issue": "No CI/CD configuration found",
                    "recommendation": "Set up CI/CD pipeline with automated testing. Consider GitHub Actions, GitLab CI, or similar.",
                }
            )

        integration_tests = self.test_structure.get("metrics", {}).get(
            "integration_tests", 0
        )
        unit_tests = self.test_structure.get("metrics", {}).get("unit_tests", 0)

        if integration_tests == 0 and unit_tests == 0 and total_tests > 0:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Test Types",
                    "issue": "Test categorization not clear",
                    "recommendation": "Use markers or naming conventions to distinguish unit, integration, and e2e tests",
                }
            )

        return recommendations


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    auditor = TestingAuditor(str(project_root))

    print("=" * 60)
    print("Echoes Project - Testing Coverage & Quality Audit")
    print("=" * 60)

    auditor.find_test_files()
    auditor.analyze_test_structure()
    auditor.check_test_coverage()
    auditor.check_ci_cd_config()
    auditor.analyze_test_quality()
    auditor.check_test_organization()

    report = auditor.generate_report()

    # Save report
    output_file = project_root / "audit_results" / "testing_audit_report.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {output_file}")
    print("\nSummary:")
    print(f"  Test files: {report['summary']['test_files_count']}")
    print(f"  Total tests: {report['summary']['total_tests']}")
    print(f"  Coverage: {report['summary']['coverage_percent']}%")
    print(f"  CI/CD configs: {report['summary']['ci_cd_configs']}")
    print(f"  Quality issues: {report['summary']['quality_issues']}")
    print(f"\nRecommendations: {len(report['recommendations'])}")
    for rec in report["recommendations"]:
        print(f"  [{rec['priority']}] {rec['category']}: {rec['issue']}")


if __name__ == "__main__":
    main()
