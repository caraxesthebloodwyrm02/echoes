"""Configuration management for the automation framework."""

from pathlib import Path
from typing import Any, Dict, Union

import yaml


class Config:
    """Configuration manager for the automation framework."""

    def __init__(self, config_path: Union[str, Path]):
        """Initialize with path to configuration file.

        Args:
            config_path: Path to the configuration file (YAML or JSON)

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is not valid YAML
        """
        self.config_path = Path(config_path).resolve()
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            # Use an empty config if the file doesn't exist
            self._config = {}
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            # If there's an error parsing the YAML, use an empty config
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot notation.

        Args:
            key: Dot-notation key (e.g., 'database.host')
            default: Default value if key not found

        Returns:
            The configuration value or default if not found
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_section(
        self, section: str, default: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a configuration section.

        Args:
            section: Section name
            default: Default value if section not found

        Returns:
            The configuration section or default if not found
        """
        return self.get(section, default or {})

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

    def __getitem__(self, key: str) -> Any:
        """Get a configuration value using dict-style access."""
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists.

        Args:
            key: Dot-notation key to check (e.g., 'framework.version')

        Returns:
            bool: True if the key exists, False otherwise
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                if k not in value:
                    return False
                value = value[k]
            return True
        except (KeyError, TypeError):
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Get the entire configuration as a dictionary."""
        return self._config.copy()
