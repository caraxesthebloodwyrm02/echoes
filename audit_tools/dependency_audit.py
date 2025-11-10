"""
Dependency Management Audit Tool for Echoes Project
Analyzes requirements, checks conflicts, identifies unused dependencies.
"""

import json
import re
import subprocess
from pathlib import Path


class DependencyAuditor:
    """Comprehensive dependency auditor"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.requirements_files: list[Path] = []
        self.installed_packages: dict[str, str] = {}
        self.dependency_conflicts: list[dict] = []
        self.unused_dependencies: list[str] = []
        self.outdated_packages: list[dict] = []

    def find_requirements_files(self):
        """Find all requirements files"""
        print("Finding requirements files...")

        requirements_patterns = [
            "requirements.txt",
            "requirements*.txt",
            "pyproject.toml",
            "setup.py",
            "Pipfile",
            "poetry.lock",
        ]

        for pattern in requirements_patterns:
            if "*" in pattern:
                for req_file in self.project_root.rglob(pattern):
                    if "venv" not in req_file.parts:
                        self.requirements_files.append(req_file)
            else:
                req_file = self.project_root / pattern
                if req_file.exists():
                    self.requirements_files.append(req_file)

        print(f"Found {len(self.requirements_files)} requirements files")

    def parse_requirements(self) -> dict[str, dict]:
        """Parse requirements from all files"""
        print("Parsing requirements...")

        all_dependencies: dict[str, dict] = {}

        for req_file in self.requirements_files:
            rel_path = str(req_file.relative_to(self.project_root))

            if req_file.name == "requirements.txt" or req_file.name.startswith(
                "requirements"
            ):
                deps = self.parse_requirements_txt(req_file)
                for dep, version in deps.items():
                    if dep not in all_dependencies:
                        all_dependencies[dep] = {"files": [], "versions": set()}
                    all_dependencies[dep]["files"].append(rel_path)
                    all_dependencies[dep]["versions"].add(version)
            elif req_file.name == "pyproject.toml":
                deps = self.parse_pyproject_toml(req_file)
                for dep, version in deps.items():
                    if dep not in all_dependencies:
                        all_dependencies[dep] = {"files": [], "versions": set()}
                    all_dependencies[dep]["files"].append(rel_path)
                    all_dependencies[dep]["versions"].add(version)
            elif req_file.name == "setup.py":
                deps = self.parse_setup_py(req_file)
                for dep, version in deps.items():
                    if dep not in all_dependencies:
                        all_dependencies[dep] = {"files": [], "versions": set()}
                    all_dependencies[dep]["files"].append(rel_path)
                    all_dependencies[dep]["versions"].add(version)

        # Check for conflicts
        for dep, info in all_dependencies.items():
            if len(info["versions"]) > 1:
                self.dependency_conflicts.append(
                    {
                        "package": dep,
                        "versions": list(info["versions"]),
                        "files": info["files"],
                    }
                )

        return all_dependencies

    def parse_requirements_txt(self, file_path: Path) -> dict[str, str]:
        """Parse requirements.txt file"""
        deps = {}
        try:
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse package and version
                    if ">=" in line:
                        parts = line.split(">=")
                        pkg = parts[0].strip()
                        version = f">={parts[1].strip()}"
                    elif "==" in line:
                        parts = line.split("==")
                        pkg = parts[0].strip()
                        version = f"=={parts[1].strip()}"
                    elif "~=" in line:
                        parts = line.split("~=")
                        pkg = parts[0].strip()
                        version = f"~={parts[1].strip()}"
                    else:
                        pkg = line.split()[0]
                        version = "any"

                    deps[pkg] = version
        except Exception:
            pass

        return deps

    def parse_pyproject_toml(self, file_path: Path) -> dict[str, str]:
        """Parse pyproject.toml for dependencies"""
        deps = {}
        try:
            with open(file_path) as f:
                content = f.read()

                # Simple regex extraction (not perfect but works for common cases)
                dep_section = re.search(
                    r"\[project\]\s+dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL
                )
                if dep_section:
                    dep_lines = dep_section.group(1)
                    for line in dep_lines.split("\n"):
                        line = line.strip().strip('",')
                        if not line or line.startswith("#"):
                            continue

                        # Extract package and version
                        match = re.match(
                            r'["\']?([^>="\']+)["\']?\s*([>~=]+)?\s*([0-9.]+)?', line
                        )
                        if match:
                            pkg = match.group(1).strip()
                            op = match.group(2) if match.group(2) else ""
                            version_str = match.group(3) if match.group(3) else ""
                            version = (
                                f"{op}{version_str}" if op and version_str else "any"
                            )
                            deps[pkg] = version
        except Exception:
            pass

        return deps

    def parse_setup_py(self, file_path: Path) -> dict[str, str]:
        """Parse setup.py for dependencies"""
        deps = {}
        try:
            with open(file_path) as f:
                content = f.read()

                # Look for install_requires
                match = re.search(
                    r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL
                )
                if match:
                    deps_str = match.group(1)
                    for line in deps_str.split("\n"):
                        line = line.strip().strip('",')
                        if not line or line.startswith("#"):
                            continue

                        # Extract package
                        match_dep = re.match(
                            r'["\']?([^>="\']+)["\']?\s*([>~=]+)?\s*([0-9.]+)?', line
                        )
                        if match_dep:
                            pkg = match_dep.group(1).strip()
                            op = match_dep.group(2) if match_dep.group(2) else ""
                            version_str = (
                                match_dep.group(3) if match_dep.group(3) else ""
                            )
                            version = (
                                f"{op}{version_str}" if op and version_str else "any"
                            )
                            deps[pkg] = version
        except Exception:
            pass

        return deps

    def check_installed_packages(self):
        """Check currently installed packages"""
        print("Checking installed packages...")

        try:
            result = subprocess.run(
                ["python", "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.project_root),
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                for pkg in packages:
                    self.installed_packages[pkg["name"].lower()] = pkg["version"]
        except Exception:
            pass

    def identify_unused_dependencies(self, all_dependencies: dict):
        """Identify potentially unused dependencies"""
        print("Identifying unused dependencies...")

        # This is a heuristic - check if package is imported in code
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [
            f
            for f in python_files
            if "venv" not in f.parts and "__pycache__" not in f.parts
        ]

        imports_in_code: set[str] = set()

        # Sample first 200 files to check imports
        for py_file in python_files[:200]:
            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Extract imports
                import_matches = re.findall(
                    r"^import\s+(\w+)|^from\s+(\w+)", content, re.MULTILINE
                )
                for match in import_matches:
                    pkg_name = match[0] or match[1]
                    imports_in_code.add(pkg_name.lower())
            except Exception:
                pass

        # Check dependencies against imports
        for dep_name in all_dependencies.keys():
            # Normalize package name (handle package-name vs package_name)
            normalized = dep_name.lower().replace("-", "_")
            if (
                normalized not in imports_in_code
                and dep_name.lower() not in imports_in_code
            ):
                # Additional check for subpackages
                found = False
                for imp in imports_in_code:
                    if normalized in imp or imp in normalized:
                        found = True
                        break

                if not found:
                    self.unused_dependencies.append(dep_name)

    def check_outdated_packages(self):
        """Check for outdated packages"""
        print("Checking for outdated packages...")

        try:
            result = subprocess.run(
                ["python", "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.project_root),
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                for pkg in packages:
                    self.outdated_packages.append(
                        {
                            "package": pkg["name"],
                            "current": pkg["version"],
                            "latest": pkg.get("latest_version", "unknown"),
                        }
                    )
        except Exception:
            pass

    def generate_report(self) -> dict:
        """Generate dependency audit report"""
        print("\nGenerating dependency report...")

        all_dependencies = self.parse_requirements()
        self.check_installed_packages()
        self.identify_unused_dependencies(all_dependencies)
        self.check_outdated_packages()

        report = {
            "summary": {
                "requirements_files": len(self.requirements_files),
                "total_dependencies": len(all_dependencies),
                "dependency_conflicts": len(self.dependency_conflicts),
                "potentially_unused": len(self.unused_dependencies),
                "outdated_packages": len(self.outdated_packages),
                "installed_packages": len(self.installed_packages),
            },
            "requirements_files": [
                str(f.relative_to(self.project_root)) for f in self.requirements_files
            ],
            "dependencies": {
                k: {"files": v["files"], "versions": list(v["versions"])}
                for k, v in list(all_dependencies.items())[:50]
            },  # Limit to 50
            "conflicts": self.dependency_conflicts,
            "potentially_unused": self.unused_dependencies[:20],  # Limit to 20
            "outdated_packages": self.outdated_packages[:30],  # Limit to 30
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> list[dict]:
        """Generate recommendations"""
        recommendations = []

        if len(self.requirements_files) > 3:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Organization",
                    "issue": f"Multiple requirements files found: {len(self.requirements_files)}",
                    "recommendation": "Consolidate requirements files. Use pyproject.toml as single source of truth, or clearly separate dev/prod requirements.",
                }
            )

        if self.dependency_conflicts:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Conflicts",
                    "issue": f"{len(self.dependency_conflicts)} dependency conflicts found",
                    "recommendation": "Resolve version conflicts by standardizing on single version requirements across all files.",
                }
            )

        if len(self.unused_dependencies) > 5:
            recommendations.append(
                {
                    "priority": "LOW",
                    "category": "Unused Dependencies",
                    "issue": f"{len(self.unused_dependencies)} potentially unused dependencies",
                    "recommendation": "Review and remove unused dependencies to reduce attack surface and installation time.",
                }
            )

        if len(self.outdated_packages) > 10:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Updates",
                    "issue": f"{len(self.outdated_packages)} packages have updates available",
                    "recommendation": "Review and update outdated packages. Test thoroughly after updates. Use dependency security scanner (pip-audit).",
                }
            )

        return recommendations


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    auditor = DependencyAuditor(str(project_root))

    print("=" * 60)
    print("Echoes Project - Dependency Management Audit")
    print("=" * 60)

    auditor.find_requirements_files()
    auditor.check_installed_packages()
    auditor.check_outdated_packages()

    report = auditor.generate_report()

    # Save report
    output_file = project_root / "audit_results" / "dependency_audit_report.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {output_file}")
    print("\nSummary:")
    print(f"  Requirements files: {report['summary']['requirements_files']}")
    print(f"  Total dependencies: {report['summary']['total_dependencies']}")
    print(f"  Conflicts: {report['summary']['dependency_conflicts']}")
    print(f"  Potentially unused: {report['summary']['potentially_unused']}")
    print(f"  Outdated packages: {report['summary']['outdated_packages']}")
    print(f"\nRecommendations: {len(report['recommendations'])}")
    for rec in report["recommendations"]:
        print(f"  [{rec['priority']}] {rec['category']}: {rec['issue']}")


if __name__ == "__main__":
    main()
