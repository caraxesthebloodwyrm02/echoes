"""
Dependency Resolution Tool
Analyzes conflicts and creates consolidated requirements file based on pyproject.toml
"""

import json
from pathlib import Path


def parse_version_constraint(constraint: str) -> tuple[str, str]:
    """Parse version constraint and return operator and version"""
    if ">=" in constraint:
        return (">=", constraint.split(">=")[1].strip())
    elif "==" in constraint:
        return ("==", constraint.split("==")[1].strip())
    elif "~=" in constraint:
        return ("~=", constraint.split("~=")[1].strip())
    elif ">" in constraint:
        return (">", constraint.split(">")[1].strip())
    elif "<" in constraint:
        return ("<", constraint.split("<")[1].strip())
    else:
        return ("any", constraint.strip())


def resolve_version_conflict(package: str, versions: list[str]) -> str:
    """Resolve version conflict by choosing most restrictive constraint"""
    if not versions:
        return ""

    # Remove duplicates and clean
    versions = [v.strip() for v in versions if v.strip()]

    # If only one unique version, use it
    unique_versions = list(set(versions))
    if len(unique_versions) == 1:
        return unique_versions[0]

    # Parse constraints
    constraints = []
    for v in unique_versions:
        op, ver = parse_version_constraint(v)
        if op != "any":
            constraints.append((op, ver))

    # Strategy: Use >= with highest minimum version
    # Or == if all are exact versions
    exact_versions = [ver for op, ver in constraints if op == "=="]
    min_versions = [ver for op, ver in constraints if op == ">="]

    if exact_versions:
        # If multiple exact versions conflict, use the latest
        # This is a heuristic - needs manual review
        return f"=={exact_versions[-1]}"
    elif min_versions:
        # Use highest minimum
        return f">={max(min_versions)}"
    else:
        # Fallback: use first constraint
        return versions[0]


def main():
    """Main dependency resolution"""
    project_root = Path(__file__).parent.parent

    # Load dependency audit report
    audit_file = project_root / "audit_results" / "dependency_audit_report.json"
    if not audit_file.exists():
        print("❌ Dependency audit report not found. Run dependency_audit.py first.")
        return

    with open(audit_file) as f:
        audit_data = json.load(f)

    # Get conflicts
    conflicts = audit_data.get("conflicts", [])
    dependencies = audit_data.get("dependencies", {})

    print("=" * 60)
    print("Dependency Resolution Analysis")
    print("=" * 60)
    print(f"\nTotal conflicts: {len(conflicts)}")
    print(f"Total dependencies: {len(dependencies)}")

    # Resolve conflicts
    resolutions = {}
    for conflict in conflicts[:20]:  # Limit to first 20 for review
        pkg = conflict["package"]
        versions = conflict["versions"]
        resolved = resolve_version_conflict(pkg, versions)
        resolutions[pkg] = resolved
        print(f"\n{pkg}:")
        print(f"  Conflicts: {versions}")
        print(f"  Resolved: {resolved}")

    # Generate recommendation
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    print("\nUse pyproject.toml as single source of truth.")
    print("Create requirements.txt from pyproject.toml:")
    print("  pip-compile pyproject.toml --output-file=requirements.txt")
    print("\nFor production, use:")
    print("  pip-compile pyproject.toml --output-file=requirements-lock.txt")

    # Save resolutions
    output_file = project_root / "audit_results" / "dependency_resolutions.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "resolutions": resolutions,
                "total_conflicts": len(conflicts),
                "resolved": len(resolutions),
            },
            f,
            indent=2,
        )

    print(f"\n[OK] Resolutions saved to: {output_file}")


if __name__ == "__main__":
    main()
