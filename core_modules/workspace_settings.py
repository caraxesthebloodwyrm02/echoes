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

# MIT License
#
# Copyright (c) 2025 Echoes Project
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

"""
Unified Workspace Settings with Stability and Security Hardening
Fixes: Timeout issues, schema validation, memory leaks, and shady settings
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StabilitySettings(BaseSettings):
    """Stability and timeout settings to prevent hangs and crashes"""

    model_config = SettingsConfigDict(
        env_prefix="STABILITY_",
        case_sensitive=False,
        extra="forbid",  # CRITICAL: No extra fields allowed
    )

    # Timeout settings (milliseconds)
    max_response_time_ms: int = Field(
        default=30000,
        ge=5000,
        le=120000,
        description="Maximum time to wait for AI response",
    )
    request_timeout_ms: int = Field(default=60000, ge=10000, le=300000, description="Overall request timeout")
    idle_timeout_ms: int = Field(
        default=300000,
        ge=60000,
        le=1800000,
        description="Idle timeout before auto-save",
    )

    # Memory management
    max_memory_mb: int = Field(default=2048, ge=512, le=8192, description="Maximum memory usage in MB")
    gc_interval_ms: int = Field(default=60000, ge=10000, le=300000, description="Garbage collection interval")

    # Health checks
    health_check_interval_ms: int = Field(default=10000, ge=5000, le=60000, description="Health check interval")
    auto_save_interval_ms: int = Field(default=30000, ge=10000, le=120000, description="Auto-save interval")


class AIProviderSettings(BaseSettings):
    """AI Provider configuration with proper timeouts and rate limiting"""

    model_config = SettingsConfigDict(
        env_prefix="AI_",
        case_sensitive=False,
        extra="forbid",
    )

    # Provider settings
    provider: str = Field(default="openai", description="AI provider (openai, azure, ollama)")
    model_primary: str = Field(default="gpt-4o-mini", description="Primary model")
    model_fallback: str = Field(default="gpt-4o", description="Fallback model")

    # API Keys (validated separately)
    api_key_primary: Optional[str] = Field(default=None, description="Primary API key")
    api_key_secondary: Optional[str] = Field(default=None, description="Secondary API key for failover")

    # Timeout and retry settings
    timeout_ms: int = Field(
        default=45000,
        ge=5000,
        le=120000,
        description="API call timeout in milliseconds",
    )
    max_retries: int = Field(default=3, ge=0, le=5, description="Maximum retry attempts")
    retry_delay_ms: int = Field(default=1000, ge=100, le=5000, description="Delay between retries")

    # Rate limiting (CRITICAL for stability)
    requests_per_minute: int = Field(default=50, ge=1, le=500, description="Max requests per minute")
    tokens_per_minute: int = Field(default=40000, ge=1000, le=200000, description="Max tokens per minute")

    # Model parameters
    max_tokens: int = Field(default=4096, ge=256, le=128000, description="Maximum tokens per response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v):
        allowed = {"openai", "azure", "ollama", "gemini"}
        if v.lower() not in allowed:
            raise ValueError(f"Provider must be one of {allowed}")
        return v.lower()


class SecuritySettings(BaseSettings):
    """Security hardening settings"""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        case_sensitive=False,
        extra="forbid",
    )

    # Schema validation
    validate_schemas: bool = Field(default=True, description="Validate all data against schemas")
    strict_mode: bool = Field(default=True, description="Enable strict validation mode")
    allow_extra_fields: bool = Field(default=False, description="Allow extra fields in data (DANGEROUS if True)")

    # Input sanitization
    sanitize_inputs: bool = Field(default=True, description="Sanitize all user inputs")
    max_input_length: int = Field(
        default=100000,
        ge=1000,
        le=1000000,
        description="Maximum input length in characters",
    )

    # API security
    require_api_keys: bool = Field(default=True, description="Require API keys for operations")
    rotate_keys_days: int = Field(default=90, ge=30, le=365, description="Days before key rotation reminder")


class PerformanceSettings(BaseSettings):
    """Performance optimization settings"""

    model_config = SettingsConfigDict(
        env_prefix="PERF_",
        case_sensitive=False,
        extra="forbid",
    )

    # Concurrency
    parallel_requests: int = Field(default=4, ge=1, le=20, description="Maximum parallel requests")
    batch_size: int = Field(default=10, ge=1, le=100, description="Batch processing size")

    # Debouncing
    debounce_ms: int = Field(default=300, ge=0, le=5000, description="Debounce delay in milliseconds")

    # Caching
    cache_enabled: bool = Field(default=True, description="Enable response caching")
    max_cache_size_mb: int = Field(default=512, ge=64, le=4096, description="Maximum cache size in MB")
    cache_ttl_seconds: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")

    # Loading strategies
    lazy_loading: bool = Field(default=True, description="Enable lazy loading")
    prefetch: bool = Field(default=True, description="Enable prefetching")


class WorkspaceSettings(BaseSettings):
    """Unified workspace settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",  # CRITICAL: Prevent shady settings
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Environment (development, staging, production)",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Workspace paths
    workspace_root: Path = Field(default_factory=lambda: Path.cwd(), description="Workspace root directory")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_to_file: bool = Field(default=True, description="Enable file logging")
    log_max_size_mb: int = Field(default=10, ge=1, le=100, description="Max log file size")

    # Features
    enable_knowledge_graph: bool = Field(default=True, description="Enable knowledge graph integration")
    enable_semantic_search: bool = Field(default=True, description="Enable semantic search")
    enable_agent_orchestration: bool = Field(default=True, description="Enable agent orchestration")

    # Telemetry (DISABLED by default for stability)
    enable_telemetry: bool = Field(default=False, description="Enable telemetry collection")
    enable_crash_reporting: bool = Field(default=False, description="Enable crash reporting")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v.lower()


