# Echoes API - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r apiuser -g 1000 && \
    useradd -u 1000 -r -g apiuser -d /home/apiuser -s /sbin/nologin -c "API User" apiuser && \
    mkdir -p /home/apiuser && \
    chown -R apiuser:apiuser /home/apiuser

# Copy requirements and install dependencies
COPY echoes/api/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY echoes/api/ ./echoes/api/
COPY echoes/core/ ./echoes/core/

# Copy app directory (needed for assistant components)
COPY app/ ./app/

# Copy tools directory (needed for assistant)
COPY tools/ ./tools/

# Copy assistant core (needed for multimodal processing)
COPY assistant_v2_core.py .

# Set working directory to project root for proper imports
WORKDIR /app

# Set permissions
RUN chown -R apiuser:apiuser /app

# Switch to non-root user
USER apiuser

# Set environment variables
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API server
CMD ["python", "echoes/api/start_prod.py"]
