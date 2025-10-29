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
Hyperparameter Tuner - Automated Hyperparameter Optimization
Optimizes model hyperparameters using intelligent search strategies.
"""

import logging
import time
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score

from packages.automl.core.orchestrator import AutoMLConfig


class HyperparameterTuner:
    """
    Intelligent hyperparameter tuning using multiple optimization strategies.

    Supports:
    - Randomized search for exploration
    - Grid search for exploitation
    - Bayesian optimization (when available)
    - Early stopping for time-constrained tuning
    """

    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Suppress convergence warnings during tuning
        warnings.filterwarnings("ignore", category=ConvergenceWarning)

    def tune_model(
        self,
        model: BaseEstimator,
        model_name: str,
        X: np.ndarray,
        y: np.ndarray,
        time_limit: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Tune hyperparameters for a single model.

        Args:
            model: The model to tune
            model_name: Name/identifier of the model
            X: Feature matrix
            y: Target variable
            time_limit: Optional time limit in seconds

        Returns:
            Dictionary with tuned model and parameters
        """
        start_time = time.time()
        time_limit = time_limit or self.config.max_time_seconds / 10  # 10% of total time per model

        self.logger.info(f"🔧 Tuning hyperparameters for {model_name}")

        try:
            # Get parameter grid for this model
            param_grid = self._get_model_params(model_name)
            if not param_grid:
                self.logger.info(f"ℹ️ No hyperparameters to tune for {model_name}")
                return {
                    "name": model_name,
                    "model": model,
                    "params": {},
                    "score": self._evaluate_model(model, X, y),
                    "tuning_time": time.time() - start_time,
                }

            # Choose tuning strategy based on parameter space size
            n_combinations = self._estimate_param_combinations(param_grid)

            if n_combinations > 100:
                # Use randomized search for large parameter spaces
                best_model, best_params, best_score = self._randomized_search(model, param_grid, X, y, time_limit)
            else:
                # Use grid search for smaller parameter spaces
                best_model, best_params, best_score = self._grid_search(model, param_grid, X, y, time_limit)

            tuning_time = time.time() - start_time

            self.logger.info(f"✅ Tuned {model_name} - Score: {best_score:.4f} (Time: {tuning_time:.1f}s)")

            return {
                "name": model_name,
                "model": best_model,
                "params": best_params,
                "score": best_score,
                "tuning_time": tuning_time,
            }

        except Exception as e:
            self.logger.warning(f"⚠️ Hyperparameter tuning failed for {model_name}: {e}")
            # Return original model if tuning fails
            return {
                "name": model_name,
                "model": model,
                "params": {},
                "score": self._evaluate_model(model, X, y),
                "tuning_time": time.time() - start_time,
            }

    def _get_model_params(self, model_name: str) -> Dict[str, List[Any]]:
        """Get parameter grid for a specific model."""
        # Import here to avoid circular imports
        from packages.automl.pipeline.model_selector import ModelSelector

        selector = ModelSelector(self.config)
        available_models = selector.model_libraries.get(self.config.task_type, {})
        model_config = available_models.get(model_name, {})

        return model_config.get("params", {})

    def _estimate_param_combinations(self, param_grid: Dict[str, List[Any]]) -> int:
        """Estimate the total number of parameter combinations."""
        if not param_grid:
            return 0

        combinations = 1
        for param_values in param_grid.values():
            combinations *= len(param_values)

        return combinations

    def _randomized_search(
        self,
        model: BaseEstimator,
        param_grid: Dict[str, List[Any]],
        X: np.ndarray,
        y: np.ndarray,
        time_limit: float,
    ) -> Tuple[BaseEstimator, Dict[str, Any], float]:
        """Perform randomized search with time constraints."""
        self.logger.debug("Using randomized search for hyperparameter tuning")

        # Calculate iterations based on time limit
        # Aim for ~60 iterations per minute
        max_iter = min(100, max(10, int(time_limit * 60 / 1)))

        scorer = self._get_scorer()
        search = RandomizedSearchCV(
            model,
            param_grid,
            n_iter=max_iter,
            cv=self.config.cv_folds,
            scoring=scorer,
            random_state=self.config.random_state,
            n_jobs=1,  # Avoid parallelism issues
            error_score=np.nan,
        )

        search.fit(X, y)

        return search.best_estimator_, search.best_params_, search.best_score_

    def _grid_search(
        self,
        model: BaseEstimator,
        param_grid: Dict[str, List[Any]],
        X: np.ndarray,
        y: np.ndarray,
        time_limit: float,
    ) -> Tuple[BaseEstimator, Dict[str, Any], float]:
        """Perform grid search with time constraints."""
        self.logger.debug("Using grid search for hyperparameter tuning")

        scorer = self._get_scorer()
        search = GridSearchCV(
            model,
            param_grid,
            cv=self.config.cv_folds,
            scoring=scorer,
            n_jobs=1,  # Avoid parallelism issues
            error_score=np.nan,
        )

        search.fit(X, y)

        return search.best_estimator_, search.best_params_, search.best_score_

    def _get_scorer(self) -> str:
        """Get the appropriate scorer for the task type."""
        if self.config.task_type == "classification":
            if self.config.metric == "accuracy":
                return "accuracy"
            elif self.config.metric == "f1":
                return "f1_macro"
            elif self.config.metric == "precision":
                return "precision_macro"
            elif self.config.metric == "recall":
                return "recall_macro"
            else:
                return "accuracy"
        elif self.config.task_type == "regression":
            if self.config.metric == "r2":
                return "r2"
            elif self.config.metric == "mse":
                return "neg_mean_squared_error"
            elif self.config.metric == "mae":
                return "neg_mean_absolute_error"
            else:
                return "r2"
        else:
            return "accuracy"

    def _evaluate_model(self, model: BaseEstimator, X: np.ndarray, y: np.ndarray) -> float:
        """Evaluate a model using cross-validation."""
        try:
            scorer = self._get_scorer()
            scores = cross_val_score(model, X, y, cv=self.config.cv_folds, scoring=scorer, n_jobs=1)
            return np.mean(scores)
        except Exception:
            # Fallback to simple train/test split
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=self.config.random_state
            )

            model.fit(X_train, y_train)

            if self.config.task_type == "classification":
                from sklearn.metrics import accuracy_score

                y_pred = model.predict(X_test)
                return accuracy_score(y_test, y_pred)
            else:
                from sklearn.metrics import r2_score

                y_pred = model.predict(X_test)
                return r2_score(y_test, y_pred)


