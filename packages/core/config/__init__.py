"""Configuration management."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import yaml
from dotenv import load_dotenv


@dataclass
class Config:
    """Base configuration class."""

    env: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Paths
    workspace_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
    data_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)

    def __post_init__(self):
        self.data_dir = self.workspace_root / "data"
        self.logs_dir = self.workspace_root / "logs"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


def load_config(config_file: Optional[Path] = None, env_file: Optional[Path] = None) -> Config:
    """
    Load configuration from environment and optional files.

    Args:
        config_file: Optional YAML config file
        env_file: Optional .env file (defaults to .env in workspace root)

    Returns:
        Config instance
    """
    # Load .env file
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()  # Looks for .env in current and parent dirs

    # Load YAML config if provided
    config_data = {}
    if config_file and config_file.exists():
        with open(config_file) as f:
            config_data = yaml.safe_load(f) or {}

    # Merge with environment variables (env vars take precedence)
    return Config(**config_data)


__all__ = ["Config", "load_config"]
