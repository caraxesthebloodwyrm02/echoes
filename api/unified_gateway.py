#!/usr/bin/env python3
"""
Unified Gateway API
FastAPI service providing unified access to cross-platform capabilities

Endpoints:
- /analyze: Unified analysis combining bias detection, knowledge graphs, trajectory analysis
- /health: Platform health status
- /capabilities: Available platform capabilities
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from integrations.turbo_bridge import create_bridge
from packages.core.config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Unified Gateway API",
    description="Cross-platform integration gateway for Echoes, TurboBookshelf, and GlimpsePreview",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize bridge
bridge = create_bridge()

# Pydantic models for API
class AnalysisRequest(BaseModel):
    text: List[str] = []
    query: str = ""
    trajectory_data: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    status: str
    platforms: Dict[str, bool]
    timestamp: str

class CapabilitiesResponse(BaseModel):
    platforms: Dict[str, List[str]]
    unified_features: List[str]
    version: str

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Unified Gateway API",
        "version": "1.0.0",
        "endpoints": [
            "/analyze - Unified analysis",
            "/health - Platform health",
            "/capabilities - Available capabilities"
        ]
    }

@app.post("/analyze")
async def analyze(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Perform unified analysis combining capabilities from all platforms.

    Combines:
    - Bias detection (TurboBookshelf)
    - Knowledge graph queries (Echoes)
    - Trajectory analysis (GlimpsePreview)
    """
    try:
        # Prepare data for bridge
        data = {
            "text": request.text,
            "query": request.query,
            "trajectory": request.trajectory_data
        }

        # Perform unified analysis
        results = bridge.unified_analysis(data)

        return {
            "success": True,
            "results": results,
            "request_id": f"analysis_{len(request.text)}_{len(request.query)}"
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health() -> HealthResponse:
    """Get health status of all integrated platforms."""
    try:
        system_status = bridge.get_system_status()

        # Determine overall status
        all_connected = all(system_status["connections"].values())
        status = "healthy" if all_connected else "degraded"

        return HealthResponse(
            status=status,
            platforms=system_status["connections"],
            timestamp=system_status.get("timestamp", "unknown")
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/capabilities")
async def capabilities() -> CapabilitiesResponse:
    """Get available capabilities across all platforms."""
    try:
        # Get system status for available platforms
        system_status = bridge.get_system_status()
        connections = system_status["connections"]

        # Define platform capabilities
        platform_capabilities = {
            "echoes": [
                "knowledge_graph_query",
                "ai_orchestration",
                "deterministic_workflows"
            ],
            "turbo": [
                "bias_detection",
                "web_interface",
                "creative_content"
            ] if connections.get("turbo", False) else [],
            "glimpse": [
                "trajectory_analysis",
                "real_time_visualization",
                "comprehension_metrics"
            ] if connections.get("glimpse", False) else []
        }

        unified_features = [
            "cross_platform_analysis",
            "streamlined_communication",
            "unified_suggestions"
        ]

        return CapabilitiesResponse(
            platforms=platform_capabilities,
            unified_features=unified_features,
            version="1.0.0"
        )

    except Exception as e:
        logger.error(f"Capabilities check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Capabilities check failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("Starting Unified Gateway API")
    logger.info(f"Bridge connections: {bridge.connections}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Unified Gateway API")

if __name__ == "__main__":
    import uvicorn

    # Load configuration
    config = load_config()

    # Start server
    uvicorn.run(
        "unified_gateway:app",
        host="127.0.0.1",
        port=8000,
        reload=config.debug,
        log_level=config.log_level.lower()
    )
