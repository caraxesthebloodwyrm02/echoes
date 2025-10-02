import os
from typing import Optional

class Context:
    def __init__(self, dry_run: bool = False, user: Optional[str] = None, env: Optional[str] = None):
        self.dry_run = dry_run
        self.user = user or os.getenv('USERNAME') or os.getenv('USER')
        self.env = env or os.getenv('ENVIRONMENT', 'development')
        self.confirmed = False
        self.extra = {}

    def require_confirmation(self, message: str):
        resp = input(f"[CONFIRM] {message} (y/N): ").strip().lower()
        self.confirmed = resp == 'y'
        return self.confirmed
