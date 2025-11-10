# ------------ Stage 1: Build the Python package ------------
FROM python:3.11-slim AS builder
WORKDIR /app
COPY . .
RUN pip install --upgrade pip build twine
RUN python -m build

# ------------ Stage 2: Final runtime image ------------
FROM python:3.11-slim
WORKDIR /app

# Add non-root user (best practice)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Only install build/publish tools for TEST/DEV use (not needed in prod if just running)
RUN pip install --user build twine

# Copy source and wheels
COPY --chown=appuser:appuser . .
COPY --from=builder --chown=appuser:appuser /app/dist/*.whl ./dist/

# Ensure user local bin is in PATH
ENV PATH="/home/appuser/.local/bin:$PATH"

# No credentials! Only publish wheels if you override CMD
CMD ["python", "scripts/publish.py", "--repository", "testpypi"]