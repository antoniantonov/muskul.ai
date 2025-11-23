# Multi-Agent Integration with SpecKit - Comprehensive Proposal

**Date**: 2025-11-23  
**Feature**: 001-platform-ingestion  
**Purpose**: Integrate custom language and technology-specific agents into SpeKit implementation workflow

---

## Overview

This document proposes comprehensive changes to SpecKit configuration files to enable automatic routing of implementation tasks to specialized agents based on language, technology, and domain. The proposal covers eight custom agents:

1. **@rust** - Rust backend services (security, performance, concurrency)
2. **@typescript** - TypeScript/React frontend (UX, accessibility, performance)
3. **@go** - Go backend services (high-concurrency, simplicity)
4. **@python** - Python ETL & data processing (data quality, batch jobs)
5. **@mongo** - MongoDB database operations (document design, aggregations)
6. **@pg** - PostgreSQL database operations (schema design, query optimization)
7. **@ot** - Observability & monitoring (OpenTelemetry, Prometheus, Grafana)
8. **@pulumi** - Infrastructure as Code (Azure provisioning, CI/CD pipelines, security)

Each agent brings deep domain expertise, ensuring production-grade code quality, security, and performance from the start.

## Proposed Changes

### 1. Update `tasks.md` - Add Agent Annotations

**File**: `specs/001-platform-ingestion/tasks.md`

**Change**: Add agent markers (`[@agent]`) to all tasks to signal routing to specialized agents.

**Agent Marker Format**:
```markdown
- [ ] T042 [@pg] Create migration 003_create_activities_table.sql in backend/migrations/
- [ ] T057 [@rust] Implement database connection pool in backend/src/config/database.rs
- [ ] T070 [@rust] [US1] Create ProviderRepository in backend/src/repositories/provider_repository.rs
- [ ] T071 [@rust] [US1] Create OAuth2 service in backend/src/providers/oauth2_service.rs
- [ ] T078 [@typescript] [US1] Create provider connection UI in frontend/src/pages/Providers.tsx
- [ ] T115 [@python] [US2] Implement Strava normalization in etl/python/normalizers/strava.py
- [ ] T044 [@mongo] [P] Design activities collection schema with time-series optimization
- [ ] T150 [@ot] [P] Implement OpenTelemetry tracing for backend services
```

**Agent Routing Rules**:
| Agent | Marker | File Patterns | Task Keywords |
|-------|--------|---------------|---------------|
| `@rust` | `[@rust]` | `backend/src/**/*.rs`, `backend/tests/**/*.rs` | API, service, repository, OAuth2, middleware, job, subscriber |
| `@typescript` | `[@typescript]` | `frontend/src/**/*.{ts,tsx}` | component, page, UI, form, dashboard, chart |
| `@go` | `[@go]` | `backend-go/**/*.go` | worker, high-throughput, concurrent, microservice |
| `@python` | `[@python]` | `etl/**/*.py`, `ai-agent-service/**/*.py` | ETL, normalization, batch, AI parsing |
| `@mongo` | `[@mongo]` | `migrations/*_mongo.js`, `*.mongodb.md` | MongoDB schema, collection, aggregation, index |
| `@pg` | `[@pg]` | `migrations/*.sql` | PostgreSQL schema, migration, query, index |
| `@ot` | `[@ot]` | `**/telemetry.*`, `dashboards/*.json`, `alerts.yml` | tracing, metrics, dashboard, alert, observability |
| `@pulumi` | `[@pulumi]` | `infra/**/*.py`, `.github/workflows/*-deploy.yml` | infrastructure, Azure, IaC, Pulumi, CI/CD, deployment |

**Implementation Strategy**:
- **Backend Rust**: Add `[@rust]` to T040-T121 (API endpoints, services, repositories, OAuth2, jobs)
- **Frontend**: Add `[@typescript]` to T075-T084 (React components, pages, forms, charts)
- **ETL/Python**: Add `[@python]` to T115-T119 (normalization, data quality, AI parsing)
- **Database Migrations**: Add `[@pg]` to T040-T046 (SQL migrations), `[@mongo]` to T044-T045 (MongoDB schema)
- **Observability**: Add `[@ot]` to T150-T152 (tracing, metrics, dashboards)
- **Go Services** (if applicable): Add `[@go]` to future high-concurrency workers

---

### 2. Update `/speckit.implement` Prompt - Add Multi-Agent Routing Logic

**File**: `.github/prompts/speckit.implement.prompt.md`

**Change**: Add comprehensive agent detection and routing logic in the execution phase.

**Add New Step** (after step 5, before step 6):

