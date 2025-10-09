#!/usr/bin/env python3
"""
Privacy Scanner CLI Tool
Scan files and directories for PII
"""

import json
import sys
from pathlib import Path

try:
    from privacy_filter import PrivacyFilter
except ImportError:
    privacy_filter_path = Path(__file__).parent.parent / "privacy_filter.py"
    if not privacy_filter_path.exists():
        print("Error: privacy_filter.py not found.")
        print(
            "Please run 'python privacy_filters.py' first to create the privacy filter module."
        )
        sys.exit(1)

    # Add parent directory to path for imports and retry
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from privacy_filter import PrivacyFilter


class PrivacyScanner:
    """CLI tool for scanning files for PII"""

    def __init__(self):
        self.filter = PrivacyFilter()

    def scan_directory(self, directory: Path, extensions: list = None):
        """Scan all files in directory for PII"""
        results = []

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                if extensions and file_path.suffix not in extensions:
                    continue

                result = self.filter.scan_file(str(file_path))
                if result.get("pii_found", 0) > 0:
                    results.append(result)

        return results

    def generate_report(self, scan_results: list) -> str:
        """Generate scan report"""
        total_files = len(scan_results)
        total_pii = sum(r.get("pii_found", 0) for r in scan_results)

        report = {
            "scan_time": "2024-10-06T17:48:56-07:00",
            "total_files_scanned": total_files,
            "files_with_pii": len(scan_results),
            "total_pii_found": total_pii,
            "results": scan_results,
        }

        return json.dumps(report, indent=2)


def main():
    """Main scanner execution"""
    if len(sys.argv) < 2:
        print("Usage: python privacy_scanner.py <directory> [--extensions .py,.txt]")
        sys.exit(1)

    directory = Path(sys.argv[1])
    extensions = None

    if len(sys.argv) > 2 and sys.argv[2] == "--extensions":
        extensions = [f".{ext}" for ext in sys.argv[3].split(",")]

    scanner = PrivacyScanner()
    results = scanner.scan_directory(directory, extensions)

    print(f"Scanned {len(results)} files")
    print(f"Found PII in {len(results)} files")

    report = scanner.generate_report(results)
    print("\nScan Report:")
    print(report)


if __name__ == "__main__":
    main()
