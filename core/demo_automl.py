#!/usr/bin/env python3
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
AutoML Pipeline Demo - Showcase Automated Machine Learning Capabilities
Demonstrates the complete AutoML workflow with sample datasets.
"""

import logging
import time

import pandas as pd
from sklearn.datasets import make_classification, make_regression

from packages.automl.config import AutoMLConfigManager
from packages.automl.core.orchestrator import AutoMLConfig, AutoMLOrchestrator
from packages.automl.models.model_registry import ModelRegistry

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_classification_dataset(
    n_samples=1000, n_features=20, n_classes=2, random_state=42
):
    """Create a sample classification dataset."""
    logger.info(
        f"Creating sample classification dataset: {n_samples} samples, {n_features} features, {n_classes} classes"
    )

    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=n_features // 2,
        n_redundant=n_features // 4,
        n_classes=n_classes,
        random_state=random_state,
    )

    # Convert to DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    return df


def create_sample_regression_dataset(n_samples=1000, n_features=15, random_state=42):
    """Create a sample regression dataset."""
    logger.info(
        f"Creating sample regression dataset: {n_samples} samples, {n_features} features"
    )

    X, y = make_regression(
        n_samples=n_samples, n_features=n_features, noise=0.1, random_state=random_state
    )

    # Convert to DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y

    return df


def demo_quick_automl():
    """Demonstrate quick AutoML on a small classification dataset."""
    logger.info("\n" + "=" * 60)
    logger.info("🚀 DEMO 1: Quick AutoML Classification")
    logger.info("=" * 60)

    # Create sample dataset
    df = create_sample_classification_dataset(n_samples=500, n_features=10, n_classes=2)
    X = df.drop("target", axis=1).values
    y = df["target"].values
    feature_names = list(df.columns[:-1])

    # Quick configuration
    config = AutoMLConfig(
        task_type="classification",
        metric="accuracy",
        max_models=5,
        max_time_seconds=300,  # 5 minutes
        cv_folds=3,
        enable_hyperparameter_tuning=False,  # Skip tuning for speed
        verbose=True,
    )

    # Run AutoML
    start_time = time.time()
    orchestrator = AutoMLOrchestrator(config)
    result = orchestrator.fit(X, y, feature_names=feature_names)
    execution_time = time.time() - start_time

    # Display results
    logger.info("✅ Quick AutoML completed!")
    logger.info(f"⏱️ Execution time: {execution_time:.1f} seconds")
    logger.info(f"🎯 Best score: {result.best_score:.4f}")
    logger.info(f"🏆 Best Model: {result.best_params.get('model_name', 'Unknown')}")
    logger.info(f"📊 Models Evaluated: {len(result.model_rankings)}")

    # Show top 3 models
    logger.info("\n🏅 Top 3 Models:")
    for i, ranking in enumerate(result.model_rankings[:3], 1):
        model_name = ranking.get("name", "Unknown")
        score = ranking.get("score", 0)
        logger.info(f"  {i}. {model_name}: {score:.4f}")
    return result


def demo_advanced_automl():
    """Demonstrate advanced AutoML with hyperparameter tuning."""
    logger.info("\n" + "=" * 60)
    logger.info("🎯 DEMO 2: Advanced AutoML with Hyperparameter Tuning")
    logger.info("=" * 60)

    # Create larger dataset
    df = create_sample_classification_dataset(
        n_samples=1000, n_features=15, n_classes=3
    )
    X = df.drop("target", axis=1).values
    y = df["target"].values
    feature_names = list(df.columns[:-1])

    # Advanced configuration
    config = AutoMLConfig(
        task_type="classification",
        metric="f1_macro",  # Better for multiclass
        max_models=8,
        max_time_seconds=600,  # 10 minutes
        cv_folds=5,
        enable_hyperparameter_tuning=True,
        max_tuning_time_seconds=60,  # 1 minute per model
        enable_feature_selection=True,
        verbose=True,
    )

    # Run AutoML
    start_time = time.time()
    orchestrator = AutoMLOrchestrator(config)
    result = orchestrator.fit(X, y, feature_names=feature_names)
    execution_time = time.time() - start_time

    # Display results
    logger.info("✅ Advanced AutoML completed!")
    logger.info(f"⏱️ Execution time: {execution_time:.1f} seconds")
    logger.info(f"🎯 Best score: {result.best_score:.4f}")
    logger.info(f"🏆 Best Model: {result.best_params.get('model_name', 'Unknown')}")

    # Show feature importance if available
    if result.feature_importance:
        logger.info("\n🔍 Top 5 Important Features:")
        sorted_features = sorted(
            result.feature_importance.items(), key=lambda x: x[1], reverse=True
        )
        for feature, importance in sorted_features[:5]:
            logger.info(f"  • {feature}: {importance:.4f}")
    return result


def demo_regression_automl():
    """Demonstrate AutoML for regression tasks."""
    logger.info("\n" + "=" * 60)
    logger.info("📈 DEMO 3: AutoML Regression")
    logger.info("=" * 60)

    # Create regression dataset
    df = create_sample_regression_dataset(n_samples=800, n_features=12)
    X = df.drop("target", axis=1).values
    y = df["target"].values
    feature_names = list(df.columns[:-1])

    # Regression configuration
    config = AutoMLConfig(
        task_type="regression",
        metric="r2",
        max_models=6,
        max_time_seconds=400,  # 6-7 minutes
        cv_folds=5,
        enable_hyperparameter_tuning=True,
        max_tuning_time_seconds=45,
        verbose=True,
    )

    # Run AutoML
    start_time = time.time()
    orchestrator = AutoMLOrchestrator(config)
    result = orchestrator.fit(X, y, feature_names=feature_names)
    execution_time = time.time() - start_time

    # Display results
    logger.info("✅ Regression AutoML completed!")
    logger.info(f"⏱️ Execution time: {execution_time:.1f} seconds")
    logger.info(f"🎯 Best score: {result.best_score:.4f}")
    logger.info(f"🏆 Best Model: {result.best_params.get('model_name', 'Unknown')}")

    # Show regression metrics
    metrics = result.evaluation_metrics
    logger.info("\n📊 Regression Metrics:")
    logger.info(f"  • R² Score: {metrics.get('r2_score', 0):.4f}")
    logger.info(f"  • MAE: {metrics.get('mae', 0):.4f}")
    logger.info(f"  • MSE: {metrics.get('mse', 0):.4f}")
    logger.info(f"  • RMSE: {metrics.get('rmse', metrics.get('mse', 0) ** 0.5):.4f}")
    return result


def demo_config_presets():
    """Demonstrate different AutoML configuration presets."""
    logger.info("\n" + "=" * 60)
    logger.info("⚙️ DEMO 4: AutoML Configuration Presets")
    logger.info("=" * 60)

    config_manager = AutoMLConfigManager()

    presets = ["quick", "balanced", "thorough", "production"]

    logger.info("Available AutoML presets:")
    for preset in presets:
        try:
            config = config_manager.get_preset(preset)
            logger.info(
                f"  • {preset}: max_models={config.max_models}, time={config.max_time_seconds // 60}min, tuning={config.enable_hyperparameter_tuning}"
            )
        except Exception as e:
            logger.warning(f"Failed to load preset {preset}: {e}")

    # Demonstrate custom configuration
    logger.info("\n🔧 Creating custom configuration...")
    custom_config = config_manager.create_custom_config(
        base_preset="balanced",
        overrides={
            "max_models": 12,
            "metric": "f1_macro",
            "enable_feature_selection": True,
        },
    )

    logger.info(
        f"Custom config: max_models={custom_config.max_models}, metric={custom_config.metric}"
    )


def demo_model_registry():
    """Demonstrate model registry capabilities."""
    logger.info("\n" + "=" * 60)
    logger.info("📚 DEMO 5: Model Registry")
    logger.info("=" * 60)

    # Create a simple model for demonstration
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier

    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    # Register model
    registry = ModelRegistry()

    version_id = registry.register_model(
        model,
        "demo_model",
        metadata={"demo": True, "dataset_size": len(X)},
        performance_metrics={"accuracy": 0.95, "f1_score": 0.93},
        training_info={"training_time": 1.2, "random_state": 42},
    )

    logger.info(f"✅ Model registered with version: {version_id}")

    # List models
    models = registry.list_models()
    logger.info(f"📋 Total registered models: {len(models)}")

    # Get model info
    model_info = registry.get_model_history("demo_model")
    logger.info(f"📖 Model history for demo_model: {len(model_info)} versions")

    # Registry stats
    stats = registry.get_registry_stats()
    logger.info(f"📊 Registry stats: {stats}")


def main():
    """Run all AutoML demos."""
    logger.info("🤖 ECHOES AUTOML PIPELINE DEMO")
    logger.info("=" * 80)
    logger.info("This demo showcases the comprehensive AutoML capabilities:")
    logger.info("  • Automated model selection and evaluation")
    logger.info("  • Hyperparameter tuning and optimization")
    logger.info("  • Model comparison and ranking")
    logger.info("  • Feature importance analysis")
    logger.info("  • Model registry and versioning")
    logger.info("=" * 80)

    try:
        # Run demos
        demo_quick_automl()
        demo_advanced_automl()
        demo_regression_automl()
        demo_config_presets()
        demo_model_registry()

        logger.info("\n" + "=" * 80)
        logger.info("🎉 ALL AUTOML DEMOS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info("Key achievements:")
        logger.info("  ✅ Automated model selection across multiple algorithms")
        logger.info("  ✅ Intelligent hyperparameter optimization")
        logger.info("  ✅ Comprehensive model evaluation and comparison")
        logger.info("  ✅ Support for classification and regression tasks")
        logger.info("  ✅ Model registry with versioning and metadata")
        logger.info("  ✅ Flexible configuration presets")
        logger.info("")
        logger.info("🚀 Ready for production deployment!")
        logger.info("   Use the AutoML API at /automl/run for web-based automation")
        logger.info("   Access model registry at /automl/models for model management")

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
