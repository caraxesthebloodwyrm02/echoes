import argparse

import yaml

from automation.core.context import Context
from automation.core.orchestrator import run_tasks


def main():
    parser = argparse.ArgumentParser(description="Run AI Advisor automation framework")
    parser.add_argument("--config", required=True, help="Path to automation config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    context = Context(dry_run=args.dry_run)
    run_tasks(config, context)


if __name__ == "__main__":
    main()
