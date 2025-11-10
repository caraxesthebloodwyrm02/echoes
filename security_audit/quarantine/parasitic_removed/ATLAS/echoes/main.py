"""
Echoes AI Main Application

This module provides the main FastAPI application and server functionality
for the Echoes AI Multi-Agent System.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agents import AgentManager
from .config import Settings, get_settings
from .exceptions import setup_exception_handlers
from .middleware import setup_middleware
from .workflows import WorkflowManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EchoesApp:
    """Main Echoes AI application class."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.app = FastAPI(
            title="Echoes AI Multi-Agent System",
            description="A comprehensive AI platform for building and managing intelligent agents, workflows, and media search capabilities.",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
        )
        self.agent_manager = AgentManager(self.settings)
        self.workflow_manager = WorkflowManager(self.settings)

        self._setup_app()

    def _setup_app(self):
        """Set up the FastAPI application."""
        # Set up CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Set up custom middleware
        setup_middleware(self.app, self.settings)

        # Set up exception handlers
        setup_exception_handlers(self.app)

        # Set up routes
        self._setup_routes()

        # Set up lifecycle events
        self._setup_lifecycle()

    def _setup_routes(self):
        """Set up application routes."""
        from .routes import agents, ai, chatkit, health, workflows

        self.app.include_router(health.router, prefix="/health", tags=["Health"])

        self.app.include_router(ai.router, prefix="/api/ai", tags=["AI"])

        self.app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])

        self.app.include_router(
            workflows.router, prefix="/api/workflows", tags=["Workflows"]
        )

        self.app.include_router(chatkit.router, prefix="/api/chatkit", tags=["ChatKit"])

    def _setup_lifecycle(self):
        """Set up application lifecycle events."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("Starting Echoes AI application...")

            # Initialize managers
            await self.agent_manager.initialize()
            await self.workflow_manager.initialize()

            logger.info("Echoes AI application started successfully")

            yield

            # Shutdown
            logger.info("Shutting down Echoes AI application...")

            # Cleanup managers
            await self.agent_manager.cleanup()
            await self.workflow_manager.cleanup()

            logger.info("Echoes AI application shut down successfully")

        self.app.router.lifespan_context = lifespan

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app


# Global application instance
_app_instance: EchoesApp | None = None


def get_app() -> FastAPI:
    """Get the global FastAPI application instance."""
    global _app_instance
    if _app_instance is None:
        _app_instance = EchoesApp()
    return _app_instance.get_app()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a new Echoes AI application instance."""
    echoes_app = EchoesApp(settings)
    return echoes_app.get_app()


# Server functions
def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info",
):
    """Run the Echoes AI server."""
    get_settings()

    # Configure uvicorn
    config = uvicorn.Config(
        app="echoes.main:get_app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=log_level,
        access_log=True,
    )

    # Start server
    server = uvicorn.Server(config)
    server.run()


# Development server
def run_dev_server():
    """Run the Echoes AI development server."""
    run_server(host="127.0.0.1", port=8000, reload=True, workers=1, log_level="debug")


# Production server
def run_prod_server():
    """Run the Echoes AI production server."""
    settings = get_settings()

    run_server(
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=settings.workers,
        log_level="info",
    )


if __name__ == "__main__":
    run_dev_server()
