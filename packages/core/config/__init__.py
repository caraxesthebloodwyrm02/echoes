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

"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Unified configuration using pydantic-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ECHO_",
        case_sensitive=False,
        extra="ignore",  # Allow extra fields for backward compatibility, but validate known ones
    )

    # Environment and paths
    env: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    workspace_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent,
        description="Workspace root directory",
    )

    # Detector configuration
    min_support: float = Field(
        default=0.1, description="Minimum support threshold for detectors"
    )
    confidence_threshold: float = Field(
        default=0.5, description="Confidence threshold for detector decisions"
    )
    min_votes: int = Field(
        default=1, description="Minimum votes required for detector consensus"
    )
    debounce_window: int = Field(
        default=300, description="Debounce window in seconds for detector firings"
    )

    # Derived paths (computed after loading)
    data_dir: Optional[Path] = Field(default=None, exclude=True)
    logs_dir: Optional[Path] = Field(default=None, exclude=True)

    def model_post_init(self, __context):
        """Initialize derived paths after loading."""
        self.data_dir = self.workspace_root / "data"
        self.logs_dir = self.workspace_root / "logs"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


def load_config(
    env_file: Optional[Path] = None, override_env: Optional[dict] = None
) -> Config:
    """
    Load configuration from environment and optional overrides.

    Args:
        env_file: Optional custom .env file path
        override_env: Optional environment variable overrides

    Returns:
        Config instance
    """
    # Prepare settings sources
    settings_kwargs = {}

    if env_file:
        settings_kwargs["env_file"] = env_file

    if override_env:
        # Create a temporary config class with overrides
        class OverrideConfig(Config):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            ):
                # Apply overrides first, then environment
                return (init_settings, env_settings, dotenv_settings)

        settings_kwargs.update(override_env)
        return OverrideConfig(**settings_kwargs)

    return Config(**settings_kwargs)


__all__ = ["Config", "load_config"]
