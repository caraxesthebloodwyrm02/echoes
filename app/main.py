"""
AI Advisor API - Main Application

FastAPI application with:
- Provenance enforcement
- Human-in-the-loop feedback
- Agent safety controls
- Domain-aligned intelligence (Science, Commerce, Arts)
"""

import logging
import os
from datetime import datetime

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency fallback for tests

    def load_dotenv(*args, **kwargs):
        return None


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import provenance middleware with fallback for tests that add `app/` to sys.path
try:
    from app.core.validation.provenance_enforcer import ProvenanceEnforcerMiddleware
except ImportError:  # pragma: no cover
    from core.validation.provenance_enforcer import ProvenanceEnforcerMiddleware  # type: ignore

# Support running as package (app.main) and as module with app/ on sys.path (tests)
try:
    from app.api.routes import system_router, auth_router
    from app.domains.science.science_module import science_router
    from app.domains.commerce.commerce_module import commerce_router
    from app.domains.arts.arts_module import arts_router
    from app.domains.commerce.finance import finance_router
except ImportError:  # pragma: no cover - fallback for alternate sys.path in tests
    from api.routes import system_router, auth_router  # type: ignore
    from domains.science.science_module import science_router  # type: ignore
    from domains.commerce.commerce_module import commerce_router  # type: ignore
    from domains.arts.arts_module import arts_router  # type: ignore
    from domains.commerce.finance import finance_router  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Advisor API",
    description="""
    **AI Advisor** - Domain-aligned AI with safety controls

    ## Features

    - 🔒 **Provenance Enforcement**: All assertions must cite sources
    - 🤝 **Human-in-the-Loop**: Continuous improvement through feedback
    - 🛡️ **Agent Safety**: Dry-run mode, kill-switch, action whitelist
    - 🔬 **Science Domain**: Biomedical research, chemistry, physics
    - 💼 **Commerce Domain**: FinanceAdvisor, UBI simulation, employment matching
    - 🎨 **Arts Domain**: Creative intelligence, cultural preservation

    ## FinanceAdvisor Module

    - 📊 **7-Phase Financial Intelligence**: Complete lifecycle from analysis to success
    - 🎯 **Goal Analysis**: Natural language to structured objectives
    - 📈 **Smart Predictions**: ML-powered income, retirement, and market forecasting
    - 💡 **Portfolio Optimization**: Risk-based asset allocation
    - 🗺️ **Success Roadmaps**: Clear paths with milestones and contingencies
    - ✅ **Ethical AI**: Bias-free, fair, and transparent recommendations

    ## Safety First

    - All agent actions default to dry-run mode
    - Provenance required on all assertions
    - Feedback queue for human review
    - Emergency kill-switch for runaway agents

    ## Domains

    - **Science**: Health, Physics, Chemistry, Biology
    - **Commerce**: Finance, Universal Income, Employment
    - **Arts**: Creativity, History, Language, Culture
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AI Advisor Team",
        "url": "https://github.com/yourusername/ai-advisor",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS middleware (configure appropriately for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],  # Specific origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add provenance enforcer middleware
app.add_middleware(
    ProvenanceEnforcerMiddleware,
    enforce_strict=True,  # Set to False for development
)


# Include routers


app.include_router(system_router, prefix="/api", tags=["System"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(science_router, prefix="/api/science", tags=["Science"])
app.include_router(commerce_router, prefix="/api/commerce", tags=["Commerce"])
app.include_router(arts_router, prefix="/api/arts", tags=["Arts"])
app.include_router(finance_router, prefix="/api/finance", tags=["Finance Advisor"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Advisor API",
        "version": "0.1.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs",
        "health": "/api/health",
        "metrics": "/api/metrics",
        "domains": ["science", "commerce", "arts"],
        "safety_features": [
            "provenance_enforcement",
            "hil_feedback",
            "agent_dry_run",
            "kill_switch",
        ],
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": str(exc),
            "type": "validation_error",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors."""
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("🚀 AI Advisor API starting up...")
    logger.info("✅ Provenance enforcement: ENABLED")
    logger.info("✅ Agent safety layer: ENABLED")
    logger.info("✅ HIL feedback: ENABLED")
    logger.info("💰 FinanceAdvisor module: LOADED")
    logger.info("📡 API documentation: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("👋 AI Advisor API shutting down...")


# Load environment variables from .env file if it exists
load_dotenv()

# Main entry point
if __name__ == "__main__":
    import uvicorn

    # Get host and port from environment variables with secure defaults
    host = os.getenv("HOST", "127.0.0.1")  # Default to localhost for security
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    # Log startup configuration
    logger.info(f"🚀 Starting AI Advisor API on {host}:{port}")
    logger.info(f"🔧 Reload: {reload_enabled}, Log Level: {log_level}")

    # Start the server with secure configuration
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level=log_level,
    )
