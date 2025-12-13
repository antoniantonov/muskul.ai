# ETL Service Dockerfile
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
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY python/ /app/

# Copy main entry point
COPY main.py /app/

# Create non-root user
RUN groupadd -g 1000 muskul && \
    useradd -u 1000 -g muskul -s /bin/bash -m muskul && \
    chown -R muskul:muskul /app

# Switch to non-root user
USER muskul

# Run batch job
CMD ["python", "main.py"]
