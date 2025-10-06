import argparse
import os

import yaml

from automation.core.context import Context
from automation.core.orchestrator import run_tasks


def main():
    parser = argparse.ArgumentParser(description="Run AI Advisor automation framework")
    parser.add_argument(
        "--config",
        default=os.path.join("automation", "config", "automation_config.yaml"),
        help="Path to automation config YAML (default: automation/config/automation_config.yaml)",
    )
    parser.add_argument("--task", help="Run only the specified task name", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    context = Context(dry_run=args.dry_run)
    run_tasks(config, context, selected_task=args.task)


if __name__ == "__main__":
    main()
