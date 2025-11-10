#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from examples.fastapi_archer_integration import app

print("Available routes:")
for route in app.routes:
    print(f"  {route.methods} {route.path}")
