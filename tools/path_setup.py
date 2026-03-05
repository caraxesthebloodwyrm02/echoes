"""
Single source of truth for Echoes repo root and sys.path setup.

Use this module instead of scattering sys.path.insert(0, ...) across scripts.
Prefer running from repo root with PYTHONPATH=. so imports work without mutation.
"""

import os
import sys
from pathlib import Path

# Repo root: ECHOES_ROOT env, or derived from this file (tools/path_setup.py -> repo root)
REPO_ROOT: Path = Path(
    os.environ.get("ECHOES_ROOT", str(Path(__file__).resolve().parent.parent))
)


def ensure_repo_on_path() -> None:
    """Prepend repo root to sys.path if not already present. Idempotent."""
    root_str = str(REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
