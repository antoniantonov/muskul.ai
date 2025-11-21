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
- [ ] T016 Create GitHub Actions CI workflow in .github/workflows/backend.yml (build, test, lint, coverage)
- [ ] T017 [P] Create GitHub Actions CI workflow in .github/workflows/frontend.yml (build, test, lint, accessibility)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Setup

- [ ] T018 Create PostgreSQL migration framework setup with sqlx-cli in backend/migrations/
- [ ] T019 Create migration 001_create_users_table.sql in backend/migrations/
- [ ] T020 [P] Create migration 002_create_provider_accounts_table.sql in backend/migrations/
- [ ] T021 [P] Create migration 003_create_activities_table.sql in backend/migrations/
- [ ] T022 [P] Create migration 004_create_workouts_table.sql in backend/migrations/
- [ ] T023 [P] Create migration 005_create_supplemental_data_table.sql in backend/migrations/
- [ ] T024 [P] Create migration 006_create_import_jobs_table.sql in backend/migrations/
- [ ] T025 [P] Create migration 007_create_sync_jobs_table.sql in backend/migrations/
- [ ] T026 [P] Create MongoDB initialization script for raw_activities collection in infra/mongodb/init.js
- [ ] T027 [P] Create MongoDB initialization script for heart_rate_data collection in infra/mongodb/init.js

### Core Models

- [ ] T028 Create User model in backend/src/models/user.rs (id, email, name, auth_provider, privacy_settings)
- [ ] T029 [P] Create ProviderAccount model in backend/src/models/provider_account.rs (id, user_id, provider_name, tokens, sync_status)
- [ ] T030 [P] Create Activity model in backend/src/models/activity.rs (id, user_id, metrics JSONB, gps_track, source, is_duplicate)
- [ ] T031 [P] Create Workout model in backend/src/models/workout.rs (id, activity_id, exercises JSONB)
- [ ] T032 [P] Create SupplementalData model in backend/src/models/supplemental_data.rs (id, activity_id, weather, altitude)
- [ ] T033 [P] Create ImportJob model in backend/src/models/import_job.rs (id, user_id, status, progress, errors)
- [ ] T034 [P] Create SyncJob model in backend/src/models/sync_job.rs (id, provider_account_id, status, sync_type)

### Core Infrastructure

- [ ] T035 Implement database connection pool in backend/src/config/database.rs (PostgreSQL SQLx pool, MongoDB client)
- [ ] T036 [P] Implement Valkey cache client in backend/src/config/cache.rs (connection pool, TTL helpers)
- [ ] T037 Implement authentication middleware in backend/src/middleware/auth.rs (JWT validation, user context)
- [ ] T038 [P] Implement logging middleware in backend/src/middleware/logging.rs (structured JSON, correlation IDs)
- [ ] T039 [P] Implement OpenTelemetry tracing in backend/src/middleware/tracing.rs (trace_id, span_id propagation)
- [ ] T040 [P] Implement error handling middleware in backend/src/middleware/error.rs (standardized error responses)
- [ ] T041 Implement API router setup in backend/src/api/mod.rs (Axum router with versioning /api/v1/)
- [ ] T042 [P] Implement rate limiting middleware in backend/src/middleware/rate_limit.rs (per-user, per-endpoint limits)
- [ ] T043 [P] Create TypeScript API client base in frontend/src/services/api-client.ts (axios/fetch wrapper with auth)
- [ ] T044 [P] Create React Query setup in frontend/src/store/query-client.ts (cache config, error handling)
- [ ] T045 [P] Create authentication context in frontend/src/contexts/auth-context.tsx (login, logout, token refresh)
- [ ] T046 [P] Create base layout components in frontend/src/components/layout/ (header, sidebar, footer)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import Fitness Data (Priority: P1) 🎯 MVP

**Goal**: Enable users to connect fitness providers via OAuth2, upload files (CSV/JSON/GPX), and manually enter activities

**Independent Test**: Connect a provider (Garmin), upload a sample CSV file, manually enter a workout, verify all appear in database

