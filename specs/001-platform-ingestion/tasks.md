# Tasks: muskul.ai Platform Ingestion & Analytics

**Input**: Design documents from `/specs/001-platform-ingestion/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Feature**: 001-platform-ingestion
**Branch**: `001-platform-ingestion`
**Generated**: 2025-11-19

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure (establish quality, testing, UX, performance foundations)

- [ ] T001 Create project structure: backend/, frontend/, etl/, ai-agent-service/, infra/, docs/
- [ ] T002 Initialize Rust backend project with Cargo.toml (tokio, axum, reqwest, serde, sqlx, opentelemetry dependencies)
- [ ] T003 Initialize React frontend project with package.json (react 18+, typescript 5.x, vite, plotly.js, react-query, tailwind)
- [ ] T004 [P] Configure Rust linting with clippy in backend/.cargo/config.toml
- [ ] T005 [P] Configure TypeScript eslint in frontend/.eslintrc.json (strict mode enabled)
- [ ] T006 [P] Setup Rust static analysis with cargo-audit in backend/Cargo.toml
- [ ] T007 [P] Configure Tailwind CSS design tokens in frontend/tailwind.config.js (colors, spacing, typography for WCAG 2.1 AA)
- [ ] T008 [P] Setup Vitest for frontend unit tests in frontend/vite.config.ts
- [ ] T009 [P] Setup Playwright for E2E tests in frontend/playwright.config.ts
- [ ] T010 [P] Setup cargo-tarpaulin for Rust coverage in backend/.github/workflows/backend.yml
- [ ] T011 [P] Setup criterion for Rust benchmarks in backend/benches/
- [ ] T012 Create docker-compose.yml for local development (MongoDB 7.x, PostgreSQL 16+, Valkey)
- [ ] T013 Create .env.example with configuration template (database URLs, OAuth2 client IDs, API keys)
- [ ] T014 [P] Setup Grafana dashboards config in infra/grafana/dashboards/
- [ ] T015 [P] Setup Prometheus scrape config in infra/prometheus/prometheus.yml
- [ ] T016 [P] Create Dockerfile for backend service in backend/Dockerfile (multi-stage build: cargo build --release, runtime image)
- [ ] T017 [P] Create Dockerfile for AI agent service in ai-agent-service/Dockerfile (Python base image, requirements.txt, gunicorn)
- [ ] T018 [P] Create Dockerfile for ETL service in etl/Dockerfile (Python base image, requirements.txt for batch jobs)
- [ ] T019 [P] Create .dockerignore files for backend/, ai-agent-service/, etl/ (exclude target/, node_modules/, .git/)
- [ ] T020 Create GitHub Actions CI workflow in .github/workflows/backend.yml (build, test, lint, coverage, docker build, push to ACR with tag 1.0.YYYYMMDD.buildnumber)
- [ ] T021 [P] Create GitHub Actions CI workflow in .github/workflows/ai-agent.yml (build, test, lint, docker build, push to ACR with tag 1.0.YYYYMMDD.buildnumber)
- [ ] T022 [P] Create GitHub Actions CI workflow in .github/workflows/etl.yml (build, test, lint, docker build, push to ACR with tag 1.0.YYYYMMDD.buildnumber)
- [ ] T023 [P] Create GitHub Actions CI workflow in .github/workflows/frontend.yml (build, test, lint, accessibility)
- [ ] T024 Create GitHub Actions CD workflow in .github/workflows/deploy-infra.yml (trigger Pulumi up on infra changes, deploy to Azure)
- [ ] T025 [P] Initialize Pulumi Python project in infra/pulumi/ (Pulumi.yaml, __main__.py, requirements.txt for azure-native)
- [ ] T026 [P] Create Pulumi stack configs in infra/pulumi/ (Pulumi.dev.yaml, Pulumi.staging.yaml, Pulumi.prod.yaml)
- [ ] T027 [P] Create Azure resource group module in infra/pulumi/modules/resource_group.py
- [ ] T028 [P] Create Azure Container Registry module in infra/pulumi/modules/acr.py (ACR for storing container images)
- [ ] T029 [P] Create Azure Storage Account module in infra/pulumi/modules/storage.py (blob storage for file import landing zone)
- [ ] T030 [P] Create Azure Cosmos DB for MongoDB module in infra/pulumi/modules/cosmos_mongo.py (MongoDB-compatible API)
- [ ] T031 [P] Create Azure Database for PostgreSQL module in infra/pulumi/modules/postgres.py (flexible server, VNet integration)
- [ ] T032 [P] Create Azure Cache for Redis module in infra/pulumi/modules/redis.py (Valkey-compatible Redis)
- [ ] T033 [P] Create Azure Service Bus module in infra/pulumi/modules/service_bus.py (namespace, queues for etl, enrichment, ai-parsing, ingestion, import jobs)
- [ ] T034 [P] Create Azure Container Apps module for backend in infra/pulumi/modules/container_app_backend.py (scale rules, ingress, environment variables)
- [ ] T035 [P] Create Azure Container Apps module for AI agent in infra/pulumi/modules/container_app_ai_agent.py
- [ ] T036 [P] Create Azure Container Apps module for ETL jobs in infra/pulumi/modules/container_app_etl.py (Service Bus queue subscriber, scale-to-zero)
- [ ] T037 [P] Create Azure Virtual Network module in infra/pulumi/modules/vnet.py (subnets for Container Apps, PostgreSQL, private endpoints)
- [ ] T038 [P] Create Azure Application Insights module in infra/pulumi/modules/app_insights.py (monitoring, OpenTelemetry ingestion)
- [ ] T039 Create main Pulumi program in infra/pulumi/__main__.py (orchestrate all modules, export endpoints/connection strings)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Setup

- [ ] T040 Create PostgreSQL migration framework setup with sqlx-cli in backend/migrations/
- [ ] T041 Create migration 001_create_users_table.sql in backend/migrations/
- [ ] T042 [P] Create migration 002_create_provider_accounts_table.sql in backend/migrations/
- [ ] T043 [P] Create migration 003_create_activities_table.sql in backend/migrations/
- [ ] T044 [P] Create migration 004_create_workouts_table.sql in backend/migrations/
- [ ] T045 [P] Create migration 005_create_supplemental_data_table.sql in backend/migrations/
- [ ] T046 [P] Create migration 006_create_import_jobs_table.sql in backend/migrations/
- [ ] T047 [P] Create migration 007_create_sync_jobs_table.sql in backend/migrations/
- [ ] T048 [P] Create MongoDB initialization script for raw_activities collection in infra/mongodb/init.js
- [ ] T049 [P] Create MongoDB initialization script for heart_rate_data collection in infra/mongodb/init.js

### Core Models

- [ ] T050 Create User model in backend/src/models/user.rs (id, email, name, auth_provider, privacy_settings)
- [ ] T051 [P] Create ProviderAccount model in backend/src/models/provider_account.rs (id, user_id, provider_name, tokens, sync_status)
- [ ] T052 [P] Create Activity model in backend/src/models/activity.rs (id, user_id, metrics JSONB, gps_track, source, is_duplicate)
- [ ] T053 [P] Create Workout model in backend/src/models/workout.rs (id, activity_id, exercises JSONB)
- [ ] T054 [P] Create SupplementalData model in backend/src/models/supplemental_data.rs (id, activity_id, weather, altitude)
- [ ] T055 [P] Create ImportJob model in backend/src/models/import_job.rs (id, user_id, status, progress, errors)
- [ ] T056 [P] Create SyncJob model in backend/src/models/sync_job.rs (id, provider_account_id, status, sync_type)

### Core Infrastructure

- [ ] T057 Implement database connection pool in backend/src/config/database.rs (PostgreSQL SQLx pool, MongoDB client)
- [ ] T058 [P] Implement Valkey cache client in backend/src/config/cache.rs (connection pool, TTL helpers)
- [ ] T059 [P] Implement Azure Service Bus client in backend/src/config/service_bus.rs (queue sender, message publishing)
- [ ] T060 Implement authentication middleware in backend/src/middleware/auth.rs (JWT validation, user context)
- [ ] T061 [P] Implement logging middleware in backend/src/middleware/logging.rs (structured JSON, correlation IDs)
- [ ] T062 [P] Implement OpenTelemetry tracing in backend/src/middleware/tracing.rs (trace_id, span_id propagation)
- [ ] T063 [P] Implement error handling middleware in backend/src/middleware/error.rs (standardized error responses)
- [ ] T064 Implement API router setup in backend/src/api/mod.rs (Axum router with versioning /api/v1/)
- [ ] T065 [P] Implement rate limiting middleware in backend/src/middleware/rate_limit.rs (per-user, per-endpoint limits)
- [ ] T066 [P] Create TypeScript API client base in frontend/src/services/api-client.ts (axios/fetch wrapper with auth)
- [ ] T067 [P] Create React Query setup in frontend/src/store/query-client.ts (cache config, error handling)
- [ ] T068 [P] Create authentication context in frontend/src/contexts/auth-context.tsx (login, logout, token refresh)
- [ ] T069 [P] Create base layout components in frontend/src/components/layout/ (header, sidebar, footer)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import Fitness Data (Priority: P1) 🎯 MVP

**Goal**: Enable users to connect fitness providers via OAuth2, upload files (CSV/JSON/GPX), and manually enter activities

**Independent Test**: Connect a provider (Garmin), upload a sample CSV file, manually enter a workout, verify all appear in database

### OAuth2 Provider Connection [US1]

- [ ] T070 [P] [US1] Create ProviderRepository in backend/src/repositories/provider_repository.rs (CRUD for provider_accounts)
- [ ] T071 [P] [US1] Create OAuth2 service in backend/src/providers/oauth2_service.rs (PKCE flow, token exchange, encryption AES-256-GCM)
- [ ] T072 [P] [US1] Create Garmin provider integration in backend/src/providers/garmin.rs (OAuth2 endpoints, API client)
- [ ] T073 [P] [US1] Create Fitbit provider integration in backend/src/providers/fitbit.rs (OAuth2 endpoints, API client)
- [ ] T074 [P] [US1] Create Strava provider integration in backend/src/providers/strava.rs (OAuth2 endpoints, API client)
- [ ] T075 [P] [US1] Create Polar provider integration in backend/src/providers/polar.rs (OAuth2 endpoints, API client)
- [ ] T076 [P] [US1] Create Apple Health provider integration in backend/src/providers/apple_health.rs (OAuth2 endpoints, API client)
- [ ] T077 [US1] Implement connect-provider endpoint (POST /api/v1/providers/connect) in backend/src/api/providers/connect.rs per contracts/connect-provider.md
- [ ] T078 [US1] Implement oauth-callback endpoint (GET /api/v1/providers/callback) in backend/src/api/providers/callback.rs per contracts/oauth-callback.md
- [ ] T079 [US1] Generate OpenAPI/Swagger spec for connect-provider and oauth-callback endpoints in backend/src/api/openapi.rs
- [ ] T080 [P] [US1] Create provider connection UI in frontend/src/pages/connect-provider-page.tsx (provider selection, OAuth2 redirect)
- [ ] T081 [P] [US1] Create OAuth2 callback handler component in frontend/src/pages/oauth-callback-page.tsx (handle redirect, token storage)
- [ ] T082 [P] [US1] Create provider list component in frontend/src/components/providers/provider-list.tsx (show connected accounts)

### Provider Sync [US1]

- [ ] T083 [P] [US1] Create SyncJobRepository in backend/src/repositories/sync_job_repository.rs (CRUD for sync_jobs)
- [ ] T084 [US1] Create provider sync service in backend/src/services/sync_service.rs (trigger sync, retry logic, token refresh)
- [ ] T085 [US1] Implement trigger-sync endpoint (POST /api/v1/providers/{id}/sync) in backend/src/api/providers/sync.rs per contracts/trigger-sync.md
- [ ] T086 [US1] Implement sync status endpoint (GET /api/v1/providers/{id}/sync/{syncId}) in backend/src/api/providers/sync_status.rs per contracts/trigger-sync.md
- [ ] T087 [US1] Generate OpenAPI/Swagger spec for trigger-sync and sync-status endpoints in backend/src/api/openapi.rs
- [ ] T088 [US1] Create scheduled cron job for provider sync in backend/src/jobs/provider_sync_cron_job.rs (pre-scheduled intervals, exponential backoff, distributed lock with Valkey)
- [ ] T089 [P] [US1] Create sync trigger UI in frontend/src/components/providers/sync-button.tsx (manual sync, status polling)

### Data Ingestion (Raw Landing) [US1]

- [ ] T090 [P] [US1] Create MongoDB repository for raw_activities in backend/src/repositories/raw_activity_repository.rs (insert, query time-series)
- [ ] T091 [P] [US1] Create ingestion service in backend/src/services/ingestion_service.rs (store raw data from providers, publish to Service Bus ingestion queue)
- [ ] T092 [US1] Create Service Bus subscriber for data ingestion in backend/src/jobs/ingestion_subscriber.rs (subscribe to ingestion queue, process messages, store in MongoDB)
- [ ] T093 [US1] Integrate ingestion queue publishing with provider sync in backend/src/jobs/provider_sync_cron_job.rs (fetch from provider API → publish to Service Bus)

### File Upload [US1]

- [ ] T094 [P] [US1] Create ImportJobRepository in backend/src/repositories/import_job_repository.rs (CRUD for import_jobs)
- [ ] T095 [P] [US1] Create CSV parser in backend/src/parsers/csv_parser.rs (metadata format, heart rate format per contracts/import-file.md)
- [ ] T096 [P] [US1] Create JSON parser in backend/src/parsers/json_parser.rs (activity array format)
- [ ] T097 [P] [US1] Create GPX parser in backend/src/parsers/gpx_parser.rs (GPS track extraction)
- [ ] T098 [P] [US1] Create TCX parser in backend/src/parsers/tcx_parser.rs (Garmin Training Center XML)
- [ ] T099 [P] [US1] Create FIT parser in backend/src/parsers/fit_parser.rs (Garmin FIT binary format)
- [ ] T100 [US1] Create file upload service in backend/src/services/file_upload_service.rs (Azure Blob Storage integration, publish to Service Bus import queue)
- [ ] T101 [US1] Implement import-file endpoint (POST /api/v1/activities/import/file) in backend/src/api/activities/import.rs per contracts/import-file.md
- [ ] T102 [US1] Implement import status endpoint (GET /api/v1/activities/import/{importId}/status) in backend/src/api/activities/import_status.rs per contracts/import-file.md
- [ ] T103 [US1] Generate OpenAPI/Swagger spec for import-file and import-status endpoints in backend/src/api/openapi.rs
- [ ] T104 [US1] Create Service Bus subscriber for file import in backend/src/jobs/file_import_subscriber.rs (subscribe to import queue, parse file, validate, store raw → MongoDB)
- [ ] T105 [P] [US1] Create file upload UI in frontend/src/pages/import-page.tsx (drag-drop, format selection, progress bar)
- [ ] T106 [P] [US1] Create import status polling component in frontend/src/components/import/import-status.tsx (progress, errors)

### Manual Activity Entry [US1]

- [ ] T107 [P] [US1] Create ActivityRepository in backend/src/repositories/activity_repository.rs (CRUD for activities)
- [ ] T108 [P] [US1] Create activity validation service in backend/src/services/activity_validation_service.rs (endTime > startTime, heart rate 30-220)
- [ ] T109 [US1] Implement create-activity endpoint (POST /api/v1/activities) in backend/src/api/activities/create.rs per contracts/create-activity.md
- [ ] T110 [US1] Generate OpenAPI/Swagger spec for create-activity endpoint in backend/src/api/openapi.rs
- [ ] T111 [P] [US1] Create manual entry form in frontend/src/pages/manual-entry-page.tsx (date, time, type, metrics, notes)
- [ ] T112 [P] [US1] Create activity type selector in frontend/src/components/forms/activity-type-select.tsx (running, cycling, swimming, etc.)
- [ ] T113 [P] [US1] Create metrics input component in frontend/src/components/forms/metrics-input.tsx (heart rate, calories, distance)

### ETL & Normalization [US1]

- [ ] T114 Create ETL schema mapping config in etl/python/config/schema_mappings.yml (provider field → unified field)
- [ ] T115 [P] Create JSON schema validation in etl/python/common/validators.py (activity schema, metric ranges)
- [ ] T116 [US1] Create Service Bus subscriber for ETL in etl/python/jobs/etl_subscriber.py (subscribe to etl queue, read MongoDB raw → validate → transform → write PostgreSQL)
- [ ] T117 [US1] Create duplicate detection service in etl/python/jobs/detect_duplicates.py (hash provider+external_id+start_time, mark is_duplicate)
- [ ] T118 [US1] Update ingestion/import services to publish ETL messages to Service Bus queue after raw data storage

### AI Note Parsing [US1]

- [ ] T119 [P] [US1] Create AI agent service stub in ai-agent-service/src/api/parse_note.py (POST /ai-agent/api/v1/parse-note endpoint)
- [ ] T120 [P] [US1] Create Service Bus subscriber for AI parsing in ai-agent-service/src/jobs/ai_parsing_subscriber.py (subscribe to ai-parsing queue, process notes)
- [ ] T121 [US1] Update create-activity endpoint to publish AI parsing messages to Service Bus queue when notes present in backend/src/api/activities/create.rs

**Checkpoint**: At this point, User Story 1 should be fully functional - users can connect providers, upload files, enter activities manually, and see raw data stored

---

## Phase 4: User Story 2 - Visualize & Explore Data (Priority: P2)

**Goal**: Enable users to view interactive dashboards, filter activities, compare metrics, and export data/charts

**Independent Test**: Import activities (via US1), open dashboard, apply filters (date range, activity type), overlay metrics, export CSV/PNG

### Dashboard Data Retrieval [US2]

- [ ] T122 [US2] Create dashboard query service in backend/src/services/dashboard_service.rs (query activities with filters, JOIN supplemental_data)
- [ ] T123 [US2] Implement list-activities endpoint (GET /api/v1/activities) in backend/src/api/activities/list.rs per contracts/list-activities.md (pagination, user_query search)
- [ ] T124 [US2] Generate OpenAPI/Swagger spec for list-activities endpoint in backend/src/api/openapi.rs
- [ ] T125 [US2] Implement Valkey caching in dashboard service (cache key: dashboard:{user_id}:{start}:{end}:{activity_type}:{user_query}:{page}, TTL: 5 min)
- [ ] T126 [US2] Add cache invalidation logic in backend/src/services/cache_invalidation_service.rs (invalidate on new activity, import, sync)

### Data Visualization [US2]

- [ ] T127 [P] [US2] Create dashboard page in frontend/src/pages/dashboard-page.tsx (main layout, filter controls)
- [ ] T128 [P] [US2] Create date range picker component in frontend/src/components/forms/date-range-picker.tsx (start/end date selection)
- [ ] T129 [P] [US2] Create activity type filter in frontend/src/components/forms/activity-type-filter.tsx (multi-select checkboxes)
- [ ] T130 [P] [US2] Create user query search input in frontend/src/components/forms/user-query-input.tsx (comma-separated search terms)
- [ ] T131 [US2] Create Plotly line chart component in frontend/src/components/charts/line-chart.tsx (time-series metrics, WebGL rendering)
- [ ] T132 [P] [US2] Create Plotly bar chart component in frontend/src/components/charts/bar-chart.tsx (aggregate metrics by activity type)
- [ ] T133 [P] [US2] Create metric overlay component in frontend/src/components/charts/metric-overlay.tsx (overlay heart rate + calories on same chart)
- [ ] T134 [US2] Create activity list table in frontend/src/components/activities/activity-table.tsx (paginated, sortable, clickable rows)
- [ ] T135 [P] [US2] Create activity detail modal in frontend/src/components/activities/activity-detail-modal.tsx (full metrics, GPS map if available)

### Data Export [US2]

- [ ] T136 [P] [US2] Create CSV export service in backend/src/services/export_service.rs (metadata format, heart rate time-series format)
- [ ] T137 [P] [US2] Create PNG export service in backend/src/services/chart_export_service.rs (Plotly chart → PNG via headless browser)
- [ ] T138 [P] [US2] Create PDF export service in backend/src/services/pdf_export_service.rs (activities + charts → PDF layout)
- [ ] T139 [US2] Implement export-activities endpoint (GET /api/v1/activities/export) in backend/src/api/activities/export.rs per contracts/export-activities.md (format, csv_type, chart_type params)
- [ ] T140 [US2] Generate OpenAPI/Swagger spec for export-activities endpoint in backend/src/api/openapi.rs
- [ ] T141 [P] [US2] Create export button component in frontend/src/components/export/export-button.tsx (format selector, download trigger)
- [ ] T142 [P] [US2] Create export settings modal in frontend/src/components/export/export-settings-modal.tsx (CSV type, chart type, metric selection)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can import data and visualize it with rich charts and filters

---

## Phase 5: User Story 3 - Data Supplementation & Enrichment (Priority: P3)

**Goal**: Automatically enrich activities with weather, air quality, and altitude data based on location/time

**Independent Test**: Import an activity with GPS coordinates and timestamp, verify weather/altitude data is added to supplemental_data table

### Enrichment Infrastructure [US3]

- [ ] T143 [P] [US3] Create SupplementalDataRepository in backend/src/repositories/supplemental_data_repository.rs (CRUD for supplemental_data)
- [ ] T144 [P] [US3] Create weather API client in backend/src/enrichment/weather_client.rs (OpenWeatherMap or Open-Meteo API)
- [ ] T145 [P] [US3] Create altitude API client in backend/src/enrichment/altitude_client.rs (Open-Elevation API)
- [ ] T146 [US3] Create Service Bus subscriber for enrichment in backend/src/jobs/enrichment_subscriber.rs (subscribe to enrichment queue, batch activities by location/time, call APIs, store results)
- [ ] T147 [US3] Update activity validation service to publish enrichment messages to Service Bus queue when GPS/time present in backend/src/services/activity_validation_service.rs

### Enrichment Display [US3]

- [ ] T148 [P] [US3] Create weather badge component in frontend/src/components/activities/weather-badge.tsx (temp, humidity, description icon)
- [ ] T149 [P] [US3] Create altitude display in frontend/src/components/activities/altitude-display.tsx (elevation gain, max altitude)
- [ ] T150 [US3] Integrate weather/altitude into activity detail modal in frontend/src/components/activities/activity-detail-modal.tsx
- [ ] T151 [US3] Add weather/altitude columns to activity table in frontend/src/components/activities/activity-table.tsx (optional columns, sortable)

### Correlation Analysis [US3]

- [ ] T152 [US3] Create correlation chart component in frontend/src/components/charts/correlation-chart.tsx (scatter plot: weather vs performance)
- [ ] T153 [US3] Add weather filter to dashboard in frontend/src/components/forms/weather-filter.tsx (temperature range, weather type)
- [ ] T154 [US3] Add altitude filter to dashboard in frontend/src/components/forms/altitude-filter.tsx (elevation range)

**Checkpoint**: All user stories should now be independently functional - complete platform with ingestion, visualization, and enrichment

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Performance Optimization

- [ ] T155 [P] Add database indexes per data-model.md in backend/migrations/008_add_performance_indexes.sql (composite, partial, GIN for JSONB)
- [ ] T156 [P] Optimize dashboard query with query planning in backend/src/services/dashboard_service.rs (EXPLAIN ANALYZE, query hints)
- [ ] T157 [P] Add connection pooling tuning in backend/src/config/database.rs (min/max connections, idle timeout)
- [ ] T158 [P] Benchmark API endpoints with criterion in backend/benches/api_benchmarks.rs (verify p95 <200ms budget)
- [ ] T159 [P] Run Lighthouse on frontend pages (verify p99 <1s dashboard load budget)

### Security Hardening

- [ ] T160 [P] Add input validation tests in backend/tests/unit/validation_tests.rs (SQL injection, XSS, oversized payloads)
- [ ] T161 [P] Add rate limiting tests in backend/tests/integration/rate_limit_tests.rs (verify limits enforced)
- [ ] T162 [P] Add CORS configuration in backend/src/middleware/cors.rs (restrict origins)
- [ ] T163 [P] Add CSP headers in backend/src/middleware/security.rs (Content Security Policy)
- [ ] T164 [P] Audit dependencies with cargo-audit in .github/workflows/backend.yml

### Accessibility

- [ ] T165 [P] Run axe-core accessibility tests in frontend/tests/a11y/ (verify WCAG 2.1 AA compliance)
- [ ] T166 [P] Add ARIA labels to all interactive elements in frontend/src/components/ (buttons, inputs, charts)
- [ ] T167 [P] Test keyboard navigation in frontend/tests/e2e/keyboard_navigation.spec.ts (tab order, focus management)
- [ ] T168 [P] Test screen reader compatibility with NVDA/JAWS (manual testing checklist)
- [ ] T169 [P] Verify color contrast ratios ≥4.5:1 in frontend/tailwind.config.js (automated check)

### Observability

- [ ] T170 [P] Add OpenTelemetry metrics for critical paths in backend/src/middleware/tracing.rs (OAuth2 latency, provider API response times, normalization throughput, dashboard render time, export generation time)
- [ ] T171 [P] Create Grafana dashboards in infra/grafana/dashboards/ (API latency, error rates, sync job status, cache hit rates)
- [ ] T172 [P] Add structured logging for errors in backend/src/middleware/logging.rs (error_message, stack_trace, user_id, provider, activity_id)
- [ ] T173 [P] Setup alerting rules in infra/prometheus/alerts.yml (API p95 >200ms, sync job failures >10%, cache hit rate <80%)

### Documentation

- [ ] T174 [P] Generate OpenAPI documentation page in docs/api/openapi.html (from Swagger specs)
- [ ] T175 [P] Create architecture diagrams in docs/architecture/ (system overview, data flow, OAuth2 flow)
- [ ] T176 [P] Document deployment guide in docs/deployment/kubernetes.md (Kubernetes manifests, environment variables)
- [ ] T177 [P] Validate quickstart.md instructions in specs/001-platform-ingestion/quickstart.md (follow steps on fresh environment)

### Testing

- [ ] T178 [P] Add contract tests for all endpoints in backend/tests/contract/ (verify Swagger specs match implementations)
- [ ] T179 [P] Add E2E tests for critical user flows in frontend/tests/e2e/ (connect provider, upload file, view dashboard, export data)
- [ ] T180 [P] Verify test coverage ≥80% overall, ≥90% for core domain in .github/workflows/backend.yml (cargo-tarpaulin report)
- [ ] T181 [P] Add integration tests for ETL pipeline in etl/python/tests/ (raw → normalized data flow)

### Code Quality

- [ ] T182 [P] Code cleanup pass in backend/src/ (remove unused imports, dead code, TODO comments)
- [ ] T183 [P] Code cleanup pass in frontend/src/ (remove unused components, console.logs, commented code)
- [ ] T184 [P] Refactor duplicated logic in backend/src/providers/ (extract shared OAuth2 flow, token refresh)
- [ ] T185 [P] Refactor duplicated chart logic in frontend/src/components/charts/ (extract base chart component)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion (can run in parallel with US1 if staffed)
- **User Story 3 (Phase 5)**: Depends on Foundational phase completion (can run in parallel with US1/US2 if staffed)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - Can start after Foundational phase
- **User Story 2 (P2)**: Depends on User Story 1 for data to visualize (technically can start in parallel, but no test data without US1)
- **User Story 3 (P3)**: Depends on User Story 1 for activities to enrich (technically can start in parallel, but no test data without US1)

### Within Each User Story

**User Story 1 (Import Data)**:
- OAuth2 foundation (T070-T071) before provider integrations (T072-T076)
- Provider integrations before endpoints (T077-T078)
- Repository layer (T070) before service layer (T071) before API layer (T077-T078)
- Backend endpoints before frontend UI (T080-T082)
- Service Bus client (T059) before any job subscribers
- File parsers (T095-T099) before upload service (T100) before endpoint (T101)
- ETL infrastructure (T114-T115) before ETL subscriber (T116)
- Provider sync cron job (T088) runs independently on schedule
- Background subscribers: ingestion (T092), file import (T104), ETL (T116), AI parsing (T120), enrichment (T146) all subscribe to Service Bus queues

**User Story 2 (Visualize Data)**:
- Dashboard service (T122) before list endpoint (T123)
- Backend endpoints before frontend components (T127-T135)
- Chart components (T131-T133) before export components (T141-T142)
- Export services (T136-T138) before export endpoint (T139)

**User Story 3 (Enrichment)**:
- Repository (T143) and API clients (T144-T145) before enrichment subscriber (T146)
- Service Bus queue setup (T033) before enrichment subscriber (T146)
- Backend enrichment before frontend display (T148-T151)

---

## Parallel Opportunities

### Setup Phase (Phase 1)
- All linting/static analysis tasks (T004-T006) can run in parallel
- All design token/test framework setup (T007-T011) can run in parallel
- All Dockerfile creation (T016-T018) can run in parallel
- All CI workflow creation (T020-T023) can run in parallel
- All Pulumi resource modules (T027-T037) can run in parallel after Pulumi project init (T025-T026)

### Foundational Phase (Phase 2)
- All migration files (T042-T049) can run in parallel after T040
- All model definitions (T051-T056) can run in parallel after migrations
- All infrastructure components (T057-T069) can run in parallel after database setup

### User Story 1
- All provider integrations (T072-T076) can run in parallel
- All file parsers (T095-T099) can run in parallel
- OAuth2 UI (T080-T082) can run in parallel with backend OAuth2 work
- File upload UI (T105-T106) can run in parallel with backend file upload work
- All Service Bus subscribers (T092, T104, T116, T120) can be developed in parallel

### User Story 2
- All chart components (T131-T133) can run in parallel
- All export services (T136-T138) can run in parallel
- Filter components (T128-T130) can run in parallel

### User Story 3
- Weather and altitude API clients (T144-T145) can run in parallel
- Display components (T148-T151) can run in parallel

### Polish Phase
- All performance optimization tasks (T155-T159) can run in parallel
- All security tasks (T160-T164) can run in parallel
- All accessibility tasks (T165-T169) can run in parallel
- All observability tasks (T170-T173) can run in parallel
- All documentation tasks (T174-T177) can run in parallel
- All testing tasks (T178-T181) can run in parallel
- All code cleanup tasks (T182-T185) can run in parallel

---

## Parallel Example: User Story 1

```bash
# All provider integrations together:
Task: T072 [P] [US1] Create Garmin provider integration
Task: T073 [P] [US1] Create Fitbit provider integration
Task: T074 [P] [US1] Create Strava provider integration
Task: T075 [P] [US1] Create Polar provider integration
Task: T076 [P] [US1] Create Apple Health provider integration

