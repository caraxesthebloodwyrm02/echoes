# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# MIT License
# Copyright (c) 2025 Echoes Project

"""
Configuration Management - .env and config.yaml loading
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemConfig(BaseSettings):
    """System configuration with validation"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",
    )

    # Environment
    environment: str = Field(default="production", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent
    )
    config_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    # Monitoring
    monitor_interval_seconds: int = Field(default=60, ge=10, le=3600)
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Security
    enable_encryption: bool = Field(default=True)
    use_credential_manager: bool = Field(default=True)

    # Networking
    http_timeout: int = Field(default=30, ge=5, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)

    def model_post_init(self, __context):
        """Initialize derived paths"""
        self.config_dir = self.config_dir or self.project_root / "config"
        self.logs_dir = self.logs_dir or self.project_root / "logs"

        # Create directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """
    Centralized configuration manager
    Loads from .env and config.yaml
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.base_path = Path(__file__).parent.parent.parent
        self.config_path = config_path or self.base_path / "config"

        # Load .env
        env_file = self.base_path / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        # Load system config
        self.system_config = SystemConfig()

        # Load YAML config
        self.yaml_config = self._load_yaml_config()

    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML"""
        yaml_file = self.config_path / "config.yaml"

        if not yaml_file.exists():
            # Create default config
            default_config = {
                "system": {
                    "name": "Windsurf System Orchestrator",
                    "version": "1.0.0",
                    "platform": "Windows 11",
                },
                "monitoring": {
                    "enabled": True,
                    "metrics": ["cpu", "memory", "disk", "network"],
                },
                "networking": {"enabled": True, "ports": [8000, 8001]},
                "windows": {"registry_monitoring": True, "com_enabled": True},
            }

            yaml_file.parent.mkdir(parents=True, exist_ok=True)
            with open(yaml_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)

            return default_config

        with open(yaml_file, "r") as f:
            return yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        # Try system config first
        if hasattr(self.system_config, key):
            return getattr(self.system_config, key)

        # Try YAML config
        keys = key.split(".")
        value = self.yaml_config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        return self.system_config

    def get_yaml_config(self) -> Dict[str, Any]:
        """Get YAML configuration"""
        return self.yaml_config


__all__ = ["ConfigManager", "SystemConfig"]
