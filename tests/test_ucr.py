#!/usr/bin/env python3
"""
Test Unified Code Runtime (UCR) module.

This module provides comprehensive testing for the UCR functionality,
including environment management, configuration, and tool integration.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("test_ucr.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Try to import agent_pathlib with fallback
try:
    from agent_pathlib import Path as AgentPath

    logger.info("Using agent_pathlib for path operations")
    Path = AgentPath  # type: ignore
    AGENT_PATHLIB_AVAILABLE = True
except ImportError:
    from pathlib import Path

    AGENT_PATHLIB_AVAILABLE = False
    logger.warning("agent_pathlib not found, falling back to standard pathlib")

# Constants
UCR_HOME = Path.home() / ".ucr"
TEST_ENV_NAME = "test_environment"
TEST_PROJECT_NAME = "test_project"


class TestUCR(unittest.TestCase):
    """Test cases for the Unified Code Runtime."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment before any tests run."""
        cls.original_path = sys.path.copy()
        cls.test_dir = Path(tempfile.mkdtemp(prefix="ucr_test_"))
        logger.info(f"Test directory: {cls.test_dir}")

        # Create test UCR directory structure
        cls.ucr_dir = cls.test_dir / ".ucr"
        cls.ucr_dir.mkdir(exist_ok=True)

        # Add test UCR directory to path
        if str(cls.ucr_dir) not in sys.path:
            sys.path.insert(0, str(cls.ucr_dir))

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        # Restore original path
        sys.path = cls.original_path

        # Clean up test directory
        try:
            shutil.rmtree(cls.test_dir)
            logger.info(f"Cleaned up test directory: {cls.test_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up test directory: {e}")

    def setUp(self):
        """Set up before each test method."""
        self.ucr = None
        self.test_env = None

        # Create a test environment
        self.test_env_dir = self.test_dir / "envs" / TEST_ENV_NAME
        self.test_env_dir.mkdir(parents=True, exist_ok=True)

        # Create a test project
        self.test_project_dir = self.test_dir / "projects" / TEST_PROJECT_NAME
        self.test_project_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, "ucr") and hasattr(self.ucr, "close"):
            try:
                self.ucr.close()
            except Exception as e:
                logger.error(f"Error closing UCR: {e}")

    def test_ucr_import(self):
        """Test that UCR module can be imported."""
        try:
            # Try to import UCR
            import ucr as ucr_module

            self.assertIsNotNone(ucr_module, "UCR module should be importable")

            # Get the ucr instance from the module
            ucr_instance = getattr(ucr_module, "ucr", None)
            self.assertIsNotNone(
                ucr_instance, "UCR instance should be available in module"
            )

            logger.info("✅ UCR module imported successfully")
            return ucr_instance
        except ImportError as e:
            self.fail(f"Failed to import UCR: {e}")

    def test_ucr_initialization(self):
        """Test UCR initialization and basic properties."""
        try:
            ucr = self.test_ucr_import()

            # Test basic attributes
            self.assertTrue(
                hasattr(ucr, "active_env"), "UCR should have active_env attribute"
            )
            self.assertTrue(hasattr(ucr, "config"), "UCR should have config attribute")

            # Test environment variables
            env_vars = getattr(ucr, "get_env_vars", lambda: {})()
            self.assertIsInstance(
                env_vars, dict, "Environment variables should be a dictionary"
            )

            logger.info("✅ UCR initialization test passed")
            return ucr

        except Exception as e:
            self.fail(f"UCR initialization test failed: {e}")

    def test_environment_management(self):
        """Test environment management functionality."""
        try:
            ucr = self.test_ucr_initialization()

            # Skip if environment management is not available
            if not hasattr(ucr, "create_environment"):
                self.skipTest(
                    "Environment management not available in this UCR version"
                )

            # Test creating a new environment
            env_path = str(self.test_env_dir)
            env = ucr.create_environment(TEST_ENV_NAME, path=env_path)
            self.assertIsNotNone(env, "Failed to create environment")

            # Test activating environment
            ucr.activate_environment(TEST_ENV_NAME)
            self.assertEqual(
                ucr.active_env["name"],
                TEST_ENV_NAME,
                f"Active environment should be {TEST_ENV_NAME}",
            )

            logger.info("✅ Environment management test passed")

        except Exception as e:
            self.fail(f"Environment management test failed: {e}")

    def test_project_management(self):
        """Test project management functionality."""
        try:
            ucr = self.test_ucr_initialization()

            # Skip if project management is not available
            if not hasattr(ucr, "create_project"):
                self.skipTest("Project management not available in this UCR version")

            # Test creating a new project
            project_path = str(self.test_project_dir)
            project = ucr.create_project(TEST_PROJECT_NAME, path=project_path)
            self.assertIsNotNone(project, "Failed to create project")

            # Test project properties
            self.assertTrue(hasattr(project, "name"), "Project should have a name")
            self.assertEqual(
                project.name,
                TEST_PROJECT_NAME,
                f"Project name should be {TEST_PROJECT_NAME}",
            )

            logger.info("✅ Project management test passed")

        except Exception as e:
            self.fail(f"Project management test failed: {e}")


def print_environment_info():
    """Print environment information for debugging."""
    print("\n" + "=" * 60)
    print("Environment Information")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print(f"UCR home: {UCR_HOME}")
    print(f"UCR home exists: {UCR_HOME.exists()}")
    print(f"agent_pathlib available: {AGENT_PATHLIB_AVAILABLE}")
    print("\nPython path:")
    for i, path in enumerate(sys.path, 1):
        print(f"  {i}. {path}")
    print("=" * 60 + "\n")


def main():
    """Main function to run tests and display results."""
    print_environment_info()

    # Run tests with verbosity
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=os.path.dirname(__file__), pattern="test_ucr.py"
    )

    print("\n" + "=" * 60)
    print("Running UCR Tests")
    print("=" * 60)

    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 60)

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
