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
Privacy Scanner - Automated PII Detection Tool

Scans codebase for potential PII exposure and provides recommendations.

Usage:
    python privacy_scanner.py <directory> [--extensions .py,.txt,.md]
"""

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List

# Handle imports for both script and module execution
try:
    from .privacy_filter import PrivacyFilter
except ImportError:
    # Running as script, use absolute import
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from privacy_filter import PrivacyFilter


class PrivacyScanResult:
    """Result of a privacy scan on a single file"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.entities: List[Dict] = []
        self.line_numbers: List[int] = []
        self.has_pii = False

    def add_entity(self, line_number: int, entity_data: Dict):
        """Add detected PII entity"""
        self.entities.append(entity_data)
        self.line_numbers.append(line_number)
        self.has_pii = True

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "file_path": str(self.file_path),
            "has_pii": self.has_pii,
            "entity_count": len(self.entities),
            "entities": self.entities,
            "line_numbers": self.line_numbers,
        }


class PrivacyScanner:
    """
    Comprehensive privacy scanner for codebase analysis

    Scans files for PII exposure and provides detailed reports.
    """

    def __init__(self, extensions: List[str] = None):
        self.privacy_filter = PrivacyFilter()
        self.extensions = extensions or [".py", ".txt", ".md", ".json", ".yaml", ".yml"]

    def scan_directory(self, directory: Path, max_workers: int = 4) -> Dict:
        """
        Scan entire directory for PII exposure

        Args:
            directory: Directory to scan
            max_workers: Number of parallel workers

        Returns:
            Scan results dictionary
        """
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist")

        print(f"Scanning directory: {directory}")
        print(f"Extensions: {', '.join(self.extensions)}")
        print("-" * 50)

        # Collect all files to scan
        files_to_scan = []
        for ext in self.extensions:
            files_to_scan.extend(directory.rglob(f"*{ext}"))

        # Filter out common non-source directories
        exclude_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "build",
            "dist",
            "htmlcov",
            ".pytest_cache",
            ".mypy_cache",
        ]

        filtered_files = []
        for file_path in files_to_scan:
            if not any(excl in str(file_path) for excl in exclude_patterns):
                filtered_files.append(file_path)

        print(f"Found {len(filtered_files)} files to scan")

        # Scan files in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._scan_file, file_path)
                for file_path in filtered_files
            ]

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result.has_pii:
                    results.append(result)
                if (i + 1) % 10 == 0:
                    print(f"Scanned {i + 1}/{len(filtered_files)} files...")

        # Generate summary
        summary = self._generate_summary(results, len(filtered_files))

        return {"summary": summary, "results": [result.to_dict() for result in results]}

    def _scan_file(self, file_path: Path) -> PrivacyScanResult:
        """Scan individual file for PII"""
        result = PrivacyScanResult(file_path)

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                entities = self.privacy_filter.detect_pii(line.strip())
                for entity in entities:
                    result.add_entity(
                        line_num,
                        {
                            "type": entity.type,
                            "value": entity.value,
                            "confidence": entity.confidence,
                            "line_content": (
                                line.strip()[:100] + "..."
                                if len(line.strip()) > 100
                                else line.strip()
                            ),
                        },
                    )

        except Exception as e:
            # Log error but continue scanning
            print(f"Error scanning {file_path}: {e}")

        return result

    def _generate_summary(
        self, results: List[PrivacyScanResult], total_files: int
    ) -> Dict:
        """Generate summary statistics"""
        files_with_pii = len(results)
        total_entities = sum(len(result.entities) for result in results)

        # Count by PII type
        pii_type_counts = {}
        for result in results:
            for entity in result.entities:
                pii_type = entity["type"]
                pii_type_counts[pii_type] = pii_type_counts.get(pii_type, 0) + 1

        return {
            "total_files_scanned": total_files,
            "files_with_pii": files_with_pii,
            "total_pii_entities": total_entities,
            "pii_types_found": pii_type_counts,
            "risk_level": self._calculate_risk_level(
                files_with_pii, total_files, total_entities
            ),
        }

    def _calculate_risk_level(
        self, files_with_pii: int, total_files: int, total_entities: int
    ) -> str:
        """Calculate overall risk level"""
        pii_percentage = (files_with_pii / total_files) * 100 if total_files > 0 else 0

        if pii_percentage > 20 or total_entities > 50:
            return "HIGH"
        elif pii_percentage > 10 or total_entities > 20:
            return "MEDIUM"
        elif total_entities > 0:
            return "LOW"
        else:
            return "NONE"


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Privacy Scanner - Automated PII Detection"
    )
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument(
        "--extensions",
        default=".py,.txt,.md,.json,.yaml,.yml",
        help="File extensions to scan (comma-separated)",
    )
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--max-workers", type=int, default=4, help="Maximum parallel workers"
    )

    args = parser.parse_args()

    # Parse extensions
    extensions = [ext.strip() for ext in args.extensions.split(",")]

    # Initialize scanner
    scanner = PrivacyScanner(extensions=extensions)

    # Scan directory
    directory = Path(args.directory)
    results = scanner.scan_directory(directory, max_workers=args.max_workers)

    # Print summary
    summary = results["summary"]
    print("\n" + "=" * 50)
    print("PRIVACY SCAN RESULTS")
    print("=" * 50)
    print(f"Files scanned: {summary['total_files_scanned']}")
    print(f"Files with PII: {summary['files_with_pii']}")
    print(f"Total PII entities: {summary['total_pii_entities']}")
    print(f"Risk level: {summary['risk_level']}")
    print(f"PII types found: {summary['pii_types_found']}")

    if results["results"]:
        print(
            f"\nDetailed results for {len(results['results'])} files saved to output."
        )

    # Save results if output specified
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")
    else:
        # Print first few results to console
        for result in results["results"][:5]:
            print(f"\n{result['file_path']}: {result['entity_count']} entities")
            for entity in result["entities"][:3]:  # Show first 3 entities
                print(f"  - {entity['type']}: {entity['value']}")


if __name__ == "__main__":
    main()
