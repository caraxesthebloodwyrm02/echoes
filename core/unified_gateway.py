"""Unified API gateway for health monitoring endpoints."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.health_monitor import router as health_router

app = FastAPI(
    title="Unified Platform API",
    version="2.0.0",
    description="Production-ready API for platform health monitoring",
)

# Enable CORS for frontend integration and dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router, prefix="/api", tags=["Health"])


@app.get("/")
async def root():
    return {
        "message": "Unified Platform API",
        "version": "2.0.0",
        "endpoints": ["/api/health", "/api/health/simple"],
    }


@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon"}
