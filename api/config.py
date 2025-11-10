"""
Configuration management for Echoes API

Provides centralized configuration for all API components including
Glimpse settings, security, and performance parameters.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from pathlib import Path


class EngineConfig(BaseSettings):
    """Configuration for RAG Orbit engines"""

    # Embedding settings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL"
    )
    embedding_cache_dir: str = Field(
        default=".cache/embeddings", env="EMBEDDING_CACHE_DIR"
    )
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")

    # Retrieval settings
    retrieval_index_type: str = Field(
        default="flat", env="RETRIEVAL_INDEX_TYPE"
    )  # flat or ivf
    retrieval_metric: str = Field(
        default="cosine", env="RETRIEVAL_METRIC"
    )  # cosine or l2
    retrieval_top_k: int = Field(default=10, env="RETRIEVAL_TOP_K")

    # Chunking settings
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    chunk_method: str = Field(default="sentence", env="CHUNK_METHOD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SecurityConfig(BaseSettings):
    """Security and authentication configuration"""

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    api_key_required: bool = Field(default=False, env="API_KEY_REQUIRED")
    allowed_api_keys: list = Field(default_factory=list, env="ALLOWED_API_KEYS")

    # Rate limiting
    rate_limit_requests: int = Field(
        default=60, env="RATE_LIMIT_REQUESTS"
    )  # per minute
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds

    # CORS
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: list = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: list = Field(default=["*"], env="CORS_ALLOW_HEADERS")


class APIConfig(BaseSettings):
    """Main API server configuration"""

    # Server settings
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=True, env="API_RELOAD")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Performance
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")  # seconds

    # WebSocket
    websocket_ping_interval: int = Field(default=20, env="WEBSOCKET_PING_INTERVAL")
    websocket_ping_timeout: int = Field(default=20, env="WEBSOCKET_PING_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class PatternDetectionConfig(BaseSettings):
    """Configuration for pattern detection Glimpse"""

    min_confidence: float = Field(default=0.6, env="PATTERN_MIN_CONFIDENCE")
    max_patterns: int = Field(default=10, env="PATTERN_MAX_PATTERNS")
    enable_semantic_analysis: bool = Field(default=True, env="PATTERN_SEMANTIC_ENABLED")
    enable_statistical_analysis: bool = Field(
        default=True, env="PATTERN_STATISTICAL_ENABLED"
    )


class SelfRAGConfig(BaseSettings):
    """Configuration for SELF-RAG truth verification"""

    min_evidence_threshold: float = Field(default=0.7, env="RAG_MIN_EVIDENCE_THRESHOLD")
    contradiction_threshold: float = Field(
        default=0.8, env="RAG_CONTRADICTION_THRESHOLD"
    )
    uncertainty_threshold: float = Field(default=0.4, env="RAG_UNCERTAINTY_THRESHOLD")
    max_evidence_chunks: int = Field(default=10, env="RAG_MAX_EVIDENCE_CHUNKS")


class EchoesAPIConfig(BaseSettings):
    """Complete configuration for Echoes API"""

    # Component configs
    api: APIConfig = APIConfig()
    engines: EngineConfig = EngineConfig()
    security: SecurityConfig = SecurityConfig()
    patterns: PatternDetectionConfig = PatternDetectionConfig()
    rag: SelfRAGConfig = SelfRAGConfig()

    # Data paths
    data_dir: str = Field(default="data", env="DATA_DIR")
    models_dir: str = Field(default="models", env="MODELS_DIR")
    logs_dir: str = Field(default="logs", env="LOGS_DIR")

    # Environment
    environment: str = Field(
        default="development", env="ENVIRONMENT"
    )  # development, staging, production

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global configuration instance
config = None


def get_config() -> EchoesAPIConfig:
    """Get the global configuration instance"""
    global config
    if config is None:
        config = EchoesAPIConfig()
    return config


def load_config_from_env() -> EchoesAPIConfig:
    """Load configuration from environment variables"""
    return EchoesAPIConfig()


def validate_config(config: EchoesAPIConfig) -> Dict[str, Any]:
    """Validate configuration and return validation results"""
    issues = []

    # Check required API keys
    if config.security.api_key_required and not config.security.allowed_api_keys:
        issues.append("API key authentication enabled but no allowed keys configured")

    # Check OpenAI API key for required features
    if not config.security.openai_api_key:
        issues.append("OpenAI API key not configured - some features may not work")

    # Check data directories
    data_path = Path(config.data_dir)
    if not data_path.exists():
        try:
            data_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create data directory: {e}")

    models_path = Path(config.models_dir)
    if not models_path.exists():
        try:
            models_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create models directory: {e}")

    logs_path = Path(config.logs_dir)
    if not logs_path.exists():
        try:
            logs_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create logs directory: {e}")

    # Check Glimpse configurations
    if config.engines.embedding_model not in [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
    ]:
        issues.append(f"Unsupported embedding model: {config.engines.embedding_model}")

    if config.engines.retrieval_index_type not in ["flat", "ivf"]:
        issues.append(
            f"Unsupported retrieval index type: {config.engines.retrieval_index_type}"
        )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config_summary": {
            "environment": config.environment,
            "host": config.api.host,
            "port": config.api.port,
            "engines_configured": True,
            "security_enabled": config.security.api_key_required,
        },
    }


def setup_logging(config: EchoesAPIConfig):
    """Setup logging based on configuration"""
    import logging
    from pathlib import Path

    # Create logs directory if it doesn't exist
    logs_path = Path(config.logs_dir)
    logs_path.mkdir(parents=True, exist_ok=True)

    # Configure logging
    log_level = getattr(logging, config.api.log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # File handler
    log_file = logs_path / "api.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger


# Initialize configuration on import
config = get_config()
