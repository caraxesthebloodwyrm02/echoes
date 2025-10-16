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
AutoML API - REST API Endpoints for AutoML Pipeline
Provides web interface for automated machine learning workflows.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from packages.automl.config import AutoMLConfigManager
from packages.automl.core.orchestrator import (
    AutoMLConfig,
    AutoMLOrchestrator,
)
from packages.automl.models.model_registry import ModelRegistry

# Import privacy middleware
try:
    from packages.security.privacy_middleware import PrivacyMiddleware

    privacy_middleware = PrivacyMiddleware(filter_mode="mask")
except ImportError:
    privacy_middleware = None

# Create router
router = APIRouter(prefix="/automl", tags=["automl"])
logger = logging.getLogger(__name__)

# Initialize components
config_manager = AutoMLConfigManager()
model_registry = ModelRegistry()


class AutoMLRequest(BaseModel):
    """Request model for AutoML execution."""

    task_type: str = Field("classification", description="Type of ML task")
    metric: str = Field("accuracy", description="Primary evaluation metric")
    max_models: int = Field(10, description="Maximum number of models to evaluate")
    max_time_seconds: int = Field(3600, description="Maximum execution time in seconds")
    cv_folds: int = Field(5, description="Number of cross-validation folds")
    enable_hyperparameter_tuning: bool = Field(
        True, description="Enable hyperparameter tuning"
    )
    dataset_info: Optional[Dict[str, Any]] = Field(None, description="Dataset metadata")


class AutoMLResponse(BaseModel):
    """Response model for AutoML results."""

    job_id: str
    status: str
    message: str
    results_path: Optional[str] = None


class AutoMLStatus(BaseModel):
    """Status response for AutoML job."""

    job_id: str
    status: str
    progress: float
    message: str
    results: Optional[Dict[str, Any]] = None


class PresetConfig(BaseModel):
    """Preset configuration response."""

    name: str
    description: str
    config: Dict[str, Any]


# In-memory job storage (in production, use database)
automl_jobs = {}