### OAuth2 Provider Connection [US1]

- [ ] T047 [P] [US1] Create ProviderRepository in backend/src/repositories/provider_repository.rs (CRUD for provider_accounts)
- [ ] T048 [P] [US1] Create OAuth2 service in backend/src/providers/oauth2_service.rs (PKCE flow, token exchange, encryption AES-256-GCM)
- [ ] T049 [P] [US1] Create Garmin provider integration in backend/src/providers/garmin.rs (OAuth2 endpoints, API client)
- [ ] T050 [P] [US1] Create Fitbit provider integration in backend/src/providers/fitbit.rs (OAuth2 endpoints, API client)
- [ ] T051 [P] [US1] Create Strava provider integration in backend/src/providers/strava.rs (OAuth2 endpoints, API client)
- [ ] T052 [P] [US1] Create Polar provider integration in backend/src/providers/polar.rs (OAuth2 endpoints, API client)
- [ ] T053 [P] [US1] Create Apple Health provider integration in backend/src/providers/apple_health.rs (OAuth2 endpoints, API client)
- [ ] T054 [US1] Implement connect-provider endpoint (POST /api/v1/providers/connect) in backend/src/api/providers/connect.rs per contracts/connect-provider.md
- [ ] T055 [US1] Implement oauth-callback endpoint (GET /api/v1/providers/callback) in backend/src/api/providers/callback.rs per contracts/oauth-callback.md
- [ ] T056 [US1] Generate OpenAPI/Swagger spec for connect-provider and oauth-callback endpoints in backend/src/api/openapi.rs
- [ ] T057 [P] [US1] Create provider connection UI in frontend/src/pages/connect-provider-page.tsx (provider selection, OAuth2 redirect)
- [ ] T058 [P] [US1] Create OAuth2 callback handler component in frontend/src/pages/oauth-callback-page.tsx (handle redirect, token storage)
- [ ] T059 [P] [US1] Create provider list component in frontend/src/components/providers/provider-list.tsx (show connected accounts)

### Provider Sync [US1]

- [ ] T060 [P] [US1] Create SyncJobRepository in backend/src/repositories/sync_job_repository.rs (CRUD for sync_jobs)
- [ ] T061 [US1] Create provider sync service in backend/src/services/sync_service.rs (trigger sync, retry logic, token refresh)
- [ ] T062 [US1] Implement trigger-sync endpoint (POST /api/v1/providers/{id}/sync) in backend/src/api/providers/sync.rs per contracts/trigger-sync.md
- [ ] T063 [US1] Implement sync status endpoint (GET /api/v1/providers/{id}/sync/{syncId}) in backend/src/api/providers/sync_status.rs per contracts/trigger-sync.md
- [ ] T064 [US1] Generate OpenAPI/Swagger spec for trigger-sync and sync-status endpoints in backend/src/api/openapi.rs
- [ ] T065 [US1] Create background sync job in backend/src/jobs/provider_sync_job.rs (scheduled sync, exponential backoff, distributed lock with Valkey)
- [ ] T066 [P] [US1] Create sync trigger UI in frontend/src/components/providers/sync-button.tsx (manual sync, status polling)

### Data Ingestion (Raw Landing) [US1]

- [ ] T067 [P] [US1] Create MongoDB repository for raw_activities in backend/src/repositories/raw_activity_repository.rs (insert, query time-series)
- [ ] T068 [P] [US1] Create ingestion service in backend/src/services/ingestion_service.rs (store raw data from providers)
- [ ] T069 [US1] Integrate ingestion service with provider sync job in backend/src/jobs/provider_sync_job.rs (fetch from provider API → store in MongoDB)

### File Upload [US1]

