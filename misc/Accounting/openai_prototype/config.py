"""Configuration for OpenAI AAE Prototype."""
import os
from pydantic import BaseSettings, Field

class OpenAIConfig(BaseSettings):
    """Configuration settings for OpenAI integration."""
    
    # OpenAI API settings
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    openai_vision_model: str = Field("gpt-4o", env="OPENAI_VISION_MODEL")
    openai_temperature: float = Field(0.0, env="OPENAI_TEMPERATURE")
    
    # Processing settings
    max_batch_size: int = Field(100, env="MAX_BATCH_SIZE")
    max_file_size_mb: int = Field(10, env="MAX_FILE_SIZE_MB")
    request_timeout_seconds: int = Field(300, env="REQUEST_TIMEOUT_SECONDS")
    
    # Rate limiting
    requests_per_minute: int = Field(60, env="REQUESTS_PER_MINUTE")
    tokens_per_minute: int = Field(100000, env="TOKENS_PER_MINUTE")
    
    # Feature flags
    enable_vision: bool = Field(True, env="ENABLE_VISION")
    enable_policies: bool = Field(True, env="ENABLE_POLICIES")
    enable_explanations: bool = Field(True, env="ENABLE_EXPLANATIONS")
    
    class Config:
        env_file = ".env"
        extra = "forbid"

# Global config instance
config = OpenAIConfig()
