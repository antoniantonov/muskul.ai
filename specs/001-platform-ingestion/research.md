# Research & Best Practices
**Feature**: 001-platform-ingestion  
**Generated**: 2025-11-15  
**Purpose**: Document technology decisions, patterns, and best practices for fitness data ingestion platform.

---

## Technology Stack Decisions

### 1. Backend Language: Rust 1.75+

**Decision**: Use Rust for backend API and data processing services.

**Rationale**:
- **Performance**: Zero-cost abstractions, minimal runtime overhead, compiled to native code. Critical for high-throughput data ingestion (1000+ activities/minute).
- **Memory Safety**: Ownership model prevents memory leaks, data races, and null pointer errors without garbage collection overhead.
- **Concurrency**: Tokio async runtime provides efficient concurrency for handling multiple provider API calls and database operations simultaneously.
- **Type Safety**: Strong static typing catches errors at compile time, reducing runtime bugs in production.
- **Ecosystem Maturity**: Robust crates for HTTP clients (Reqwest), serialization (Serde), database access (SQLx), and observability (OpenTelemetry).

**Alternatives Considered**:
- **Go**: Simpler learning curve, good concurrency, but garbage collection introduces latency spikes that could violate p95 <200ms API budget.
- **Node.js/TypeScript**: Unified language with frontend, but single-threaded event loop struggles with CPU-intensive normalization tasks.
- **Python**: Excellent data processing libraries, but GIL limits concurrency and performance for high-throughput scenarios.