- [ ] T070 [P] [US1] Create ImportJobRepository in backend/src/repositories/import_job_repository.rs (CRUD for import_jobs)
- [ ] T071 [P] [US1] Create CSV parser in backend/src/parsers/csv_parser.rs (metadata format, heart rate format per contracts/import-file.md)
- [ ] T072 [P] [US1] Create JSON parser in backend/src/parsers/json_parser.rs (activity array format)
- [ ] T073 [P] [US1] Create GPX parser in backend/src/parsers/gpx_parser.rs (GPS track extraction)
- [ ] T074 [P] [US1] Create TCX parser in backend/src/parsers/tcx_parser.rs (Garmin Training Center XML)
- [ ] T075 [P] [US1] Create FIT parser in backend/src/parsers/fit_parser.rs (Garmin FIT binary format)
- [ ] T076 [US1] Create file upload service in backend/src/services/file_upload_service.rs (temp storage S3/local, async processing)
- [ ] T077 [US1] Implement import-file endpoint (POST /api/v1/activities/import/file) in backend/src/api/activities/import.rs per contracts/import-file.md
- [ ] T078 [US1] Implement import status endpoint (GET /api/v1/activities/import/{importId}/status) in backend/src/api/activities/import_status.rs per contracts/import-file.md
- [ ] T079 [US1] Generate OpenAPI/Swagger spec for import-file and import-status endpoints in backend/src/api/openapi.rs
- [ ] T080 [US1] Create background import job in backend/src/jobs/file_import_job.rs (parse file, validate, store raw → MongoDB)
- [ ] T081 [P] [US1] Create file upload UI in frontend/src/pages/import-page.tsx (drag-drop, format selection, progress bar)
- [ ] T082 [P] [US1] Create import status polling component in frontend/src/components/import/import-status.tsx (progress, errors)

### Manual Activity Entry [US1]

- [ ] T083 [P] [US1] Create ActivityRepository in backend/src/repositories/activity_repository.rs (CRUD for activities)
- [ ] T084 [P] [US1] Create activity validation service in backend/src/services/activity_validation_service.rs (endTime > startTime, heart rate 30-220)
- [ ] T085 [US1] Implement create-activity endpoint (POST /api/v1/activities) in backend/src/api/activities/create.rs per contracts/create-activity.md
- [ ] T086 [US1] Generate OpenAPI/Swagger spec for create-activity endpoint in backend/src/api/openapi.rs
- [ ] T087 [P] [US1] Create manual entry form in frontend/src/pages/manual-entry-page.tsx (date, time, type, metrics, notes)
- [ ] T088 [P] [US1] Create activity type selector in frontend/src/components/forms/activity-type-select.tsx (running, cycling, swimming, etc.)
- [ ] T089 [P] [US1] Create metrics input component in frontend/src/components/forms/metrics-input.tsx (heart rate, calories, distance)

### ETL & Normalization [US1]

- [ ] T090 Create ETL schema mapping config in etl/python/config/schema_mappings.yml (provider field → unified field)
- [ ] T091 [P] Create JSON schema validation in etl/python/common/validators.py (activity schema, metric ranges)
- [ ] T092 [US1] Create normalization service in etl/python/jobs/normalize_activities.py (read MongoDB raw → validate → transform → write PostgreSQL)
- [ ] T093 [US1] Create duplicate detection service in etl/python/jobs/detect_duplicates.py (hash provider+external_id+start_time, mark is_duplicate)
- [ ] T094 [US1] Integrate normalization with import/sync jobs in backend/src/jobs/ (trigger ETL after raw data ingestion)

### AI Note Parsing [US1]

- [ ] T095 [P] [US1] Create AI agent service stub in ai-agent-service/src/api/parse_note.py (POST /ai-agent/api/v1/parse-note endpoint)
- [ ] T096 [P] [US1] Create note parsing client in backend/src/ai_agent/client.rs (HTTP client for AI service)
- [ ] T097 [US1] Integrate AI note parsing with create-activity endpoint in backend/src/api/activities/create.rs (async call, store parsed_notes)
- [ ] T098 [US1] Create background AI parsing job in backend/src/jobs/ai_parse_notes_job.rs (batch process activities with notes)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can connect providers, upload files, enter activities manually, and see raw data stored

---

## Phase 4: User Story 2 - Visualize & Explore Data (Priority: P2)

