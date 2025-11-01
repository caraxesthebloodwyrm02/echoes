# Use a specific Python version that has better package compatibility
FROM python:3.11-slim-bookworm as builder

# Install security updates in builder stage
RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/venv

# Create and activate virtual environment
RUN python -m venv .
ENV PATH="/opt/venv/bin:$PATH"

# Install build dependencies
RUN pip install --upgrade pip wheel

# Copy and install dependencies
COPY requirements.txt* ./

# Install core dependencies (skip Windows-specific packages)
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings \
    httpx pytest pytest-cov python-multipart python-dotenv \
    PyJWT cryptography slowapi openai || true

# Final stage
FROM python:3.11-slim-bookworm

# Install security updates in final stage
RUN apt-get update && apt-get upgrade -y --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a non-root user
RUN groupadd -r appuser -g 1000 && \
    useradd -u 1000 -r -g appuser -d /home/appuser -s /sbin/nologin -c "Application User" appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

# Create data directory with proper permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code with proper permissions
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser api ./api
COPY --chown=appuser:appuser automation ./automation
COPY --chown=appuser:appuser echoes ./echoes
COPY --chown=appuser:appuser src ./src
COPY --chown=appuser:appuser tools ./tools
COPY --chown=appuser:appuser main.py* .
COPY --chown=appuser:appuser assistant_v2_core.py* .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "echoes.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
