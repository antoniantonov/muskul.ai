# Muskul.ai Backend

Rust backend API service for the muskul.ai fitness platform.

## Technology Stack

- **Rust**: 1.75+ (stable)
- **Runtime**: Tokio (async)
- **Framework**: Axum
- **Databases**: PostgreSQL (SQLx), MongoDB, Redis/Valkey
- **Observability**: OpenTelemetry, tracing

## Project Structure

```
src/
├── main.rs              # Application entry point
├── lib.rs               # Library exports
├── error.rs             # Error types and handling
├── api/                 # REST API endpoints
├── config/              # Configuration management
├── models/              # Data models and DTOs
├── services/            # Business logic layer
├── repositories/        # Data access layer
├── providers/           # Fitness provider integrations
└── middleware/          # HTTP middleware (auth, tracing, etc.)
```

## Getting Started

### Prerequisites

- Rust 1.75 or later
- PostgreSQL 15+
- MongoDB 7+
- Redis/Valkey 7+

### Development

```bash
# Build the project
cargo build

# Run in development mode
cargo run

# Run tests
cargo test

# Run with hot reload (install cargo-watch)
cargo watch -x run
```

### Configuration

Configuration is loaded from multiple sources in order of precedence:
1. `config/default.toml` - Default values
2. `config/{RUN_MODE}.toml` - Environment-specific (development, production)
3. `config/local.toml` - Local overrides (gitignored)
4. Environment variables with `MUSKUL_` prefix

Example environment variables:
```bash
export MUSKUL__DATABASE__URL="postgresql://user:pass@localhost/muskul"
export MUSKUL__SERVER__PORT=8080
```

## API Endpoints

- `GET /health` - Health check
- `GET /` - API information
- `/api/*` - REST API endpoints (to be implemented)

## Development Guidelines

- Follow Rust standard conventions and idiomatic patterns
- Use `async`/`await` for all I/O operations
- Implement proper error handling with `thiserror`
- Add tracing spans for observability
- Write unit tests for business logic
- Write integration tests for API endpoints
- Use `validator` for input validation
- Document public APIs with rustdoc comments

## Testing

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_name

# Run with logging
RUST_LOG=debug cargo test

# Run integration tests only
cargo test --test '*'
```

## License

Proprietary - Muskul.ai
