"""
Echoes AI Setup Script

This script provides backward compatibility and additional setup functionality
for the Echoes AI Multi-Agent System.
"""

import os

from setuptools import find_packages, setup

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# Read version from __init__.py
def get_version():
    version_file = os.path.join(this_directory, "echoes", "__init__.py")
    with open(version_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    return "1.0.0"


# Setup configuration
setup(
    name="echoes-ai",
    version=get_version(),
    author="Echoes AI Team",
    author_email="team@echoes.ai",
    description="Echoes AI Multi-Agent System with Media Search and Workflow Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/echoes-ai/echoes",
    project_urls={
        "Bug Tracker": "https://github.com/echoes-ai/echoes/issues",
        "Documentation": "https://echoes-ai.readthedocs.io",
        "Source Code": "https://github.com/echoes-ai/echoes",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Office/Business",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.11",
    keywords=[
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
    ],
    install_requires=[
        # Core AI & API Layers
        "openai>=1.3.7",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.2",
        "requests>=2.32.5",
        "python-dotenv>=1.0.0",
        # Security & Rate Limiting
        "slowapi>=0.1.9",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "pygments>=2.19.2",
        # Database & Storage
        "psycopg2-binary>=2.9.9",
        "sqlalchemy>=2.0.23",
        "alembic>=1.13.1",
        # "asyncpg>=0.29.0",  # Commented out due to Windows build issues
        "redis>=5.0.1",
        "aioredis>=2.0.1",
        # Data Processing
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "tiktoken>=0.5.2",
        # Utilities
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.1",
        "click>=8.1.7",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "pyyaml>=6.0.1",
        "jinja2>=3.1.2",
        "orjson>=3.9.10",
        "cryptography>=41.0.8",
        # Monitoring & Observability
        "prometheus-client>=0.19.0",
        "jaeger-client>=4.8.0",
        "opentelemetry-api>=1.21.0",
        "opentelemetry-sdk>=1.21.0",
        "opentelemetry-instrumentation-fastapi>=0.42b0",
        # Additional Features
        "websockets>=12.0",
        "cachetools>=5.3.2",
        "strawberry-graphql>=0.215.1",
        "anthropic>=0.7.8",
    ],
    extras_require={
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
    },
    entry_points={
        "console_scripts": [
            "echoes=echoes.cli:main",
            "echoes-server=echoes.main:run_server",
            "echoes-cluster=echoes.cluster:main",
        ],
    },
    include_package_data=True,
    package_data={
        "echoes": [
            "py.typed",
            "templates/**/*",
            "static/**/*",
            "config/*.yaml",
            "config/*.json",
        ]
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    # Additional metadata
    maintainer="Echoes AI Team",
    maintainer_email="team@echoes.ai",
    # Test suite
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "pytest-cov>=4.1.0",
    ],
    # URLs
    download_url="https://github.com/echoes-ai/echoes/archive/v1.0.0.tar.gz",
    # Development status
    development_status="Production/Stable",
)
