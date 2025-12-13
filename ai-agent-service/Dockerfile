# AI Agent Service Dockerfile
# Base: python:3.12-slim-bookworm
# Target size: <200MB
# Security: Non-root user (UID 1000)

FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application source
COPY src/ /app/src/

# Create non-root user
RUN groupadd -g 1000 muskul && \
    useradd -u 1000 -g muskul -s /bin/bash -m muskul && \
    chown -R muskul:muskul /app

# Switch to non-root user
USER muskul

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
