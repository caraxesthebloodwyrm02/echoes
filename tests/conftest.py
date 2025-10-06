"""
Pytest configuration for ensuring the application package is importable.
This adds the project's `app/` directory to sys.path so imports like
`from api.routes.system import router` work reliably in all environments.
"""
import os
import sys

# Resolve project base directory (the parent of this tests directory)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
APP_DIR = os.path.join(BASE_DIR, "app")

# Ensure project root is on path for absolute imports like `app.main`
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ensure `app/` is directly importable for tests that expect `api.*` under `app`
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
