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

"""Application settings and configuration management."""

import secrets
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from utils.path_resolver import get_project_root


class AppSettings(BaseSettings):
    """Application settings with Pydantic validation."""

    # Environment
    environment: str = Field(default="development", env="APP_ENV")
    debug: bool = Field(default=False, env="DEBUG")

    # API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_max_retries: int = Field(default=3, env="OPENAI_MAX_RETRIES")
    openai_timeout: int = Field(default=30, env="OPENAI_TIMEOUT")

    # Database (if needed in future)
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

    # File paths
    project_root: Path = Field(default_factory=get_project_root)
    data_dir: Path = Field(default_factory=lambda: get_project_root() / "data")
    logs_dir: Path = Field(default_factory=lambda: get_project_root() / "logs")
    temp_dir: Path = Field(default_factory=lambda: get_project_root() / "temp")

    # Processing settings
    batch_max_workers: int = Field(default=4, env="BATCH_MAX_WORKERS")
    batch_file_pattern: str = Field(default="*.txt", env="BATCH_FILE_PATTERN")

    # Security
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",  # Security: Prevent unvalidated fields
    )


class LoggingSettings:
    """Logging configuration."""

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.date_format = "%Y-%m-%d %H:%M:%S"

    def get_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": self.log_format,
                    "datefmt": self.date_format,
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
                    "datefmt": self.date_format,
                },
            },
            "handlers": {
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.settings.logs_dir / "app.log"),
                    "maxBytes": 10 * 1024 * 1024,  # 10MB
                    "backupCount": 5,
                    "formatter": "detailed",
                },
                "error_file": {
                    "level": "ERROR",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(self.settings.logs_dir / "error.log"),
                    "maxBytes": 10 * 1024 * 1024,  # 10MB
                    "backupCount": 3,
                    "formatter": "detailed",
                },
            },
            "root": {
                "level": "DEBUG" if self.settings.debug else "INFO",
                "handlers": ["console", "file", "error_file"],
            },
            "loggers": {
                "ai_modules": {
                    "level": "DEBUG",
                    "handlers": ["file"],
                    "propagate": False,
                },
            },
        }


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        load_dotenv()
        _settings = AppSettings()
    return _settings


def reload_settings() -> AppSettings:
    """Reload settings from environment."""
    global _settings
    load_dotenv()
    _settings = AppSettings()
    return _settings


def ensure_directories():
    """Ensure required directories exist."""
    settings = get_settings()
    directories = [
        settings.data_dir,
        settings.logs_dir,
        settings.temp_dir,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
ensure_directories()
