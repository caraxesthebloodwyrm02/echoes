"""
Test runner for FinanceAdvisor module

Executes all tests and generates coverage reports.
"""

import subprocess
import sys
from pathlib import Path


def run_tests(verbose=True, coverage=True, markers=None):
    """
    Run all tests for FinanceAdvisor module

    Args:
        verbose: Enable verbose output
        coverage: Generate coverage report
        markers: Run only tests with specific markers (e.g., 'security', 'integration')
    """
    test_dir = Path(__file__).parent

    # Build pytest command
    cmd = ["pytest", str(test_dir)]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(
            [
                "--cov=app.domains.commerce.finance",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-report=xml",
            ]
        )

    if markers:
        cmd.append(f"-m {markers}")

    # Add other useful options
    cmd.extend(
        [
            "--tb=short",  # Shorter traceback format
            "--strict-markers",  # Strict marker validation
            "-ra",  # Show summary of all test outcomes
        ]
    )

    print(f"Running command: {' '.join(cmd)}")
    print("=" * 80)

    try:
        result = subprocess.run(cmd, cwd=test_dir.parent.parent.parent.parent)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Install it with: pip install pytest pytest-cov")
        return 1


def run_security_tests():
    """Run only security-related tests"""
    print("Running security tests...")
    return run_tests(markers="security")


def run_integration_tests():
    """Run only integration tests"""
    print("Running integration tests...")
    return run_tests(markers="integration")


def run_all_tests():
    """Run all tests with coverage"""
    print("Running all tests with coverage...")
    return run_tests(verbose=True, coverage=True)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "security":
            return run_security_tests()
        elif test_type == "integration":
            return run_integration_tests()
        elif test_type == "all":
            return run_all_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [all|security|integration]")
            return 1
    else:
        # Default: run all tests
        return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
"""
Test runner for FinanceAdvisor module

Executes all tests and generates coverage reports.
"""

import sys


def run_tests(verbose=True, coverage=True, markers=None):
    """
    Run all tests for FinanceAdvisor module

    Args:
        verbose: Enable verbose output
        coverage: Generate coverage report
        markers: Run only tests with specific markers (e.g., 'security', 'integration')
    """
    test_dir = Path(__file__).parent

    # Build pytest command
    cmd = ["pytest", str(test_dir)]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(
            [
                "--cov=app.domains.commerce.finance",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-report=xml",
            ]
        )

    if markers:
        cmd.append(f"-m {markers}")

    # Add other useful options
    cmd.extend(
        [
            "--tb=short",  # Shorter traceback format
            "--strict-markers",  # Strict marker validation
            "-ra",  # Show summary of all test outcomes
        ]
    )

    print(f"Running command: {' '.join(cmd)}")
    print("=" * 80)

    try:
        result = subprocess.run(cmd, cwd=test_dir.parent.parent.parent.parent)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Install it with: pip install pytest pytest-cov")
        return 1


def run_security_tests():
    """Run only security-related tests"""
    print("Running security tests...")
    return run_tests(markers="security")


def run_integration_tests():
    """Run only integration tests"""
    print("Running integration tests...")
    return run_tests(markers="integration")


def run_all_tests():
    """Run all tests with coverage"""
    print("Running all tests with coverage...")
    return run_tests(verbose=True, coverage=True)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]

        if test_type == "security":
            return run_security_tests()
        elif test_type == "integration":
            return run_integration_tests()
        elif test_type == "all":
            return run_all_tests()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [all|security|integration]")
            return 1
    else:
        # Default: run all tests
        return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