**Goal**: Enable users to view interactive dashboards, filter activities, compare metrics, and export data/charts

**Independent Test**: Import activities (via US1), open dashboard, apply filters (date range, activity type), overlay metrics, export CSV/PNG

### Dashboard Data Retrieval [US2]

- [ ] T099 [US2] Create dashboard query service in backend/src/services/dashboard_service.rs (query activities with filters, JOIN supplemental_data)
- [ ] T100 [US2] Implement list-activities endpoint (GET /api/v1/activities) in backend/src/api/activities/list.rs per contracts/list-activities.md (pagination, user_query search)
- [ ] T101 [US2] Generate OpenAPI/Swagger spec for list-activities endpoint in backend/src/api/openapi.rs
- [ ] T102 [US2] Implement Valkey caching in dashboard service (cache key: dashboard:{user_id}:{start}:{end}:{activity_type}:{user_query}:{page}, TTL: 5 min)
- [ ] T103 [US2] Add cache invalidation logic in backend/src/services/cache_invalidation_service.rs (invalidate on new activity, import, sync)

### Data Visualization [US2]

- [ ] T104 [P] [US2] Create dashboard page in frontend/src/pages/dashboard-page.tsx (main layout, filter controls)
- [ ] T105 [P] [US2] Create date range picker component in frontend/src/components/forms/date-range-picker.tsx (start/end date selection)
- [ ] T106 [P] [US2] Create activity type filter in frontend/src/components/forms/activity-type-filter.tsx (multi-select checkboxes)
- [ ] T107 [P] [US2] Create user query search input in frontend/src/components/forms/user-query-input.tsx (comma-separated search terms)
- [ ] T108 [US2] Create Plotly line chart component in frontend/src/components/charts/line-chart.tsx (time-series metrics, WebGL rendering)
- [ ] T109 [P] [US2] Create Plotly bar chart component in frontend/src/components/charts/bar-chart.tsx (aggregate metrics by activity type)
- [ ] T110 [P] [US2] Create metric overlay component in frontend/src/components/charts/metric-overlay.tsx (overlay heart rate + calories on same chart)
- [ ] T111 [US2] Create activity list table in frontend/src/components/activities/activity-table.tsx (paginated, sortable, clickable rows)
- [ ] T112 [P] [US2] Create activity detail modal in frontend/src/components/activities/activity-detail-modal.tsx (full metrics, GPS map if available)

### Data Export [US2]

- [ ] T113 [P] [US2] Create CSV export service in backend/src/services/export_service.rs (metadata format, heart rate time-series format)
- [ ] T114 [P] [US2] Create PNG export service in backend/src/services/chart_export_service.rs (Plotly chart → PNG via headless browser)
- [ ] T115 [P] [US2] Create PDF export service in backend/src/services/pdf_export_service.rs (activities + charts → PDF layout)
- [ ] T116 [US2] Implement export-activities endpoint (GET /api/v1/activities/export) in backend/src/api/activities/export.rs per contracts/export-activities.md (format, csv_type, chart_type params)
- [ ] T117 [US2] Generate OpenAPI/Swagger spec for export-activities endpoint in backend/src/api/openapi.rs
- [ ] T118 [P] [US2] Create export button component in frontend/src/components/export/export-button.tsx (format selector, download trigger)
- [ ] T119 [P] [US2] Create export settings modal in frontend/src/components/export/export-settings-modal.tsx (CSV type, chart type, metric selection)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can import data and visualize it with rich charts and filters

---

## Phase 5: User Story 3 - Data Supplementation & Enrichment (Priority: P3)

**Goal**: Automatically enrich activities with weather, air quality, and altitude data based on location/time

**Independent Test**: Import an activity with GPS coordinates and timestamp, verify weather/altitude data is added to supplemental_data table

### Enrichment Infrastructure [US3]

