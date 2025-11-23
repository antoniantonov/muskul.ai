# Rust Backend Quality Checklist

**Agent**: `@rust` | **Scope**: `backend/src/`, `backend/tests/`, `backend/benches/`

This checklist ensures all Rust backend code meets production-grade quality standards before marking tasks complete.

---

## Code Quality

- [ ] **Formatting**: All code passes `cargo fmt --check` with no changes needed
- [ ] **Linting**: All code passes `cargo clippy -- -D warnings` with zero warnings
- [ ] **Documentation**: Public APIs have doc comments (///), modules have module-level docs
- [ ] **Complexity**: Cyclomatic complexity ≤10 per function (use `cargo-cyclomatic` if available)
- [ ] **No Unsafe Code**: Avoid `unsafe` blocks unless absolutely necessary and documented with safety invariants
- [ ] **Error Handling**: Use `Result<T, E>` for recoverable errors, proper error types with context
- [ ] **Type Safety**: Strong typing, minimal use of `Option::unwrap()` (prefer `?`, `unwrap_or`, `expect` with context)

---

## Testing

- [ ] **Unit Tests**: All functions have unit tests in module `#[cfg(test)]` blocks
- [ ] **Integration Tests**: Cross-module tests in `tests/` directory
- [ ] **Coverage - Overall**: ≥80% code coverage via `cargo tarpaulin`
- [ ] **Coverage - Core Domain**: ≥90% coverage for OAuth2, ingestion, normalization, repositories
- [ ] **Test Naming**: Tests follow `test_<scenario>_<expected_outcome>` convention
- [ ] **Test Isolation**: Tests don't depend on execution order, use test fixtures
- [ ] **Mock External Dependencies**: Use `mockall` or similar for external APIs, databases in unit tests
- [ ] **Contract Tests**: API endpoints tested with real HTTP calls (use `reqwest` or `actix-test`)

---

## Security

- [ ] **No Secrets in Code**: No hardcoded API keys, passwords, or tokens
- [ ] **Input Validation**: All user inputs validated (use `validator` crate or custom validation)
- [ ] **SQL Injection Prevention**: Use SQLx prepared statements, parameterized queries only
- [ ] **OAuth2 PKCE**: All OAuth2 flows use PKCE for authorization code flow
- [ ] **Token Encryption**: OAuth2 tokens encrypted at rest (AES-256-GCM)
- [ ] **Rate Limiting**: Middleware applied to public endpoints (use `tower-governor` or similar)
- [ ] **Security Audit**: `cargo audit` passes with no known vulnerabilities
- [ ] **HTTPS Only**: All external API calls use HTTPS, no plaintext HTTP
- [ ] **CORS Configuration**: CORS middleware configured with allowed origins (no `*` in production)

---

## Performance

- [ ] **Benchmarks**: Performance-critical code has benchmarks in `benches/` using `criterion`
- [ ] **p95 Latency - Reads**: API read endpoints <200ms p95 (verified via benchmarks or load tests)
- [ ] **p95 Latency - Writes**: API write endpoints <500ms p95 (verified via benchmarks or load tests)
- [ ] **Memory Usage**: Service consumes <512MB memory under normal load (1000 concurrent users)
- [ ] **Async I/O**: All I/O operations use async/await (Tokio runtime)
- [ ] **Connection Pooling**: Database connections use pooling (SQLx pool size 5-20)
- [ ] **Query Optimization**: Database queries use indexes, no N+1 queries
- [ ] **Caching**: Frequently accessed data cached in Valkey with appropriate TTL

---

## Observability

- [ ] **OpenTelemetry Tracing**: Critical paths instrumented with spans (use `tracing` crate)
- [ ] **Structured Logging**: All logs use `tracing::info!`, `error!`, `warn!` with structured fields
- [ ] **Log Context**: Logs include `trace_id`, `span_id`, `user_id`, `request_id`, `latency_ms`
- [ ] **Metrics**: Prometheus metrics exported (use `prometheus` crate) - RED metrics (Rate, Errors, Duration)
- [ ] **Error Tracking**: Errors logged with full context (error chain, backtrace if available)
- [ ] **Health Checks**: `/health` endpoint with dependency checks (PostgreSQL, MongoDB, Valkey)
- [ ] **No Sensitive Data in Logs**: Passwords, tokens, PII redacted from logs

---

## Architecture

- [ ] **Layered Design**: Clear separation of concerns (handlers → services → repositories)
- [ ] **Repository Pattern**: Database access abstracted behind repository traits
- [ ] **Dependency Injection**: `Arc<AppState>` pattern for shared state (DB pools, HTTP clients, config)
- [ ] **Domain Models**: Business entities in `models/`, separate from database DTOs
- [ ] **API Contracts**: Endpoints match contract specifications in `contracts/*.md`
- [ ] **Error Types**: Custom error enum with `thiserror` for domain errors
- [ ] **Configuration**: All config from environment variables or config files (use `config` crate)

---

## Deployment

- [ ] **Multi-Stage Docker Build**: Dockerfile uses multi-stage build (builder + runtime)
- [ ] **Non-Root User**: Container runs as non-root user
- [ ] **Small Image Size**: Final image <100MB (use `alpine` or `distroless` base)
- [ ] **Environment Variables**: All secrets loaded from environment (Azure Key Vault in production)
- [ ] **Graceful Shutdown**: Server handles SIGTERM for graceful shutdown (Axum/Actix server config)
- [ ] **Readiness Probe**: `/ready` endpoint for Kubernetes readiness checks
- [ ] **Resource Limits**: Dockerfile or deployment manifest specifies CPU/memory limits

---

## Task Completion Validation

Before marking a Rust backend task as `[X]` complete:

1. ✅ Run `cargo fmt && cargo clippy -- -D warnings` - all pass
2. ✅ Run `cargo test` - all tests pass
3. ✅ Run `cargo tarpaulin` - coverage thresholds met (≥80% overall, ≥90% core)
4. ✅ Run `cargo bench` (if applicable) - no performance regressions
5. ✅ Run `cargo audit` - no vulnerabilities
6. ✅ Verify all checklist items above are complete for the specific task

---

**Agent Reference**: `.github/agents/rust.agent.md`  
**Last Updated**: 2025-11-23
