#!/usr/bin/env python3
"""Automation Framework Runner.

This script provides a command-line interface to run automation tasks.
"""
import argparse
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation.core.orchestrator import Orchestrator
from automation.core.logger import log

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Automation Framework Runner')
    
    # Main arguments
    parser.add_argument(
        '--config', 
        type=str, 
        default=str(project_root / 'config' / 'automation.yaml'),
        help='Path to configuration file (YAML)'
    )
    
    # Task selection
    subparsers = parser.add_subparsers(dest='command', required=True, help='Command to execute')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run automation tasks')
    run_parser.add_argument(
        '--category', 
        type=str, 
        required=True,
        help='Task category to run (e.g., maintenance, security)'
    )
    run_parser.add_argument(
        '--frequency', 
        type=str, 
        required=True,
        choices=['daily', 'weekly', 'monthly'],
        help='Frequency of tasks to run'
    )
    run_parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Run in dry-run mode (no changes will be made)'
    )
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available tasks')
    list_parser.add_argument(
        '--category',
        type=str,
        help='Filter tasks by category'
    )
    
    return parser.parse_args()

def list_tasks(orchestrator: Orchestrator, category: str = None) -> None:
    """List available tasks."""
    categories = [category] if category else orchestrator.get_task_categories()
    
    for cat in categories:
        print(f"\n{cat.upper()}:")
        print("-" * (len(cat) + 2))
        
        for freq in orchestrator.get_task_frequencies(cat):
            tasks = orchestrator.get_tasks(cat, freq)
            if tasks:
                print(f"\n  {freq.capitalize()}:")
                for task in tasks:
                    print(f"    - {task}")
    print()

def main() -> int:
    """Main entry point for the script."""
    args = parse_args()
    
    try:
        orchestrator = Orchestrator(args.config)
        
        if args.command == 'list':
            list_tasks(orchestrator, args.category)
            return 0
            
        elif args.command == 'run':
            log.info(f"Running {args.category} tasks ({args.frequency} frequency)")
            if args.dry_run:
                log.info("DRY RUN: No changes will be made")
                
            results = orchestrator.run_tasks(
                category=args.category,
                frequency=args.frequency,
                dry_run=args.dry_run
            )
            
            # Print summary
            success = sum(1 for r in results.values() if r)
            total = len(results)
            
            if total > 0:
                log.info(f"\nTask execution complete: {success}/{total} tasks succeeded")
                return 0 if success == total else 1
            else:
                log.warning("No tasks were executed")
                return 0
                
    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
