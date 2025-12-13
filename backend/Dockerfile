# syntax=docker/dockerfile:1

# ============================================================================
# Builder Stage - Compile the Rust binary
# ============================================================================
FROM rust:1.91-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependency manifests first for layer caching
COPY Cargo.toml Cargo.lock ./

# Create dummy src and benches to build dependencies
# Note: benches are referenced in Cargo.toml and must exist to parse manifest
RUN mkdir -p src benches && \
    echo "fn main() {println!(\"dummy\")}" > src/main.rs && \
    echo "fn main() {}" > benches/api_bench.rs && \
    echo "fn main() {}" > benches/database_bench.rs && \
    cargo build --release --locked --bins && \
    rm -rf src benches

# Copy the actual source code
COPY src ./src
COPY benches ./benches
COPY config ./config

# Build the application with all optimizations
# Note: strip is already configured in Cargo.toml profile.release.strip = true
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/app/target \
    cargo build --release --locked && \
    cp /app/target/release/muskul-backend /usr/local/bin/muskul-backend

# ============================================================================
# Runtime Stage - Minimal production image
# ============================================================================
FROM debian:bookworm-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -g 1000 muskul && \
    useradd -r -u 1000 -g muskul muskul && \
    mkdir -p /app /app/config && \
    chown -R muskul:muskul /app

# Copy the compiled binary from builder
COPY --from=builder /usr/local/bin/muskul-backend /usr/local/bin/muskul-backend

# Copy configuration files
COPY --chown=muskul:muskul config /app/config

# Set working directory
WORKDIR /app

# Switch to non-root user
USER muskul

# Environment variables with sensible defaults
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8080
ENV RUST_LOG=info

# Expose the service port (currently hardcoded in main.rs)
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the binary
CMD ["/usr/local/bin/muskul-backend"]
