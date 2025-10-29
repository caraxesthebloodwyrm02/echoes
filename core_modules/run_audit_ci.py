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
Audit Trigger Script for CI/Local Use

Runs the auto-audit script and logs results with timestamps.
Can be used locally or integrated into CI pipelines.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_audit():
    """Run the automated audit and log results."""
    print("[AUDIT] Running automated audit...")
    print("=" * 50)

    # Ensure audit script exists
    audit_script = Path("audit_codebase.py")
    if not audit_script.exists():
        print("[ERROR] audit_codebase.py not found!")
        return False

    # Run the audit
    try:
        result = subprocess.run(
            [sys.executable, str(audit_script)],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)

        # Create logs directory if it doesn't exist
        logs_dir = Path("audit_logs")
        logs_dir.mkdir(exist_ok=True)

        # Save timestamped log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"audit_{timestamp}.log"

        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"AUDIT RUN: {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\nSTDERR:\n")
                f.write(result.stderr)

        print(f"[SUCCESS] Audit complete — logs saved to {log_file}")

        # Check for failures
        if result.returncode != 0:
            print(f"[ERROR] Audit failed with exit code {result.returncode}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] Error running audit: {e}")
        return False


def run_audit_with_format(format_type="markdown", output_file=None):
    """Run audit with specific format and optional output file."""
    print(f"[AUDIT] Running audit with format: {format_type}")

    cmd = [sys.executable, "audit_codebase.py", "--format", format_type]
    if output_file:
        cmd.extend(["--output", output_file])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print("[SUCCESS] Audit completed successfully")
            return True
        else:
            print(f"[ERROR] Audit failed with exit code {result.returncode}")
            return False

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automated codebase audit")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--log-only", action="store_true", help="Only run audit without format options")

    args = parser.parse_args()

    if args.log_only:
        success = run_audit()
    else:
        success = run_audit_with_format(args.format, args.output)

    sys.exit(0 if success else 1)