class BayesianOptimizer:
    """
    Bayesian optimization for hyperparameter tuning (when optuna is available).

    This provides more sophisticated optimization for complex parameter spaces,
    but requires additional dependencies.
    """

    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def optimize(
        self,
        model_class: type,
        param_space: Dict[str, Any],
        X: np.ndarray,
        y: np.ndarray,
        n_trials: int = 50,
    ) -> Tuple[BaseEstimator, Dict[str, Any], float]:
        """
        Perform Bayesian optimization of hyperparameters.

        Note: Requires optuna to be installed.
        """
        try:
            import optuna
        except ImportError:
            self.logger.warning("Optuna not available, falling back to random search")
            raise ImportError("Bayesian optimization requires optuna")

        def objective(trial):
            # Sample parameters from the search space
            params = {}
            for param_name, param_config in param_space.items():
                if isinstance(param_config, list):
                    # Categorical parameter
                    params[param_name] = trial.suggest_categorical(param_name, param_config)
                elif isinstance(param_config, dict):
                    # Numerical parameter with range
                    param_type = param_config.get("type", "float")
                    if param_type == "int":
                        params[param_name] = trial.suggest_int(param_name, param_config["low"], param_config["high"])
                    else:
                        params[param_name] = trial.suggest_float(
                            param_name,
                            param_config["low"],
                            param_config["high"],
                            log=param_config.get("log", False),
                        )

            # Train and evaluate model
            model = model_class(**params)
            score = self._evaluate_model_quick(model, X, y)
            return score

        # Create and run optimization study
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        # Get best parameters and create final model
        best_params = study.best_params
        best_model = model_class(**best_params)
        best_model.fit(X, y)

        # Final evaluation
        best_score = self._evaluate_model_quick(best_model, X, y)

        return best_model, best_params, best_score

    def _evaluate_model_quick(self, model: BaseEstimator, X: np.ndarray, y: np.ndarray) -> float:
        """Quick model evaluation for optimization."""
        try:
            # Simple train/test split for speed
            from sklearn.model_selection import train_test_split

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

            model.fit(X_train, y_train)

            if hasattr(model, "predict_proba"):
                # Classification
                y_pred = model.predict(X_test)
                from sklearn.metrics import accuracy_score

                return accuracy_score(y_test, y_pred)
            else:
                # Regression
                y_pred = model.predict(X_test)
                from sklearn.metrics import r2_score

                return r2_score(y_test, y_pred)

        except Exception:
            return 0.0  # Return poor score on failure