# All file parsers together:
Task: T095 [P] [US1] Create CSV parser
Task: T096 [P] [US1] Create JSON parser
Task: T097 [P] [US1] Create GPX parser
Task: T098 [P] [US1] Create TCX parser
Task: T099 [P] [US1] Create FIT parser
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T039) - Infrastructure, Dockerization, CI/CD, Pulumi, Service Bus
2. Complete Phase 2: Foundational (T040-T069) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T070-T121)
4. **STOP and VALIDATE**: 
   - Connect Garmin account via OAuth2
   - Upload sample CSV file
   - Manually enter a workout
   - Verify all data appears in PostgreSQL activities table
5. Deploy/demo if ready - **Minimum Viable Product achieved!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (can deploy to Azure Container Apps)
2. Add User Story 1 → Test independently → Deploy/Demo (**MVP!** Users can import data)
3. Add User Story 2 → Test independently → Deploy/Demo (Users can visualize and export data)
4. Add User Story 3 → Test independently → Deploy/Demo (Data enriched with weather/altitude)
5. Polish Phase → Production-ready (performance, security, accessibility hardened)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (critical path, some parallelism in Pulumi modules)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (OAuth2, file upload, ETL)
   - **Developer B**: User Story 2 (dashboard, charts, export) - starts after some US1 data available
   - **Developer C**: User Story 3 (enrichment APIs, background jobs)
   - **Developer D**: Polish tasks (performance, security, accessibility)
