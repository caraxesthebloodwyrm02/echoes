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
Example Python CLI Script with Argument Parsing

This demonstrates how to use argparse to handle command-line arguments
in a Python script's __main__ block.

Usage:
    python main.py --mode dev --verbose
    python main.py --mode prod
    python main.py --help
"""

import argparse
import sys


def main():
    """Main entry point with CLI argument parsing."""

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Echoes Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode dev --verbose    # Development mode with verbose output
  python main.py --mode prod             # Production mode
  python main.py --help                  # Show this help message
        """,
    )

    # Add arguments
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "test"],
        default="dev",
        help="Run mode (default: dev)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    parser.add_argument("--config", type=str, help="Path to configuration file")

    # Parse arguments
    args = parser.parse_args()

    # Use the parsed arguments
    print("Echoes CLI Started")
    print(f"Mode: {args.mode}")
    print(f"Verbose: {args.verbose}")

    if args.config:
        print(f"Config file: {args.config}")

    # Example logic based on arguments
    if args.mode == "dev":
        print("Running in DEVELOPMENT mode")
        if args.verbose:
            print("  - Debug logging enabled")
            print("  - Hot reload active")
            print("  - Development server starting...")

    elif args.mode == "prod":
        print("Running in PRODUCTION mode")
        if args.verbose:
            print("  - Optimized for performance")
            print("  - Security checks enabled")
            print("  - Production server starting...")

    elif args.mode == "test":
        print("Running in TEST mode")
        if args.verbose:
            print("  - Test environment loaded")
            print("  - Mock services active")
            print("  - Running test suite...")

    # You can access all arguments via args object
    print(f"\nAll arguments: {vars(args)}")
    print(f"Script name: {sys.argv[0]}")
    print(f"All CLI args: {sys.argv[1:]}")


if __name__ == "__main__":
    main()
