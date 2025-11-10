"""
Configuration management for Echoes API with Selective Attention

Provides centralized configuration for all API components including
Glimpse settings, security, performance parameters, and selective attention models.
"""

from pathlib import Path
from typing import Any
from pydantic_settings import BaseSettings

from echoes.utils.selective_attention import selective_attention


class SelectiveAttentionConfig(BaseSettings):
    """Configuration for selective attention models and algorithms"""

    # Model configurations
    attention_threshold: float = 0.5
    focus_criteria: str = (
        "even_numbers"  # even_numbers, high_value, semantic_similarity
    )
    enable_ml_explanation: bool = True

    # LIME and SHAP settings
    lime_num_features: int = 6
    shap_sample_size: int = 100

    # Visualization settings
    plot_style: str = "seaborn"
    color_scheme: str = "viridis"

    # Performance optimization
    batch_size: int = 32
    max_concurrent_attention: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class EngineConfig(BaseSettings):
    """Configuration for RAG Orbit engines"""

    # Embedding settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_cache_dir: str = ".cache/embeddings"
    embedding_batch_size: int = 32

    # Retrieval settings
    retrieval_index_type: str = "flat"  # flat or ivf
    retrieval_metric: str = "cosine"  # cosine or l2
    retrieval_top_k: int = 10

    # Chunking settings
    chunk_size: int = 512
    chunk_overlap: int = 50
    chunk_method: str = "sentence"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class SecurityConfig(BaseSettings):
    """Security and authentication configuration"""

    # API Keys
    openai_api_key: str | None = None
    # IMPORTANT: Set to True for production to require API key authentication
    api_key_required: bool = False  # DISABLED - Direct Connection  # Change to True for production
    allowed_api_keys: list = []

    # Rate limiting
    rate_limit_requests: int = 1000  # DISABLED - Direct Connection  # per minute
    rate_limit_window: int = 60  # seconds

    # CORS - Restricted for security (change for production)
    # In production, replace with specific allowed origins:
    # cors_origins: list = ["https://yourdomain.com", "https://app.yourdomain.com"]
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list = ["Content-Type", "Authorization", "X-API-Key"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class APIConfig(BaseSettings):
    """Main API server configuration"""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    reload: bool = True

    # Logging
    log_level: str = "INFO"

    # Performance
    max_concurrent_requests: int = 100
    request_timeout: int = 30  # seconds

    # WebSocket
    websocket_ping_interval: int = 20
    websocket_ping_timeout: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class PatternDetectionConfig(BaseSettings):
    """Configuration for pattern detection Glimpse"""

    min_confidence: float = 0.6
    max_patterns: int = 10
    enable_semantic_analysis: bool = True
    enable_statistical_analysis: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class SelfRAGConfig(BaseSettings):
    """Configuration for SELF-RAG truth verification"""

    min_evidence_threshold: float = 0.7
    contradiction_threshold: float = 0.8
    uncertainty_threshold: float = 0.4
    max_evidence_chunks: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class EchoesAPIConfig(BaseSettings):
    """Complete configuration for Echoes API with selective attention"""

    # Component configs
    api: APIConfig = APIConfig()
    engines: EngineConfig = EngineConfig()
    security: SecurityConfig = SecurityConfig()
    patterns: PatternDetectionConfig = PatternDetectionConfig()
    rag: SelfRAGConfig = SelfRAGConfig()
    attention: SelectiveAttentionConfig = SelectiveAttentionConfig()

    # Data paths
    data_dir: str = "data"
    models_dir: str = "models"
    logs_dir: str = "logs"
    attention_cache_dir: str = ".cache/attention"

    # Environment
    environment: str = "development"  # development, staging, production
    # Orchestral feature flags
    orchestral_enabled: bool = False
    orchestral_debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


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


def validate_config(cfg: EchoesAPIConfig) -> dict[str, Any]:
    """Validate configuration and return validation results with selective attention"""
    import logging

    logger = logging.getLogger(__name__)
    issues = []

    # Demonstrate selective attention in validation
    sample_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    attention_result = selective_attention(sample_numbers)
    logger.info("Selective attention validation: %s", attention_result)

    # Check required API keys
    if cfg.security.api_key_required and not cfg.security.allowed_api_keys:
        issues.append("API key authentication enabled but no allowed keys configured")

    # Check OpenAI API key for required features
    if not cfg.security.openai_api_key:
        issues.append("OpenAI API key not configured - some features may not work")

    # Check data directories
    data_path = Path(cfg.data_dir)
    if not data_path.exists():
        try:
            data_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            issues.append(f"Cannot create data directory: {e}")

    models_path = Path(cfg.models_dir)
    if not models_path.exists():
        try:
            models_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            issues.append(f"Cannot create models directory: {e}")

    logs_path = Path(cfg.logs_dir)
    if not logs_path.exists():
        try:
            logs_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            issues.append(f"Cannot create logs directory: {e}")

    # Check selective attention cache directory
    attention_cache_path = Path(cfg.attention_cache_dir)
    if not attention_cache_path.exists():
        try:
            attention_cache_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            issues.append(f"Cannot create attention cache directory: {e}")

    # Check Glimpse configurations
    if cfg.engines.embedding_model not in [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
    ]:
        issues.append(f"Unsupported embedding model: {cfg.engines.embedding_model}")

    if cfg.engines.retrieval_index_type not in ["flat", "ivf"]:
        issues.append(
            f"Unsupported retrieval index type: {cfg.engines.retrieval_index_type}"
        )

    # Validate selective attention configuration
    if (
        cfg.attention.attention_threshold < 0
        or cfg.attention.attention_threshold > 1
    ):
        issues.append("Attention threshold must be between 0 and 1")

    if cfg.attention.focus_criteria not in [
        "even_numbers",
        "high_value",
        "semantic_similarity",
    ]:
        issues.append(f"Unsupported focus criteria: {cfg.attention.focus_criteria}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config_summary": {
            "environment": cfg.environment,
            "host": cfg.api.host,
            "port": cfg.api.port,
            "engines_configured": True,
            "security_enabled": cfg.security.api_key_required,
            "selective_attention_enabled": True,
            "attention_threshold": cfg.attention.attention_threshold,
            "focus_criteria": cfg.attention.focus_criteria,
            "orchestral_enabled": getattr(cfg, "orchestral_enabled", False),
            "orchestral_debug": getattr(cfg, "orchestral_debug", False),
        },
        "selective_attention_demo": {
            "sample_input": sample_numbers,
            "attention_result": attention_result,
        },
    }


def setup_logging(cfg: EchoesAPIConfig):
    """Setup logging based on configuration"""
    import logging

    # Create logs directory if it doesn't exist
    logs_path = Path(cfg.logs_dir)
    logs_path.mkdir(parents=True, exist_ok=True)

    # Configure logging
    log_level = getattr(logging, cfg.api.log_level.upper(), logging.INFO)

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
