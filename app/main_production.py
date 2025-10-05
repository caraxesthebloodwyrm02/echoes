"""
Production Entry Point for AI Advisor API

This module provides a production-optimized configuration for the AI Advisor API.
It includes security best practices, performance optimizations, and production-specific settings.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging before importing other modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/ai_advisor.log")],
)
logger = logging.getLogger(__name__)


def create_application():
    """Create and configure the FastAPI application for production."""
    from fastapi import FastAPI
    from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    # Import the main app after configuring logging
    from app.main import app as main_app

    # Create a new FastAPI instance with production settings
    app = FastAPI(
        title="AI Advisor API - Production",
        description="Production deployment of the AI Advisor API with enhanced security",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Apply all routes and middleware from main app
    app.include_router(main_app.router)

    # Production security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["your-production-domain.com", "api.your-production-domain.com"],
    )

    # Enable HTTPS redirection in production (requires SSL termination at load balancer)
    if os.getenv("ENABLE_HTTPS_REDIRECT", "true").lower() == "true":
        app.add_middleware(HTTPSRedirectMiddleware)

    # Add security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    return app


# Create the application
app = create_application()

if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/ai_advisor.log",
                    "maxBytes": 10485760,  # 10MB
                    "backupCount": 5,
                    "formatter": "default",
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": os.getenv("LOG_LEVEL", "INFO"),
            },
        }
    )

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Get configuration from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "80"))
    workers = int(os.getenv("WEB_CONCURRENCY", "4"))

    # Log startup information
    logger.info(f"🚀 Starting AI Advisor API in PRODUCTION mode on {host}:{port}")
    logger.info(f"🔧 Workers: {workers}")

    # Run the application with Uvicorn
    uvicorn.run(
        "app.main_production:app",
        host=host,
        port=port,
        workers=workers,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        proxy_headers=True,
        forwarded_allow_ips="*",
        timeout_keep_alive=30,
    )
