# Multi-stage Dockerfile for echoe packages - Week 2 Foundation
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY packages/ /app/packages/
COPY workspace-setup/requirements/ /app/workspace-setup/requirements/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r workspace-setup/requirements/base.txt && \
    pip install --no-cache-dir -r workspace-setup/requirements/dev.txt

# Install our packages in editable mode
RUN pip install -e packages/core && \
    pip install -e packages/security && \
    pip install -e packages/monitoring

# Development stage
FROM base as development

# Install additional dev tools
RUN pip install --no-cache-dir \
    ipython \
    black \
    mypy \
    bandit

# Copy test files
COPY packages/core/tests/ /app/packages/core/tests/
COPY packages/security/tests/ /app/packages/security/tests/
COPY packages/monitoring/tests/ /app/packages/monitoring/tests/

# Test stage
FROM development as test

# Run all tests
RUN pytest packages/ -v --tb=short --junitxml=test-results.xml || true

# Production stage
FROM base as production

# Remove dev dependencies for smaller image
RUN pip uninstall -y pytest pytest-cov black mypy bandit

# Create non-root user
RUN useradd -m -u 1000 echoe && chown -R echoe:echoe /app
USER echoe

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from core import get_logger; from security import AuthManager; from monitoring import MetricsCollector; print('OK')" || exit 1

CMD ["python"]