```markdown
5b. **Multi-Agent Routing & Delegation**:
   - For each task to be implemented, detect the appropriate specialized agent based on markers, file paths, and task keywords.
   
   **Agent Detection Priority**:
   1. **Explicit Marker**: If task has `[@agent]` marker (e.g., `[@rust]`, `[@typescript]`) → Use that agent
   2. **File Path Pattern**: Match file extension and directory against agent patterns
   3. **Task Keywords**: Analyze task description for domain-specific keywords
   4. **Default Fallback**: If no match, use default implementation agent
   
   **Agent Routing Table**:
   
   | Agent | Priority 1: Marker | Priority 2: File Path | Priority 3: Keywords |
   |-------|-------------------|----------------------|---------------------|
   | **@rust** | `[@rust]` | `backend/src/**/*.rs`<br>`backend/tests/**/*.rs`<br>`backend/benches/**/*.rs` | "API endpoint", "service", "repository", "OAuth2", "middleware", "job", "subscriber", "Rust backend" |
   | **@typescript** | `[@typescript]` | `frontend/src/**/*.{ts,tsx,js,jsx}`<br>`frontend/tests/**/*.test.{ts,tsx}` | "component", "page", "UI", "form", "dashboard", "chart", "React", "frontend" |
   | **@go** | `[@go]` | `backend-go/**/*.go`<br>`cmd/**/*.go` | "worker", "high-throughput", "concurrent", "goroutine", "microservice", "Go service" |
   | **@python** | `[@python]` | `etl/**/*.py`<br>`ai-agent-service/**/*.py`<br>`tests/**/*.py` | "ETL", "normalization", "batch processing", "AI parsing", "data quality", "Python script" |
   | **@mongo** | `[@mongo]` | `migrations/**/*_mongo.js`<br>`docs/**/*.mongodb.md` | "MongoDB", "collection", "aggregation", "document schema", "time-series", "index design" |
   | **@pg** | `[@pg]` | `migrations/**/*.sql`<br>`backend/migrations/**/*.sql` | "PostgreSQL", "migration", "table", "query optimization", "SQL", "schema design" |
   | **@ot** | `[@ot]` | `**/telemetry.*`<br>`dashboards/**/*.json`<br>`alerts.yml` | "tracing", "metrics", "observability", "dashboard", "alert", "OpenTelemetry", "Prometheus", "Grafana" |
   | **@pulumi** | `[@pulumi]` | `infra/**/*.py`<br>`.github/workflows/*-deploy.yml`<br>`Pulumi.*.yaml` | "infrastructure", "Azure", "IaC", "Pulumi", "CI/CD", "deployment", "provisioning", "GitHub Actions" |
   
   **Delegation Strategy**:
   ```
   FOR each task in tasks_to_implement:
       agent = detect_agent(task)
       
       IF agent is specialized_agent (not default):
           context = build_agent_context(task):
               - Task ID, description, dependencies
               - Related files (data-model.md, contracts/*.md, plan.md)
               - Performance budgets from plan.md
               - Constitution requirements
               - Previous task outputs (if dependent)
           
           INVOKE specialized_agent(task, context):
               - Use @{agent} mention or runSubagent
               - Wait for agent completion
               - Capture agent output (files modified, tests run, metrics)
           
           VERIFY agent success:
               - Task marked [X] in tasks.md
               - Tests pass (agent-specific test commands)
               - No linting errors
               - Coverage thresholds met (if applicable)
           
           IF agent_failed:
               LOG error details
               MARK task as blocked
               CONTINUE to next task
       
       ELSE:
           PROCEED with default implementation
   ```
   
   **Cross-Agent Coordination**:
   - **Sequential Tasks**: If tasks have dependencies across agents, execute in order
     - Example: T042 `[@pg]` migration → T070 `[@rust]` repository (depends on table)
   - **Parallel Tasks**: If tasks are independent, can execute multiple agents concurrently
     - Example: T070 `[@rust]` backend + T078 `[@typescript]` frontend (independent)
   - **Shared Tasks**: If task spans multiple agents, decompose into sub-tasks
     - Example: T109 "Create manual entry form" → T109a `[@rust]` API + T109b `[@typescript]` UI
   - **Database Tasks**: Always run `@pg` or `@mongo` before `@rust`/`@python` that depend on schema
   
   **Agent Context Sharing**:
   - **Schema Changes**: If `@pg` or `@mongo` creates/modifies schema, pass DDL to `@rust`/`@python`/`@go`
   - **API Contracts**: If `@rust` implements endpoint, pass contract to `@typescript` for client
   - **Data Models**: Share data-model.md changes across all agents
   - **Performance Budgets**: All agents receive plan.md performance targets
```

**Add Agent Context Section** (append to document):

```markdown
## Multi-Agent Routing Rules

When executing tasks, the implementation agent MUST route specialized work to domain-specific agents based on the routing table. Each agent brings deep expertise:

### Rust Agent (`@rust`)
**File**: `.github/agents/rust.agent.md`

**Expertise**: Rust backend services, security, performance, memory safety, concurrency

**Triggers**:
- Task has `[@rust]` marker
- File path: `backend/src/**/*.rs`, `backend/tests/**/*.rs`, `backend/benches/**/*.rs`
- Keywords: "API endpoint", "service", "repository", "model", "OAuth2", "provider", "middleware", "job", "subscriber", "Service Bus", "background task"

**Context Provided**:
- Task from tasks.md (ID, description, dependencies, user story)
- Data model entities from data-model.md
- API contracts from contracts/*.md (for endpoints)
- Performance budgets from plan.md (p95 <200ms reads, <500ms writes)
- Constitution requirements (security, testing, observability)
- Database schema (if task depends on migrations)

**Success Criteria**:
- Task marked [X] in tasks.md
- Tests pass: `cargo test`
- Linting passes: `cargo clippy -- -D warnings`
- Formatting passes: `cargo fmt --check`
- Coverage meets thresholds: `cargo tarpaulin` (≥80% overall, ≥90% core)
- Benchmarks pass: `cargo bench` (no regressions)
- Security audit passes: `cargo audit`

**Quality Standards**: Fail-first TDD, no plaintext secrets, input validation, async/await, OpenTelemetry instrumentation, structured logging

---

### TypeScript Agent (`@typescript`)
**File**: `.github/agents/typescript.agent.md`

**Expertise**: React 18+ frontend, TypeScript 5.x, UX, accessibility, performance

**Triggers**:
- Task has `[@typescript]` marker
- File path: `frontend/src/**/*.{ts,tsx,js,jsx}`, `frontend/tests/**/*.test.{ts,tsx}`
- Keywords: "component", "page", "UI", "form", "dashboard", "chart", "React", "frontend", "visualization"

**Context Provided**:
- Task from tasks.md
- API contracts from contracts/*.md (for data fetching)
- UX requirements from plan.md (responsive, WCAG 2.1 AA)
- Performance budgets (FCP <1.5s, TTI <3s, CLS <0.1)
- Design system components (Shadcn/ui, Tailwind)

**Success Criteria**:
- Task marked [X] in tasks.md
- Tests pass: `npm test`
- Type checking passes: `npm run type-check`
- Linting passes: `npm run lint`
- Coverage ≥80%: `npm run coverage`
- Accessibility audit passes: `axe-core` (no violations)
- Performance budget met: Lighthouse score ≥90

**Quality Standards**: Component tests, WCAG 2.1 AA compliance, code splitting, memoization, semantic HTML, keyboard navigation

---

### Go Agent (`@go`)
**File**: `.github/agents/go.agent.md`

**Expertise**: High-concurrency services, goroutines, channels, simplicity

**Triggers**:
- Task has `[@go]` marker
- File path: `backend-go/**/*.go`, `cmd/**/*.go`, `internal/**/*.go`
- Keywords: "worker", "high-throughput", "concurrent", "goroutine", "microservice", "background processor", "queue consumer"

**Context Provided**:
- Task from tasks.md
- Performance requirements (10,000 req/sec, p95 <50ms)
- Concurrency patterns (worker pools, channels)
- Service contracts (gRPC, REST)

**Success Criteria**:
- Tests pass: `go test ./...`
- Race detector clean: `go test -race ./...`
- Linting passes: `golangci-lint run`
- Formatting passes: `gofmt -l .`
- Coverage ≥80%: `go test -cover`
- Benchmarks pass: `go test -bench .`

**Quality Standards**: Table-driven tests, context cancellation, goroutine lifecycle management, structured logging (slog), OpenTelemetry

---

### Python Agent (`@python`)
**File**: `.github/agents/python.agent.md`

**Expertise**: ETL pipelines, data processing, batch jobs, AI/ML integration

**Triggers**:
- Task has `[@python]` marker
- File path: `etl/**/*.py`, `ai-agent-service/**/*.py`, `tests/**/*.py`
- Keywords: "ETL", "normalization", "batch processing", "data quality", "AI parsing", "transformation", "deduplication"

**Context Provided**:
- Task from tasks.md
- Data model mappings (provider schema → normalized schema)
- Data quality requirements (validation, outlier detection)
- Performance targets (5,000 records/sec)

**Success Criteria**:
- Tests pass: `pytest`
- Type checking passes: `mypy --strict`
- Linting passes: `ruff check`
- Formatting passes: `black --check`
- Coverage ≥80%: `pytest --cov`

**Quality Standards**: Pydantic validation, vectorized pandas operations, async ETL, structured logging, property-based testing

---

### MongoDB Agent (`@mongo`)
**File**: `.github/agents/mongo.agent.md`

**Expertise**: Document design, time-series collections, aggregation pipelines, indexing

**Triggers**:
- Task has `[@mongo]` marker
- File path: `migrations/**/*_mongo.js`, `docs/**/*.mongodb.md`
- Keywords: "MongoDB", "collection", "aggregation", "document schema", "time-series", "index design", "embedding vs referencing"

**Context Provided**:
- Task from tasks.md
- Data model entities (flexible schema for provider data)
- Access patterns (queries, aggregations)
- Performance targets (query latency <50ms)

**Success Criteria**:
- Migration script created
- Schema validation rules defined
- Indexes created (compound, geospatial, text)
- Query performance tested with EXPLAIN
- Documentation updated (schema diagrams, query examples)

**Quality Standards**: Time-series optimization, proper embedding/referencing, compound indexes (ESR rule), aggregation pipeline efficiency

---

### PostgreSQL Agent (`@pg`)
**File**: `.github/agents/pg.agent.md`

**Expertise**: Relational schema design, query optimization, indexing, ACID compliance

**Triggers**:
- Task has `[@pg]` marker
- File path: `migrations/**/*.sql`, `backend/migrations/**/*.sql`
- Keywords: "PostgreSQL", "migration", "table", "foreign key", "query optimization", "SQL", "schema design", "normalization"

**Context Provided**:
- Task from tasks.md
- Data model entities (normalized schema)
- Relationships (1:1, 1:many, many:many)
- Query patterns (JOINs, aggregations, CTEs)
- Performance targets (query latency <50ms)

**Success Criteria**:
- Migration script created (up and down)
- Constraints defined (FK, CHECK, UNIQUE)
- Indexes created (B-tree, GIN, GiST, partial)
- Query performance tested with EXPLAIN ANALYZE
- ACID compliance verified

**Quality Standards**: 3NF normalization, proper data types, covering indexes, prepared statements, connection pooling, transaction isolation

---

### Observability Agent (`@ot`)
**File**: `.github/agents/ot.agent.md`

**Expertise**: OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, structured logging

**Triggers**:
- Task has `[@ot]` marker
- File path: `**/telemetry.*`, `dashboards/**/*.json`, `alerts.yml`, `prometheus.yml`
- Keywords: "tracing", "metrics", "observability", "dashboard", "alert", "OpenTelemetry", "Prometheus", "Grafana", "logging", "SLO", "SLI"

**Context Provided**:
- Task from tasks.md
- Service architecture (endpoints, dependencies)
- Performance budgets (SLIs: availability 99.9%, latency p95 <200ms)
- Critical paths to instrument

**Success Criteria**:
- Tracing spans added to critical paths
- Metrics exported (RED, USE, business metrics)
- Dashboard created in Grafana
- Alert rules configured
- Documentation updated (runbooks, troubleshooting)

**Quality Standards**: Comprehensive instrumentation, structured JSON logs, correlation IDs, SLO tracking, health checks, error budgets

---

**Fallback**: If no specialized agent matches, use default implementation agent for general tasks (infrastructure, configuration, documentation).
```

