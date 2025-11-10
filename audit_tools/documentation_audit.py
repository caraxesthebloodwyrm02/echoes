"""
Documentation Audit Tool for Echoes Project
Inventories all documentation, assesses quality, and plans consolidation.
"""

import json
import re
from pathlib import Path


class DocumentationAuditor:
    """Comprehensive documentation auditor"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs: list[Path] = []
        self.doc_categories: dict[str, list[dict]] = {
            "readme": [],
            "api_docs": [],
            "implementation_reports": [],
            "guides": [],
            "tutorials": [],
            "changelog": [],
            "other": [],
        }
        self.duplicates: list[dict] = []
        self.outdated_docs: list[dict] = []
        self.missing_docs: list[str] = []
        self.code_docs: dict = {}

    def find_documentation_files(self):
        """Find all documentation files"""
        print("Finding documentation files...")

        # Find all markdown files
        for md_file in self.project_root.rglob("*.md"):
            if any(
                exclude in md_file.parts
                for exclude in ["venv", "__pycache__", ".git", "node_modules"]
            ):
                continue
            self.docs.append(md_file)

        # Find RST files
        for rst_file in self.project_root.rglob("*.rst"):
            if any(
                exclude in rst_file.parts
                for exclude in ["venv", "__pycache__", ".git", "node_modules"]
            ):
                continue
            self.docs.append(rst_file)

        # Find TXT documentation
        for txt_file in self.project_root.rglob("*.txt"):
            if any(
                exclude in txt_file.parts
                for exclude in ["venv", "__pycache__", ".git", "node_modules"]
            ):
                continue
            # Filter to likely documentation files
            if any(
                keyword in txt_file.name.lower()
                for keyword in [
                    "readme",
                    "license",
                    "changelog",
                    "contributing",
                    "docs",
                ]
            ):
                self.docs.append(txt_file)

        print(f"Found {len(self.docs)} documentation files")

    def categorize_documentation(self):
        """Categorize documentation files"""
        print("Categorizing documentation...")

        for doc_file in self.docs:
            rel_path = str(doc_file.relative_to(self.project_root))
            name_lower = doc_file.name.lower()

            doc_info = {
                "path": rel_path,
                "name": doc_file.name,
                "size": doc_file.stat().st_size,
                "directory": str(doc_file.parent.relative_to(self.project_root)),
            }

            # Categorize
            if name_lower == "readme.md" or "readme" in name_lower:
                self.doc_categories["readme"].append(doc_info)
            elif "api" in name_lower or "endpoint" in name_lower:
                self.doc_categories["api_docs"].append(doc_info)
            elif any(
                keyword in name_lower
                for keyword in ["implementation", "report", "summary", "complete"]
            ):
                self.doc_categories["implementation_reports"].append(doc_info)
            elif any(
                keyword in name_lower
                for keyword in ["guide", "howto", "tutorial", "walkthrough"]
            ):
                self.doc_categories["guides"].append(doc_info)
            elif "changelog" in name_lower:
                self.doc_categories["changelog"].append(doc_info)
            else:
                self.doc_categories["other"].append(doc_info)

    def find_duplicates(self):
        """Find duplicate or similar documentation"""
        print("Finding duplicate documentation...")

        # Group by similar names
        name_groups: dict[str, list[dict]] = {}

        for category, docs in self.doc_categories.items():
            for doc in docs:
                # Normalize name (remove common prefixes/suffixes)
                normalized = doc["name"].lower()
                normalized = re.sub(
                    r"^(readme|docs?|guide|tutorial|manual)[_-]?", "", normalized
                )
                normalized = re.sub(
                    r"[_-](readme|docs?|guide|tutorial|manual)$", "", normalized
                )
                normalized = re.sub(r"[_-]+", "_", normalized)

                if normalized not in name_groups:
                    name_groups[normalized] = []
                name_groups[normalized].append({**doc, "category": category})

        # Find groups with multiple files
        for normalized_name, group in name_groups.items():
            if len(group) > 1:
                self.duplicates.append(
                    {
                        "normalized_name": normalized_name,
                        "files": group,
                        "count": len(group),
                    }
                )

    def analyze_code_documentation(self):
        """Analyze code documentation (docstrings)"""
        print("Analyzing code documentation...")

        python_files = list(self.project_root.rglob("*.py"))
        # Exclude venv and cache
        python_files = [
            f
            for f in python_files
            if "venv" not in f.parts and "__pycache__" not in f.parts
        ]

        stats = {
            "total_files": len(python_files),
            "files_with_docstrings": 0,
            "files_without_docstrings": 0,
            "modules_without_docstrings": [],
            "functions_without_docstrings": 0,
            "classes_without_docstrings": 0,
        }

        for py_file in python_files[:100]:  # Sample first 100 files
            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                rel_path = str(py_file.relative_to(self.project_root))

                # Check for module docstring
                has_module_docstring = content.strip().startswith(
                    '"""'
                ) or content.strip().startswith("'''")

                # Count functions and classes
                functions = re.findall(r"def\s+(\w+)", content)
                classes = re.findall(r"class\s+(\w+)", content)

                # Count functions with docstrings
                funcs_with_docs = len(
                    re.findall(
                        r'def\s+\w+[^:]*:\s*\n\s*"""[^"]*"""', content, re.MULTILINE
                    )
                )

                if has_module_docstring:
                    stats["files_with_docstrings"] += 1
                else:
                    stats["files_without_docstrings"] += 1
                    if (
                        py_file.name == "__init__.py"
                        or "core" in rel_path.lower()
                        or "echoes" in rel_path.lower()
                    ):
                        stats["modules_without_docstrings"].append(rel_path)

                stats["functions_without_docstrings"] += (
                    len(functions) - funcs_with_docs
                )
                stats["classes_without_docstrings"] += len(classes)

            except Exception:
                pass

        self.code_docs = stats

    def check_missing_documentation(self):
        """Check for missing documentation"""
        print("Checking for missing documentation...")

        # Expected documentation files
        expected_docs = {
            "README.md": "Main project readme",
            "CHANGELOG.md": "Change log",
            "CONTRIBUTING.md": "Contribution guidelines",
            "LICENSE": "License file",
            "SECURITY.md": "Security policy",
            "docs/API.md": "API documentation",
            "docs/ARCHITECTURE.md": "Architecture documentation",
        }

        for doc_path, description in expected_docs.items():
            full_path = self.project_root / doc_path
            if not full_path.exists():
                self.missing_docs.append(
                    {
                        "file": doc_path,
                        "description": description,
                        "priority": "HIGH" if "README" in doc_path else "MEDIUM",
                    }
                )

    def assess_documentation_quality(self):
        """Assess documentation quality"""
        print("Assessing documentation quality...")

        quality_issues = []

        for doc_file in self.docs[:50]:  # Sample first 50
            try:
                with open(doc_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                rel_path = str(doc_file.relative_to(self.project_root))
                issues = []

                # Check file size
                if len(content) < 100:
                    issues.append("Very short (may be placeholder)")

                # Check for placeholder text
                placeholder_patterns = [
                    r"TODO",
                    r"FIXME",
                    r"\[.*placeholder.*\]",
                    r"\[.*TBD.*\]",
                    r"\[.*coming soon.*\]",
                ]
                for pattern in placeholder_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append(f"Contains placeholder text: {pattern}")
                        break

                # Check for broken links (simple check)
                markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
                for link_text, link_url in markdown_links:
                    if link_url.startswith("http"):
                        # External link - can't verify
                        pass
                    elif not link_url.startswith("#"):
                        # Relative link - check if file exists
                        link_path = (doc_file.parent / link_url).resolve()
                        if not link_path.exists():
                            issues.append(f"Broken link: {link_url}")

                # Check for empty sections
                if re.search(r"^#+\s+\w+\s*\n\s*\n\s*\n", content, re.MULTILINE):
                    issues.append("Contains empty sections")

                if issues:
                    quality_issues.append({"file": rel_path, "issues": issues})

            except Exception:
                pass

        return quality_issues

    def generate_report(self) -> dict:
        """Generate documentation audit report"""
        print("\nGenerating documentation report...")

        quality_issues = self.assess_documentation_quality()

        total_docs = len(self.docs)

        report = {
            "summary": {
                "total_documentation_files": total_docs,
                "readme_files": len(self.doc_categories["readme"]),
                "api_docs": len(self.doc_categories["api_docs"]),
                "implementation_reports": len(
                    self.doc_categories["implementation_reports"]
                ),
                "guides": len(self.doc_categories["guides"]),
                "duplicate_groups": len(self.duplicates),
                "missing_docs": len(self.missing_docs),
                "files_with_quality_issues": len(quality_issues),
                "code_documentation_stats": self.code_docs,
            },
            "categories": self.doc_categories,
            "duplicates": self.duplicates[:20],  # Limit to first 20
            "missing_documentation": self.missing_docs,
            "quality_issues": quality_issues[:30],  # Limit to first 30
            "code_documentation": self.code_docs,
            "recommendations": self.generate_recommendations(),
        }

        return report

    def generate_recommendations(self) -> list[dict]:
        """Generate recommendations"""
        recommendations = []

        if len(self.doc_categories["implementation_reports"]) > 20:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Organization",
                    "issue": f'{len(self.doc_categories["implementation_reports"])} implementation reports found',
                    "recommendation": "Consolidate implementation reports into a single docs/ directory or archive old ones",
                }
            )

        if len(self.duplicates) > 10:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Duplicates",
                    "issue": f"{len(self.duplicates)} duplicate documentation groups found",
                    "recommendation": "Review and consolidate duplicate documentation files. Keep the most current version.",
                }
            )

        if len(self.missing_docs) > 0:
            high_priority_missing = [
                d for d in self.missing_docs if d.get("priority") == "HIGH"
            ]
            if high_priority_missing:
                recommendations.append(
                    {
                        "priority": "HIGH",
                        "category": "Missing Documentation",
                        "issue": f"{len(high_priority_missing)} high-priority documentation files missing",
                        "recommendation": "Create missing essential documentation files (README, CONTRIBUTING, etc.)",
                    }
                )

        code_docs = self.code_docs.get("files_without_docstrings", 0)
        total_files = self.code_docs.get("total_files", 1)
        doc_coverage = (
            (total_files - code_docs) / total_files * 100 if total_files > 0 else 0
        )

        if doc_coverage < 80:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Code Documentation",
                    "issue": f"Code documentation coverage: {doc_coverage:.1f}%",
                    "recommendation": "Add docstrings to modules, classes, and functions. Aim for 80%+ coverage.",
                }
            )

        return recommendations


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    auditor = DocumentationAuditor(str(project_root))

    print("=" * 60)
    print("Echoes Project - Documentation Audit")
    print("=" * 60)

    auditor.find_documentation_files()
    auditor.categorize_documentation()
    auditor.find_duplicates()
    auditor.analyze_code_documentation()
    auditor.check_missing_documentation()

    report = auditor.generate_report()

    # Save report
    output_file = project_root / "audit_results" / "documentation_audit_report.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to: {output_file}")
    print("\nSummary:")
    print(f"  Total docs: {report['summary']['total_documentation_files']}")
    print(f"  README files: {report['summary']['readme_files']}")
    print(f"  Implementation reports: {report['summary']['implementation_reports']}")
    print(f"  Duplicate groups: {report['summary']['duplicate_groups']}")
    print(f"  Missing docs: {report['summary']['missing_docs']}")
    print(f"  Quality issues: {report['summary']['files_with_quality_issues']}")
    print(f"\nRecommendations: {len(report['recommendations'])}")
    for rec in report["recommendations"]:
        print(f"  [{rec['priority']}] {rec['category']}: {rec['issue']}")


if __name__ == "__main__":
    main()
