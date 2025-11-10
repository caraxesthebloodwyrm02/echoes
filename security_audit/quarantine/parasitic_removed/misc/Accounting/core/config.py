"""Configuration management for AAE framework."""
import os
from pathlib import Path
from typing import Any


class AAEConfig:
    """Configuration manager for AAE experiments."""

    def __init__(self, config_file: str | None = None):
        self.config_file = config_file or self._get_default_config_path()
        self._config = {}
        self.load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        return os.path.join(Path(__file__).parent.parent, "config", "aae_config.json")

    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                import json

                with open(self.config_file) as f:
                    self._config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            self._config = self._get_default_config()

    def save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            import json

            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "experiment": {
                "default_duration_hours": 8,
                "max_duration_hours": 48,
                "min_participants_per_group": 1,
                "max_participants_per_group": 10,
            },
            "dataset": {
                "default_years": 2,
                "max_years": 5,
                "default_transaction_volume": "medium",
                "supported_sizes": ["small", "medium", "large"],
            },
            "ai_platform": {
                "default_model": "gpt-4",
                "timeout_seconds": 300,
                "max_retries": 3,
                "confidence_threshold": 0.7,
            },
            "metrics": {
                "enable_real_time_tracking": True,
                "save_intermediate_results": True,
                "generate_reports": True,
                "report_formats": ["json", "csv", "html"],
            },
            "security": {
                "enable_audit_logging": True,
                "anonymize_participant_data": True,
                "encrypt_sensitive_data": True,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value

    def validate_experiment_config(self, config: dict[str, Any]) -> bool:
        """Validate experiment configuration."""
        required_keys = ["name", "groups"]

        # Check required keys
        for key in required_keys:
            if key not in config:
                return False

        # Validate groups
        valid_groups = ["human", "ai", "hybrid", "oracle"]
        for group in config["groups"]:
            if group not in valid_groups:
                return False

        # Validate duration
        duration = config.get("duration_hours", 8)
        if not (1 <= duration <= self.get("experiment.max_duration_hours", 48)):
            return False

        return True

    def validate_dataset_config(self, config: dict[str, Any]) -> bool:
        """Validate dataset configuration."""
        years = config.get("years", 2)
        if not (1 <= years <= self.get("dataset.max_years", 5)):
            return False

        size = config.get("transaction_volume", "medium")
        if size not in self.get(
            "dataset.supported_sizes", ["small", "medium", "large"]
        ):
            return False

        return True
