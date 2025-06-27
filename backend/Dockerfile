# Use Python 3.13 slim image for security and size
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && \
    uv venv && \
    . .venv/bin/activate && \
    uv sync --no-dev

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["./.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
