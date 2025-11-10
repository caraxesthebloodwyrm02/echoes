"""
Tests for API configuration management.
"""

from pathlib import Path

from api.config import (
    APIConfig,
    EchoesAPIConfig,
    EngineConfig,
    PatternDetectionConfig,
    SecurityConfig,
    SelfRAGConfig,
    get_config,
    load_config_from_env,
    setup_logging,
    validate_config,
)


class TestEngineConfig:
    """Test EngineConfig class."""

    def test_engine_config_defaults(self):
        """Test EngineConfig with default values."""
        config = EngineConfig()
        assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.embedding_cache_dir == ".cache/embeddings"
        assert config.embedding_batch_size == 32
        assert config.retrieval_index_type == "flat"
        assert config.retrieval_metric == "cosine"
        assert config.retrieval_top_k == 10
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.chunk_method == "sentence"


class TestSecurityConfig:
    """Test SecurityConfig class."""

    def test_security_config_defaults(self):
        """Test SecurityConfig with default values."""
        config = SecurityConfig()
        # OPENAI_API_KEY is loaded from .env file, so just check it's a string or None
        assert config.openai_api_key is None or isinstance(config.openai_api_key, str)
        assert config.api_key_required is False
        assert config.allowed_api_keys == []
        assert config.rate_limit_requests == 60
        assert config.rate_limit_window == 60
        assert config.cors_origins == ["*"]
        assert config.cors_allow_credentials is True


class TestAPIConfig:
    """Test APIConfig class."""

    def test_api_config_defaults(self):
        """Test APIConfig with default values."""
        config = APIConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.workers == 1
        assert config.reload is True
        assert config.log_level == "INFO"
        assert config.max_concurrent_requests == 100
        assert config.request_timeout == 30


class TestPatternDetectionConfig:
    """Test PatternDetectionConfig class."""

    def test_pattern_config_defaults(self):
        """Test PatternDetectionConfig with default values."""
        config = PatternDetectionConfig()
        assert config.min_confidence == 0.6
        assert config.max_patterns == 10
        assert config.enable_semantic_analysis is True
        assert config.enable_statistical_analysis is True


class TestSelfRAGConfig:
    """Test SelfRAGConfig class."""

    def test_rag_config_defaults(self):
        """Test SelfRAGConfig with default values."""
        config = SelfRAGConfig()
        assert config.min_evidence_threshold == 0.7
        assert config.contradiction_threshold == 0.8
        assert config.uncertainty_threshold == 0.4
        assert config.max_evidence_chunks == 10


class TestEchoesAPIConfig:
    """Test EchoesAPIConfig class."""

    def test_echoes_config_defaults(self):
        """Test EchoesAPIConfig with default values."""
        config = EchoesAPIConfig()
        assert config.data_dir == "data"
        assert config.models_dir == "models"
        assert config.logs_dir == "logs"
        assert config.environment == "development"
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.engines, EngineConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.patterns, PatternDetectionConfig)
        assert isinstance(config.rag, SelfRAGConfig)


class TestConfigFunctions:
    """Test configuration utility functions."""

    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, EchoesAPIConfig)

    def test_load_config_from_env(self):
        """Test load_config_from_env function."""
        config = load_config_from_env()
        assert isinstance(config, EchoesAPIConfig)

    def test_validate_config_valid(self):
        """Test validate_config with valid configuration."""
        config = EchoesAPIConfig()
        result = validate_config(config)
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert "config_summary" in result

    def test_setup_logging(self, tmp_path):
        """Test setup_logging function."""
        config = EchoesAPIConfig()
        config.logs_dir = str(tmp_path / "logs")
        logger = setup_logging(config)
        assert logger is not None
        # Check that logs directory was created
        logs_path = Path(config.logs_dir)
        assert logs_path.exists()