- [ ] T120 [P] [US3] Create SupplementalDataRepository in backend/src/repositories/supplemental_data_repository.rs (CRUD for supplemental_data)
- [ ] T121 [P] [US3] Create weather API client in backend/src/enrichment/weather_client.rs (OpenWeatherMap or Open-Meteo API)
- [ ] T122 [P] [US3] Create altitude API client in backend/src/enrichment/altitude_client.rs (Open-Elevation API)
- [ ] T123 [US3] Create enrichment service in backend/src/services/enrichment_service.rs (batch activities by location/time, call APIs, store results)
- [ ] T124 [US3] Create background enrichment job in backend/src/jobs/enrichment_job.rs (query pending activities, enrich, update status)
- [ ] T125 [US3] Add enrichment queue logic in backend/src/services/activity_validation_service.rs (mark activities for enrichment if GPS/time present)

### Enrichment Display [US3]

- [ ] T126 [P] [US3] Create weather badge component in frontend/src/components/activities/weather-badge.tsx (temp, humidity, description icon)
- [ ] T127 [P] [US3] Create altitude display in frontend/src/components/activities/altitude-display.tsx (elevation gain, max altitude)
- [ ] T128 [US3] Integrate weather/altitude into activity detail modal in frontend/src/components/activities/activity-detail-modal.tsx
- [ ] T129 [US3] Add weather/altitude columns to activity table in frontend/src/components/activities/activity-table.tsx (optional columns, sortable)

### Correlation Analysis [US3]

- [ ] T130 [US3] Create correlation chart component in frontend/src/components/charts/correlation-chart.tsx (scatter plot: weather vs performance)
- [ ] T131 [US3] Add weather filter to dashboard in frontend/src/components/forms/weather-filter.tsx (temperature range, weather type)
- [ ] T132 [US3] Add altitude filter to dashboard in frontend/src/components/forms/altitude-filter.tsx (elevation range)

**Checkpoint**: All user stories should now be independently functional - complete platform with ingestion, visualization, and enrichment

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Performance Optimization

- [ ] T133 [P] Add database indexes per data-model.md in backend/migrations/008_add_performance_indexes.sql (composite, partial, GIN for JSONB)
- [ ] T134 [P] Optimize dashboard query with query planning in backend/src/services/dashboard_service.rs (EXPLAIN ANALYZE, query hints)
- [ ] T135 [P] Add connection pooling tuning in backend/src/config/database.rs (min/max connections, idle timeout)
- [ ] T136 [P] Benchmark API endpoints with criterion in backend/benches/api_benchmarks.rs (verify p95 <200ms budget)
- [ ] T137 [P] Run Lighthouse on frontend pages (verify p99 <1s dashboard load budget)

### Security Hardening

- [ ] T138 [P] Add input validation tests in backend/tests/unit/validation_tests.rs (SQL injection, XSS, oversized payloads)
- [ ] T139 [P] Add rate limiting tests in backend/tests/integration/rate_limit_tests.rs (verify limits enforced)
- [ ] T140 [P] Add CORS configuration in backend/src/middleware/cors.rs (restrict origins)
- [ ] T141 [P] Add CSP headers in backend/src/middleware/security.rs (Content Security Policy)
- [ ] T142 [P] Audit dependencies with cargo-audit in .github/workflows/backend.yml

### Accessibility

- [ ] T143 [P] Run axe-core accessibility tests in frontend/tests/a11y/ (verify WCAG 2.1 AA compliance)
- [ ] T144 [P] Add ARIA labels to all interactive elements in frontend/src/components/ (buttons, inputs, charts)
- [ ] T145 [P] Test keyboard navigation in frontend/tests/e2e/keyboard_navigation.spec.ts (tab order, focus management)
- [ ] T146 [P] Test screen reader compatibility with NVDA/JAWS (manual testing checklist)
- [ ] T147 [P] Verify color contrast ratios ≥4.5:1 in frontend/tailwind.config.js (automated check)

### Observability