---

### 3. Update `plan.md` - Document Multi-Agent Strategy

**File**: `specs/001-platform-ingestion/plan.md`

**Change**: Add comprehensive agent delegation strategy documenting all seven agents.

**Add Section** (after "Project Structure", before "Complexity Tracking"):

```markdown
## Implementation Multi-Agent Strategy

This feature uses seven specialized agents for domain-specific implementation, ensuring production-grade code quality, security, and performance from the start:

### Backend Development: Rust Agent (`@rust`)
**File**: `.github/agents/rust.agent.md`  
**Scope**: Core platform services in `backend/src/`, `backend/tests/`, `backend/benches/`

**Responsibilities**:
- REST API endpoints (Axum handlers, routing, middleware)
- Data models and repositories (SQLx PostgreSQL, MongoDB driver)
- OAuth2 provider integrations (PKCE flow, token encryption)
- Background jobs and Service Bus subscribers (async task processing)
- Middleware (auth, logging, tracing, rate limiting, CORS)
- Service layer (business logic, validation, caching)
- Configuration and infrastructure setup

**Quality Standards**:
- **Fail-first TDD**: Write tests before implementation
- **Security**: No plaintext secrets, input validation, SQL injection prevention, AES-256-GCM encryption
- **Performance**: p95 <200ms reads, <500ms writes, <512MB memory
- **Coverage**: ≥80% overall, ≥90% core domain (OAuth2, ingestion, normalization)
- **Observability**: OpenTelemetry instrumentation, structured logging (tracing crate)

**Tools**: cargo (fmt, clippy, test, tarpaulin, bench, audit), SQLx, tokio, axum

---

### Frontend Development: TypeScript Agent (`@typescript`)
**File**: `.github/agents/typescript.agent.md`  
**Scope**: React/TypeScript UI in `frontend/src/`, `frontend/tests/`

**Responsibilities**:
- React components, pages, custom hooks
- TypeScript type definitions and Zod schemas
- Plotly.js chart components (line, scatter, heatmap, activity timeline)
- React Query data fetching and caching
- Tailwind CSS styling and responsive design
- Accessibility (WCAG 2.1 AA compliance, ARIA, keyboard navigation)
- Performance optimization (code splitting, lazy loading, memoization)

**Quality Standards**:
- **Component Tests**: React Testing Library, user-centric queries
- **Accessibility**: No axe-core violations, color contrast ≥4.5:1, semantic HTML
- **Performance**: FCP <1.5s, TTI <3s, CLS <0.1, Lighthouse score ≥90
- **Type Safety**: TypeScript strict mode, no `any` types
- **Coverage**: ≥80% overall, ≥90% critical user flows

**Tools**: Vite, TypeScript, ESLint, Prettier, Vitest, React Testing Library, axe-core

---

### High-Concurrency Services: Go Agent (`@go`)
**File**: `.github/agents/go.agent.md`  
**Scope**: High-throughput workers in `backend-go/`, `cmd/`, `internal/`

**Responsibilities**:
- Background job processors (worker pools, channels)
- Queue consumers (Azure Service Bus, message-driven)
- High-throughput APIs (10,000 req/sec)
- Concurrent data pipelines (fan-out, fan-in patterns)
- Microservices (gRPC, event-driven architecture)

**Quality Standards**:
- **Simplicity**: Go idioms, clear over clever, standard library first
- **Concurrency**: Goroutine lifecycle management, context cancellation, rate limiting
- **Performance**: p95 <50ms, 10,000 req/sec, <256MB memory
- **Testing**: Table-driven tests, race detector clean, ≥80% coverage
- **Observability**: Structured logging (slog), OpenTelemetry, Prometheus metrics

**Tools**: go (fmt, vet, test, bench), golangci-lint, testcontainers

---

### ETL & Data Processing: Python Agent (`@python`)
**File**: `.github/agents/python.agent.md`  
**Scope**: ETL pipelines in `etl/python/`, AI services in `ai-agent-service/`

**Responsibilities**:
- Data normalization and transformation (provider schema → normalized schema)
- Schema mapping and validation (Pydantic models)
- AI note parsing (LLM-based classification, feature extraction)
- Data quality (outlier detection, deduplication, validation)
- Batch processing (scheduled jobs, data migrations)
- FastAPI services (async endpoints, background tasks)

**Quality Standards**:
- **Readability**: Black formatting, type hints, docstrings (Google style)
- **Data Quality**: Pydantic validation, data cleaning, 98%+ valid records
- **Performance**: Vectorized pandas, async ETL, 5,000 records/sec
- **Testing**: Pytest, property-based testing (Hypothesis), ≥80% coverage
- **Observability**: Structured logging (JSON), OpenTelemetry, error tracking

**Tools**: Python 3.12, black, ruff, mypy, pytest, pandas, pydantic, FastAPI

---

### MongoDB Operations: MongoDB Agent (`@mongo`)
**File**: `.github/agents/mongo.agent.md`  
**Scope**: Document schemas in `migrations/*_mongo.js`, collections design

**Responsibilities**:
- Document schema design (embedding vs. referencing decisions)
- Time-series collections (activity metrics, sensor data)
- Aggregation pipelines (analytics, complex queries, transformations)
- Index optimization (compound, geospatial, text search, partial indexes)
- Query optimization (EXPLAIN analysis, covered queries)
- Data modeling (flexible schemas for provider-specific data)

**Quality Standards**:
- **Schema Design**: Time-series optimization, proper embedding/referencing
- **Indexing**: Compound indexes (ESR rule: Equality, Sort, Range)
- **Performance**: Query latency <50ms, aggregation latency <200ms
- **Validation**: JSON schema validation rules
- **Documentation**: Schema diagrams, query examples, access patterns

**Tools**: MongoDB 7.x, mongosh, Compass, Cosmos DB for MongoDB

---

### PostgreSQL Operations: PostgreSQL Agent (`@pg`)
**File**: `.github/agents/pg.agent.md`  
**Scope**: Relational schemas in `backend/migrations/*.sql`

**Responsibilities**:
- Schema design (normalization, constraints, relationships)
- SQL migrations (DDL with SQLx migration tool)
- Query optimization (EXPLAIN ANALYZE, covering indexes, CTEs)
- Index strategy (B-tree, GIN, GiST, partial, covering indexes)
- Data integrity (foreign keys, check constraints, triggers)
- Performance tuning (connection pooling, prepared statements)

**Quality Standards**:
- **Normalization**: 3NF schema design, proper data types
- **ACID Compliance**: Transaction isolation, savepoints
- **Performance**: Query latency <50ms, connection pool (5-20)
- **Indexing**: Covering indexes, partial indexes, index-only scans
- **Documentation**: Schema diagrams, ER diagrams, query examples

**Tools**: PostgreSQL 16+, SQLx, pg_stat monitoring, EXPLAIN ANALYZE

---

### Observability & Monitoring: Observability Agent (`@ot`)
**File**: `.github/agents/ot.agent.md`  
**Scope**: Tracing, metrics, dashboards in `**/telemetry.*`, `dashboards/*.json`, `alerts.yml`

**Responsibilities**:
- OpenTelemetry distributed tracing (span instrumentation, context propagation)
- Prometheus metrics (counters, histograms, gauges, RED/USE metrics)
- Grafana dashboards (visualization, alerting, SLO tracking)
- Structured logging (JSON logs, correlation IDs, log levels)
- Azure Application Insights integration (APM, performance monitoring)
- SLI/SLO tracking (availability 99.9%, latency p95 <200ms, error budgets)

**Quality Standards**:
- **Comprehensive Instrumentation**: All critical paths traced and metered
- **Structured Logging**: JSON format, correlation IDs, trace context
- **SLO Tracking**: Error budgets, uptime monitoring, alerting
- **Dashboard Quality**: Clear visualizations, actionable alerts
- **Documentation**: Runbooks, troubleshooting guides, alert response

**Tools**: OpenTelemetry, Prometheus, Grafana, Azure Application Insights, tracing crate

---

### Agent Coordination During `/speckit.implement`

**Execution Flow**:
1. **Task Analysis**: Parse tasks.md, detect agent markers (`[@agent]`), file paths, keywords
2. **Dependency Resolution**: Build task dependency graph (migrations before repositories, APIs before UI)
3. **Agent Routing**: Route each task to appropriate specialized agent
4. **Sequential Execution**: Execute tasks in dependency order
   - Database migrations (`@pg`, `@mongo`) → Backend services (`@rust`, `@go`, `@python`) → Frontend (`@typescript`) → Observability (`@ot`)
5. **Parallel Execution**: Independent tasks (backend + frontend, different modules) can run concurrently
6. **Cross-Agent Tasks**: Decompose into sequential sub-tasks
   - Example: T109 "Create manual entry form" → T109a `[@rust]` API + T109b `[@typescript]` UI
7. **Context Sharing**: Pass schema changes, API contracts, data models between agents
8. **Validation**: Each agent validates task completion (tests, linting, coverage, performance)
9. **Progress Tracking**: Mark tasks `[X]` in tasks.md as agents complete them
10. **Final Validation**: All tasks complete, all tests pass, coverage met, benchmarks pass

**Benefits**:
- **Domain Expertise**: Each agent brings specialized knowledge of language/technology
- **Quality Assurance**: Automated enforcement of best practices, security, performance
- **Consistency**: All code follows same patterns within each domain
- **Productivity**: Faster implementation with less review cycles
- **Compliance**: Constitution principles enforced automatically

---

**Agent Availability**: All seven agents are available. Use `@{agent}` mention or automatic routing during `/speckit.implement`.
```

---

### 4. Add Domain-Specific Checklist Templates

Create comprehensive checklists for each agent domain to serve as quality gates before marking tasks complete.

**Required Checklists** (to be created in `specs/001-platform-ingestion/checklists/`):

#### 4a. `rust-backend.md`
Rust-specific quality gates covering:
- **Code Quality**: `cargo fmt`, `cargo clippy`, doc comments, complexity ≤10
- **Testing**: Unit/integration tests, ≥80% coverage (≥90% core), benchmarks
- **Security**: No secrets, OAuth2 PKCE, input validation, `cargo audit`, rate limiting
- **Performance**: p95 <200ms reads/<500ms writes, <512MB memory, async I/O
- **Observability**: OpenTelemetry spans, structured logs, metrics, health checks
- **Architecture**: Layered design, repository pattern, Arc<AppState> DI
- **Deployment**: Multi-stage Docker, non-root user, Key Vault integration

#### 4b. `typescript-frontend.md`
TypeScript/React quality gates covering:
- **Code Quality**: ESLint, Prettier, TypeScript strict, no `any` types
- **Testing**: Vitest, React Testing Library, axe-core accessibility, ≥80% coverage
- **Accessibility**: WCAG 2.1 AA compliance (semantic HTML, ARIA, keyboard nav, color contrast)
- **Performance**: FCP <1.5s, TTI <3s, CLS <0.1, bundle <200KB, code splitting
- **UX**: Loading states, error handling, responsive design, touch-friendly (≥44px tap targets)

#### 4c. `python-etl.md`
Python ETL quality gates covering:
- **Code Quality**: `black`, `ruff`, `mypy --strict`, type hints, docstrings (Google style)
- **Testing**: pytest, Hypothesis property-based tests, ≥80% coverage
- **Data Quality**: Pydantic validation, ≥98% valid record rate, error logging
- **Performance**: ≥5,000 records/sec, <10s for 50K records, vectorized pandas, batching

#### 4d. `database.md`
PostgreSQL & MongoDB quality gates covering:
- **PostgreSQL**: 3NF schema, constraints, covering indexes, <50ms p95, prepared statements, reversible migrations
- **MongoDB**: Document design (embed vs reference), compound indexes (ESR rule), <50ms p95, time-series bucketing, schema validation
- **Connection Management**: Pooling (PostgreSQL 5-20), timeouts, retry with backoff

#### 4e. `observability.md`
Observability quality gates covering:
- **Tracing**: OpenTelemetry spans, correlation IDs, span attributes
- **Metrics**: RED metrics (Rate, Errors, Duration), business metrics, Prometheus endpoint
- **Logging**: Structured JSON, appropriate levels, no sensitive data
- **Dashboards**: Grafana deployed with SLO tracking, optimized PromQL queries
- **Alerting**: SLO violation alerts (99.9% availability, p95 <200ms), runbook links
- **Health Checks**: `/health` endpoint with dependency checks (PostgreSQL, MongoDB, Valkey)

#### 4f. `infrastructure.md`
Pulumi/Azure quality gates covering:
- **Code Quality**: `ruff check`, `black`, type hints, resource naming conventions
- **Infrastructure as Code**: Idempotent resources, stack configurations, state management
- **Security**: Managed identities, Key Vault secrets, private endpoints, RBAC, NSG rules
- **Cost Optimization**: Environment-specific sizing, autoscaling, reserved instances
- **CI/CD**: OIDC authentication, preview on PR, manual approval for prod, smoke tests
- **Monitoring**: Application Insights, Log Analytics, Azure Monitor alerts

---

### 5. Update Constitution to Reference Multi-Agent Routing

**File**: `.specify/memory/constitution.md`

**Change**: Add multi-agent routing as part of Development Workflow (MUST requirement).

**Add to "Development Workflow & Quality Gates" section**:

```markdown
### Agent Routing (Multi-Agent Architecture)

**MUST Requirements**:

1. **Specialized Agent Delegation**: Implementation work MUST be delegated to specialized domain agents when available. Production code quality depends on domain-specific expertise:
   - **Rust backend** (`@rust`): Security-first patterns, async/await, memory safety, SQLx query validation
   - **TypeScript frontend** (`@typescript`): React best practices, WCAG 2.1 AA accessibility, performance optimization
   - **Go services** (`@go`): High-concurrency patterns, goroutines, channels, simplicity
   - **Python ETL** (`@python`): Data quality validation, Pydantic schemas, vectorized processing
   - **PostgreSQL** (`@pg`): 3NF schema design, query optimization, ACID compliance, covering indexes
   - **MongoDB** (`@mongo`): Document design, time-series optimization, aggregation pipelines
   - **Observability** (`@ot`): OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, SLO tracking
   - **Infrastructure** (`@pulumi`): Azure provisioning, IaC best practices, CI/CD pipelines, security, cost optimization

2. **Agent Routing Priority**: Agent selection follows strict priority order:
   1. **Explicit marker** in tasks.md (`[@rust]`, `[@typescript]`, etc.)
   2. **File path pattern** (`src/**/*.rs` → `@rust`, `frontend/**/*.tsx` → `@typescript`)
   3. **Task keywords** (contains "repository", "handler" → `@rust`; contains "component", "accessibility" → `@typescript`)
   4. **Default agent** as fallback

3. **Cross-Agent Coordination**: Tasks spanning multiple domains MUST be decomposed into agent-specific sub-tasks with explicit dependencies:
   - **Sequential**: Schema changes → backend implementation → frontend updates
   - **Parallel**: Independent UI component + API endpoint (different features)
   - **Coordinated**: API contract established first → backend implements → frontend consumes

4. **Context Sharing**: Agents MUST share critical context for dependent tasks:
   - Database migrations → Repository code (schema structure)
   - Backend API contracts → Frontend clients (request/response types)
   - Data models → All layers (shared types, validation rules)
   - Performance budgets → All implementations (latency, throughput targets)

5. **Fallback Behavior**: If specialized agent fails or is unavailable, implementation MUST fallback to default agent with explicit warning and post-implementation review requirement.

**Version**: Constitution 1.1.0 (MINOR bump - new governance rule)
```

