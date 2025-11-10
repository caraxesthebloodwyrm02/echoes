#!/usr/bin/env python3
"""
Verify that critical security tooling meets minimum version requirements.
This prevents accidental downgrades of security dependencies in PRs.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Tuple, Optional


# Minimum required versions for critical security tools
SECURITY_REQUIREMENTS = {
    "pip-audit": "2.7.3",
    "safety": "3.2.4",
    "cyclonedx-bom": "4.3.5",
    "bandit": "1.7.5",
    "pytest-socket": "0.6.0",
}


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string into tuple of integers for comparison."""
    # Remove any pre-release markers and extract version numbers
    version_match = re.search(r'(\d+(?:\.\d+)*)', version_str)
    if not version_match:
        return (0, 0, 0)

    version_parts = version_match.group(1).split('.')
    return tuple(int(part) for part in version_parts)


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    Returns: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
    """
    v1_parts = parse_version(version1)
    v2_parts = parse_version(version2)

    # Pad with zeros to make same length
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts = v1_parts + (0,) * (max_len - len(v1_parts))
    v2_parts = v2_parts + (0,) * (max_len - len(v2_parts))

    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
    return 0


def extract_package_version(requirements_content: str, package_name: str) -> Optional[str]:
    """Extract version for a specific package from requirements content."""
    for line in requirements_content.split('\n'):
        line = line.strip()
        if line.startswith(f'{package_name}>='):
            # Extract version after >=
            version_match = re.search(rf'{re.escape(package_name)}>=(\d+(?:\.\d+)*)', line)
            if version_match:
                return version_match.group(1)
        elif line.startswith(f'{package_name}=='):
            # Extract version after ==
            version_match = re.search(rf'{re.escape(package_name)}==(\d+(?:\.\d+)*)', line)
            if version_match:
                return version_match.group(1)
    return None


def verify_requirements_file(file_path: Path) -> Tuple[bool, Dict[str, str]]:
    """Verify a requirements file against security requirements."""
    if not file_path.exists():
        return True, {}  # File doesn't exist, no violation

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False, {"error": str(e)}

    violations = {}

    for package, min_version in SECURITY_REQUIREMENTS.items():
        current_version = extract_package_version(content, package)

        if current_version is None:
            # Package not found in requirements
            continue

        if compare_versions(current_version, min_version) < 0:
            violations[package] = f"{current_version} < {min_version}"

    return len(violations) == 0, violations


def main():
    """Main verification logic."""
    project_root = Path(__file__).parent.parent

    # Check all requirements files
    requirements_files = [
        project_root / "requirements.txt",
        project_root / "requirements-security.txt",
        project_root / "requirements-dev.txt",
    ]

    all_passed = True
    all_violations = {}

    for req_file in requirements_files:
        passed, violations = verify_requirements_file(req_file)

        if not passed:
            all_passed = False
            if "error" in violations:
                print(f"❌ Error checking {req_file.name}: {violations['error']}")
            else:
                print(f"❌ Security version violations in {req_file.name}:")
                for package, issue in violations.items():
                    print(f"   - {package}: {issue}")
                    all_violations[f"{req_file.name}:{package}"] = issue

    if all_passed:
        print("✅ All security tooling versions meet requirements")
        return 0
    else:
        print("\n🔒 Security tooling version requirements:")
        for package, min_version in SECURITY_REQUIREMENTS.items():
            print(f"   - {package}: >= {min_version}")

        print("\n❌ PR blocked: Security tooling downgrades detected")
        print("   Update the versions in requirements files to proceed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
