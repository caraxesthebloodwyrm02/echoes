# test_ucr.py
import sys
import os
from pathlib import Path

# Print Python version for debugging
print(f"Python {sys.version}")

# Add UCR directory to Python path
ucr_path = str(Path.home() / ".ucr")
if os.path.exists(ucr_path) and ucr_path not in sys.path:
    sys.path.insert(0, ucr_path)

print("\nPython paths containing UCR:", [p for p in sys.path if "ucr" in str(p).lower()])

try:
    from ucr import ucr

    print("\n✅ UCR module loaded successfully!")
    print(f"Active Environment: {ucr.active_env.get('name')}")
    print(f"Project Roots: {ucr.config.get('projectsRoot')}")
    print(f"Environment Variables: {ucr.get_env_vars()}")
except Exception as e:
    print(f"\n❌ Error loading UCR: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"UCR path exists: {os.path.exists(ucr_path)}")
    print(f"UCR path: {ucr_path}")
    print(f"sys.path: {sys.path}")