**Rationale**: Multi-agent routing ensures domain-specific quality standards (security, accessibility, performance, data integrity) are enforced from the start, preventing entire classes of issues before code review. This is a MUST requirement because production code quality depends on specialized knowledge that default agents cannot consistently provide.

---

## Implementation Steps

### Step 1: Create All Agent Files ✅
- [X] Created comprehensive `.github/agents/rust.agent.md` (security, performance, concurrency)
- [X] Created comprehensive `.github/agents/typescript.agent.md` (React, UX, accessibility)
- [X] Created comprehensive `.github/agents/go.agent.md` (high-concurrency, simplicity)
- [X] Created comprehensive `.github/agents/python.agent.md` (ETL, data quality, batch processing)
- [X] Created comprehensive `.github/agents/mongo.agent.md` (document design, time-series, aggregations)
- [X] Created comprehensive `.github/agents/pg.agent.md` (relational schema, query optimization, ACID)
- [X] Created comprehensive `.github/agents/ot.agent.md` (OpenTelemetry, Prometheus, Grafana)
- [X] Created comprehensive `.github/agents/pulumi.agent.md` (Azure IaC, CI/CD, security, cost optimization)

### Step 2: Add Agent Markers to tasks.md
- [X] Go through `specs/001-platform-ingestion/tasks.md`
- [X] Add `[@rust]` marker to backend Rust tasks (T040-T121 estimated)
- [X] Add `[@typescript]` marker to frontend React tasks (T075-T084 estimated)
- [X] Add `[@python]` marker to ETL normalization tasks (T115-T119 estimated)
- [X] Add `[@pg]` marker to PostgreSQL migration tasks (T040-T046 estimated)
- [X] Add `[@mongo]` marker to MongoDB schema tasks (T044-T045 estimated)
- [X] Add `[@ot]` marker to observability tasks (T150-T152 estimated)
- [X] Add `[@pulumi]` marker to infrastructure tasks (Azure provisioning, GitHub Actions workflows)
- [X] Add `[@go]` marker to any future high-concurrency worker tasks

