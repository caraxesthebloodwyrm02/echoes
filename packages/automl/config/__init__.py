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

"""
AutoML Configuration - Centralized Configuration Management
Provides configuration validation, environment variable loading, and preset configurations.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union

from packages.core.config import Config


@dataclass
class AutoMLConfig:
    """Configuration for AutoML pipeline execution."""

    # Task configuration
    task_type: str = "classification"
    metric: str = "accuracy"

    # Model selection
    max_models: int = 10
    enable_ensemble_methods: bool = True

    # Hyperparameter tuning
    enable_hyperparameter_tuning: bool = True
    max_tuning_time_seconds: int = 300  # 5 minutes per model

    # Cross-validation
    cv_folds: int = 5
    test_size: float = 0.2

    # Feature engineering
    enable_feature_selection: bool = True
    max_features: Optional[int] = None

    # Computational resources
    random_state: int = 42
    n_jobs: int = -1  # Use all available cores

    # Time constraints
    max_time_seconds: int = 3600  # 1 hour total

    # Output and logging
    verbose: bool = True
    save_models: bool = True
    output_directory: str = "automl_results"

    # Advanced options
    early_stopping: bool = True
    feature_importance_method: str = "auto"  # auto, permutation, tree_based
    handle_imbalanced_data: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()

    def _validate_config(self):
        """Validate configuration parameters."""
        if self.task_type not in ["classification", "regression"]:
            raise ValueError(
                f"task_type must be 'classification' or 'regression', got {self.task_type}"
            )

        valid_metrics = {
            "classification": ["accuracy", "precision", "recall", "f1", "roc_auc"],
            "regression": ["r2", "mse", "mae", "rmse"],
        }

        if self.metric not in valid_metrics[self.task_type]:
            raise ValueError(f"metric '{self.metric}' not valid for {self.task_type}")

        if self.cv_folds < 2:
            raise ValueError("cv_folds must be at least 2")

        if not 0 < self.test_size < 1:
            raise ValueError("test_size must be between 0 and 1")

        if self.max_models < 1:
            raise ValueError("max_models must be at least 1")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AutoMLConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)

    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> "AutoMLConfig":
        """Load configuration from JSON file."""
        with open(json_path, "r") as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_env(cls) -> "AutoMLConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Override with environment variables if present
        env_mappings = {
            "AUTOML_TASK_TYPE": "task_type",
            "AUTOML_METRIC": "metric",
            "AUTOML_MAX_MODELS": ("max_models", int),
            "AUTOML_CV_FOLDS": ("cv_folds", int),
            "AUTOML_MAX_TIME": ("max_time_seconds", int),
            "AUTOML_RANDOM_STATE": ("random_state", int),
            "AUTOML_VERBOSE": ("verbose", lambda x: x.lower() in ("true", "1", "yes")),
        }

        for env_var, (attr_name, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if callable(converter):
                        setattr(config, attr_name, converter(value))
                    else:
                        setattr(config, attr_name, converter(value))
                except (ValueError, TypeError):
                    logging.warning(f"Invalid value for {env_var}: {value}")

        config._validate_config()
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)

    def to_json(self, json_path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        with open(json_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def save(self, path: Union[str, Path]) -> None:
        """Save configuration to file."""
        self.to_json(path)


class AutoMLConfigManager:
    """
    Configuration manager for AutoML with preset configurations and validation.

    Provides:
    - Preset configurations for common use cases
    - Configuration validation and suggestions
    - Environment-specific configurations
    - Configuration inheritance and overrides
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.presets = self._load_presets()

    def _load_presets(self) -> Dict[str, AutoMLConfig]:
        """Load preset configurations for common use cases."""
        return {
            "quick": AutoMLConfig(
                max_models=5,
                max_time_seconds=600,  # 10 minutes
                cv_folds=3,
                enable_hyperparameter_tuning=False,
                verbose=True,
            ),
            "balanced": AutoMLConfig(
                max_models=8,
                max_time_seconds=1800,  # 30 minutes
                cv_folds=5,
                enable_hyperparameter_tuning=True,
                max_tuning_time_seconds=120,  # 2 minutes per model
            ),
            "thorough": AutoMLConfig(
                max_models=15,
                max_time_seconds=7200,  # 2 hours
                cv_folds=10,
                enable_hyperparameter_tuning=True,
                max_tuning_time_seconds=600,  # 10 minutes per model
                enable_feature_selection=True,
                early_stopping=True,
            ),
            "production": AutoMLConfig(
                max_models=20,
                max_time_seconds=14400,  # 4 hours
                cv_folds=10,
                enable_hyperparameter_tuning=True,
                max_tuning_time_seconds=1800,  # 30 minutes per model
                enable_feature_selection=True,
                handle_imbalanced_data=True,
                early_stopping=True,
                save_models=True,
            ),
            "classification_binary": AutoMLConfig(
                task_type="classification", metric="f1", handle_imbalanced_data=True
            ),
            "classification_multiclass": AutoMLConfig(
                task_type="classification",
                metric="accuracy",
                handle_imbalanced_data=False,
            ),
            "regression_standard": AutoMLConfig(
                task_type="regression", metric="r2", enable_feature_selection=True
            ),
            "regression_robust": AutoMLConfig(
                task_type="regression",
                metric="mae",
                enable_feature_selection=True,
                handle_imbalanced_data=False,
            ),
        }

    def get_preset(self, preset_name: str) -> AutoMLConfig:
        """
        Get a preset configuration.

        Args:
            preset_name: Name of the preset configuration

        Returns:
            AutoMLConfig instance

        Raises:
            ValueError: If preset doesn't exist
        """
        if preset_name not in self.presets:
            available_presets = list(self.presets.keys())
            raise ValueError(
                f"Preset '{preset_name}' not found. Available presets: {available_presets}"
            )

        return self.presets[preset_name]

    def create_custom_config(
        self,
        base_preset: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> AutoMLConfig:
        """
        Create a custom configuration based on a preset with overrides.

        Args:
            base_preset: Base preset to start from (optional)
            overrides: Configuration overrides

        Returns:
            Custom AutoMLConfig instance
        """
        if base_preset:
            config = self.get_preset(base_preset)
            config_dict = config.to_dict()
        else:
            config_dict = AutoMLConfig().to_dict()

        # Apply overrides
        if overrides:
            config_dict.update(overrides)

        return AutoMLConfig.from_dict(config_dict)

    def suggest_config(
        self,
        dataset_info: Dict[str, Any],
        time_budget: Optional[int] = None,
        priority: str = "balanced",
    ) -> AutoMLConfig:
        """
        Suggest an appropriate configuration based on dataset characteristics.

        Args:
            dataset_info: Information about the dataset
            time_budget: Available time in seconds (optional)
            priority: Priority level ('speed', 'quality', 'balanced')

        Returns:
            Suggested AutoMLConfig
        """
        n_samples = dataset_info.get("n_samples", 1000)
        n_features = dataset_info.get("n_features", 10)
        task_type = dataset_info.get("task_type", "classification")

        # Base suggestion logic
        if n_samples < 100:
            # Very small dataset
            base_config = "quick"
        elif n_samples < 1000:
            # Small dataset
            base_config = "balanced"
        elif n_samples < 10000:
            # Medium dataset
            base_config = (
                "thorough" if time_budget and time_budget > 3600 else "balanced"
            )
        else:
            # Large dataset
            base_config = (
                "production" if time_budget and time_budget > 7200 else "thorough"
            )

        config = self.get_preset(base_config)

        # Adjust for time budget
        if time_budget:
            if time_budget < 600:  # Less than 10 minutes
                config.max_models = min(config.max_models, 3)
                config.enable_hyperparameter_tuning = False
            elif time_budget < 1800:  # Less than 30 minutes
                config.max_models = min(config.max_models, 5)

        # Adjust for task type
        if task_type == "classification":
            n_classes = dataset_info.get("n_classes", 2)
            if n_classes > 10:
                config.metric = "accuracy"  # For multiclass
            elif dataset_info.get("is_imbalanced", False):
                config.metric = "f1"
        elif task_type == "regression":
            if dataset_info.get("target_variance", 1.0) > 2.0:
                config.metric = "mae"  # More robust for high variance

        # Adjust for feature space
        if n_features > 100:
            config.enable_feature_selection = True
            config.max_features = min(n_features, 50)

        return config

    def validate_config_for_dataset(
        self, config: AutoMLConfig, dataset_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate configuration against dataset characteristics and provide recommendations.

        Args:
            config: Configuration to validate
            dataset_info: Dataset information

        Returns:
            Validation results with recommendations
        """
        issues = []
        recommendations = []

        n_samples = dataset_info.get("n_samples", 1000)
        n_features = dataset_info.get("n_features", 10)

        # Check cross-validation folds
        if config.cv_folds > n_samples:
            issues.append("CV folds exceed dataset size")
            recommendations.append(
                f"Reduce cv_folds to {min(config.cv_folds, max(2, n_samples // 10))}"
            )

        # Check test size
        if config.test_size * n_samples < 10:
            issues.append("Test set too small")
            recommendations.append("Increase test_size or reduce cv_folds")

        # Check model complexity vs dataset size
        if config.max_models > 15 and n_samples < 1000:
            recommendations.append("Consider reducing max_models for small dataset")

        # Check time constraints
        estimated_time = self._estimate_runtime(config, dataset_info)
        if estimated_time > config.max_time_seconds:
            issues.append("Estimated runtime exceeds time limit")
            recommendations.append(
                f"Increase max_time_seconds to at least {estimated_time}"
            )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "estimated_runtime": estimated_time,
        }

    def _estimate_runtime(
        self, config: AutoMLConfig, dataset_info: Dict[str, Any]
    ) -> int:
        """Estimate total runtime in seconds."""
        n_samples = dataset_info.get("n_samples", 1000)
        n_features = dataset_info.get("n_features", 10)

        # Base time per model (rough estimates)
        base_time_per_model = 30  # seconds

        # Adjust for dataset size
        if n_samples > 10000:
            base_time_per_model *= 3
        elif n_samples > 1000:
            base_time_per_model *= 2

        # Adjust for feature count
        if n_features > 100:
            base_time_per_model *= 2

        # Add hyperparameter tuning time
        if config.enable_hyperparameter_tuning:
            base_time_per_model += config.max_tuning_time_seconds

        # Total time
        total_time = (
            config.max_models * base_time_per_model * config.cv_folds / 5
        )  # Normalize for 5-fold CV

        return int(total_time)
