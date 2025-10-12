"""
Task wrapper for automated test generation.
Uses automation/test_generator.py's TestGenerator to create pytest skeletons.
"""

from pathlib import Path

from automation.core.logger import AutomationLogger
from automation.test_generator import TestGenerator


def generate_tests(context):
    log = AutomationLogger()
    source_file = context.extra_data.get("source_file")
    overwrite = bool(context.extra_data.get("overwrite", False))
    if not source_file:
        raise ValueError("source_file is required (e.g., app/domains/science/science_module.py)")

    sf = Path(source_file)
    if not sf.exists():
        raise FileNotFoundError(f"Source file not found: {sf}")

    if context.dry_run:
        log.info(f"[DRY-RUN] Would generate tests for: {sf}")
        return

    gen = TestGenerator(str(sf))
    gen.generate(overwrite=overwrite)
    log.info("Test generation completed.")
