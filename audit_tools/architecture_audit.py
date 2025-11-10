"""
Architecture and Code Quality Audit Tool for Echoes Project
Analyzes module structure, dependencies, circular imports, and code quality metrics.
"""

import ast
import json
from collections import defaultdict
from pathlib import Path


class ArchitectureAuditor:
    """Comprehensive architecture and code quality auditor"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.modules: dict[str, set[str]] = {}  # module -> imports
        self.dependents: dict[str, set[str]] = {}  # module -> modules that import it
        self.file_sizes: dict[str, int] = {}
        self.circular_imports: list[list[str]] = []
        self.config_files: list[str] = []
        self.issues: list[dict] = []

    def find_python_files(self, directory: Path) -> list[Path]:
        """Find all Python files in the directory"""
        python_files = []
        for path in directory.rglob("*.py"):
            # Skip virtual environments and cache
            if any(
                skip in path.parts
                for skip in ["venv", "__pycache__", ".git", "node_modules"]
            ):
                continue
            python_files.append(path)
        return python_files

    def extract_imports(self, file_path: Path) -> set[str]:
        """Extract import statements from a Python file"""
        imports = set()
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
        except Exception as e:
            self.issues.append(
                {
                    "type": "parse_error",
                    "file": str(file_path.relative_to(self.project_root)),
                    "error": str(e),
                }
            )

        return imports

    def get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name"""
        rel_path = file_path.relative_to(self.project_root)
        parts = rel_path.parts[:-1] if rel_path.suffix == ".py" else rel_path.parts
        return ".".join(parts + (rel_path.stem,))

    def analyze_dependencies(self):
        """Analyze module dependencies and detect circular imports"""
        print("Analyzing module dependencies...")

        python_files = self.find_python_files(self.project_root)
        print(f"Found {len(python_files)} Python files")

        # Build dependency graph
        for file_path in python_files:
            rel_path = file_path.relative_to(self.project_root)
            module_key = str(rel_path)
            imports = self.extract_imports(file_path)
            self.modules[module_key] = imports

            # Track file size
            self.file_sizes[module_key] = file_path.stat().st_size

            # Build reverse dependency graph
            for imp in imports:
                if imp not in self.dependents:
                    self.dependents[imp] = set()
                self.dependents[imp].add(module_key)

        # Detect circular imports
        self.detect_circular_imports()

    def detect_circular_imports(self):
        """Detect circular import dependencies"""
        print("Detecting circular imports...")

        # Build graph where nodes are modules and edges are imports
        graph: dict[str, set[str]] = defaultdict(set)

        for module, imports in self.modules.items():
            for imp in imports:
                # Check if import is from this project
                imp_module = self.find_module_file(imp)
                if imp_module:
                    graph[module].add(imp_module)

        # DFS to detect cycles
        visited = set()
        rec_stack = set()
        cycle_path = []

        def dfs(node: str, path: list[str]):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                self.circular_imports.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor in self.modules:  # Only check internal modules
                    dfs(neighbor, path.copy())

            rec_stack.remove(node)

        for module in self.modules.keys():
            if module not in visited:
                dfs(module, [])

    def find_module_file(self, module_name: str) -> str | None:
        """Find file path for a module name"""
        # Try different patterns
        patterns = [
            f"{module_name}.py",
            f"{module_name}/__init__.py",
            f"core_modules/{module_name}.py",
            f"echoes/{module_name}.py",
            f"app/{module_name}.py",
        ]

        for pattern in patterns:
            path = self.project_root / pattern
            if path.exists():
                return str(path.relative_to(self.project_root))

        return None

    def analyze_config_files(self):
        """Identify and analyze configuration files"""
        print("Analyzing configuration files...")

        config_patterns = ["config.py", "settings.py", ".env", "config.json"]
        config_locations = ["api", "echoes", "ATLAS/echoes", "misc/Accounting"]

        for location in config_locations:
            loc_path = self.project_root / location
            if loc_path.exists():
                for pattern in config_patterns:
                    for config_file in loc_path.rglob(pattern):
                        self.config_files.append(
                            str(config_file.relative_to(self.project_root))
                        )

        # Also check root level
        for pattern in config_patterns:
            if pattern.startswith("."):
                for env_file in self.project_root.glob(pattern):
                    if (
                        "example" not in env_file.name
                        and "template" not in env_file.name
                    ):
                        self.config_files.append(
                            str(env_file.relative_to(self.project_root))
                        )

    def analyze_code_quality(self):
        """Basic code quality checks"""
        print("Analyzing code quality...")

        python_files = self.find_python_files(self.project_root)

        for file_path in python_files:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                rel_path = str(file_path.relative_to(self.project_root))

                # Check for common issues
                issues_found = []

                # Check line length
                long_lines = [
                    i + 1 for i, line in enumerate(lines) if len(line.rstrip()) > 120
                ]
                if long_lines:
                    issues_found.append(
                        {
                            "type": "long_lines",
                            "count": len(long_lines),
                            "lines": long_lines[:10],  # First 10
                        }
                    )

                # Check for TODO/FIXME
                todos = []
                for i, line in enumerate(lines):
                    if any(
                        keyword in line.upper()
                        for keyword in ["TODO", "FIXME", "XXX", "HACK"]
                    ):
                        todos.append((i + 1, line.strip()[:80]))

                if todos:
                    issues_found.append(
                        {
                            "type": "todos",
                            "count": len(todos),
                            "items": todos[:5],  # First 5
                        }
                    )

                # Check file size (very large files might need splitting)
                file_size_kb = file_path.stat().st_size / 1024
                if file_size_kb > 100:  # > 100KB
                    issues_found.append(
                        {"type": "large_file", "size_kb": round(file_size_kb, 2)}
                    )

                if issues_found:
                    self.issues.append({"file": rel_path, "issues": issues_found})

            except Exception:
                pass  # Already logged in extract_imports

    def generate_report(self) -> dict:
        """Generate comprehensive audit report"""
        print("\nGenerating audit report...")

        # Analyze module organization
        core_modules = [m for m in self.modules.keys() if "core_modules" in m]
        echoes_modules = [m for m in self.modules.keys() if m.startswith("echoes/")]
        app_modules = [m for m in self.modules.keys() if m.startswith("app/")]

        report = {
            "summary": {
                "total_python_files": len(self.modules),
                "core_modules_count": len(core_modules),
                "echoes_modules_count": len(echoes_modules),
                "app_modules_count": len(app_modules),
                "config_files_count": len(self.config_files),
                "circular_imports_count": len(self.circular_imports),
                "files_with_issues": len(self.issues),
            },
            "module_organization": {
                "core_modules": sorted(core_modules),
                "echoes_modules": sorted(echoes_modules),
                "app_modules": sorted(app_modules),
            },
            "circular_imports": self.circular_imports,
            "configuration_files": self.config_files,
            "code_quality_issues": self.issues[:50],  # Limit to first 50
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> list[dict]:
        """Generate recommendations based on findings"""
        recommendations = []

        if self.circular_imports:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Architecture",
                    "issue": f"Found {len(self.circular_imports)} circular import cycles",
                    "recommendation": "Refactor modules to break circular dependencies. Consider dependency injection or lazy imports.",
                }
            )

        if len(self.config_files) > 3:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Configuration",
                    "issue": f"Multiple configuration files found: {len(self.config_files)}",
                    "recommendation": "Consolidate configuration into a single source of truth. Use environment variables for environment-specific values.",
                }
            )

        large_files = [
            issue
            for issue in self.issues
            if any(i.get("type") == "large_file" for i in issue.get("issues", []))
        ]
        if large_files:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Code Quality",
                    "issue": f"{len(large_files)} files exceed 100KB",
                    "recommendation": "Consider splitting large files into smaller, focused modules for better maintainability.",
                }
            )

        todos_count = sum(
            1
            for issue in self.issues
            if any(i.get("type") == "todos" for i in issue.get("issues", []))
        )
        if todos_count > 0:
            recommendations.append(
                {
                    "priority": "LOW",
                    "category": "Code Quality",
                    "issue": f"TODO/FIXME comments found in {todos_count} files",
                    "recommendation": "Review and address TODO/FIXME comments or move them to issue tracking system.",
                }
            )

        return recommendations


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    auditor = ArchitectureAuditor(str(project_root))

    print("=" * 60)
    print("Echoes Project - Architecture & Code Quality Audit")
    print("=" * 60)

    auditor.analyze_dependencies()
    auditor.analyze_config_files()
    auditor.analyze_code_quality()

    report = auditor.generate_report()

    # Save report
    output_file = project_root / "audit_results" / "architecture_audit_report.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {output_file}")
    print("\nSummary:")
    print(f"  Total Python files: {report['summary']['total_python_files']}")
    print(f"  Circular imports: {report['summary']['circular_imports_count']}")
    print(f"  Configuration files: {report['summary']['config_files_count']}")
    print(f"  Files with issues: {report['summary']['files_with_issues']}")
    print(f"\nRecommendations: {len(report['recommendations'])}")
    for rec in report["recommendations"]:
        print(f"  [{rec['priority']}] {rec['category']}: {rec['issue']}")


if __name__ == "__main__":
    main()