**References**:
- [Tokio Documentation](https://tokio.rs/)
- [Rust Async Book](https://rust-lang.github.io/async-book/)
- [SQLx Documentation](https://github.com/launchbadge/sqlx)

---

### 2. Frontend: React 18+ with TypeScript 5.x

**Decision**: Use React 18+ with TypeScript for SPA frontend.

**Rationale**:
- **Component Reusability**: React's component model promotes modular, testable UI components (charts, forms, dashboards).
- **Type Safety**: TypeScript 5.x provides strong typing for API contracts, state management, and component props, reducing runtime errors.
- **Performance**: React 18's concurrent rendering and automatic batching optimize render performance for interactive dashboards.
- **Ecosystem**: Rich ecosystem for charting (Plotly.js), state management (React Query), styling (Tailwind CSS), testing (Vitest, Playwright).
- **Developer Experience**: Hot module replacement via Vite, strong IDE support, extensive community resources.

**Alternatives Considered**:
- **Vue.js**: Simpler API, but smaller ecosystem for data visualization and enterprise tooling.
- **Svelte**: Excellent performance, but less mature ecosystem and hiring pool.
- **Angular**: Enterprise-grade, but heavier bundle size and steeper learning curve.

**References**:
- [React 18 Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)

---

### 3. Storage Strategy: MongoDB (Landing Zone) + PostgreSQL (Normalized) + Valkey (Cache)

**Decision**: Use multi-tier storage strategy with MongoDB for raw data, PostgreSQL for structured data, and Valkey for caching.

**Rationale**:
- **MongoDB 7.x (Raw Data Landing Zone)**:
  - Schema-less design accommodates varying provider data formats without upfront normalization.
  - Horizontal scalability via sharding for 100M+ records/year.
  - Time-series collections optimize storage and queries for activity data.
  - Atomic writes ensure data durability during high-throughput ingestion.
  
- **PostgreSQL 16+ (Normalized Structured Data)**:
  - ACID transactions ensure data consistency for user accounts, provider connections, and supplemental data.
  - JSONB column type stores flexible activity metrics while maintaining queryability.
  - Advanced indexing (B-tree, GiST, GIN) optimizes dashboard queries.
  - Foreign keys enforce referential integrity between users, activities, and workouts.
  
- **Valkey (In-Memory Cache)**:
  - Redis-compatible API with open-source license (Redis fork).
  - Sub-millisecond latency for frequently accessed dashboard data.
  - Reduces database load and meets p99 <1s dashboard budget.
  - TTL-based expiration for stale data invalidation.

**Alternatives Considered**:
- **Single Database (PostgreSQL only)**: Simpler architecture, but JSONB queries struggle with 100M+ records at scale.
- **TimescaleDB**: Purpose-built for time-series, but less flexible than MongoDB for varying provider schemas.
- **Redis (instead of Valkey)**: Same performance, but licensing concerns for commercial use (Redis 7.4+ licensing changes).

**References**:
- [MongoDB Time Series Collections](https://www.mongodb.com/docs/manual/core/timeseries-collections/)
- [PostgreSQL JSONB](https://www.postgresql.org/docs/current/datatype-json.html)
- [Valkey Documentation](https://valkey.io/)

---

### 4. OAuth2 Provider Integration

**Decision**: Implement OAuth2 2.0 authorization code flow with PKCE for provider connections.

**Rationale**:
- **Security**: PKCE (Proof Key for Code Exchange) prevents authorization code interception attacks, critical for mobile/SPA clients.
- **Token Management**: Automatic refresh token rotation maintains long-lived connections without re-authentication.
- **Provider Support**: All target providers (Garmin, Fitbit, Apple Health, Strava, Polar) support OAuth2 with documented flows.
- **User Experience**: Single sign-on flow with provider-hosted consent screens (no credential handling by muskul.ai).

**Implementation Pattern**:
1. **Authorization Request**: Redirect user to provider's OAuth2 endpoint with `client_id`, `redirect_uri`, `scope`, `state`, `code_challenge` (PKCE).
2. **Authorization Grant**: Provider redirects back with authorization `code` and `state`.
3. **Token Exchange**: Backend exchanges `code` for `access_token` and `refresh_token` using `code_verifier` (PKCE).
4. **Token Storage**: Store tokens encrypted in PostgreSQL `ProviderAccount` table (AES-256-GCM).
5. **Token Refresh**: Automatic refresh before expiration using stored `refresh_token` (background job).

**Alternatives Considered**:
- **API Keys**: Simpler, but less secure (no expiration, harder to revoke) and not supported by all providers.
- **Basic Auth**: Not supported by modern fitness providers.

**References**:
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
- [PKCE RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636)
- [OAuth 2.0 for Browser-Based Apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps)

---

### 5. Data Normalization Strategy

**Decision**: Use ETL pipeline with schema mapping and validation for provider data normalization.

**Rationale**:
- **Consistency**: Unified schema ensures consistent queries across providers (e.g., Garmin "heart_rate" vs. Fitbit "heartrate").
- **Validation**: Schema validation catches malformed data before storage, reducing downstream errors.
- **Extensibility**: Mapping configuration allows adding new providers without code changes.
- **Duplicate Handling**: Source tracking (provider + external_id) enables cross-source analysis per FR-003a.

**Implementation Pattern**:
1. **Ingestion**: Raw provider data stored in MongoDB `raw_activities` collection with metadata (provider, timestamp, user_id).
2. **Mapping**: ETL job reads mapping config (YAML/JSON) defining field transformations (e.g., `garmin.heart_rate → unified.heart_rate_bpm`).
3. **Validation**: JSON Schema validation ensures required fields, data types, and ranges (e.g., heart rate 30-220 bpm).
4. **Normalization**: Transform raw data to unified schema, store in PostgreSQL `activities` table with JSONB `metrics` column.
5. **Deduplication Detection**: Hash (provider + external_id + start_time) to detect duplicates, preserve all records with `is_duplicate` flag per FR-003a.

**Alternatives Considered**:
- **Real-Time Normalization**: Lower latency, but blocks ingestion on validation failures and increases API latency.
- **Single Schema in MongoDB**: Simpler, but harder to query consistently and enforce referential integrity.

**References**:
- [JSON Schema Specification](https://json-schema.org/)
- [ETL Best Practices](https://www.oreilly.com/library/view/data-pipelines-pocket/9781492087816/)

---

### 6. AI-Powered Note Parsing (FR-003b)

**Decision**: Delegate AI note parsing to separate microservice with REST API contract.

**Rationale**:
- **Decoupling**: AI service can use Python/TensorFlow or LLM APIs (OpenAI, Anthropic) without affecting Rust backend.
- **Scalability**: Independent scaling for AI workloads (GPU instances) vs. API (CPU instances).
- **Flexibility**: AI implementation can evolve (fine-tuned models, prompt engineering) without backend changes.
- **Testing**: Clear API contract allows mocking AI responses in backend tests.

**API Contract** (defined in `contracts/ai-agent-parse-note.md`):
- **Endpoint**: `POST /api/v1/parse-note`
- **Request**: `{"note": "5 sets of 10 squats at 135 lbs, felt strong"}`
- **Response**: `{"type": "strength", "exercises": [{"name": "squat", "sets": 5, "reps": 10, "weight_lbs": 135}], "intensity": "moderate", "notes": "felt strong"}`
- **Timeout**: 10 seconds (backend retries on timeout per FR-007a).

**Alternatives Considered**:
- **Inline AI in Rust Backend**: Simpler deployment, but Rust lacks mature ML libraries and LLM client SDKs.
- **Client-Side Parsing**: Lower latency, but exposes API keys and reduces accuracy (limited client-side models).

**References**:
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Microservices Patterns](https://microservices.io/patterns/microservices.html)

---

### 7. Weather & Altitude Supplementation

**Decision**: Use public APIs (OpenWeatherMap, Open-Meteo) with background enrichment jobs.

**Rationale**:
- **Asynchronous**: Enrichment doesn't block activity ingestion, reducing API latency.
- **Retry Logic**: Background jobs can retry on API failures without user intervention.
- **Cost Optimization**: Batch requests reduce API call count (e.g., request weather for all activities in a 1-hour window).
- **Caching**: Weather data rarely changes; cache by (lat, lon, hour) in Valkey with 24-hour TTL.

**Implementation Pattern**:
1. **Activity Ingestion**: Store activity with GPS coordinates and timestamp in PostgreSQL.
2. **Enrichment Queue**: Mark activity for enrichment (`enrichment_status = 'pending'`).
3. **Background Job**: Python/Go job queries pending activities, batches by location/time, calls weather API, stores in `SupplementalData` table.
4. **Failure Handling**: Retry with exponential backoff (per FR-007a), mark as `enrichment_status = 'failed'` after 3 attempts.

**Alternatives Considered**:
- **Synchronous Enrichment**: Simpler, but increases API latency and blocks on external API failures.
- **No Enrichment**: User manual entry, but reduces platform value and violates User Story 3 requirements.

**References**:
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Open-Meteo API](https://open-meteo.com/)

---

### 8. Data Visualization: Plotly.js

**Decision**: Use Plotly.js (via react-plotly.js) for interactive dashboards.

**Rationale**:
- **Interactivity**: Built-in zoom, pan, hover tooltips, and click events for exploring time-series data.
- **Chart Types**: Supports line, bar, scatter, heatmap charts critical for fitness metrics (heart rate over time, workout trends).
- **Performance**: WebGL rendering handles 10K+ data points without lag, meeting p99 <1s dashboard budget.
- **Export**: Built-in export to PNG (raster) and SVG (vector) for chart downloads per FR-005a.

**Implementation Pattern**:
- **Data Fetching**: React Query fetches dashboard data from backend (`GET /api/v1/activities?start=X&end=Y`), caches in memory.
- **Chart Components**: Reusable `LineChart`, `BarChart` components accept data props and Plotly config.
- **Responsive Design**: Charts resize based on container width (CSS Grid/Flexbox layout).

**Alternatives Considered**:
- **D3.js**: Maximum customization, but requires custom implementation for every chart type (slower development).
- **Chart.js**: Lightweight, but limited interactivity and performance for large datasets.
- **Recharts**: React-native, but less feature-rich and slower rendering than Plotly.

**References**:
- [Plotly.js Documentation](https://plotly.com/javascript/)
- [react-plotly.js](https://github.com/plotly/react-plotly.js)

---

### 9. Observability: OpenTelemetry

**Decision**: Instrument backend and frontend with OpenTelemetry SDK for distributed tracing and metrics.

**Rationale**:
- **Vendor-Neutral**: OpenTelemetry exports to Prometheus, Grafana, Azure Monitor, Datadog without vendor lock-in.
- **Distributed Tracing**: Trace requests across backend API → MongoDB → PostgreSQL → AI service, visualize in Grafana Tempo.
- **Custom Metrics**: Emit domain-specific metrics (activities ingested/min, OAuth2 refresh failures, AI parsing latency).
- **Structured Logs**: Correlate logs with traces using `trace_id` and `span_id` in JSON log entries.

**Implementation Pattern**:
- **Rust Backend**: Use `opentelemetry` and `tracing-opentelemetry` crates, configure OTLP exporter to Grafana Cloud or local collector.
- **React Frontend**: Use `@opentelemetry/sdk-trace-web`, instrument fetch calls, emit custom spans for render performance.
- **Metrics**: Expose Prometheus metrics at `/metrics` endpoint (request count, latency histogram, error rate).

**Alternatives Considered**:
- **Proprietary APM (Datadog, New Relic)**: Richer UI, but expensive and vendor lock-in.
- **Custom Logging**: Cheaper, but lacks distributed tracing and requires manual correlation.

**References**:
- [OpenTelemetry Rust SDK](https://github.com/open-telemetry/opentelemetry-rust)
- [OpenTelemetry JavaScript SDK](https://github.com/open-telemetry/opentelemetry-js)
- [Grafana Cloud](https://grafana.com/products/cloud/)

---

### 10. Testing Strategy

**Decision**: Implement fail-first TDD with multi-layer testing (unit, contract, integration, E2E).

**Rationale**:
- **Fail-First TDD**: Write failing test → implement feature → test passes. Ensures code is testable and requirements are met.
- **Coverage Targets**: Overall ≥80%, core domain ≥90% per Constitution Principle II.
- **Fast Feedback**: Unit tests run in milliseconds, integration tests in seconds, E2E in minutes.

**Test Layers**:
1. **Unit Tests**: Test individual functions/modules in isolation (mocked dependencies).
   - Rust: `cargo test` with `mockall` for mocking.
   - React: Vitest with `@testing-library/react` for component tests.
   
2. **Contract Tests**: Verify API endpoints match OpenAPI schema, return expected status codes.
   - Rust: `actix-web::test` or `axum::test` with real HTTP requests.
   
3. **Integration Tests**: Test cross-service interactions (backend ↔ databases, backend ↔ AI service).
   - Use testcontainers for MongoDB/PostgreSQL/Valkey in Docker.
   
4. **E2E Tests**: Test critical user flows in real browser (Playwright).
   - Scenarios: Connect provider → view dashboard → export data.

**Alternatives Considered**:
- **Manual Testing Only**: Faster initial development, but regressions accumulate and violate Constitution.
- **E2E Only**: High confidence, but slow feedback loop and brittle tests.

**References**:
- [Test-Driven Development by Kent Beck](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
- [Testing Rust Applications](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Playwright Documentation](https://playwright.dev/)

---

### 11. Data Export: CSV & PNG/PDF

**Decision**: Generate CSV exports server-side (Rust), PNG/PDF exports client-side (Plotly.js + jsPDF).

**Rationale**:
- **CSV**: Server-side generation ensures consistent formatting, handles large datasets (streaming), and supports filtering/pagination.
- **PNG**: Plotly.js built-in `Plotly.downloadImage()` generates high-quality raster images for social sharing.
- **PDF**: jsPDF library converts SVG charts to PDF for printing and archiving.

**Implementation Pattern**:
- **CSV Export**: `GET /api/v1/activities/export?format=csv&start=X&end=Y` returns CSV stream with headers (date, type, distance, calories, etc.).
- **PNG Export**: Client-side button triggers `Plotly.downloadImage('chart-div', {format: 'png', width: 1200, height: 800})`.
- **PDF Export**: Client-side button captures Plotly chart as SVG, embeds in jsPDF document with title/metadata, downloads as PDF.

**Alternatives Considered**:
- **Server-Side PNG/PDF**: Consistent output, but requires headless browser (Puppeteer) and increases server resource usage.
- **Client-Side CSV**: Simpler, but struggles with large datasets (OOM in browser) and lacks server-side filtering.

**References**:
- [Plotly.js Export Documentation](https://plotly.com/javascript/static-image-export/)
- [jsPDF Documentation](https://github.com/parallax/jsPDF)

---

### 12. Authentication: Multi-Provider OAuth2

**Decision**: Support Google, Facebook, Apple, Microsoft at launch using OAuth2 with JWT for session management.

**Rationale**:
- **User Convenience**: Users authenticate with existing accounts (no password management).
- **Security**: Delegated authentication reduces attack surface (no password storage, no credential leaks).
- **Scalability**: JWT tokens are stateless, enabling horizontal scaling without session store.

**Implementation Pattern**:
1. **Provider Login**: User clicks "Sign in with Google" → redirect to Google OAuth2 endpoint.
2. **Token Exchange**: Backend exchanges authorization code for access token, retrieves user profile (email, name).
3. **JWT Issuance**: Backend generates JWT with claims (`user_id`, `email`, `exp`) signed with RS256 (private key).
4. **Session Management**: Frontend stores JWT in httpOnly cookie (CSRF protection) or localStorage (XSS risk mitigation via CSP).
5. **Token Refresh**: JWT expires after 1 hour, frontend refreshes using refresh token stored in httpOnly cookie.

**Alternatives Considered**:
- **Session-Based Auth**: Simpler, but requires session store (Redis) and limits horizontal scaling.
- **Email/Password Auth**: More control, but increases responsibility (password hashing, reset flows, credential breaches).

**References**:
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [OAuth 2.0 Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

## Architecture Patterns

### 1. Layered Architecture (Backend)

**Pattern**: Organize backend code into distinct layers (API → Services → Repositories → Models).

**Benefits**:
- **Separation of Concerns**: Each layer has single responsibility (API = HTTP handling, Services = business logic, Repositories = data access).
- **Testability**: Layers can be tested in isolation with mocked dependencies.
- **Maintainability**: Changes to one layer (e.g., switching from Axum to Actix) don't affect other layers.

**Implementation**:
```text
backend/src/
├── api/          # HTTP handlers, request/response serialization
├── services/     # Business logic (OAuth2 flow, normalization, export)
├── repositories/ # Database queries (SQLx), MongoDB operations
├── models/       # Domain entities (User, Activity, ProviderAccount)
└── middleware/   # Cross-cutting concerns (auth, logging, tracing)
```

---

### 2. Repository Pattern (Data Access)

**Pattern**: Abstract database operations behind trait interfaces, enabling swappable implementations.

**Benefits**:
- **Testing**: Mock repository implementations for unit tests (no database required).
- **Flexibility**: Swap PostgreSQL for MySQL or MongoDB without changing service layer.
- **Readability**: Service layer calls `activity_repo.find_by_user(user_id)` instead of raw SQL.

**Implementation**:
```rust
#[async_trait]
trait ActivityRepository {
    async fn find_by_user(&self, user_id: Uuid) -> Result<Vec<Activity>>;
    async fn save(&self, activity: &Activity) -> Result<()>;
}

struct PostgresActivityRepository { pool: PgPool }

#[async_trait]
impl ActivityRepository for PostgresActivityRepository {
    async fn find_by_user(&self, user_id: Uuid) -> Result<Vec<Activity>> {
        sqlx::query_as("SELECT * FROM activities WHERE user_id = $1")
            .bind(user_id)
            .fetch_all(&self.pool)
            .await
    }
}
```

---

### 3. React Query for Data Fetching

**Pattern**: Use React Query (TanStack Query) for server state management, caching, and background refetching.

**Benefits**:
- **Automatic Caching**: Fetched data cached in memory, reduces API calls.
- **Background Refetching**: Stale data refetched in background, keeping UI fresh.
- **Error Handling**: Built-in retry logic and error states.
- **Optimistic Updates**: Update UI before API response for snappy UX.

**Implementation**:
```typescript
import { useQuery } from '@tanstack/react-query';

function useDashboardData(userId: string, start: string, end: string) {
  return useQuery({
    queryKey: ['dashboard', userId, start, end],
    queryFn: () => fetch(`/api/v1/activities?user_id=${userId}&start=${start}&end=${end}`).then(r => r.json()),
    staleTime: 60000, // Data fresh for 1 minute
    cacheTime: 300000, // Cache for 5 minutes
  });
}
```

---

### 4. Domain-Driven Design (DDD) Entities

**Pattern**: Model domain entities (User, Activity, Workout) as rich objects with behavior, not anemic data structures.

**Benefits**:
- **Encapsulation**: Business rules enforced within entity methods (e.g., `Activity::validate_metrics()`).
- **Testability**: Entity logic tested independently of database or API.
- **Clarity**: Domain concepts explicit in code (e.g., `ProviderAccount::refresh_token()` instead of scattered logic).

**Implementation**:
```rust
struct Activity {
    id: Uuid,
    user_id: Uuid,
    activity_type: ActivityType,
    metrics: HashMap<String, f64>,
    start_time: DateTime<Utc>,
}

impl Activity {
    fn validate_metrics(&self) -> Result<()> {
        if let Some(hr) = self.metrics.get("heart_rate_bpm") {
            if *hr < 30.0 || *hr > 220.0 {
                return Err(ValidationError::InvalidHeartRate);
            }
        }
        Ok(())
    }
}
```

---

## Performance Optimization Strategies

### 1. Database Indexing

**Strategy**: Create indexes on frequently queried columns (user_id, provider, start_time).

**Impact**: Reduces query time from seconds to milliseconds for dashboard loads.

**Implementation**:
```sql
-- PostgreSQL indexes
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_start_time ON activities(start_time);
CREATE INDEX idx_provider_accounts_user_id ON provider_accounts(user_id);
CREATE INDEX idx_supplemental_data_activity_id ON supplemental_data(activity_id);
```

---

### 2. Caching Strategy

**Strategy**: Cache dashboard data in Valkey with TTL-based invalidation.

**Impact**: Reduces database load by 80%, meets p99 <1s dashboard budget.

**Implementation**:
- **Cache Key**: `dashboard:{user_id}:{start_date}:{end_date}`
- **TTL**: 5 minutes (balance freshness vs. cache hit rate)
- **Invalidation**: Invalidate on new activity ingestion or manual refresh

---

### 3. Pagination & Lazy Loading

**Strategy**: Paginate activity lists (50 per page), lazy-load chart data (window-based queries).

**Impact**: Reduces initial page load time and API payload size.

**Implementation**:
- **Pagination**: `GET /api/v1/activities?page=1&per_page=50`
- **Window Queries**: `GET /api/v1/activities?start=2024-01-01&end=2024-01-31` (request only visible window)

---

### 4. Connection Pooling

**Strategy**: Use connection pools for PostgreSQL (SQLx) and MongoDB (official driver) to reuse connections.

**Impact**: Reduces connection overhead from 100ms to <1ms per query.

**Implementation**:
```rust
let pool = PgPoolOptions::new()
    .max_connections(50)
    .connect("postgres://localhost/muskul").await?;
```

---

## Security Best Practices

### 1. Token Encryption

**Strategy**: Encrypt OAuth2 tokens (access_token, refresh_token) at rest using AES-256-GCM.

**Implementation**: Use `ring` crate for encryption, store keys in environment variables or Azure Key Vault.

---

### 2. Input Validation

**Strategy**: Validate all user inputs (file uploads, manual entries, query parameters) using strongly-typed structs.

**Implementation**:
```rust
#[derive(Deserialize, Validate)]
struct ImportActivityRequest {
    #[validate(length(min = 1, max = 100))]
    activity_type: String,
    #[validate(range(min = 30.0, max = 220.0))]
    heart_rate_bpm: Option<f64>,
}
```

---

### 3. Rate Limiting

**Strategy**: Implement rate limiting (100 requests/minute per user) to prevent abuse.

**Implementation**: Use `governor` crate (Rust) or Valkey-based token bucket algorithm.

---

### 4. HTTPS Enforcement

**Strategy**: Enforce HTTPS for all API endpoints, redirect HTTP to HTTPS.

**Implementation**: Configure reverse proxy (nginx, Traefik) or cloud load balancer to terminate TLS.

---

## Scalability Considerations

### 1. Horizontal Scaling

**Strategy**: Deploy stateless backend instances behind load balancer (Azure Container Apps, Kubernetes).

**Impact**: Supports 10K concurrent users by adding instances.

---

### 2. Database Sharding

**Strategy**: Shard MongoDB by `user_id` to distribute 100M+ records across multiple nodes.

**Impact**: Maintains query performance as data grows.

---

### 3. Async Background Jobs

**Strategy**: Use message queue (Azure Service Bus, RabbitMQ) for async tasks (data enrichment, export generation).

**Impact**: Decouples workloads, prevents API blocking on long-running tasks.

---

## Conclusion

This research document establishes the technical foundation for the muskul.ai platform. All decisions prioritize **performance** (p99 <1s dashboard), **scalability** (10K users, 100M records), **security** (encrypted tokens, HTTPS, input validation), and **maintainability** (layered architecture, testing, observability). The technology stack (Rust, React, MongoDB, PostgreSQL, Valkey) is production-ready and aligns with the Constitution's principles for code quality, testing standards, UX consistency, and performance requirements.

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md) to translate these patterns into concrete schemas, API specifications, and setup instructions.