3. Stories integrate seamlessly since they're independently designed

---

## Task Statistics

- **Total Tasks**: 185
- **Setup Phase**: 39 tasks (includes Docker, CI/CD, Pulumi infrastructure, Service Bus)
- **Foundational Phase**: 30 tasks
- **User Story 1 (P1 - MVP)**: 52 tasks
- **User Story 2 (P2)**: 21 tasks
- **User Story 3 (P3)**: 12 tasks
- **Polish Phase**: 31 tasks

### Tasks by Priority
- **P1 (MVP - US1)**: 52 tasks (critical for first deployment)
- **P2 (Visualization - US2)**: 21 tasks (adds value, can defer if needed)
- **P3 (Enrichment - US3)**: 12 tasks (nice-to-have, can defer)
- **Infrastructure/Polish**: 100 tasks (setup + foundational + cross-cutting)

### Parallel Tasks
- **Marked [P]**: ~95 tasks can run in parallel with appropriate team capacity
- **Sequential**: ~90 tasks require ordering due to dependencies

---

## Notes

- All tasks include exact file paths for clarity
- [P] marker indicates parallelizable tasks (different files, no dependencies)
- [Story] label (US1, US2, US3) maps to user stories from spec.md
- Constitution alignment:
  - Code Quality: Clippy, ESLint, static analysis (T004-T006)
  - Testing: Contract, integration, E2E tests in Polish phase (T178-T181)
  - UX Consistency: Tailwind tokens, WCAG 2.1 AA compliance (T007, T165-T169)
  - Performance: Benchmarks, optimization, budgets (T011, T155-T159)
  - Observability: OpenTelemetry, Grafana, Prometheus (T062, T170-T173)
  - Security: Input validation, rate limiting, CORS, CSP (T160-T164)
  - Documentation: OpenAPI specs, architecture diagrams, deployment guides (T174-T177)
- OpenAPI/Swagger generation tasks ensure API contracts match implementations (per contract file instructions)
- Each user story has checkpoint for independent validation
- MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = ~121 tasks
- Message-driven architecture: Background jobs (ETL, enrichment, AI parsing, ingestion, import) subscribe to Azure Service Bus queues
- Provider sync runs as scheduled cron job (not message-driven)
- Tests are integrated into implementation (not separate phase) per Constitution TDD approach
- Commit frequently after logical task groups
- Stop at any checkpoint to validate story independently before proceeding
