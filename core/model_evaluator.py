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
Model Evaluator - Comprehensive Model Evaluation and Comparison
Provides detailed evaluation metrics and model comparison capabilities.
"""

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    explained_variance_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.preprocessing import label_binarize

from packages.automl.core.orchestrator import AutoMLConfig


class ModelEvaluator:
    """
    Comprehensive model evaluation with multiple metrics and statistical analysis.

    Provides:
    - Cross-validation results
    - Detailed classification/regression metrics
    - Statistical significance testing
    - Model comparison and ranking
    - Performance stability analysis
    """

    def __init__(self, config: AutoMLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def evaluate_models(self, models: List[Dict[str, Any]], X: np.ndarray, y: np.ndarray) -> List[Dict[str, Any]]:
        """
        Evaluate multiple models and provide comprehensive rankings.

        Args:
            models: List of model dictionaries with 'name', 'model', 'params', etc.
            X: Feature matrix
            y: Target variable

        Returns:
            List of model evaluation results sorted by performance
        """
        self.logger.info(f"📊 Evaluating {len(models)} models")

        evaluated_models = []

        for model_info in models:
            try:
                evaluation_result = self._evaluate_single_model(model_info, X, y)
                evaluated_models.append(evaluation_result)

                self.logger.info(
                    f"✅ Evaluated {model_info['name']}: "
                    f"Score={evaluation_result['score']:.4f} ± {evaluation_result['std_score']:.4f}"
                )

            except Exception as e:
                self.logger.warning(f"⚠️ Failed to evaluate {model_info['name']}: {e}")
                # Add failed model with poor score
                evaluated_models.append(
                    {
                        "name": model_info["name"],
                        "model": model_info["model"],
                        "params": model_info.get("params", {}),
                        "score": 0.0,
                        "std_score": 0.0,
                        "metrics": {},
                        "cv_results": [],
                        "evaluation_error": str(e),
                    }
                )

        # Sort by score (descending)
        evaluated_models.sort(key=lambda x: x["score"], reverse=True)

        self.logger.info("🏆 Model evaluation complete - rankings determined")

        return evaluated_models

    def _evaluate_single_model(self, model_info: Dict[str, Any], X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Evaluate a single model comprehensively."""
        model = model_info["model"]
        model_name = model_info["name"]

        # Perform cross-validation
        cv_results = self._cross_validate_model(model, X, y)

        # Calculate comprehensive metrics
        metrics = self._calculate_metrics(model, X, y, cv_results)

        # Determine primary score
        primary_score = self._get_primary_score(metrics)

        return {
            "name": model_name,
            "model": model,
            "params": model_info.get("params", {}),
            "score": primary_score,
            "std_score": cv_results["std_test_score"],
            "metrics": metrics,
            "cv_results": cv_results,
            "suitability_score": model_info.get("suitability_score", 0),
            "tuning_time": model_info.get("tuning_time", 0),
        }

    def _cross_validate_model(self, model: BaseEstimator, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Perform cross-validation and return detailed results."""
        scoring_metrics = self._get_scoring_metrics()

        cv_results = cross_validate(
            model,
            X,
            y,
            cv=self.config.cv_folds,
            scoring=scoring_metrics,
            return_train_score=False,
            n_jobs=1,  # Avoid parallelism issues
        )

        return cv_results

    def _get_scoring_metrics(self) -> List[str]:
        """Get appropriate scoring metrics for the task type."""
        if self.config.task_type == "classification":
            return ["accuracy", "precision_macro", "recall_macro", "f1_macro"]
        elif self.config.task_type == "regression":
            return ["r2", "neg_mean_squared_error", "neg_mean_absolute_error"]
        else:
            return ["accuracy"]

    def _calculate_metrics(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        cv_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate comprehensive evaluation metrics."""
        # Train model on full dataset for detailed metrics
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=y if self.config.task_type == "classification" else None,
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        metrics = {}

        # Cross-validation summary
        metrics["cv_mean_score"] = np.mean(
            cv_results["test_accuracy" if self.config.task_type == "classification" else "test_r2"]
        )
        metrics["cv_std_score"] = np.std(
            cv_results["test_accuracy" if self.config.task_type == "classification" else "test_r2"]
        )
        metrics["cv_scores"] = cv_results[
            "test_accuracy" if self.config.task_type == "classification" else "test_r2"
        ].tolist()

        if self.config.task_type == "classification":
            metrics.update(self._calculate_classification_metrics(y_test, y_pred, model, X_test))
        else:
            metrics.update(self._calculate_regression_metrics(y_test, y_pred))

        return metrics

    def _calculate_classification_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model: BaseEstimator,
        X_test: np.ndarray,
    ) -> Dict[str, Any]:
        """Calculate detailed classification metrics."""
        metrics = {}

        # Basic metrics
        metrics["accuracy"] = accuracy_score(y_true, y_pred)
        metrics["precision"] = precision_score(y_true, y_pred, average="macro", zero_division=0)
        metrics["recall"] = recall_score(y_true, y_pred, average="macro", zero_division=0)
        metrics["f1_score"] = f1_score(y_true, y_pred, average="macro", zero_division=0)

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        # Per-class metrics
        class_report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        metrics["per_class_metrics"] = class_report

        # ROC-AUC if applicable
        if hasattr(model, "predict_proba"):
            try:
                y_prob = model.predict_proba(X_test)
                if y_prob.shape[1] == 2:
                    # Binary classification
                    metrics["roc_auc"] = roc_auc_score(y_true, y_prob[:, 1])
                else:
                    # Multi-class - use one-vs-rest
                    y_bin = label_binarize(y_true, classes=np.unique(y_true))
                    if y_bin.shape[1] > 1:
                        metrics["roc_auc"] = roc_auc_score(y_bin, y_prob, multi_class="ovr")
            except Exception:
                pass  # ROC-AUC calculation failed

        return metrics

    def _calculate_regression_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculate detailed regression metrics."""
        metrics = {}

        # Basic metrics
        metrics["r2_score"] = r2_score(y_true, y_pred)
        metrics["mse"] = mean_squared_error(y_true, y_pred)
        metrics["mae"] = mean_absolute_error(y_true, y_pred)
        metrics["explained_variance"] = explained_variance_score(y_true, y_pred)
        metrics["median_absolute_error"] = median_absolute_error(y_true, y_pred)

        # Additional statistics
        residuals = y_true - y_pred
        metrics["residual_mean"] = np.mean(residuals)
        metrics["residual_std"] = np.std(residuals)
        metrics["max_error"] = np.max(np.abs(residuals))

        return metrics

    def _get_primary_score(self, metrics: Dict[str, Any]) -> float:
        """Extract the primary evaluation score from metrics."""
        if self.config.task_type == "classification":
            if self.config.metric == "accuracy":
                return metrics.get("accuracy", 0)
            elif self.config.metric == "f1":
                return metrics.get("f1_score", 0)
            elif self.config.metric == "precision":
                return metrics.get("precision", 0)
            elif self.config.metric == "recall":
                return metrics.get("recall", 0)
            else:
                return metrics.get("cv_mean_score", 0)
        else:  # regression
            if self.config.metric == "r2":
                return metrics.get("r2_score", 0)
            elif self.config.metric == "mse":
                return -metrics.get("mse", 0)  # Negative for consistency (higher is better)
            elif self.config.metric == "mae":
                return -metrics.get("mae", 0)  # Negative for consistency (higher is better)
            else:
                return metrics.get("cv_mean_score", 0)

    def compare_models(self, model_results: List[Dict[str, Any]], statistical_test: bool = False) -> Dict[str, Any]:
        """
        Compare multiple models statistically and provide insights.

        Args:
            model_results: Results from evaluate_models
            statistical_test: Whether to perform statistical significance testing

        Returns:
            Comparison results with insights and recommendations
        """
        if len(model_results) < 2:
            return {"error": "Need at least 2 models to compare"}

        comparison = {
            "best_model": model_results[0]["name"],
            "best_score": model_results[0]["score"],
            "model_comparison": [],
            "insights": [],
            "recommendations": [],
        }

        # Compare each model to the best
        best_score = model_results[0]["score"]
        for result in model_results:
            comparison["model_comparison"].append(
                {
                    "name": result["name"],
                    "score": result["score"],
                    "score_diff": result["score"] - best_score,
                    "std_score": result.get("std_score", 0),
                    "relative_performance": result["score"] / best_score if best_score > 0 else 0,
                }
            )

        # Generate insights
        comparison["insights"] = self._generate_comparison_insights(model_results)

        # Generate recommendations
        comparison["recommendations"] = self._generate_recommendations(model_results)

        if statistical_test:
            comparison["statistical_tests"] = self._perform_statistical_tests(model_results)

        return comparison

    def _generate_comparison_insights(self, model_results: List[Dict[str, Any]]) -> List[str]:
        """Generate insights about model performance differences."""
        insights = []

        if len(model_results) >= 2:
            best = model_results[0]
            second_best = model_results[1]

            score_diff = best["score"] - second_best["score"]

            if score_diff < 0.01:
                insights.append("Models have very similar performance - consider simpler model for production")
            elif score_diff < 0.05:
                insights.append("Best model has slight edge - consider trade-offs between complexity and performance")
            else:
                insights.append("Clear performance winner identified")

            # Check stability
            std_scores = [r.get("std_score", 0) for r in model_results[:3]]
            if any(s > 0.1 for s in std_scores):
                insights.append("Some top models show high variance - consider more stable alternatives")

        return insights

    def _generate_recommendations(self, model_results: List[Dict[str, Any]]) -> List[str]:
        """Generate deployment recommendations."""
        recommendations = []

        best_model = model_results[0]

        # Interpretability vs Performance trade-off
        simple_models = ["logistic_regression", "linear_regression", "decision_tree"]
        complex_models = ["neural_network", "svm", "random_forest"]

        if best_model["name"] in simple_models:
            recommendations.append("Best model is interpretable - good for production explainability")
        elif best_model["name"] in complex_models:
            recommendations.append("Consider adding model explainability tools for complex model")

        # Performance recommendations
        if best_model["score"] < 0.7:
            recommendations.append("Model performance below threshold - consider feature engineering or more data")
        elif best_model["score"] > 0.9:
            recommendations.append("Excellent performance achieved - ready for production deployment")

        return recommendations

    def _perform_statistical_tests(self, model_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform statistical significance tests between models."""
        # Simplified statistical testing
        # In a full implementation, this would use proper statistical tests
        tests = {}

        if len(model_results) >= 2:
            scores = [r["score"] for r in model_results]
            stds = [r.get("std_score", 0) for r in model_results]

            # Check if best model significantly outperforms others
            best_score = scores[0]
            other_scores = scores[1:]

            if all(best_score - score > 2 * max(stds) for score in other_scores):
                tests["significance"] = "Best model significantly outperforms others"
            else:
                tests["significance"] = "Performance differences may not be statistically significant"

        return tests
