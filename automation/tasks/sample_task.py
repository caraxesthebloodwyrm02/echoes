"""Sample task for the automation framework."""

import os
from pathlib import Path
from typing import Optional

from automation.core.context import Context
from automation.core.logger import log


def run(context: Context) -> None:
    """Run the sample task.

    Args:
        context: Execution context
    """
    log.info("Starting sample task")

    # Example of using the context
    if context.dry_run:
        log.info("DRY RUN: Would perform some action")
        return

    # Example of requiring confirmation
    if not context.confirmed:
        if not context.require_confirmation("Perform sample action?"):
            log.warning("Sample task cancelled by user")
            return

    # Example of using extra context
    target_dir = context.extra.get("target_dir", os.getcwd())
    log.info(f"Working in directory: {target_dir}")

    # Example of a simple operation
    try:
        file_path = Path(target_dir) / "sample.txt"
        file_path.write_text(
            "This is a sample file created by the automation framework."
        )
        log.success(f"Created sample file: {file_path}")
    except Exception as e:
        log.error(f"Error in sample task: {e}")
        raise

    log.info("Sample task completed")
