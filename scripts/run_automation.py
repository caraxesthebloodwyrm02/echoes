import argparse
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automation.core.orchestrator import Orchestrator

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automation Framework Runner')
    parser.add_argument('--config', type=str, default='../config/automation_config.yaml', help='Path to config file')
    parser.add_argument('--task-type', type=str, required=True, choices=['security', 'cleanup', 'maintenance', 'monitoring'])
    parser.add_argument('--frequency', type=str, required=True, choices=['daily', 'weekly', 'monthly', 'ondemand'])
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    args = parser.parse_args()

    orchestrator = Orchestrator(args.config, dry_run=args.dry_run)
    orchestrator.run(args.task_type, args.frequency)
