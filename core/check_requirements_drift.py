#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Requirements Drift Checker

Scans all requirements/*.txt files and detects version drift/inconsistencies
for packages that appear in multiple files.

Usage:
    python tools/check_requirements_drift.py
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def parse_requirement_line(line: str) -> Tuple[str, str]:
    """Parse a requirement line and return (package_name, version_spec)."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("-r "):
        return None, None

    # Match package==version or package>=version patterns
    match = re.match(r"^([a-zA-Z0-9\-_.]+)([><=~!]+.+)$", line)
    if match:
        return match.group(1).lower(), match.group(2)
    else:
        # Package without version spec
        match = re.match(r"^([a-zA-Z0-9\-_.]+)$", line)
        if match:
            return match.group(1).lower(), ""
    return None, None


def collect_requirements(req_dir: Path) -> Dict[str, List[Tuple[str, str]]]:
    """Collect requirements from all .txt files in the directory."""
    requirements = defaultdict(list)

    for req_file in req_dir.glob("*.txt"):
        with open(req_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                pkg, version = parse_requirement_line(line)
                if pkg:
                    requirements[pkg].append((str(req_file.name), version, line_num))

    return requirements


def check_drift(requirements: Dict[str, List[Tuple[str, str]]]) -> List[Dict]:
    """Check for version drift and return issues."""
    issues = []

    for pkg, locations in requirements.items():
        if len(locations) <= 1:
            continue

        # Group by version spec
        version_groups = defaultdict(list)
        for file_name, version, line_num in locations:
            version_groups[version].append((file_name, line_num))

        if len(version_groups) > 1:
            issue = {
                "package": pkg,
                "versions": dict(version_groups),
                "locations": locations,
            }
            issues.append(issue)

    return issues


def main():
    """Main entry point."""
    req_dir = Path(__file__).parent.parent / "requirements"

    if not req_dir.exists():
        print(f"Error: Requirements directory not found: {req_dir}")
        return 1

    print("🔍 Checking requirements for version drift...\n")

    requirements = collect_requirements(req_dir)
    issues = check_drift(requirements)

    if issues:
        print(f"⚠️  Found {len(issues)} packages with version drift:\n")

        for issue in issues:
            print(f"📦 {issue['package']}:")
            for version, files in issue["versions"].items():
                version_str = f"'{version}'" if version else "no version specified"
                file_list = [f"{f}:{line}" for f, line in files]
                print(f"  {version_str}: {', '.join(file_list)}")
            print()

        print("💡 Consider consolidating these versions in the unified requirements files.")
        return 1
    else:
        print("✅ No version drift detected. All packages have consistent versions!")
        return 0


if __name__ == "__main__":
    exit(main())
