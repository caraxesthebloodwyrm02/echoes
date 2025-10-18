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
Model Selector - Intelligent Model Selection for AutoML
Automatically selects appropriate ML models based on dataset characteristics.
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from packages.automl.core.orchestrator import AutoMLConfig


class ModelSelector:
    """
    Intelligent model selection based on dataset characteristics and task type.

    Analyzes dataset properties to recommend appropriate ML algorithms and
    provides initial model configurations for hyperparameter tuning.
    """

    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Model libraries organized by task type
        self.model_libraries = {
            "classification": {
                "random_forest": {
                    "model": RandomForestClassifier(random_state=config.random_state),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [None, 10, 20, 30],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4],
                    },
                },
                "logistic_regression": {
                    "model": LogisticRegression(
                        random_state=config.random_state, max_iter=1000
                    ),
                    "params": {
                        "C": [0.1, 1.0, 10.0, 100.0],
                        "penalty": ["l1", "l2", "elasticnet", "none"],
                        "solver": ["newton-cg", "lbfgs", "liblinear", "sag", "saga"],
                    },
                },
                "svm": {
                    "model": SVC(random_state=config.random_state),
                    "params": {
                        "C": [0.1, 1.0, 10.0],
                        "kernel": ["linear", "poly", "rbf", "sigmoid"],
                        "gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1.0],
                    },
                },
                "decision_tree": {
                    "model": DecisionTreeClassifier(random_state=config.random_state),
                    "params": {
                        "max_depth": [None, 5, 10, 15, 20],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4],
                        "criterion": ["gini", "entropy"],
                    },
                },
                "knn": {
                    "model": KNeighborsClassifier(),
                    "params": {
                        "n_neighbors": [3, 5, 7, 9, 11],
                        "weights": ["uniform", "distance"],
                        "metric": ["euclidean", "manhattan", "minkowski"],
                    },
                },
                "naive_bayes": {
                    "model": GaussianNB(),
                    "params": {},
                },  # No hyperparameters to tune
                "neural_network": {
                    "model": MLPClassifier(
                        random_state=config.random_state, max_iter=1000
                    ),
                    "params": {
                        "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50)],
                        "activation": ["relu", "tanh", "logistic"],
                        "solver": ["adam", "sgd", "lbfgs"],
                        "alpha": [0.0001, 0.001, 0.01, 0.1],
                        "learning_rate": ["constant", "invscaling", "adaptive"],
                    },
                },
            },
            "regression": {
                "random_forest": {
                    "model": RandomForestRegressor(random_state=config.random_state),
                    "params": {
                        "n_estimators": [50, 100, 200],
                        "max_depth": [None, 10, 20, 30],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4],
                    },
                },
                "linear_regression": {
                    "model": LinearRegression(),
                    "params": {},
                },  # No hyperparameters to tune
                "ridge": {
                    "model": Ridge(random_state=config.random_state),
                    "params": {
                        "alpha": [0.1, 1.0, 10.0, 100.0],
                        "solver": [
                            "auto",
                            "svd",
                            "cholesky",
                            "lsqr",
                            "sparse_cg",
                            "sag",
                            "saga",
                        ],
                    },
                },
                "lasso": {
                    "model": Lasso(random_state=config.random_state),
                    "params": {
                        "alpha": [0.001, 0.01, 0.1, 1.0, 10.0],
                        "selection": ["cyclic", "random"],
                    },
                },
                "svm": {
                    "model": SVR(),
                    "params": {
                        "C": [0.1, 1.0, 10.0],
                        "kernel": ["linear", "poly", "rbf", "sigmoid"],
                        "gamma": ["scale", "auto", 0.001, 0.01, 0.1, 1.0],
                        "epsilon": [0.1, 0.2, 0.5],
                    },
                },
                "decision_tree": {
                    "model": DecisionTreeRegressor(random_state=config.random_state),
                    "params": {
                        "max_depth": [None, 5, 10, 15, 20],
                        "min_samples_split": [2, 5, 10],
                        "min_samples_leaf": [1, 2, 4],
                        "criterion": [
                            "squared_error",
                            "friedman_mse",
                            "absolute_error",
                        ],
                    },
                },
                "knn": {
                    "model": KNeighborsRegressor(),
                    "params": {
                        "n_neighbors": [3, 5, 7, 9, 11],
                        "weights": ["uniform", "distance"],
                        "metric": ["euclidean", "manhattan", "minkowski"],
                    },
                },
                "neural_network": {
                    "model": MLPRegressor(
                        random_state=config.random_state, max_iter=1000
                    ),
                    "params": {
                        "hidden_layer_sizes": [(50,), (100,), (50, 50), (100, 50)],
                        "activation": ["relu", "tanh", "logistic"],
                        "solver": ["adam", "sgd", "lbfgs"],
                        "alpha": [0.0001, 0.001, 0.01, 0.1],
                        "learning_rate": ["constant", "invscaling", "adaptive"],
                    },
                },
            },
        }

    def select_models(
        self, X: np.ndarray, y: np.ndarray, task_type: str
    ) -> List[Dict[str, Any]]:
        """
        Select appropriate models based on dataset characteristics.

        Args:
            X: Feature matrix
            y: Target variable
            task_type: Type of ML task ('classification' or 'regression')

        Returns:
            List of model configurations with initial parameters
        """
        self.logger.info(f"🎯 Selecting models for {task_type} task")

        # Analyze dataset characteristics
        dataset_info = self._analyze_dataset(X, y, task_type)

        # Get available models for task type
        available_models = self.model_libraries.get(task_type, {})
        if not available_models:
            raise ValueError(f"No models available for task type: {task_type}")

        # Select models based on dataset characteristics
        selected_models = self._select_optimal_models(
            available_models, dataset_info, self.config.max_models
        )

        self.logger.info(f"✅ Selected {len(selected_models)} models for evaluation")

        return selected_models

    def _analyze_dataset(
        self, X: np.ndarray, y: np.ndarray, task_type: str
    ) -> Dict[str, Any]:
        """Analyze dataset characteristics to inform model selection."""
        n_samples, n_features = X.shape
        n_classes = len(np.unique(y)) if task_type == "classification" else None

        # Basic statistics
        info = {
            "n_samples": n_samples,
            "n_features": n_features,
            "n_classes": n_classes,
            "samples_per_feature": n_samples / n_features,
            "feature_variance": np.var(X, axis=0).mean(),
            "has_missing_values": np.isnan(X).any(),
            "is_high_dimensional": n_features > 100,
            "is_small_dataset": n_samples < 1000,
            "is_imbalanced": self._check_imbalance(y)
            if task_type == "classification"
            else False,
        }

        # Task-specific analysis
        if task_type == "classification":
            info.update(
                {
                    "is_binary": n_classes == 2,
                    "is_multiclass": n_classes > 2,
                    "minority_class_ratio": min(np.bincount(y)) / len(y),
                }
            )
        elif task_type == "regression":
            y_std = np.std(y)
            info.update(
                {
                    "target_variance": y_std,
                    "is_high_variance_target": y_std > np.mean(y),
                }
            )

        self.logger.debug(f"📊 Dataset analysis: {info}")
        return info

    def _check_imbalance(self, y: np.ndarray, threshold: float = 0.1) -> bool:
        """Check if classification dataset is imbalanced."""
        class_counts = np.bincount(y)
        min_ratio = class_counts.min() / class_counts.sum()
        return min_ratio < threshold

    def _select_optimal_models(
        self,
        available_models: Dict[str, Dict],
        dataset_info: Dict[str, Any],
        max_models: int,
    ) -> List[Dict[str, Any]]:
        """Select optimal models based on dataset characteristics."""
        candidates = []

        for model_name, model_config in available_models.items():
            # Calculate suitability score
            score = self._calculate_model_suitability(model_name, dataset_info)

            candidates.append(
                {
                    "name": model_name,
                    "model": model_config["model"],
                    "params": model_config["params"],
                    "suitability_score": score,
                    "estimated_complexity": self._estimate_model_complexity(model_name),
                }
            )

        # Sort by suitability score (descending)
        candidates.sort(key=lambda x: x["suitability_score"], reverse=True)

        # Select top models, preferring diversity in complexity
        selected = []
        complexity_levels = set()

        for candidate in candidates:
            if len(selected) >= max_models:
                break

            # Ensure complexity diversity (simple and complex models)
            complexity = candidate["estimated_complexity"]
            if complexity not in complexity_levels or len(complexity_levels) >= 3:
                selected.append(candidate)
                complexity_levels.add(complexity)

        # Ensure we have at least some models even if diversity is limited
        if not selected:
            selected = candidates[:max_models]

        return selected

    def _calculate_model_suitability(
        self, model_name: str, dataset_info: Dict[str, Any]
    ) -> float:
        """Calculate how suitable a model is for the given dataset."""
        score = 5.0  # Base score

        # Adjust score based on dataset characteristics
        if dataset_info["is_small_dataset"]:
            # Prefer simpler models for small datasets
            if model_name in [
                "naive_bayes",
                "logistic_regression",
                "linear_regression",
            ]:
                score += 2
            elif model_name in ["neural_network", "svm"]:
                score -= 1

        if dataset_info["is_high_dimensional"]:
            # Prefer models that handle high dimensions well
            if model_name in ["logistic_regression", "svm", "neural_network"]:
                score += 1
            elif model_name in ["decision_tree", "knn"]:
                score -= 1

        if dataset_info.get("is_imbalanced", False):
            # Prefer models that handle imbalanced data
            if model_name in ["random_forest", "svm"]:
                score += 1

        if dataset_info.get("is_binary", False):
            # All models work for binary, slight preference for linear models
            if model_name in ["logistic_regression", "linear_regression"]:
                score += 0.5

        # Task-specific adjustments
        if dataset_info.get("is_multiclass", False):
            # Most models handle multiclass well, but some are specifically good
            if model_name in ["random_forest", "neural_network"]:
                score += 0.5

        return max(0, min(10, score))  # Clamp between 0 and 10

    def _estimate_model_complexity(self, model_name: str) -> str:
        """Estimate the computational complexity of a model."""
        complexity_map = {
            "naive_bayes": "low",
            "logistic_regression": "low",
            "linear_regression": "low",
            "decision_tree": "low",
            "knn": "low",
            "ridge": "low",
            "lasso": "low",
            "random_forest": "medium",
            "svm": "medium",
            "neural_network": "high",
        }
        return complexity_map.get(model_name, "medium")