- [ ] T148 [P] Add OpenTelemetry metrics for critical paths in backend/src/middleware/tracing.rs (OAuth2 latency, provider API response times, normalization throughput, dashboard render time, export generation time)
- [ ] T149 [P] Create Grafana dashboards in infra/grafana/dashboards/ (API latency, error rates, sync job status, cache hit rates)
- [ ] T150 [P] Add structured logging for errors in backend/src/middleware/logging.rs (error_message, stack_trace, user_id, provider, activity_id)
- [ ] T151 [P] Setup alerting rules in infra/prometheus/alerts.yml (API p95 >200ms, sync job failures >10%, cache hit rate <80%)

### Documentation

- [ ] T152 [P] Generate OpenAPI documentation page in docs/api/openapi.html (from Swagger specs)
- [ ] T153 [P] Create architecture diagrams in docs/architecture/ (system overview, data flow, OAuth2 flow)
- [ ] T154 [P] Document deployment guide in docs/deployment/kubernetes.md (Kubernetes manifests, environment variables)
- [ ] T155 [P] Validate quickstart.md instructions in specs/001-platform-ingestion/quickstart.md (follow steps on fresh environment)

### Testing

- [ ] T156 [P] Add contract tests for all endpoints in backend/tests/contract/ (verify Swagger specs match implementations)
- [ ] T157 [P] Add E2E tests for critical user flows in frontend/tests/e2e/ (connect provider, upload file, view dashboard, export data)
- [ ] T158 [P] Verify test coverage ≥80% overall, ≥90% for core domain in .github/workflows/backend.yml (cargo-tarpaulin report)
- [ ] T159 [P] Add integration tests for ETL pipeline in etl/python/tests/ (raw → normalized data flow)

### Code Quality

- [ ] T160 [P] Code cleanup pass in backend/src/ (remove unused imports, dead code, TODO comments)
- [ ] T161 [P] Code cleanup pass in frontend/src/ (remove unused components, console.logs, commented code)
- [ ] T162 [P] Refactor duplicated logic in backend/src/providers/ (extract shared OAuth2 flow, token refresh)
- [ ] T163 [P] Refactor duplicated chart logic in frontend/src/components/charts/ (extract base chart component)

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
- OAuth2 foundation (T047-T048) before provider integrations (T049-T053)
- Provider integrations before endpoints (T054-T055)
- Repository layer (T047) before service layer (T048) before API layer (T054-T055)
- Backend endpoints before frontend UI (T057-T059)
- File parsers (T071-T075) before upload service (T076) before endpoint (T077)
- ETL infrastructure (T090-T091) before normalization job (T092)

**User Story 2 (Visualize Data)**:
- Dashboard service (T099) before list endpoint (T100)
- Backend endpoints before frontend components (T104-T112)
- Chart components (T108-T110) before export components (T118-T119)
- Export services (T113-T115) before export endpoint (T116)

**User Story 3 (Enrichment)**:
- Repository (T120) and API clients (T121-T122) before enrichment service (T123)
- Enrichment service before background job (T124)
- Backend enrichment before frontend display (T126-T129)

---

## Parallel Opportunities

### Setup Phase (Phase 1)
- All linting/static analysis tasks (T004-T006) can run in parallel
- All design token/test framework setup (T007-T011) can run in parallel
- All CI workflow creation (T016-T017) can run in parallel

### Foundational Phase (Phase 2)
- All migration files (T020-T027) can run in parallel after T018
- All model definitions (T029-T034) can run in parallel after migrations
- All infrastructure components (T036-T046) can run in parallel after database setup

### User Story 1
- All provider integrations (T049-T053) can run in parallel
- All file parsers (T071-T075) can run in parallel
- OAuth2 UI (T057-T059) can run in parallel with backend OAuth2 work
- File upload UI (T081-T082) can run in parallel with backend file upload work

### User Story 2
- All chart components (T108-T110) can run in parallel
- All export services (T113-T115) can run in parallel
- Filter components (T105-T107) can run in parallel

### User Story 3
- Weather and altitude API clients (T121-T122) can run in parallel
- Display components (T126-T129) can run in parallel

