---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

3. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

4. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Check if Dockerfile* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc*or eslint.config.* exists → create/verify .eslintignore
   - Check if .prettierrc* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements
   - **Multi-Agent Routing & Delegation**: For each task to be implemented, detect the appropriate specialized agent based on markers, file paths, and task keywords. Follow the agent detection priority and routing table below to delegate tasks accordingly.
   
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

6. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together  
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding

7. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

8. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

9. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/speckit.tasks` first to regenerate the task list.

---

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

### Pulumi Agent (`@pulumi`)
**File**: `.github/agents/pulumi.agent.md`

**Expertise**: Infrastructure as Code, Azure provisioning, CI/CD pipelines, security, cost optimization

**Triggers**:
- Task has `[@pulumi]` marker
- File path: `infra/**/*.py`, `.github/workflows/*-deploy.yml`, `Pulumi.*.yaml`
- Keywords: "infrastructure", "Azure", "IaC", "Pulumi", "CI/CD", "deployment", "provisioning", "GitHub Actions"

**Context Provided**:
- Task from tasks.md
- Infrastructure requirements from plan.md (Azure services, regions, environments)
- Security requirements (managed identities, Key Vault, RBAC)
- Cost optimization targets (environment-specific sizing)

**Success Criteria**:
- Pulumi program created/updated
- Resources follow Azure naming conventions
- All resources tagged (environment, project, managed-by)
- Preview passes: `pulumi preview`
- Deployment succeeds: `pulumi up`
- Infrastructure tests pass (smoke tests, connectivity checks)

**Quality Standards**: Idempotent resources, stack configurations, state management, managed identities, private endpoints, RBAC, cost optimization, CI/CD with OIDC

---

**Fallback**: If no specialized agent matches, use default implementation agent for general tasks (infrastructure, configuration, documentation).