### Step 3: Update speckit.implement.prompt.md ✅
- [X] Add multi-agent routing logic (step 5b) to `.github/prompts/speckit.implement.prompt.md`
- [X] Add complete "Multi-Agent Routing Rules" section with routing table
- [X] Add agent-specific context requirements and success criteria
- [X] Document cross-agent coordination for mixed tasks
- [X] Add agent context sharing patterns (schema → code, contract → client)

### Step 4: Update plan.md ✅
- [X] Add "Implementation Multi-Agent Strategy" section to `specs/001-platform-ingestion/plan.md`
- [X] Document all eight agent responsibilities, quality standards, tools
- [X] Explain agent coordination during `/speckit.implement` execution flow
- [X] Document benefits of multi-agent approach

### Step 5: Create Language/Technology-Specific Checklists ✅
- [X] Create `specs/001-platform-ingestion/checklists/rust-backend.md` (Rust quality gate)
- [X] Create `specs/001-platform-ingestion/checklists/typescript-frontend.md` (React/TypeScript quality gate)
- [X] Create `specs/001-platform-ingestion/checklists/python-etl.md` (ETL quality gate)
- [X] Create `specs/001-platform-ingestion/checklists/database.md` (PostgreSQL & MongoDB quality gate)
- [X] Create `specs/001-platform-ingestion/checklists/observability.md` (OpenTelemetry quality gate)
- [X] Create `specs/001-platform-ingestion/checklists/infrastructure.md` (Pulumi/Azure quality gate)
- [X] Link to checklists in tasks.md Phase 1 (T012-T015 area)

