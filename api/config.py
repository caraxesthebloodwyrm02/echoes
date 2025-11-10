"""
API configuration module.
"""

from typing import Dict, List

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class SecurityConfig(BaseSettings):
    """Security configuration settings."""

    jwt_secret: str = "your-jwt-secret"
    token_expiration: int = 3600  # seconds
    allowed_origins: List[str] = ["*"]
    cors_enabled: bool = True

    # Authentication
    api_key_required: bool = False
    allowed_api_keys: List[str] = []

    # Rate limiting
    rate_limit: int = 100  # legacy field (requests per minute)
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 60  # seconds

    model_config = ConfigDict(extra="allow", env_prefix="SEC_")


class EngineConfig(BaseModel):
    """Engine configuration settings."""

    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.95
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0

    model_config = ConfigDict(extra="allow")


class APIConfig(BaseSettings):
    """Main API configuration."""

    debug: bool = False
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    # Security settings
    security: SecurityConfig = SecurityConfig()

    # Engine settings
    engine: EngineConfig = EngineConfig()

    # Monitoring
    enable_monitoring: bool = True
    metrics_port: int = 9090

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Custom settings
    custom_settings: Dict = {}

    model_config = ConfigDict(extra="allow", env_prefix="API_")

    def update_engine_settings(self, **kwargs) -> None:
        """Update engine settings."""
        for key, value in kwargs.items():
            if hasattr(self.engine, key):
                setattr(self.engine, key, value)

    def update_security_settings(self, **kwargs) -> None:
        """Update security settings."""
        for key, value in kwargs.items():
            if hasattr(self.security, key):
                setattr(self.security, key, value)
