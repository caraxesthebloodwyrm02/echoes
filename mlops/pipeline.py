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
MLOps Pipeline System
Automated machine learning operations with MLflow tracking and BentoML serving
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import bentoml
import joblib
import mlflow
import mlflow.pytorch
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


class MLOpsPipeline:
    """Complete MLOps pipeline with tracking, versioning, and deployment"""

    def __init__(self, experiment_name: str = "default_experiment"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        self.current_run = None

    def start_run(self, run_name: str = None) -> str:
        """Start a new MLflow run"""
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_run = mlflow.start_run(run_name=run_name)
        return self.current_run.info.run_id

    def log_parameters(self, params: Dict[str, Any]):
        """Log model parameters"""
        for key, value in params.items():
            mlflow.log_param(key, value)

    def log_metrics(self, metrics: Dict[str, float]):
        """Log model metrics"""
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

    def log_model(self, model: Any, model_name: str, flavor: str = "sklearn"):
        """Log model artifact"""
        if flavor == "sklearn":
            mlflow.sklearn.log_model(model, model_name)
        elif flavor == "pytorch":
            mlflow.pytorch.log_model(model, model_name)
        else:
            mlflow.log_artifact(model, model_name)

    def train_and_track(
        self,
        model_class,
        X: pd.DataFrame,
        y: pd.Series,
        params: Dict[str, Any],
        test_size: float = 0.2,
    ) -> Dict[str, Any]:
        """Train model with full tracking"""
        run_id = self.start_run()

        try:
            # Log parameters
            self.log_parameters(params)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Train model
            model = model_class(**params)
            model.fit(X_train, y_train)

            # Make predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average="weighted"),
                "recall": recall_score(y_test, y_pred, average="weighted"),
                "f1_score": f1_score(y_test, y_pred, average="weighted"),
            }

            # Log metrics
            self.log_metrics(metrics)

            # Log model
            self.log_model(model, "model")

            # Save model locally
            model_path = f"models/{run_id}"
            os.makedirs(model_path, exist_ok=True)
            joblib.dump(model, f"{model_path}/model.pkl")

            result = {
                "run_id": run_id,
                "status": "success",
                "metrics": metrics,
                "model_path": model_path,
            }

        except Exception as e:
            result = {"run_id": run_id, "status": "failed", "error": str(e)}

        finally:
            mlflow.end_run()

        return result

    def deploy_model(self, run_id: str, model_name: str = "ml_model") -> str:
        """Deploy model using BentoML"""
        # Load model from MLflow
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.sklearn.load_model(model_uri)

        # Create BentoML service
        @bentoml.service
        class MLModelService:
            def __init__(self):
                self.model = model

            @bentoml.api
            def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                # Convert input to DataFrame
                df = pd.DataFrame([input_data])
                prediction = self.model.predict(df)[0]
                probability = self.model.predict_proba(df)[0]

                return {
                    "prediction": int(prediction),
                    "probabilities": probability.tolist(),
                }

        # Save BentoML service
        bentoml_service = MLModelService()
        saved_path = bentoml.save(bentoml_service, model_name)

        return saved_path


class ModelRegistry:
    """Model versioning and registry management"""

    def __init__(self):
        self.models = {}

    def register_model(
        self, name: str, version: str, run_id: str, metadata: Dict[str, Any] = None
    ):
        """Register a model version"""
        if name not in self.models:
            self.models[name] = {}

        self.models[name][version] = {
            "run_id": run_id,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        # Save to registry file
        self._save_registry()

    def get_model_info(
        self, name: str, version: str = "latest"
    ) -> Optional[Dict[str, Any]]:
        """Get model information"""
        if name not in self.models:
            return None

        if version == "latest":
            versions = list(self.models[name].keys())
            if not versions:
                return None
            version = max(versions)

        return self.models[name].get(version)

    def list_models(self) -> Dict[str, list]:
        """List all registered models"""
        return {name: list(versions.keys()) for name, versions in self.models.items()}

    def _save_registry(self):
        """Save registry to file"""
        os.makedirs("registry", exist_ok=True)
        with open("registry/models.json", "w") as f:
            json.dump(self.models, f, indent=2)


class AutomatedTraining:
    """Automated model training with hyperparameter optimization"""

    def __init__(self, mlops_pipeline: MLOpsPipeline):
        self.pipeline = mlops_pipeline

    def grid_search_training(
        self,
        model_class,
        X: pd.DataFrame,
        y: pd.Series,
        param_grid: Dict[str, list],
        model_name: str = None,
    ) -> Dict[str, Any]:
        """Perform grid search over hyperparameters"""
        best_result = None
        best_score = 0

        total_combinations = np.prod([len(values) for values in param_grid.values()])
        print(f"Starting grid search with {total_combinations} combinations...")

        for i, params in enumerate(self._generate_param_combinations(param_grid)):
            print(f"Training combination {i + 1}/{total_combinations}: {params}")

            result = self.pipeline.train_and_track(model_class, X, y, params)

            if result["status"] == "success":
                accuracy = result["metrics"]["accuracy"]
                if accuracy > best_score:
                    best_score = accuracy
                    best_result = result
                    best_result["params"] = params

        if best_result:
            print(f"Best model found with accuracy: {best_score}")
            if model_name:
                registry = ModelRegistry()
                registry.register_model(
                    model_name,
                    f"v{len(registry.models.get(model_name, {})) + 1}",
                    best_result["run_id"],
                    {
                        "params": best_result["params"],
                        "metrics": best_result["metrics"],
                    },
                )

        return best_result

    def _generate_param_combinations(self, param_grid: Dict[str, list]):
        """Generate all parameter combinations"""
        import itertools

        keys = param_grid.keys()
        values = param_grid.values()
        for combination in itertools.product(*values):
            yield dict(zip(keys, combination))


# Example usage and demo
def demo_mlops_pipeline():
    """Demonstrate MLOps capabilities"""
    # Initialize pipeline
    pipeline = MLOpsPipeline("demo_experiment")

    # Create sample data
    np.random.seed(42)
    X = pd.DataFrame(
        {
            "feature1": np.random.randn(1000),
            "feature2": np.random.randn(1000),
            "feature3": np.random.randn(1000),
        }
    )
    y = pd.Series(np.random.choice([0, 1], 1000))

    # Train model with tracking
    from sklearn.ensemble import RandomForestClassifier

    result = pipeline.train_and_track(
        RandomForestClassifier, X, y, {"n_estimators": 100, "max_depth": 10}
    )

    print(f"Training completed: {result}")

    # Automated training with grid search
    automated = AutomatedTraining(pipeline)

    param_grid = {"n_estimators": [50, 100, 200], "max_depth": [5, 10, 15]}

    best_result = automated.grid_search_training(
        RandomForestClassifier, X, y, param_grid, "random_forest_model"
    )

    print(f"Best model: {best_result}")

    return {
        "pipeline_demo": "completed",
        "automated_training": "completed",
        "model_registry": "initialized",
    }


if __name__ == "__main__":
    demo_mlops_pipeline()
