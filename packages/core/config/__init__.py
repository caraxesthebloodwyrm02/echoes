"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Unified configuration using pydantic-settings."""

<<<<<<< Updated upstream
    env: str = field(default_factory=lambda: os.getenv("ENV", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Paths
    workspace_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
    data_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
=======
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ECHO_",
        case_sensitive=False,
    )

    # Environment and paths
    env: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    workspace_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent,
        description="Workspace root directory",
    )
>>>>>>> Stashed changes

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


<<<<<<< Updated upstream
def load_config(config_file: Optional[Path] = None, env_file: Optional[Path] = None) -> Config:
=======
def load_config(
    env_file: Optional[Path] = None, override_env: Optional[dict] = None
) -> Config:
>>>>>>> Stashed changes
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