### Polish Phase
- All performance optimization tasks (T133-T137) can run in parallel
- All security tasks (T138-T142) can run in parallel
- All accessibility tasks (T143-T147) can run in parallel
- All observability tasks (T148-T151) can run in parallel
- All documentation tasks (T152-T155) can run in parallel
- All code cleanup tasks (T160-T163) can run in parallel

---

## Parallel Example: User Story 1

```bash
# All provider integrations together:
Task: T049 [P] [US1] Create Garmin provider integration
Task: T050 [P] [US1] Create Fitbit provider integration
Task: T051 [P] [US1] Create Strava provider integration
Task: T052 [P] [US1] Create Polar provider integration
Task: T053 [P] [US1] Create Apple Health provider integration

# All file parsers together:
Task: T071 [P] [US1] Create CSV parser
Task: T072 [P] [US1] Create JSON parser
Task: T073 [P] [US1] Create GPX parser
Task: T074 [P] [US1] Create TCX parser
Task: T075 [P] [US1] Create FIT parser
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T017)
2. Complete Phase 2: Foundational (T018-T046) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T047-T098)
4. **STOP and VALIDATE**: 
   - Connect Garmin account via OAuth2
   - Upload sample CSV file
   - Manually enter a workout
   - Verify all data appears in PostgreSQL activities table
5. Deploy/demo if ready - **Minimum Viable Product achieved!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (can deploy empty app)
2. Add User Story 1 → Test independently → Deploy/Demo (**MVP!** Users can import data)
3. Add User Story 2 → Test independently → Deploy/Demo (Users can visualize and export data)
4. Add User Story 3 → Test independently → Deploy/Demo (Data enriched with weather/altitude)
5. Polish Phase → Production-ready (performance, security, accessibility hardened)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (critical path, no parallelism)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (OAuth2, file upload, ETL)
   - **Developer B**: User Story 2 (dashboard, charts, export) - starts after some US1 data available
   - **Developer C**: User Story 3 (enrichment APIs, background jobs)
   - **Developer D**: Polish tasks (performance, security, accessibility)
3. Stories integrate seamlessly since they're independently designed

---

## Task Statistics

- **Total Tasks**: 163
- **Setup Phase**: 17 tasks
- **Foundational Phase**: 29 tasks
- **User Story 1 (P1 - MVP)**: 52 tasks
- **User Story 2 (P2)**: 21 tasks
- **User Story 3 (P3)**: 13 tasks
- **Polish Phase**: 31 tasks

### Tasks by Priority
- **P1 (MVP - US1)**: 52 tasks (critical for first deployment)
- **P2 (Visualization - US2)**: 21 tasks (adds value, can defer if needed)
- **P3 (Enrichment - US3)**: 13 tasks (nice-to-have, can defer)
- **Infrastructure/Polish**: 77 tasks (foundational + cross-cutting)

### Parallel Tasks
- **Marked [P]**: ~85 tasks can run in parallel with appropriate team capacity
- **Sequential**: ~78 tasks require ordering due to dependencies

---

## Notes

- All tasks include exact file paths for clarity
- [P] marker indicates parallelizable tasks (different files, no dependencies)
- [Story] label (US1, US2, US3) maps to user stories from spec.md
- Constitution alignment:
  - Code Quality: Clippy, ESLint, static analysis (T004-T006)
  - Testing: Contract, integration, E2E tests in Polish phase (T156-T159)
  - UX Consistency: Tailwind tokens, WCAG 2.1 AA compliance (T007, T143-T147)
  - Performance: Benchmarks, optimization, budgets (T011, T133-T137)
  - Observability: OpenTelemetry, Grafana, Prometheus (T039, T148-T151)
  - Security: Input validation, rate limiting, CORS, CSP (T138-T142)
  - Documentation: OpenAPI specs, architecture diagrams, deployment guides (T152-T155)
- OpenAPI/Swagger generation tasks ensure API contracts match implementations (per contract file instructions)
- Each user story has checkpoint for independent validation
- MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = ~98 tasks
- Tests are integrated into implementation (not separate phase) per Constitution TDD approach
- Commit frequently after logical task groups
- Stop at any checkpoint to validate story independently before proceeding
