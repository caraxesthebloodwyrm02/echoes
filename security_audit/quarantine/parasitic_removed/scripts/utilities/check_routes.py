import sys
from pathlib import Path

# Add current directory to path
current_dir = Path.cwd()
sys.path.append(str(current_dir))

from examples.fastapi_archer_integration import app

print("🔍 Checking FastAPI Routes:")
print("=" * 40)

for route in app.routes:
    if hasattr(route, "methods") and hasattr(route, "path"):
        methods = ", ".join(route.methods)
        print(f"  {methods:<15} {route.path}")

print(f"\n📊 Total routes: {len(app.routes)}")
