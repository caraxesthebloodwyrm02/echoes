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
Test script for the web demo functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all required imports work."""
    try:
        print("[OK] Streamlit imported successfully")

        from utils.budget_guard import check_budget

        print("[OK] Budget guard imported successfully")

        # Test budget functions
        ok, remaining, data = check_budget()
        print(f"[OK] Budget check works: ${remaining:.2f} remaining")

        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False


def test_file_structure():
    """Test that the file structure is correct."""
    required_files = [
        "web_demo.py",
        "batch_processor.py",
        "modules/transformer.py",
        "utils/budget_guard.py",
    ]

    required_dirs = ["data/input_samples", "data/outputs", "logs"]

    all_good = True

    for file_path in required_files:
        full_path = src_path / file_path
        if full_path.exists():
            print(f"[OK] {file_path} exists")
        else:
            print(f"[MISSING] {file_path}")
            all_good = False

    for dir_path in required_dirs:
        full_path = src_path / dir_path
        if full_path.exists():
            print(f"[OK] {dir_path} directory exists")
        else:
            print(f"[MISSING] {dir_path} directory")
            all_good = False

    return all_good


def test_budget_initialization():
    """Test budget initialization."""
    try:
        from utils.budget_guard import load_budget

        data = load_budget()
        print(f"[OK] Budget initialized: ${data['spent']:.2f} spent, {data['calls']} calls")
        return True
    except Exception as e:
        print(f"[ERROR] Budget initialization error: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing Echoes Web Demo Setup")
    print("=" * 50)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Budget Initialization", test_budget_initialization),
    ]

    all_passed = True
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}:")
        if not test_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! Web demo is ready.")
        print("\nTo launch the web demo:")
        print("   cd src")
        print("   streamlit run web_demo.py")
        print("\nThen visit: http://localhost:8501")
    else:
        print("Some tests failed. Please check the errors above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
