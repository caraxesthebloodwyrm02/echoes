#!/usr/bin/env python
"""
Full Coverage Test Runner

This script provides comprehensive test coverage reporting across the entire codebase.
It supports parallel test execution and API verification.
"""

import argparse
import asyncio
import json
import logging
import multiprocessing
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from typing import List, Optional

import pytest
import requests
from coverage import Coverage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "test_paths": ["tests/"],
    "source_paths": ["app/", "api/", "glimpse/"],
    "omit_patterns": [
        "*/tests/*",
        "*/migrations/*",
        "*/__pycache__/*",
        "*/venv/*",
        "*/env/*",
        "*.pyc",
    ],
    "pytest_args": ["-v", "--tb=short"],
    "min_coverage": 80,
    "workers": multiprocessing.cpu_count(),
}


def load_config(config_file: Optional[str] = None) -> dict:
    """Load test configuration from file or use defaults."""
    if config_file and os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = {**DEFAULT_CONFIG, **json.load(f)}
    else:
        config = DEFAULT_CONFIG
    return config


def verify_api_health(base_url: str = "http://localhost:8000") -> bool:
    """Verify API health if API testing is enabled."""
    try:
        response = requests.get(f"{base_url}/health")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return False


def run_test_suite(test_path: str, pytest_args: List[str]) -> bool:
    """Run a test suite in a separate process."""
    result = pytest.main([test_path, *pytest_args])
    return result == 0


async def run_parallel_tests(config: dict) -> bool:
    """Run test suites in parallel using a process pool."""
    test_paths = config["test_paths"]
    pytest_args = config["pytest_args"]
    max_workers = config.get("workers", multiprocessing.cpu_count())

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, run_test_suite, path, pytest_args)
            for path in test_paths
        ]
        results = await asyncio.gather(*futures)
        return all(results)


def generate_coverage_report(config: dict) -> float:
    """Generate coverage report and return coverage percentage."""
    cov = Coverage(
        source=config["source_paths"],
        omit=config["omit_patterns"],
    )

    # Start coverage measurement
    cov.start()

    # Run test suite
    pytest.main([*config["test_paths"], *config["pytest_args"]])

    # Stop coverage measurement and save
    cov.stop()
    cov.save()

    # Generate reports
    cov.html_report(directory="htmlcov")
    total = cov.report()

    return total


def main():
    parser = argparse.ArgumentParser(description="Full Coverage Test Runner")
    parser.add_argument(
        "--config", help="Path to config file", default="full_coverage_test_config.json"
    )
    parser.add_argument(
        "--check-api", action="store_true", help="Verify API health before testing"
    )
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of worker processes",
        default=multiprocessing.cpu_count(),
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    config["workers"] = args.workers

    # Check API health if requested
    if args.check_api and not verify_api_health():
        logger.error("API health check failed")
        sys.exit(1)

    # Run parallel tests
    logger.info("Starting test suite execution...")
    asyncio.run(run_parallel_tests(config))

    # Generate coverage report
    logger.info("Generating coverage report...")
    coverage_total = generate_coverage_report(config)

    # Check minimum coverage
    min_coverage = config["min_coverage"]
    if coverage_total < min_coverage:
        logger.error(
            f"Coverage {coverage_total:.2f}% is below minimum required {min_coverage}%"
        )
        sys.exit(1)

    logger.info(f"Test suite completed successfully. Coverage: {coverage_total:.2f}%")
    sys.exit(0)


if __name__ == "__main__":
    main()
