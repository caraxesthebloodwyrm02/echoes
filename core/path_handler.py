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

"""
Smart Path Handler - Centralized, secure, cross-platform path management
Fixes: hardcoded paths, path traversal vulnerabilities, inconsistent handling
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class PathCategory(str, Enum):
    """Categorized path types for organized access"""

    DATA = "data"
    LOGS = "logs"
    TEMP = "temp"
    CACHE = "cache"
    CONFIG = "config"
    MODELS = "models"
    REPORTS = "reports"
    ARTIFACTS = "artifacts"
    OUTPUTS = "outputs"
    INPUTS = "inputs"
    BACKUPS = "backups"
    ARCHIVES = "archives"


class PathConfig(BaseSettings):
    """Validated path configuration"""

    model_config = SettingsConfigDict(
        env_prefix="PATH_",
        case_sensitive=False,
        extra="forbid",
    )

    # Root paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
        description="Project root directory",
    )

    # Standard directories
    data_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None
    temp_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    config_dir: Optional[Path] = None
    models_dir: Optional[Path] = None
    reports_dir: Optional[Path] = None
    artifacts_dir: Optional[Path] = None
    outputs_dir: Optional[Path] = None
    inputs_dir: Optional[Path] = None
    backups_dir: Optional[Path] = None
    archives_dir: Optional[Path] = None

    # Security settings
    allow_absolute_paths: bool = Field(default=False, description="Allow absolute paths (security risk)")
    enforce_sandbox: bool = Field(default=True, description="Enforce all paths stay within project root")
    auto_create_dirs: bool = Field(default=True, description="Automatically create directories if they don't exist")

    def model_post_init(self, __context):
        """Initialize directory paths after model creation"""
        # Set default directories relative to project root
        self.data_dir = self.data_dir or self.project_root / "data"
        self.logs_dir = self.logs_dir or self.project_root / "logs"
        self.temp_dir = self.temp_dir or self.project_root / "temp"
        self.cache_dir = self.cache_dir or self.data_dir / "cache"
        self.config_dir = self.config_dir or self.project_root / "config"
        self.models_dir = self.models_dir or self.project_root / "models"
        self.reports_dir = self.reports_dir or self.project_root / "reports"
        self.artifacts_dir = self.artifacts_dir or self.project_root / "artifacts"
        self.outputs_dir = self.outputs_dir or self.data_dir / "outputs"
        self.inputs_dir = self.inputs_dir or self.data_dir / "inputs"
        self.backups_dir = self.backups_dir or self.data_dir / "backups"
        self.archives_dir = self.archives_dir or self.data_dir / "archives"


class SmartPathHandler:
    """
    Centralized path handling with security, validation, and routing

    Features:
    - Path traversal attack prevention
    - Cross-platform compatibility
    - Automatic directory creation
    - Path normalization
    - Centralized routing
    - Path validation
    - Type safety
    """

    def __init__(self, config: Optional[PathConfig] = None):
        """Initialize smart path handler"""
        self.config = config or PathConfig()
        self.logger = logging.getLogger(__name__)

        # Build path registry
        self._registry: Dict[PathCategory, Path] = {
            PathCategory.DATA: self.config.data_dir,
            PathCategory.LOGS: self.config.logs_dir,
            PathCategory.TEMP: self.config.temp_dir,
            PathCategory.CACHE: self.config.cache_dir,
            PathCategory.CONFIG: self.config.config_dir,
            PathCategory.MODELS: self.config.models_dir,
            PathCategory.REPORTS: self.config.reports_dir,
            PathCategory.ARTIFACTS: self.config.artifacts_dir,
            PathCategory.OUTPUTS: self.config.outputs_dir,
            PathCategory.INPUTS: self.config.inputs_dir,
            PathCategory.BACKUPS: self.config.backups_dir,
            PathCategory.ARCHIVES: self.config.archives_dir,
        }

        # Auto-create directories if enabled
        if self.config.auto_create_dirs:
            self._create_standard_directories()

    def _create_standard_directories(self):
        """Create all standard directories"""
        for category, path in self._registry.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Ensured directory exists: {path}")
            except OSError as e:
                self.logger.error(f"Failed to create {category} directory at {path}: {e}")

    def _validate_path_security(self, path: Path) -> Path:
        """
        Validate path for security issues

        Prevents:
        - Path traversal attacks (../)
        - Symlink attacks
        - Accessing outside project root
        """
        try:
            # Resolve to absolute path
            resolved = path.resolve()

            # Check if path is within project root (sandbox)
            if self.config.enforce_sandbox:
                try:
                    resolved.relative_to(self.config.project_root)
                except ValueError:
                    raise SecurityError(f"Path '{path}' is outside project root: {self.config.project_root}")

            # Check for symlink attacks
            if resolved.is_symlink() and not self.config.allow_absolute_paths:
                raise SecurityError(f"Symlinks not allowed: {path}")

            return resolved

        except Exception as e:
            raise SecurityError(f"Path validation failed for '{path}': {e}")

    def get(
        self,
        category: Union[PathCategory, str],
        *parts: str,
        validate: bool = True,
        create: bool = False,
    ) -> Path:
        """
        Get path by category with optional subpaths

        Args:
            category: Path category (DATA, LOGS, etc.)
            *parts: Additional path components
            validate: Validate path security
            create: Create directory if it doesn't exist

        Returns:
            Resolved, validated Path object

        Example:
            >>> handler.get(PathCategory.DATA, "models", "checkpoint.pth")
            PosixPath('/path/to/project/data/models/checkpoint.pth')
        """
        # Convert string to enum if needed
        if isinstance(category, str):
            try:
                category = PathCategory(category.lower())
            except ValueError:
                raise ValueError(f"Unknown path category: {category}")

        # Get base path
        base_path = self._registry.get(category)
        if base_path is None:
            raise ValueError(f"No path configured for category: {category}")

        # Build full path
        full_path = base_path.joinpath(*parts) if parts else base_path

        # Validate security
        if validate:
            full_path = self._validate_path_security(full_path)

        # Create directory if requested
        if create:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        return full_path

    def resolve(
        self,
        path: Union[str, Path],
        relative_to: Optional[PathCategory] = None,
        validate: bool = True,
    ) -> Path:
        """
        Resolve any path safely

        Args:
            path: Path to resolve (str or Path)
            relative_to: Treat as relative to this category
            validate: Validate path security

        Returns:
            Resolved Path object
        """
        # Convert to Path
        path_obj = Path(path) if isinstance(path, str) else path

        # Handle relative paths
        if not path_obj.is_absolute() and relative_to:
            base = self._registry.get(relative_to)
            if base:
                path_obj = base / path_obj

        # Make absolute if not already
        if not path_obj.is_absolute():
            path_obj = self.config.project_root / path_obj

        # Validate
        if validate:
            path_obj = self._validate_path_security(path_obj)

        return path_obj

    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists, creating if necessary"""
        path_obj = Path(path) if isinstance(path, str) else path
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj

    def safe_join(self, base: Union[str, Path], *parts: str) -> Path:
        """
        Safely join path components (prevents path traversal)

        Args:
            base: Base path
            *parts: Path components to join

        Returns:
            Validated joined path
        """
        base_path = Path(base) if isinstance(base, str) else base
        joined = base_path.joinpath(*parts)
        return self._validate_path_security(joined)

    def list_files(self, category: PathCategory, pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        List files in a category directory

        Args:
            category: Path category to search
            pattern: Glob pattern (default: "*")
            recursive: Search recursively

        Returns:
            List of matching Path objects
        """
        base_path = self._registry.get(category)
        if not base_path or not base_path.exists():
            return []

        try:
            if recursive:
                return list(base_path.rglob(pattern))
            else:
                return list(base_path.glob(pattern))
        except Exception as e:
            self.logger.error(f"Error listing files in {category}: {e}")
            return []

    def get_stats(self) -> Dict[str, any]:
        """Get path handler statistics"""
        stats = {
            "project_root": str(self.config.project_root),
            "directories": {},
            "security": {
                "sandbox_enabled": self.config.enforce_sandbox,
                "absolute_paths_allowed": self.config.allow_absolute_paths,
            },
        }

        for category, path in self._registry.items():
            stats["directories"][category.value] = {
                "path": str(path),
                "exists": path.exists(),
                "is_dir": path.is_dir() if path.exists() else False,
            }

        return stats

    def cleanup_temp(self, max_age_days: int = 7) -> int:
        """
        Clean up old temporary files

        Args:
            max_age_days: Remove files older than this many days

        Returns:
            Number of files removed
        """
        import time

        temp_dir = self._registry[PathCategory.TEMP]
        if not temp_dir.exists():
            return 0

        cutoff_time = time.time() - (max_age_days * 86400)
        removed_count = 0

        try:
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    removed_count += 1
                    self.logger.info(f"Removed old temp file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error during temp cleanup: {e}")

        return removed_count


class SecurityError(Exception):
    """Raised when path security validation fails"""

    pass


# Global path handler instance
_path_handler: Optional[SmartPathHandler] = None


def get_path_handler(reload: bool = False) -> SmartPathHandler:
    """Get or create global path handler instance"""
    global _path_handler
    if _path_handler is None or reload:
        _path_handler = SmartPathHandler()
    return _path_handler


# Convenience functions
def get_path(category: Union[PathCategory, str], *parts: str, **kwargs) -> Path:
    """Convenience function for getting paths"""
    return get_path_handler().get(category, *parts, **kwargs)


def resolve_path(path: Union[str, Path], **kwargs) -> Path:
    """Convenience function for resolving paths"""
    return get_path_handler().resolve(path, **kwargs)


def ensure_dir(path: Union[str, Path]) -> Path:
    """Convenience function for ensuring directory exists"""
    return get_path_handler().ensure_dir(path)


__all__ = [
    "SmartPathHandler",
    "PathConfig",
    "PathCategory",
    "SecurityError",
    "get_path_handler",
    "get_path",
    "resolve_path",
    "ensure_dir",
]
