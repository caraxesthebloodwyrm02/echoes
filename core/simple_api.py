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
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies OF THE SOFTWARE, and to permit persons to whom the Software is
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
Simple AutoML API - Basic REST endpoints for AutoML functionality
"""

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from packages.automl import AutoMLConfig, SimpleAutoML

# Create router
router = APIRouter(prefix="/simple-automl", tags=["simple-automl"])


@router.post("/run")
async def run_simple_automl(
    file: UploadFile = File(...),
    task_type: str = Form("classification"),
    max_models: int = Form(3),
    cv_folds: int = Form(3),
):
    """
    Run simplified AutoML on uploaded dataset.

    This endpoint provides basic automated machine learning functionality:
    - Model selection and evaluation
    - Cross-validation scoring
    - Feature importance analysis
    - Best model recommendation

    Parameters:
    - file: CSV file with dataset (features + target column)
    - task_type: "classification" or "regression"
    - max_models: Maximum number of models to evaluate (default: 3)
    - cv_folds: Number of cross-validation folds (default: 3)
    """
    try:
        # Validate file type
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # Validate parameters
        if task_type not in ["classification", "regression"]:
            raise HTTPException(
                status_code=400,
                detail="task_type must be 'classification' or 'regression'",
            )

        if max_models < 1 or max_models > 10:
            raise HTTPException(
                status_code=400, detail="max_models must be between 1 and 10"
            )

        if cv_folds < 2 or cv_folds > 10:
            raise HTTPException(
                status_code=400, detail="cv_folds must be between 2 and 10"
            )

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

        # Run AutoML
        config = AutoMLConfig(
            task_type=task_type, max_models=max_models, cv_folds=cv_folds
        )

        automl = SimpleAutoML(config)
        results = automl.fit(X, y, feature_names=feature_cols)

        # Prepare response (exclude the actual model object for JSON serialization)
        response = {
            "task_type": results["task_type"],
            "best_score": results["best_score"],
            "best_model_name": results["best_model_name"],
            "models_evaluated": results["models_evaluated"],
            "execution_time": results["execution_time"],
            "model_rankings": [
                {
                    "name": r["name"],
                    "score": r["score"],
                    "std_score": r["std_score"],
                    "feature_importance": r.get("feature_importance"),
                }
                for r in results["all_results"]
            ],
        }

        return JSONResponse(content=response, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AutoML execution failed: {e}")


@router.get("/models")
async def get_available_models():
    """Get list of available models for AutoML."""
    return {
        "classification_models": [
            "random_forest",
            "logistic_regression",
            "svm",
            "decision_tree",
        ],
        "regression_models": [
            "random_forest",
            "linear_regression",
            "svm",
            "decision_tree",
        ],
        "description": "Available models for automated evaluation",
    }


@router.get("/presets")
async def get_automl_presets():
    """Get recommended AutoML configuration presets."""
    return {
        "quick": {
            "description": "Fast evaluation with basic models",
            "max_models": 3,
            "cv_folds": 3,
            "estimated_time": "1-2 minutes",
        },
        "balanced": {
            "description": "Balanced performance and speed",
            "max_models": 5,
            "cv_folds": 5,
            "estimated_time": "3-5 minutes",
        },
        "thorough": {
            "description": "Comprehensive evaluation",
            "max_models": 8,
            "cv_folds": 5,
            "estimated_time": "5-10 minutes",
        },
    }


@router.get("/health")
async def automl_health_check():
    """Health check for AutoML service."""
    try:
        return {
            "status": "healthy",
            "service": "simple-automl",
            "components": {
                "SimpleAutoML": "available",
                "AutoMLConfig": "available",
                "scikit-learn": "available",
            },
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
