"""
Echoes AI Multi-Agent System

A comprehensive AI platform for building and managing intelligent agents,
workflows, and media search capabilities.

Features:
- Multi-agent conversation management
- OpenAI and Anthropic AI integration
- Workflow orchestration
- Media search and classification
- Real-time chat and API endpoints
- Comprehensive monitoring and observability
"""

__version__ = "1.0.0"
__author__ = "Echoes AI Team"
__email__ = "team@echoes.ai"
__license__ = "MIT"

# Core imports
from .agents import Agent, Conversation
from .config import Settings
from .main import EchoesApp
from .workflows import Workflow

# Public API
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "EchoesApp",
    "Settings",
    "Agent",
    "Conversation",
    "Workflow",
]

# Package metadata
__title__ = "echoes-ai"
__description__ = (
    "Echoes AI Multi-Agent System with Media Search and Workflow Automation"
)
__url__ = "https://github.com/echoes-ai/echoes"
__keywords__ = [
    "ai",
    "agents",
    "openai",
    "fastapi",
    "media-search",
    "workflow",
    "automation",
    "chatbot",
    "llm",
    "multimodal",
    "enterprise",
]

# Python version requirement
__python_requires__ = ">=3.11"

# Installation requirements
__install_requires__ = [
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "openai>=1.3.7",
    "httpx>=0.25.2",
    "python-dotenv>=1.0.0",
    "python-multipart>=0.0.6",
    "aiofiles>=23.2.1",
    "click>=8.1.7",
    "rich>=13.7.0",
    "typer>=0.9.0",
]

# Optional dependencies
__extras_require__ = {
    "dev": [
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "pytest-cov>=4.1.0",
        "black>=23.11.0",
        "ruff>=0.1.6",
        "mypy>=1.7.1",
        "pre-commit>=3.6.0",
        "build>=0.10.0",
        "twine>=4.0.0",
    ],
    "cluster": ["docker>=6.1.0", "docker-compose>=1.29.0"],
    "monitoring": [
        "grafana-api>=1.0.3",
        "prometheus-client>=0.19.0",
        "jaeger-client>=4.8.0",
    ],
    "docs": [
        "mkdocs>=1.4.0",
        "mkdocs-material>=9.0.0",
    ],
    "all": ["echoes-ai[dev,cluster,monitoring,docs]"],
}


def get_version():
    """Get the current version of Echoes AI."""
    return __version__


def get_info():
    """Get package information."""
    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "url": __url__,
        "keywords": __keywords__,
        "python_requires": __python_requires__,
    }


# CLI entry point
def main():
    """Main CLI entry point for Echoes AI."""
    from .cli import app

    app()


# Server entry point
def run_server():
    """Run the Echoes AI server."""
    from .main import run_server as _run_server

    _run_server()


# Cluster entry point
def run_cluster():
    """Run the Echoes AI cluster setup."""
    from .cluster import main as _run_cluster

    _run_cluster()
