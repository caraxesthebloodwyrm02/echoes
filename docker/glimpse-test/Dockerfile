# Security-hardened minimal test image for Glimpse ML
FROM python:3.13-slim

# Metadata
LABEL org.opencontainers.image.source="https://github.com/your-org/echoes"
LABEL org.opencontainers.image.description="Minimal reproducible test environment"
LABEL org.opencontainers.image.created="2025-10-20"

# Create non-root user
RUN groupadd -r glimpse && useradd -r -g glimpse glimpse

# Working directory
WORKDIR /app

# Install only essential build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install dependencies with security constraints
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --only-binary=:all: markupsafe \
    && pip install --no-cache-dir --only-binary=:all: --index-url https://download.pytorch.org/whl/cpu torch==2.9.0+cpu \
    && pip install --no-cache-dir --only-binary=:all: pytest pytest-json-report

# Copy application code
COPY . .

# Switch to non-root user
USER glimpse

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import torch; print('PyTorch OK')" || exit 1

# Default entrypoint for testing
ENTRYPOINT ["pytest"]
CMD ["tests/"]