@router.post("/run", response_model=AutoMLResponse)
async def run_automl(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    task_type: str = Form("classification"),
    metric: str = Form("accuracy"),
    max_models: int = Form(10),
    max_time_seconds: int = Form(3600),
    cv_folds: int = Form(5),
    enable_hyperparameter_tuning: bool = Form(True),
):
    """
    Execute AutoML pipeline on uploaded dataset.

    Upload a CSV file and specify AutoML parameters to automatically
    find the best ML model for your dataset.
    """
    try:
        # Validate file type
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # Read dataset
        contents = await file.read()
        try:
            dataset = pd.read_csv(pd.io.common.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {e}")

        # Validate dataset
        if dataset.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        if len(dataset.columns) < 2:
            raise HTTPException(
                status_code=400, detail="Dataset must have at least 2 columns"
            )

        # Prepare data
        feature_cols = [col for col in dataset.columns if col != dataset.columns[-1]]
        target_col = dataset.columns[-1]

        X = dataset[feature_cols].values
        y = dataset[target_col].values

        # Create configuration
        config = AutoMLConfig(
            task_type=task_type,
            metric=metric,
            max_models=max_models,
            max_time_seconds=max_time_seconds,
            cv_folds=cv_folds,
            enable_hyperparameter_tuning=enable_hyperparameter_tuning,
        )

        # Generate job ID
        import uuid

        job_id = str(uuid.uuid4())

        # Store job info
        automl_jobs[job_id] = {
            "status": "running",
            "progress": 0.0,
            "message": "Initializing AutoML pipeline...",
            "config": config,
            "X": X,
            "y": y,
            "feature_names": feature_cols,
            "target_name": target_col,
        }

        # Start background task
        background_tasks.add_task(run_automl_background, job_id)

        return AutoMLResponse(
            job_id=job_id,
            status="running",
            message="AutoML pipeline started successfully",
            results_path=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AutoML execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"AutoML execution failed: {e}")


def run_automl_background(job_id: str):
    """Background task to execute AutoML pipeline."""
    try:
        job = automl_jobs[job_id]
        config = job["config"]
        X = job["X"]
        y = job["y"]
        feature_names = job["feature_names"]

        # Update progress
        job["progress"] = 10.0
        job["message"] = "Initializing AutoML orchestrator..."

        # Create orchestrator
        orchestrator = AutoMLOrchestrator(config)

        # Update progress
        job["progress"] = 20.0
        job["message"] = "Running AutoML pipeline..."

        # Execute AutoML
        result = orchestrator.fit(X, y, feature_names=feature_names)

        # Update progress
        job["progress"] = 90.0
        job["message"] = "Saving results..."

        # Save results
        results_dir = Path("automl_results")
        results_dir.mkdir(exist_ok=True)
        results_path = results_dir / f"automl_result_{job_id}.json"

        orchestrator.save_results(result, results_path)

        # Register best model
        model_version = model_registry.register_model(
            result.best_model,
            f"automl_{job_id}",
            metadata={
                "job_id": job_id,
                "task_type": config.task_type,
                "dataset_shape": f"{X.shape[0]}x{X.shape[1]}",
                "feature_names": feature_names,
            },
            performance_metrics=result.evaluation_metrics,
            training_info={
                "training_time": result.training_time,
                "models_evaluated": len(result.model_rankings),
            },
        )

        # Update job with results
        job.update(
            {
                "status": "completed",
                "progress": 100.0,
                "message": "AutoML pipeline completed successfully",
                "results": {
                    "best_model_score": result.best_score,
                    "best_model_params": result.best_params,
                    "training_time": result.training_time,
                    "model_rankings": [
                        {"name": r.get("name", "unknown"), "score": r.get("score", 0)}
                        for r in result.model_rankings[:5]  # Top 5
                    ],
                    "model_version": model_version,
                    "results_path": str(results_path),
                },
            }
        )

        logger.info(f"AutoML job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"AutoML job {job_id} failed: {e}")
        automl_jobs[job_id].update(
            {
                "status": "failed",
                "progress": 0.0,
                "message": f"AutoML execution failed: {str(e)}",
            }
        )


@router.get("/status/{job_id}", response_model=AutoMLStatus)
async def get_automl_status(job_id: str):
    """Get the status of an AutoML job."""
    if job_id not in automl_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = automl_jobs[job_id]

    # Apply privacy filtering to results if available
    results = job.get("results")
    if results and privacy_middleware:
        # Filter any sensitive information in results
        results = privacy_middleware._filter_dict(results)

    return AutoMLStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        results=results,
    )


@router.get("/presets", response_model=List[PresetConfig])
async def get_automl_presets():
    """Get available AutoML preset configurations."""
    presets = []

    preset_descriptions = {
        "quick": "Fast AutoML for small datasets (< 5 minutes)",
        "balanced": "Balanced performance and speed (15-30 minutes)",
        "thorough": "Comprehensive evaluation with tuning (1-2 hours)",
        "production": "Enterprise-grade AutoML (4+ hours)",
        "classification_binary": "Optimized for binary classification",
        "classification_multiclass": "Optimized for multiclass problems",
        "regression_standard": "Standard regression tasks",
        "regression_robust": "Robust regression for noisy data",
    }

    for name, description in preset_descriptions.items():
        try:
            config = config_manager.get_preset(name)
            presets.append(
                PresetConfig(
                    name=name, description=description, config=config.to_dict()
                )
            )
        except Exception as e:
            logger.warning(f"Failed to load preset {name}: {e}")

    return presets


@router.post("/suggest-config")
async def suggest_automl_config(dataset_info: Dict[str, Any]):
    """
    Suggest AutoML configuration based on dataset characteristics.

    Provide dataset metadata to get recommended AutoML settings.
    """
    try:
        config = config_manager.suggest_config(dataset_info)

        # Validate configuration
        validation = config_manager.validate_config_for_dataset(config, dataset_info)

        return {"suggested_config": config.to_dict(), "validation": validation}

    except Exception as e:
        logger.error(f"Config suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Config suggestion failed: {e}")


@router.get("/models")
async def list_registered_models():
    """List all registered models in the model registry."""
    try:
        models = model_registry.list_models()
        return {"total_models": len(models), "models": models}
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {e}")


@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """Get information about a specific model."""
    try:
        history = model_registry.get_model_history(model_name)
        if not history:
            raise HTTPException(status_code=404, detail="Model not found")

        # Get latest active version
        active_versions = [v for v in history if v.get("status") == "active"]
        latest_version = (
            max(active_versions, key=lambda x: x["created_at"])
            if active_versions
            else history[-1]
        )

        return {
            "model_name": model_name,
            "latest_version": latest_version,
            "version_history": history,
            "total_versions": len(history),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {e}")


@router.post("/models/{model_name}/deploy")
async def deploy_model(model_name: str, version: Optional[str] = None):
    """Deploy a model to production."""
    try:
        # Get the model
        model = model_registry.get_model(model_name, version)
        if model is None:
            raise HTTPException(status_code=404, detail="Model not found")

        # Update model status to active
        version_id = f"{model_name}_latest" if version is None else version
        model_registry.update_model_status(
            model_name, version_id, "active", "Deployed via API"
        )

        return {
            "status": "success",
            "message": f"Model {model_name} deployed successfully",
            "version": version_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model deployment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model deployment failed: {e}")


@router.get("/health")
async def automl_health_check():
    """Health check for AutoML service."""
    return {
        "status": "healthy",
        "service": "automl",
        "components": {
            "orchestrator": "available",
            "model_registry": "available",
            "config_manager": "available",
            "privacy_middleware": "available"
            if privacy_middleware
            else "not_available",
        },
    }
