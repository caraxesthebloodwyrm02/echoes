#!/usr/bin/env python3
"""
Simple test for monitoring and logging system
"""

import sys
from pathlib import Path
import importlib.util

# Debug: Print current working directory and sys.path
cwd = Path.cwd()
print(f"Debug: Current working directory: {cwd}")
print(f"Debug: Current sys.path before modification: {sys.path}")

# Explicitly add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))
print(f"Debug: Updated sys.path: {sys.path}")

# Check if the module file exists
module_path = Path(__file__).parent / "packages" / "core" / "logging" / "logger.py"
if not module_path.exists():
    print(f"FAILED: Module file not found - {module_path}. Ensure it exists and has __init__.py in parent directories.")
    sys.exit(1)

try:
    # Dynamically import the logger module using importlib
    spec = importlib.util.spec_from_file_location("logger", str(module_path))
    logger_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(logger_module)
    setup_logger = logger_module.setup_logger
    print("PASSED: Module imported successfully using importlib")
except Exception as e:
    print(f"FAILED: Import error - {e}. Fallback import failed.")
    sys.exit(1)

print("=" * 70)
print("LOGGING SYSTEM - QUICK TEST")
print("=" * 70)

try:
    # Set up logger
    logger = setup_logger()

    # Log a test message
    logger.info("Test log message: Logging system is operational")
    print("PASSED: Logger initialized and wrote a message")
except Exception as e:
    print(f"FAILED: Logging test - {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("TEST COMPLETE - Check log output for 'Test log message'")
print("=" * 70)
