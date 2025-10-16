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
Simplified AutoML Core - Basic Automated Machine Learning Pipeline
A working implementation that demonstrates core AutoML functionality.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


class AutoMLConfig:
    """Simplified configuration for AutoML."""

    def __init__(
        self,
        task_type: str = "classification",
        max_models: int = 5,
        cv_folds: int = 3,
        random_state: int = 42,
    ):
        self.task_type = task_type
        self.max_models = max_models
        self.cv_folds = cv_folds
        self.random_state = random_state


class SimpleAutoML:
    """
    Simplified AutoML implementation that works reliably.

    Features:
    - Basic model selection for classification and regression
    - Cross-validation evaluation
    - Feature importance analysis
    - Simple configuration
    """

    def __init__(self, config: Optional[AutoMLConfig] = None):
        self.config = config or AutoMLConfig()
        self.logger = logging.getLogger(__name__)

        # Available models
        self.classification_models = {
            "random_forest": RandomForestClassifier(
                n_estimators=100, random_state=self.config.random_state
            ),
            "logistic_regression": LogisticRegression(
                random_state=self.config.random_state, max_iter=1000
            ),
            "svm": SVC(random_state=self.config.random_state),
            "decision_tree": DecisionTreeClassifier(
                random_state=self.config.random_state
            ),
        }

        self.regression_models = {
            "random_forest": RandomForestRegressor(
                n_estimators=100, random_state=self.config.random_state
            ),
            "linear_regression": LinearRegression(),
            "svm": SVR(),
            "decision_tree": DecisionTreeRegressor(
                random_state=self.config.random_state
            ),
        }

    def fit(
        self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run simplified AutoML pipeline.

        Args:
            X: Feature matrix
            y: Target variable
            feature_names: Optional feature names

        Returns:
            Dictionary with results
        """
        start_time = time.time()
        self.logger.info("🚀 Starting simplified AutoML pipeline")

        # Select appropriate models
        if self.config.task_type == "classification":
            models_to_try = list(self.classification_models.items())[
                : self.config.max_models
            ]
            scorer = "accuracy"
        else:
            models_to_try = list(self.regression_models.items())[
                : self.config.max_models
            ]
            scorer = "r2"

        # Evaluate each model
        results = []
        for name, model in models_to_try:
            try:
                self.logger.info(f"Evaluating {name}...")

                # Cross-validation
                cv_scores = cross_val_score(
                    model, X, y, cv=self.config.cv_folds, scoring=scorer, n_jobs=1
                )

                mean_score = np.mean(cv_scores)
                std_score = np.std(cv_scores)

                # Fit on full data for feature importance
                model.fit(X, y)
                feature_importance = self._get_feature_importance(model, feature_names)

                results.append(
                    {
                        "name": name,
                        "model": model,
                        "score": mean_score,
                        "std_score": std_score,
                        "cv_scores": cv_scores.tolist(),
                        "feature_importance": feature_importance,
                    }
                )

                self.logger.info(f"  ✓ {name}: {mean_score:.4f} ± {std_score:.4f}")
            except Exception as e:
                self.logger.warning(f"Failed to evaluate {name}: {e}")

        if not results:
            raise RuntimeError("No models could be evaluated successfully")

        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)

        # Get best model
        best_result = results[0]

        execution_time = time.time() - start_time

        self.logger.info("✅ AutoML pipeline completed!")
        self.logger.info(f"🏆 Best Score: {best_result['score']:.4f}")
        self.logger.info(f"⏱️ Total time: {execution_time:.1f} seconds")

        return {
            "best_model": best_result["model"],
            "best_score": best_result["score"],
            "best_model_name": best_result["name"],
            "all_results": results,
            "execution_time": execution_time,
            "task_type": self.config.task_type,
            "models_evaluated": len(results),
        }

    def _get_feature_importance(
        self, model, feature_names: Optional[List[str]]
    ) -> Optional[Dict[str, float]]:
        """Extract feature importance if available."""
        try:
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
            elif hasattr(model, "coef_"):
                importances = np.abs(model.coef_.flatten())
            else:
                return None

            if feature_names and len(importances) == len(feature_names):
                return dict(zip(feature_names, importances.tolist()))
            else:
                return {
                    f"feature_{i}": imp for i, imp in enumerate(importances.tolist())
                }

        except Exception:
            return None

    def predict(self, X: np.ndarray, model_result: Dict[str, Any]) -> np.ndarray:
        """Make predictions using the best model."""
        return model_result["best_model"].predict(X)

    def evaluate_predictions(
        self, y_true: np.ndarray, y_pred: np.ndarray, task_type: str
    ) -> Dict[str, float]:
        """Evaluate predictions."""
        if task_type == "classification":
            return {"accuracy": accuracy_score(y_true, y_pred)}
        else:
            return {"r2_score": r2_score(y_true, y_pred)}


def quick_automl_demo():
    """Run a quick demo of the simplified AutoML."""
    from sklearn.datasets import make_classification

    print("🤖 Simple AutoML Demo")
    print("=" * 40)

    # Create sample dataset
    X, y = make_classification(
        n_samples=500, n_features=10, n_informative=5, random_state=42
    )

    feature_names = [f"feature_{i}" for i in range(X.shape[1])]

    # Run AutoML
    config = AutoMLConfig(task_type="classification", max_models=3)
    automl = SimpleAutoML(config)

    results = automl.fit(X, y, feature_names)

    print("✅ Demo completed!")
    print(f"🎯 Best Score: {results['best_score']:.4f}")
    print(f"🏆 Best Model: {results['best_model_name']}")
    print(f"📊 Models Evaluated: {results['models_evaluated']}")
    print(f"⏱️ Execution Time: {results['execution_time']:.1f} seconds")
    # Show top models
    print("\n🏅 Model Rankings:")
    for i, result in enumerate(results["all_results"][:3], 1):
        print(f"  {i}. {result['name']}: {result['score']:.4f}")
    return results


if __name__ == "__main__":
    quick_automl_demo()
