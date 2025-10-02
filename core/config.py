import yaml
import os
from typing import Any, Dict

class ConfigLoader:
    def __init__(self, path: str):
        self.path = path
        self.config = self.load()

    def load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Config file not found: {self.path}")
        with open(self.path, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, default=None):
        return self.config.get(key, default)
