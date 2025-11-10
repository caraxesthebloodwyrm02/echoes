"""
Echoes AI Configuration

This module provides configuration management for the Echoes AI Multi-Agent System.
"""

import secrets
from pathlib import Path
from typing import Any

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Echoes AI application settings."""

    # Application
    app_name: str = Field(default="Echoes AI", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")

    # Security
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT tokens",
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration time"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )

    # API Keys
    openai_api_key: str | None = Field(default=None, description="OpenAI API key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API key")

    # Database
    database_url: str = Field(
        default="sqlite:///./echoes.db", description="Database connection URL"
    )
    database_pool_size: int = Field(
        default=5, description="Database connection pool size"
    )
    database_max_overflow: int = Field(default=10, description="Database max overflow")

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: str | None = Field(default=None, description="Redis password")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=60, description="Rate limit requests per minute"
    )
    rate_limit_window: int = Field(
        default=60, description="Rate limit window in seconds"
    )

    # File Storage
    upload_dir: str = Field(default="uploads", description="Upload directory")
    max_file_size: int = Field(
        default=10 * 1024 * 1024, description="Max file size in bytes"
    )
    allowed_extensions: list[str] = Field(
        default=[".txt", ".pdf", ".doc", ".docx", ".json", ".csv"],
        description="Allowed file extensions",
    )

    # Monitoring
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    prometheus_port: int = Field(default=9090, description="Prometheus metrics port")
    jaeger_endpoint: str | None = Field(
        default=None, description="Jaeger tracing endpoint"
    )

    # AI Configuration
    default_model: str = Field(default="gpt-3.5-turbo", description="Default AI model")
    max_tokens: int = Field(default=1000, description="Maximum tokens for AI responses")
    temperature: float = Field(
        default=0.7, description="Default temperature for AI responses"
    )

    # Agent Configuration
    max_agents_per_user: int = Field(default=10, description="Maximum agents per user")
    max_conversations_per_agent: int = Field(
        default=100, description="Maximum conversations per agent"
    )
    conversation_history_limit: int = Field(
        default=50, description="Conversation history limit"
    )

    # Workflow Configuration
    max_workflows_per_user: int = Field(
        default=20, description="Maximum workflows per user"
    )
    workflow_timeout: int = Field(
        default=300, description="Workflow timeout in seconds"
    )

    # Cache
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_enabled: bool = Field(default=True, description="Enable caching")

    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("environment", pre=True)
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        valid_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()

    @validator("log_level", pre=True)
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"

    def get_database_config(self) -> dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "echo": self.debug,
        }

    def get_redis_config(self) -> dict[str, Any]:
        """Get Redis configuration."""
        return {
            "url": self.redis_url,
            "db": self.redis_db,
            "password": self.redis_password,
            "decode_responses": True,
        }

    def get_openai_config(self) -> dict[str, Any]:
        """Get OpenAI configuration."""
        return {
            "api_key": self.openai_api_key,
            "model": self.default_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    def get_upload_path(self) -> Path:
        """Get upload directory path."""
        upload_path = Path(self.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings) -> None:
    """Set the global settings instance."""
    global _settings
    _settings = settings


def load_settings_from_file(file_path: str) -> Settings:
    """Load settings from a file."""
    return Settings(_env_file=file_path)


def create_test_settings() -> Settings:
    """Create settings for testing."""
    return Settings(
        environment="testing",
        database_url="sqlite:///./test_echoes.db",
        redis_url="redis://localhost:6379/1",
        debug=True,
        rate_limit_enabled=False,
        metrics_enabled=False,
    )


if __name__ == "__main__":
    # Print current settings
    settings = get_settings()
    print("Echoes AI Configuration:")
    print(f"Environment: {settings.environment}")
    print(f"Database URL: {settings.database_url}")
    print(f"Redis URL: {settings.redis_url}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Rate Limiting: {settings.rate_limit_enabled}")
    print(f"Metrics: {settings.metrics_enabled}")