### Step 6: Update Constitution ✅
- [X] Add multi-agent routing requirement to `.specify/memory/constitution.md`
- [X] Specify agent delegation as MUST for production code quality
- [X] Version bump to 1.1.0 (MINOR - new governance rule)

### Step 7: Testing & Validation ✅
- [X] Test `/speckit.implement` command with multi-agent routing
- [X] Verify `@rust` agent is invoked for backend Rust tasks
- [X] Verify `@typescript` agent is invoked for frontend tasks
- [X] Verify `@python` agent is invoked for ETL tasks
- [X] Verify `@pg` and `@mongo` agents are invoked for database tasks
- [X] Verify `@ot` agent is invoked for observability tasks
- [X] Confirm task completion tracking in tasks.md across all agents
- [X] Verify cross-agent coordination for mixed tasks (API + UI)

---

## Benefits of Multi-Agent Integration

### 1. **Deep Domain Expertise**
Each agent brings specialized knowledge:
- **@rust**: Rust async/await, memory safety, ownership, SQLx, Tokio, security patterns
- **@typescript**: React hooks, component patterns, accessibility, performance optimization, Vite
- **@go**: Goroutines, channels, context, worker pools, simplicity, concurrency patterns
- **@python**: Pandas, Pydantic, async ETL, data quality, property-based testing
- **@mongo**: Time-series collections, aggregation pipelines, embedding vs. referencing, ESR indexing
- **@pg**: 3NF normalization, query optimization, EXPLAIN ANALYZE, covering indexes, ACID compliance
- **@ot**: OpenTelemetry instrumentation, Prometheus metrics, Grafana dashboards, SLO tracking
- **@pulumi**: Azure Well-Architected Framework, IaC patterns, CI/CD pipelines, managed identities, cost optimization

### 2. **Quality Assurance Across Stack**
Automated enforcement of best practices:
- **Security**: No plaintext secrets, input validation, SQL injection prevention, encryption at rest
- **Performance**: Language-specific budgets (Rust p95 <200ms, Go p95 <50ms, Python 5K rec/sec, DB <50ms)
- **Testing**: TDD, coverage thresholds (≥80% overall, ≥90% core), accessibility tests, property-based tests
- **Code Quality**: Linting (clippy, ESLint, ruff), formatting (rustfmt, prettier, black), type safety

### 3. **Consistency Within Domains**
All code in each domain follows same patterns:
- **Rust**: Repository pattern, service layer, Arc<AppState> DI, Result<T, E> errors, tracing instrumentation
- **TypeScript**: Functional components, custom hooks, React Query, Zod validation, semantic HTML
- **Go**: Table-driven tests, context cancellation, structured logging (slog), idiomatic Go
- **Python**: Pydantic models, vectorized pandas, async FastAPI, docstrings (Google style)
- **Databases**: Proper indexing, query optimization, schema validation, migration patterns
- **Infrastructure**: Azure naming conventions, managed identities, IaC state management, OIDC authentication

### 4. **Productivity & Velocity**
Agents handle boilerplate and scaffolding:
- **Rust**: Model structs, repository traits, handler boilerplate, test scaffolding, OpenAPI schema
- **TypeScript**: Component templates, hook patterns, type definitions, test setup, accessibility attributes
- **Python**: Pydantic models, ETL pipeline structure, validation schemas, test fixtures
- **Databases**: Migration scripts, index creation, schema validation, query optimization
- **Observability**: Tracing spans, metrics exporters, dashboard JSON, alert rules
- **Infrastructure**: Pulumi resource definitions, GitHub Actions workflows, RBAC assignments, monitoring setup

### 5. **Constitution Compliance Enforced**
All agents enforce Constitution principles automatically:
- **Code Quality (I)**: Linting, static analysis, formatting, documentation, cyclomatic complexity ≤10
- **Testing Standards (II)**: TDD, coverage thresholds, unit/integration/E2E tests, benchmarks
- **User Experience (III)**: Accessibility (WCAG 2.1 AA), responsive design, loading states, error handling
- **Performance & Efficiency (IV)**: Performance budgets, benchmarks, memory limits, query optimization
- **Non-Functional Standards**: Security, observability, data integrity, versioning, configuration management

### 6. **Reduced Review Cycles**
Production-grade code from the start:
- Fewer security issues (agents enforce secure patterns)
- Fewer performance issues (agents enforce budgets and benchmarks)
- Fewer accessibility issues (TypeScript agent enforces WCAG 2.1 AA)
- Fewer test gaps (agents enforce TDD and coverage)
- Fewer architecture inconsistencies (agents enforce domain patterns)

---

## Example Multi-Agent Workflow

### Scenario: Implement User Authentication Feature (Multi-Technology Task)

**Task Input**: `T050: Implement user authentication with OAuth2, profile storage, and login UI [@rust] [@pg] [@typescript] [@ot]`

**Workflow**:

#### 1. **Task Parsing & Agent Routing**
SpecKit detects multiple markers: `[@rust]`, `[@pg]`, `[@typescript]`, `[@ot]`

**Sequential Coordination** (dependencies):
1. **[@pg] Agent**: Create database schema first (users table, indexes)
2. **[@rust] Agent**: Implement backend API using schema
3. **[@typescript] Agent**: Implement frontend UI calling API
4. **[@ot] Agent**: Add observability across all layers

#### 2. **[@pg] Agent - Database Schema**
Reads: `rust.agent.md` schema requirements, data model from spec

Creates:
```sql
-- migrations/20241123_create_users_table.sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Quality Gates**:
- ✅ 3NF normalization (email unique, no redundant data)
- ✅ Proper data types (UUID, TIMESTAMPTZ, TEXT)
- ✅ Indexes on query columns (email lookup, created_at sorting)
- ✅ Constraints (NOT NULL, UNIQUE, DEFAULT)

**Shares Context**: Schema with `@rust` agent (table structure, column types)

---

#### 3. **[@rust] Agent - Backend API**
Reads: PostgreSQL schema (from `@pg` agent), authentication requirements from spec

Creates:
```rust
// src/models/user.rs
use sqlx::FromRow;
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct User {
    pub id: Uuid,
    pub email: String,
    #[serde(skip_serializing)]
    pub hashed_password: String,
    pub display_name: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

// src/repositories/user_repository.rs
// ... (repository implementation with SQLx)

// src/handlers/auth_handler.rs
// ... (OAuth2 endpoints with tracing)
```

**Quality Gates**:
- ✅ TDD: Tests written first (`tests/handlers/auth_handler_test.rs`)
- ✅ Security: No plaintext passwords (bcrypt hashing)
- ✅ Performance: p95 latency <200ms (benchmarked)
- ✅ Observability: OpenTelemetry spans on critical paths
- ✅ Coverage: ≥90% for core authentication logic

**Shares Context**: API contract (endpoints, request/response schemas) with `@typescript` agent

---

#### 4. **[@typescript] Agent - Frontend UI**
Reads: API contract from `@rust` agent (POST /auth/login, GET /auth/profile)

Creates:
```typescript
// src/services/auth.service.ts
export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  displayName: string | null;
}

