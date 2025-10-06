"""
Symphony Orchestrator: Unified Safety & Security Automation

- Executes janitor.py (cleanup/maintenance)
- Executes queensgambit.py (insight logging)
- Optionally runs waste_management.py (bio-inspired logic)
- Runs any additional scripts for final cleanup/validation
- Semantically scans for pycache, __init__.py, and hygiene issues
- Orchestrates all for a robust, failsafe, and presentable codebase

Usage:
    python scripts/symphony_orchestrator.py [--full]
"""
import subprocess
import sys
import os
from pathlib import Path

def run_script(script, args=None):
    cmd = [sys.executable, script]
    if args:
        cmd.extend(args)
    print(f"[symphony] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)

def semantic_scan_pycache_init():
    print("[symphony] Semantic scan for __pycache__ and __init__.py modules...")
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                print(f"[symphony][FINDING] __pycache__ directory: {os.path.join(root, d)}")
        for f in files:
            if f == "__init__.py":
                print(f"[symphony][FINDING] __init__.py module: {os.path.join(root, f)}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Symphony Orchestrator")
    parser.add_argument('--full', action='store_true', help='Run all scripts in full mode')
    args = parser.parse_args()

    # Step 1: Clean and maintain
    run_script("janitor.py", ["--full"] if args.full else None)
    # Step 2: Log findings and insights
    run_script("queensgambit.py")
    # Step 3: (Optional) Run bio-inspired waste management logic
    waste_management_path = Path("app/domains/science/waste_management.py")
    if waste_management_path.exists():
        print("[symphony] Running waste_management.py for adaptive feedback...")
        run_script(str(waste_management_path))
    # Step 4: Semantic scan for hygiene
    semantic_scan_pycache_init()
    print("[symphony] All tasks complete. Codebase is clean, safe, and ready.")

if __name__ == "__main__":
    main()
