# ----------------------------------------------------------------------
# Centralised configuration – immutable once the module is imported
# ----------------------------------------------------------------------
import os
from dataclasses import dataclass

from pydantic import Field
from pydantic_settings import BaseSettings

# ----------------------------------------------------------------------
# Configuration Constants (maintained for backward compatibility)
# ----------------------------------------------------------------------
DEFAULT_MODEL = "gpt-4o-mini"
ALTERNATE_MODELS = {
    "mini": "gpt-4o-mini",
    "standard": "gpt-4o",
    "search": "gpt-4o-search-preview",
    "specialist": "o3",
    "specialist_mini": "o3-mini",
}
MAX_TOOL_ITERATIONS = 5
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4000

USE_RESPONSES_API: bool = os.getenv("USE_RESPONSES_API", "true").lower() in (
    "1",
    "true",
    "yes",
)


# ----------------------------------------------------------------------
# Unified Configuration System (BaseSettings)
# ----------------------------------------------------------------------
class CoreRuntimeConfig(BaseSettings):
    """Core runtime configuration using BaseSettings for environment variable support."""

    # Feature flags
    enable_rag: bool = Field(default=True, description="Enable RAG system")
    enable_tools: bool = Field(default=True, description="Enable tool framework")
    enable_streaming: bool = Field(
        default=True, description="Enable streaming responses"
    )
    enable_status: bool = Field(default=True, description="Enable status indicators")
    enable_glimpse: bool = Field(default=True, description="Enable Glimpse system")
    enable_external_contact: bool = Field(
        default=True, description="Enable external contact"
    )
    enable_value_system: bool = Field(default=True, description="Enable value system")
    enable_atlas_integration: bool = Field(
        default=True, description="Enable ATLAS integration"
    )
    enable_multimodal: bool = Field(
        default=True, description="Enable multimodal features"
    )
    enable_legal: bool = Field(default=True, description="Enable legal safeguards")

    # Session and model configuration
    session_id: str | None = Field(default=None, description="Session identifier")
    model: str | None = Field(
        default=None, description="Model name (overrides default)"
    )
    temperature: float | None = Field(
        default=None, description="Temperature (overrides default)"
    )
    max_tokens: int | None = Field(
        default=None, description="Max tokens (overrides default)"
    )

    # Model defaults (from environment or constants)
    default_model: str = Field(default=DEFAULT_MODEL, description="Default model")
    default_temperature: float = Field(
        default=DEFAULT_TEMPERATURE, description="Default temperature"
    )
    default_max_tokens: int = Field(
        default=DEFAULT_MAX_TOKENS, description="Default max tokens"
    )

    # Additional configuration
    use_responses_api: bool = Field(
        default=USE_RESPONSES_API,
        description="Use Responses API instead of Chat Completions",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


# ----------------------------------------------------------------------
# Backward compatibility: RuntimeOptions as dataclass
# ----------------------------------------------------------------------
# This maintains the existing API where RuntimeOptions is instantiated directly
# while allowing migration to BaseSettings-based configuration
@dataclass
class RuntimeOptions:
    """Simple data holder for runtime-wide options (backward compatibility).

    This dataclass is maintained for backward compatibility. New code should use
    CoreRuntimeConfig which supports environment variables and validation.
    """

    enable_rag: bool = True
    enable_tools: bool = True
    enable_streaming: bool = True
    enable_status: bool = True
    enable_glimpse: bool = True
    enable_external_contact: bool = True
    enable_value_system: bool = True
    enable_atlas_integration: bool = True
    enable_multimodal: bool = True
    enable_legal: bool = True
    session_id: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None

    @classmethod
    def from_config(cls, config: CoreRuntimeConfig) -> "RuntimeOptions":
        """Create RuntimeOptions from CoreRuntimeConfig."""
        return cls(
            enable_rag=config.enable_rag,
            enable_tools=config.enable_tools,
            enable_streaming=config.enable_streaming,
            enable_status=config.enable_status,
            enable_glimpse=config.enable_glimpse,
            enable_external_contact=config.enable_external_contact,
            enable_value_system=config.enable_value_system,
            enable_atlas_integration=config.enable_atlas_integration,
            enable_multimodal=config.enable_multimodal,
            enable_legal=config.enable_legal,
            session_id=config.session_id,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )


# ----------------------------------------------------------------------
# Global configuration instance (optional, for unified config access)
# ----------------------------------------------------------------------
_core_config: CoreRuntimeConfig | None = None


def get_core_config() -> CoreRuntimeConfig:
    """Get the global core configuration instance."""
    global _core_config
    if _core_config is None:
        _core_config = CoreRuntimeConfig()
    return _core_config
