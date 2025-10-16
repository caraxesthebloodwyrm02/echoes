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
AutoML Core Orchestrator - Automated Machine Learning Pipeline
Handles end-to-end ML pipeline automation with model selection, hyperparameter tuning,
and performance optimization.
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator

from packages.automl.config import AutoMLConfig
from packages.automl.evaluation.model_evaluator import ModelEvaluator
from packages.automl.models.model_registry import ModelRegistry
from packages.automl.pipeline.hyperparameter_tuner import HyperparameterTuner
from packages.automl.pipeline.model_selector import ModelSelector


@dataclass
class AutoMLResult:
    """Results from AutoML pipeline execution."""

    best_model: BaseEstimator
    best_score: float
    best_params: Dict[str, Any]
    model_rankings: List[Dict[str, Any]]
    training_time: float
    evaluation_metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    pipeline_metadata: Optional[Dict[str, Any]] = None


class AutoMLOrchestrator:
    """
    Main AutoML orchestrator that manages the complete automated ML pipeline.

    This class coordinates:
    - Data preprocessing and validation
    - Model selection from multiple algorithms
    - Hyperparameter optimization
    - Cross-validation and evaluation
    - Feature importance analysis
    - Model persistence and deployment preparation
    """

    def __init__(self, config: Optional[AutoMLConfig] = None):
        self.config = config or AutoMLConfig()
        self.logger = logging.getLogger(__name__)
        self.model_registry = ModelRegistry()
        self.model_selector = ModelSelector(self.config)
        self.hyperparameter_tuner = HyperparameterTuner(self.config)
        self.evaluator = ModelEvaluator(self.config)

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        feature_names: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
    ) -> AutoMLResult:
        """
        Execute complete AutoML pipeline.

        Args:
            X: Feature matrix
            y: Target variable
            feature_names: Optional feature names for DataFrame columns
            categorical_features: List of categorical feature names

        Returns:
            AutoMLResult with best model and comprehensive evaluation
        """
        start_time = time.time()

        try:
            self.logger.info("🚀 Starting AutoML pipeline execution")

            # Data preparation and validation
            X_processed, y_processed, feature_info = self._prepare_data(
                X, y, feature_names, categorical_features
            )

            # Model selection phase
            candidate_models = self.model_selector.select_models(
                X_processed, y_processed, self.config.task_type
            )

            # Hyperparameter tuning phase
            tuned_models = []
            if self.config.enable_hyperparameter_tuning:
                tuned_models = self._tune_hyperparameters(
                    candidate_models, X_processed, y_processed
                )
            else:
                tuned_models = candidate_models

            # Model evaluation and ranking
            model_rankings = self.evaluator.evaluate_models(
                tuned_models, X_processed, y_processed
            )

            # Select best model
            best_model_info = model_rankings[0]
            best_model = best_model_info["model"]

            # Additional analysis
            feature_importance = self._analyze_feature_importance(
                best_model, X_processed, feature_info
            )

            # Prepare comprehensive results
            training_time = time.time() - start_time
            result = AutoMLResult(
                best_model=best_model,
                best_score=best_model_info["score"],
                best_params=best_model_info["params"],
                model_rankings=model_rankings,
                training_time=training_time,
                evaluation_metrics=best_model_info["metrics"],
                feature_importance=feature_importance,
                pipeline_metadata={
                    "config": asdict(self.config),
                    "feature_info": feature_info,
                    "models_evaluated": len(model_rankings),
                    "task_type": self.config.task_type,
                },
            )

            self.logger.info("✅ AutoML pipeline completed successfully")
            self.logger.info(f"⏱️ Total execution time: {training_time:.1f} seconds")
            return result

        except Exception as e:
            self.logger.error(f"❌ AutoML pipeline failed: {e}")
            raise

    def _prepare_data(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        feature_names: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Prepare and validate input data."""
        self.logger.info("📊 Preparing and validating input data")

        # Convert to DataFrame for consistency
        if not isinstance(X, pd.DataFrame):
            feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
            X = pd.DataFrame(X, columns=feature_names)

        if not isinstance(y, pd.Series):
            y = pd.Series(y, name="target")

        # Basic validation
        if len(X) != len(y):
            raise ValueError("X and y must have the same number of samples")

        if len(X) < 10:
            raise ValueError("Dataset too small for meaningful ML (minimum 10 samples)")

        # Handle categorical features
        if categorical_features:
            X = pd.get_dummies(X, columns=categorical_features, drop_first=True)

        # Convert to numpy arrays
        X_processed = X.values
        y_processed = y.values

        # Store feature information
        feature_info = {
            "original_features": list(X.columns),
            "n_features": X.shape[1],
            "n_samples": X.shape[0],
            "categorical_features": categorical_features or [],
            "feature_types": X.dtypes.to_dict(),
        }

        return X_processed, y_processed, feature_info

    def _tune_hyperparameters(
        self, candidate_models: List[Dict[str, Any]], X: np.ndarray, y: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Tune hyperparameters for candidate models."""
        self.logger.info("🔧 Tuning hyperparameters for candidate models")

        tuned_models = []
        max_workers = min(len(candidate_models), 4)  # Parallel tuning

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.hyperparameter_tuner.tune_model,
                    model_info["model"],
                    model_info["name"],
                    X,
                    y,
                ): model_info["name"]
                for model_info in candidate_models
            }

            for future in as_completed(futures):
                model_name = futures[future]
                try:
                    tuned_model = future.result()
                    tuned_models.append(tuned_model)
                    self.logger.info(f"✅ Tuned hyperparameters for {model_name}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to tune {model_name}: {e}")
                    # Keep original model if tuning fails
                    original_model = next(
                        m for m in candidate_models if m["name"] == model_name
                    )
                    tuned_models.append(original_model)

        return tuned_models

    def _analyze_feature_importance(
        self, model: BaseEstimator, X: np.ndarray, feature_info: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """Analyze feature importance if supported by the model."""
        try:
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            elif hasattr(model, "coef_"):
                # For linear models, use absolute coefficient values
                importances = np.abs(
                    model.coef_[0] if model.coef_.ndim > 1 else model.coef_
                )
            else:
                return None

            # Map back to feature names
            feature_names = feature_info.get("original_features", [])
            if len(importances) == len(feature_names):
                return dict(zip(feature_names, importances.tolist()))

        except Exception as e:
            self.logger.debug(f"Feature importance analysis failed: {e}")

        return None

    def save_results(self, result: AutoMLResult, output_path: Union[str, Path]) -> None:
        """Save AutoML results to disk."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare serializable results
        serializable_result = {
            "best_score": result.best_score,
            "best_params": result.best_params,
            "model_rankings": [
                {
                    "name": r.get("name", "unknown"),
                    "score": r.get("score", 0),
                    "params": r.get("params", {}),
                    "metrics": r.get("metrics", {}),
                }
                for r in result.model_rankings
            ],
            "training_time": result.training_time,
            "evaluation_metrics": result.evaluation_metrics,
            "feature_importance": result.feature_importance,
            "pipeline_metadata": result.pipeline_metadata,
        }

        with open(output_path, "w") as f:
            json.dump(serializable_result, f, indent=2, default=str)

        self.logger.info(f"💾 AutoML results saved to {output_path}")

    @classmethod
    def load_results(cls, results_path: Union[str, Path]) -> Dict[str, Any]:
        """Load previously saved AutoML results."""
        with open(results_path, "r") as f:
            return json.load(f)