class UnifiedSettings:
    """Unified settings manager with validation and safety checks"""

    def __init__(self):
        self.workspace = WorkspaceSettings()
        self.stability = StabilitySettings()
        self.ai = AIProviderSettings()
        self.security = SecuritySettings()
        self.performance = PerformanceSettings()

        # Setup logging
        self._setup_logging()

        # Validate configuration
        self._validate_configuration()

    def _setup_logging(self):
        """Setup logging with proper configuration"""
        logging.basicConfig(
            level=getattr(logging, self.workspace.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                (
                    logging.FileHandler(self.workspace.workspace_root / "logs" / "workspace.log")
                    if self.workspace.log_to_file
                    else logging.NullHandler()
                ),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _validate_configuration(self):
        """Validate configuration for stability issues"""
        issues = []

        # Check for missing API keys
        if self.security.require_api_keys:
            if not self.ai.api_key_primary:
                issues.append("WARNING: Primary API key not set (OPENAI_API_KEY or AI_API_KEY_PRIMARY)")

        # Check timeout settings
        if self.ai.timeout_ms > self.stability.request_timeout_ms:
            issues.append(
                f"ERROR: AI timeout ({self.ai.timeout_ms}ms) exceeds request timeout "
                f"({self.stability.request_timeout_ms}ms)"
            )

        # Check rate limits
        if self.ai.requests_per_minute > 100:
            issues.append(
                f"WARNING: High request rate ({self.ai.requests_per_minute}/min) " "may cause stability issues"
            )

        # Check memory limits
        if self.stability.max_memory_mb < 512:
            issues.append(f"WARNING: Low memory limit ({self.stability.max_memory_mb}MB) " "may cause crashes")

        # Check dangerous settings
        if self.security.allow_extra_fields:
            issues.append("CRITICAL: allow_extra_fields=True is a security risk!")

        # Log issues
        for issue in issues:
            if issue.startswith("CRITICAL") or issue.startswith("ERROR"):
                self.logger.error(issue)
            else:
                self.logger.warning(issue)

        return issues

    def get_settings_summary(self) -> Dict[str, Any]:
        """Get settings summary for diagnostics"""
        return {
            "workspace": {
                "environment": self.workspace.environment,
                "debug": self.workspace.debug,
                "root": str(self.workspace.workspace_root),
            },
            "stability": {
                "response_timeout_ms": self.stability.max_response_time_ms,
                "request_timeout_ms": self.stability.request_timeout_ms,
                "max_memory_mb": self.stability.max_memory_mb,
            },
            "ai": {
                "provider": self.ai.provider,
                "model": self.ai.model_primary,
                "timeout_ms": self.ai.timeout_ms,
                "max_retries": self.ai.max_retries,
                "rate_limit": {
                    "requests_per_minute": self.ai.requests_per_minute,
                    "tokens_per_minute": self.ai.tokens_per_minute,
                },
            },
            "security": {
                "strict_mode": self.security.strict_mode,
                "validate_schemas": self.security.validate_schemas,
                "allow_extra_fields": self.security.allow_extra_fields,
            },
            "performance": {
                "parallel_requests": self.performance.parallel_requests,
                "cache_enabled": self.performance.cache_enabled,
                "cache_size_mb": self.performance.max_cache_size_mb,
            },
        }

    def get_problematic_settings(self) -> List[Dict[str, Any]]:
        """Identify problematic settings that could cause stability issues"""
        problems = []

        # Check for infinite timeout (None or 0)
        if self.ai.timeout_ms <= 0:
            problems.append(
                {
                    "severity": "CRITICAL",
                    "setting": "ai.timeout_ms",
                    "value": self.ai.timeout_ms,
                    "issue": "Infinite timeout can cause hangs",
                    "fix": "Set to 45000 (45 seconds)",
                }
            )

        # Check for missing rate limits
        if self.ai.requests_per_minute > 100:
            problems.append(
                {
                    "severity": "HIGH",
                    "setting": "ai.requests_per_minute",
                    "value": self.ai.requests_per_minute,
                    "issue": "Excessive requests can trigger rate limits",
                    "fix": "Reduce to 50 or lower",
                }
            )

        # Check for extra fields allowed
        if self.security.allow_extra_fields:
            problems.append(
                {
                    "severity": "CRITICAL",
                    "setting": "security.allow_extra_fields",
                    "value": True,
                    "issue": "Allows unvalidated data to enter system",
                    "fix": "Set to False",
                }
            )

        # Check for disabled validation
        if not self.security.validate_schemas:
            problems.append(
                {
                    "severity": "HIGH",
                    "setting": "security.validate_schemas",
                    "value": False,
                    "issue": "Skips schema validation",
                    "fix": "Set to True",
                }
            )

        # Check memory limits
        if self.stability.max_memory_mb < 512:
            problems.append(
                {
                    "severity": "MEDIUM",
                    "setting": "stability.max_memory_mb",
                    "value": self.stability.max_memory_mb,
                    "issue": "Insufficient memory may cause crashes",
                    "fix": "Increase to 2048 MB",
                }
            )

        return problems


# Global settings instance
_settings: Optional[UnifiedSettings] = None


def get_settings(reload: bool = False) -> UnifiedSettings:
    """Get or create unified settings instance"""
    global _settings
    if _settings is None or reload:
        _settings = UnifiedSettings()
    return _settings


def validate_workspace_settings() -> Dict[str, Any]:
    """Validate workspace settings and return diagnostic report"""
    settings = get_settings()
    problems = settings.get_problematic_settings()
    validation_issues = settings._validate_configuration()

    return {
        "status": "CRITICAL" if any(p["severity"] == "CRITICAL" for p in problems) else "OK",
        "problems": problems,
        "validation_issues": validation_issues,
        "summary": settings.get_settings_summary(),
    }


__all__ = [
    "UnifiedSettings",
    "WorkspaceSettings",
    "StabilitySettings",
    "AIProviderSettings",
    "SecuritySettings",
    "PerformanceSettings",
    "get_settings",
    "validate_workspace_settings",
]