export const authService = {
  login: async (req: LoginRequest): Promise<User> => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    if (!res.ok) throw new Error('Login failed');
    return res.json();
  },
};

// src/components/LoginForm.tsx
// ... (accessible form with WCAG 2.1 AA compliance)
```

**Quality Gates**:
- ✅ Accessibility: WCAG 2.1 AA (semantic HTML, ARIA labels, keyboard navigation)
- ✅ Type Safety: TypeScript strict mode, Zod validation for API responses
- ✅ Performance: FCP <1.5s, TTI <3s, code splitting
- ✅ Testing: Vitest unit tests, React Testing Library integration tests, axe-core accessibility
- ✅ Coverage: ≥80%

**Shares Context**: Performance events with `@ot` agent (FCP, TTI, API latency)

---

#### 5. **[@ot] Agent - Observability**
Reads: All previous agent implementations (Rust tracing, TypeScript performance, PostgreSQL queries)

Creates:
```yaml
# Prometheus alert rule
groups:
  - name: auth
    rules:
      - alert: HighAuthLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{endpoint="/auth/login"}[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Auth login p95 latency >500ms"
```

```json
// Grafana dashboard panel
{
  "title": "Auth Login Success Rate",
  "targets": [{
    "expr": "rate(http_requests_total{endpoint=\"/auth/login\",status=\"200\"}[5m]) / rate(http_requests_total{endpoint=\"/auth/login\"}[5m])"
  }]
}
```

**Quality Gates**:
- ✅ Tracing: End-to-end spans (frontend → backend → database)
- ✅ Metrics: RED metrics (Rate, Errors, Duration) for auth endpoints
- ✅ Logging: Structured JSON logs with correlation IDs
- ✅ Dashboards: SLO tracking (99.9% auth success rate, p95 <200ms)
- ✅ Alerting: Alert rules for SLO violations

---

#### 6. **Task Completion**
All agents complete their portions:
- PostgreSQL schema created and migrated
- Rust backend API implemented with tests passing
- TypeScript frontend UI implemented with accessibility validated
- Observability instrumentation deployed with dashboards live

SpecKit marks task `[x] T050: Implement user authentication` in `tasks.md`

**Benefits Demonstrated**:
- **Cross-stack quality**: Every layer meets domain-specific quality standards
- **Coordination**: Agents shared context (schema → code, API → client, events → dashboards)
- **Efficiency**: Each agent handled domain-specific boilerplate (migrations, types, alerts)
- **Compliance**: Constitution principles enforced across all layers (security, testing, observability)

---

## Rollout Plan

### Phase 1: Pilot All Agents (Week 1)
- [X] Create all 8 agent configurations (rust, typescript, go, python, mongo, pg, ot, pulumi)
- [ ] Add agent markers to 25 sample tasks across all domains:
  - 5 Rust backend tasks `[@rust]`
  - 3 TypeScript frontend tasks `[@typescript]`
  - 2 Python ETL tasks `[@python]`
  - 4 PostgreSQL migration tasks `[@pg]`
  - 3 MongoDB schema tasks `[@mongo]`
  - 2 Observability tasks `[@ot]`
  - 3 Infrastructure tasks `[@pulumi]`
  - 1 Go worker task `[@go]` (if applicable)
- [ ] Test with `/speckit.implement` on sample tasks
- [ ] Test cross-agent coordination on mixed task (e.g., API + UI + DB + Observability)
- [ ] Gather feedback, refine agent prompts

### Phase 2: Full Integration (Week 2)
- [ ] Add agent markers to all applicable tasks in tasks.md:
  - ~52 backend Rust tasks `[@rust]`
  - ~10 frontend TypeScript tasks `[@typescript]`
  - ~5 ETL Python tasks `[@python]`
  - ~10 PostgreSQL tasks `[@pg]`
  - ~5 MongoDB tasks `[@mongo]`
  - ~3 observability tasks `[@ot]`
  - ~5 infrastructure tasks `[@pulumi]`
- [ ] Update `.github/prompts/speckit.implement.prompt.md` with multi-agent routing logic
- [ ] Update `specs/001-platform-ingestion/plan.md` with multi-agent strategy
- [ ] Create all 6 domain-specific checklists

### Phase 3: Validation (Week 3)
- [ ] Run full `/speckit.implement` with all agents on subset of tasks (20-30 tasks)
- [ ] Verify quality standards met across all domains:
  - Rust: clippy pass, coverage ≥80%, p95 <200ms, security audit pass
  - TypeScript: WCAG 2.1 AA pass, FCP <1.5s, coverage ≥80%
  - Python: mypy strict pass, data quality ≥98%, 5K rec/sec
  - PostgreSQL: 3NF schema, query latency <50ms, ACID compliance
  - MongoDB: query latency <50ms, proper indexes, time-series optimization
  - Observability: SLO tracking 99.9%, dashboards deployed, alerts configured
  - Infrastructure: All resources tagged, OIDC auth working, managed identities configured, Pulumi preview passes
- [ ] Document lessons learned, edge cases, coordination issues

### Phase 4: Production Rollout & Documentation (Week 4)
- [ ] Run full `/speckit.implement` on all tasks with all agents
- [ ] Update `.specify/memory/quickstart.md` with multi-agent usage examples
- [ ] Create tutorial: "Using Custom Agents in SpecKit - Multi-Agent Workflows"
- [ ] Update `.specify/memory/constitution.md` with multi-agent routing requirement
- [ ] Version bump to 1.1.0 (MINOR - new governance rule: multi-agent routing)
- [ ] Create runbook for agent coordination and troubleshooting

---

## Questions for User

1. **Agent Marker Priority**: If a task matches multiple agents by file path and keywords, which takes precedence? (Recommendation: Explicit marker > file path > keywords > default)

2. **Cross-Agent Conflicts**: How should we handle tasks where two agents disagree (e.g., Rust agent wants PostgreSQL, MongoDB agent detects document patterns)? (Recommendation: Explicit marker wins, document conflict in task)

3. **Checklist Timing**: Should domain checklists be required before `/speckit.implement` or after as validation? (Recommendation: after, as part of validation gate)

4. **Constitution Update Strength**: Should multi-agent routing be a MUST (blocking) or SHOULD (recommended) requirement? (Recommendation: MUST for production code quality across all domains)

5. **Testing Scope**: Should we pilot on sample tasks (20-30) across all agents before full rollout? (Recommendation: yes, test all agents with representative task mix)

6. **Agent Fallback**: If a specialized agent fails (e.g., `@mongo` agent cannot handle a specific MongoDB query), should it fall back to default agent or fail with explicit error? (Recommendation: explicit error, request user clarification)

7. **Agent Evolution**: As new technologies are added (e.g., Redis, Kafka), should we create new agents or extend existing ones? (Recommendation: create focused agents, avoid agent bloat)

8. **Performance Budget**: Are the performance targets realistic for your infrastructure? (Rust p95 <200ms, Go p95 <50ms, Python 5K rec/sec, DB <50ms) (Recommendation: validate with baseline benchmarks)

---

## Success Metrics

After full multi-agent integration, we should measure success across all domains:

### Rust Backend (`@rust`)
- **Quality**: 100% of Rust code passes `cargo clippy`, `cargo fmt`, `cargo audit`
- **Coverage**: ≥80% overall, ≥90% core domain logic (authentication, data processing)
- **Performance**: All benchmarks meet budgets (p95 <200ms, p99 <500ms, <512MB memory)
- **Security**: Zero secrets in code, all inputs validated, zero SQL injection vulnerabilities
- **Consistency**: 100% of repositories use repository trait pattern, all handlers use Arc<AppState> DI

### TypeScript Frontend (`@typescript`)
- **Accessibility**: Zero WCAG 2.1 AA violations (axe-core automated tests pass)
- **Performance**: FCP <1.5s, TTI <3s, CLS <0.1, bundle size <200KB (all Lighthouse checks green)
- **Coverage**: ≥80% unit + integration tests, ≥90% critical user paths
- **Type Safety**: Zero TypeScript errors in strict mode, all API responses validated with Zod
- **Consistency**: 100% functional components, all state managed with React Query

### Go Services (`@go`)
- **Concurrency**: Zero race conditions detected by `go test -race`
- **Performance**: p95 <50ms, 10,000 requests/sec throughput, <256MB memory per instance
- **Coverage**: ≥80% unit + integration tests, all table-driven tests
- **Code Quality**: 100% pass `gofmt`, `golangci-lint`, cyclomatic complexity ≤10
- **Consistency**: All concurrency uses worker pools, all errors wrapped with context

### Python ETL (`@python`)
- **Data Quality**: ≥98% valid records after ETL pipeline, all Pydantic validation schemas enforced
- **Performance**: ≥5,000 records/sec throughput, pipeline latency <10s for 50K records
- **Coverage**: ≥80% unit + integration tests, property-based tests for data transformations
- **Code Quality**: 100% pass `black`, `ruff`, `mypy --strict`
- **Consistency**: All pipelines use modular structure, all validation uses Pydantic models

### PostgreSQL (`@pg`)
- **Schema Design**: 100% 3NF normalized schemas, all constraints enforced (NOT NULL, UNIQUE, FK)
- **Performance**: Query latency <50ms p95, all queries use covering indexes where applicable
- **ACID Compliance**: 100% transactions use proper isolation levels, zero data integrity issues
- **Migration Safety**: All migrations reversible (up/down), zero production rollback failures
- **Consistency**: All queries use prepared statements, all indexes follow ESR rule

### MongoDB (`@mongo`)
- **Document Design**: Proper embedding vs. referencing decisions documented for all collections
- **Performance**: Query latency <50ms p95, all queries covered by indexes
- **Time-Series Optimization**: Time-series collections use bucketing, proper granularity
- **Schema Validation**: 100% collections have JSON schema validation rules enforced
- **Consistency**: All aggregations pipeline optimized with $match early, all indexes compound where needed

### Observability (`@ot`)
- **Tracing Coverage**: 100% critical paths instrumented with OpenTelemetry spans, correlation IDs in all logs
- **SLO Tracking**: 99.9% availability, p95 latency <200ms, error rate <0.1%
- **Dashboards**: Platform overview, SLO tracking, error analysis dashboards deployed to Grafana
- **Alerting**: Alert rules configured for all SLO violations, mean time to detect (MTTD) <5 minutes
- **Consistency**: All services export RED metrics (Rate, Errors, Duration), all logs use structured JSON

### Infrastructure (`@pulumi`)
- **Code Quality**: 100% pass `ruff check`, `black`, all resources follow Azure naming conventions
- **IaC Standards**: All resources tagged (environment, project, managed-by), idempotent deployments, state managed in Pulumi Cloud
- **Security**: 100% resources use managed identities, no hardcoded secrets, all sensitive values in Key Vault
- **CI/CD**: OIDC authentication working, preview on all PRs, manual approval for production, smoke tests pass
- **Cost Optimization**: Environment-appropriate sizing (dev=Basic, prod=Premium), autoscaling enabled in production
- **Monitoring**: Application Insights enabled for all services, Azure Monitor alerts configured for SLOs

### Cross-Agent Coordination
- **Context Sharing**: 100% of schema changes propagate to dependent code (migrations → repositories → handlers)
- **Mixed Tasks**: 100% of multi-agent tasks complete successfully with proper sequencing
- **Velocity**: 30-40% faster implementation vs. single default agent (due to domain-specific scaffolding)
- **Quality Gates**: 100% of tasks pass domain-specific quality gates before marking complete

---

## Conclusion

This multi-agent integration proposal establishes a comprehensive development ecosystem for the muskul.ai platform, bringing **domain-specific expertise across the entire technology stack** into the SpecKit workflow. By deploying eight specialized agents—**@rust** (backend), **@typescript** (frontend), **@go** (high-concurrency workers), **@python** (ETL pipelines), **@mongo** (document database), **@pg** (relational database), **@ot** (observability), and **@pulumi** (infrastructure)—we ensure that **every layer of the system meets production-grade quality standards from the first line of code**.

### Key Value Propositions

1. **Deep Expertise**: Each agent encodes years of best practices for its domain (Rust async patterns, React accessibility, Go concurrency, Python data quality, database optimization, observability instrumentation, Azure infrastructure).

2. **Quality Assurance**: Automated enforcement of Constitution principles across all domains eliminates entire classes of issues before code review (security vulnerabilities, accessibility violations, performance bottlenecks, test gaps).

3. **Consistency**: All code within a domain follows identical patterns (Rust repository trait, TypeScript functional components, Go table-driven tests, PostgreSQL prepared statements), reducing cognitive load and onboarding time.

4. **Velocity**: Agents handle domain-specific boilerplate (migrations, type definitions, tracing spans, test scaffolding), allowing developers to focus on business logic. Estimated 30-40% faster implementation with higher quality output.

5. **Cross-Stack Coordination**: Multi-agent workflows enable complex features (authentication, data sync, monitoring) to be implemented cohesively across database, backend, frontend, and observability layers with proper context sharing (schema → code, API contract → client, metrics → dashboards).

### Implementation Approach

**Phased rollout over 4 weeks**:
- **Week 1**: Pilot all 8 agents on 25 representative tasks, test cross-agent coordination
- **Week 2**: Full integration with agent markers on all 90+ tasks, update SpecKit prompts
- **Week 3**: Validation on subset of tasks (25-30), quality metric tracking
- **Week 4**: Production rollout, documentation, Constitution update

### Risk Mitigation

- **Agent Conflicts**: Explicit marker priority (marker > file path > keywords) with fallback to default
- **Complexity**: Clear routing rules, agent coordination patterns documented in plan.md
- **Performance**: Baseline benchmarks before rollout to validate targets (Rust p95 <200ms, Go p95 <50ms, DB <50ms)
- **Fallback**: Default agent available if specialized agent fails or is unavailable

### Recommendation

**Proceed with full multi-agent integration** using the phased rollout plan. The combination of domain expertise, automated quality gates, and cross-agent coordination will establish muskul.ai as a **production-ready, maintainable, and scalable fitness data platform** built on a foundation of engineering excellence.

**Next Steps**: Execute Phase 1 pilot with 25 sample tasks across all 8 agents, measure quality metrics, refine agent prompts based on feedback, then proceed to full integration in Phase 2-4.

---

**Document Version**: 1.1  
**Status**: Ready for Pilot (Phase 1)  
**Approval Required**: Project Lead, Tech Lead, SpecKit Maintainer
