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
