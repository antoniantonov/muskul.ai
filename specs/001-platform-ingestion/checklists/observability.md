# Observability Quality Checklist

**Agent**: `@ot` | **Scope**: `**/telemetry.*`, `dashboards/*.json`, `alerts.yml`, `prometheus.yml`

This checklist ensures all observability instrumentation, metrics, dashboards, and alerting meet production-grade quality standards before marking tasks complete.

---

## Distributed Tracing

- [ ] **OpenTelemetry SDK**: All services instrumented with OpenTelemetry SDK
- [ ] **Trace Context Propagation**: Trace context propagated across service boundaries (HTTP headers, message queues)
- [ ] **Span Naming**: Spans follow naming convention (e.g., `GET /api/v1/activities`, `db.query.select_activities`)
- [ ] **Span Attributes**: Spans include relevant attributes (user_id, activity_id, provider, http.method, http.status_code)
- [ ] **Critical Paths Instrumented**: All critical paths have spans (OAuth2, data ingestion, dashboard queries, exports)
- [ ] **Error Spans**: Failed operations mark spans with error status and error message
- [ ] **Span Hierarchy**: Parent-child span relationships correctly established
- [ ] **Sampling Strategy**: Sampling configured (100% for errors, 10% for successful requests in production)

---

## Metrics (Prometheus)

- [ ] **RED Metrics**: Rate, Errors, Duration metrics exported for all endpoints
  - `http_requests_total{method, endpoint, status}` (counter)
  - `http_request_duration_seconds{method, endpoint}` (histogram)
  - `http_request_errors_total{method, endpoint, error_type}` (counter)
- [ ] **USE Metrics**: Utilization, Saturation, Errors metrics for resources
  - `cpu_usage_percent` (gauge)
  - `memory_usage_bytes` (gauge)
  - `database_connection_pool_active` (gauge)
  - `database_connection_pool_idle` (gauge)
- [ ] **Business Metrics**: Domain-specific metrics exposed
  - `activities_imported_total{provider, source}` (counter)
  - `oauth_connections_total{provider, status}` (counter)
  - `dashboard_renders_total{view_type}` (counter)
  - `exports_generated_total{format}` (counter)
- [ ] **Metric Naming**: Follow Prometheus naming conventions (snake_case, suffix with unit)
- [ ] **Metric Labels**: Labels have low cardinality (avoid user_id, activity_id as labels)
- [ ] **Histogram Buckets**: Histograms use appropriate buckets (0.01, 0.05, 0.1, 0.5, 1, 5, 10 seconds)
- [ ] **Prometheus Endpoint**: `/metrics` endpoint exposed for scraping

---

## Structured Logging

- [ ] **JSON Format**: All logs output in JSON format for machine parsing
- [ ] **Log Levels**: Appropriate log levels used (DEBUG, INFO, WARN, ERROR, CRITICAL)
- [ ] **Log Context**: Logs include structured fields:
  - `timestamp` (ISO 8601)
  - `level` (DEBUG, INFO, WARN, ERROR)
  - `trace_id`, `span_id` (OpenTelemetry context)
  - `user_id`, `request_id` (request context)
  - `service_name`, `version` (service metadata)
  - `message` (human-readable message)
- [ ] **Correlation IDs**: All logs within a request have same `trace_id`
- [ ] **Error Logs**: Error logs include `error_message`, `error_type`, `stack_trace`
- [ ] **No Sensitive Data**: PII, passwords, tokens redacted from logs
- [ ] **Log Aggregation**: Logs forwarded to centralized logging (Azure Log Analytics, Grafana Loki)
- [ ] **Log Retention**: Retention policy configured (30 days for INFO, 90 days for ERROR)

---

## Grafana Dashboards

- [ ] **Platform Overview Dashboard**: Single dashboard for platform health
  - Request rate, error rate, latency (p50, p95, p99)
  - Active users, database connections, memory usage
  - Recent errors, slow queries
- [ ] **SLO Tracking Dashboard**: Dashboard for SLI/SLO monitoring
  - Availability (99.9% target)
  - Latency p95 (200ms reads, 500ms writes targets)
  - Error rate (<0.1% target)
  - SLO burn rate, error budget remaining
- [ ] **Service-Specific Dashboards**: Dashboards per service (backend, frontend, ETL, AI agent)
  - Service-specific metrics (OAuth2 flow success rate, ETL throughput, AI parsing latency)
  - Dependency health (database, external APIs)
- [ ] **Dashboard Organization**: Dashboards organized in folders (Platform, Services, Business Metrics)
- [ ] **Panel Titles**: Clear, descriptive panel titles (not "Graph 1", "Panel 2")
- [ ] **Units**: Y-axis units specified (seconds, bytes, requests/sec)
- [ ] **Thresholds**: Visual thresholds for SLO targets (green/yellow/red)
- [ ] **Time Range**: Appropriate default time range (last 1 hour, with quick selectors)
- [ ] **Refresh Rate**: Auto-refresh configured (30s or 1m)
- [ ] **PromQL Optimization**: Queries optimized (use recording rules for complex queries)

---

## Alerting (Prometheus Alertmanager)

- [ ] **SLO Violation Alerts**: Alerts for SLO breaches
  - `HighErrorRate`: Error rate >0.1% for 5 minutes
  - `HighLatency`: p95 latency >200ms (reads) or >500ms (writes) for 5 minutes
  - `LowAvailability`: Availability <99.9% over 5-minute window
- [ ] **Saturation Alerts**: Alerts for resource saturation
  - `HighCPUUsage`: CPU >80% for 10 minutes
  - `HighMemoryUsage`: Memory >90% for 5 minutes
  - `DatabaseConnectionPoolExhaustion`: Active connections >95% of pool size
- [ ] **Dependency Alerts**: Alerts for dependency failures
  - `DatabaseDown`: Database unreachable for 1 minute
  - `ExternalAPIDown`: Provider API failing >50% requests for 5 minutes
- [ ] **Alert Severity**: Alerts labeled with severity (critical, warning, info)
- [ ] **Alert Annotations**: Alerts include annotations (summary, description, runbook URL)
- [ ] **Alert Routing**: Alerts routed to appropriate channels (PagerDuty for critical, Slack for warnings)
- [ ] **Alert Deduplication**: Alerts deduplicated (no duplicate alerts for same issue)
- [ ] **Alert Silencing**: Silencing rules for maintenance windows
- [ ] **Runbooks**: Runbook links in alerts (how to investigate, troubleshoot, resolve)

---

## Health Checks

- [ ] **Liveness Probe**: `/health` endpoint for Kubernetes liveness probe
  - Returns 200 OK if service is running
  - No external dependency checks (fast response <100ms)
- [ ] **Readiness Probe**: `/ready` endpoint for Kubernetes readiness probe
  - Checks PostgreSQL connectivity (simple SELECT 1)
  - Checks MongoDB connectivity (simple ping)
  - Checks Valkey connectivity (simple PING)
  - Returns 200 OK if all dependencies healthy, 503 Service Unavailable otherwise
- [ ] **Health Check Timeout**: Health checks timeout quickly (1-2s)
- [ ] **Health Check Caching**: Readiness check results cached (5-10s TTL) to avoid overwhelming dependencies
- [ ] **Startup Probe**: (If applicable) `/startup` endpoint for slow-starting services

---

## Error Tracking & Debugging

- [ ] **Error Budget**: Error budget calculated and tracked (0.1% error rate = 99.9% availability)
- [ ] **Error Grouping**: Errors grouped by type, endpoint, service
- [ ] **Error Context**: Errors include full context (request body, headers, stack trace, user actions)
- [ ] **Error Trends**: Error trends visualized (spike detection, error rate over time)
- [ ] **Slow Query Logging**: Database slow queries logged (queries >100ms)
- [ ] **Trace Sampling**: Failed requests always sampled (100% of errors captured)
- [ ] **Distributed Trace Visualization**: Traces visualized in Jaeger or Grafana Tempo

---

## SLI/SLO Definition

- [ ] **SLI Definition**: Service Level Indicators defined and measured
  - **Availability**: % of successful requests (non-5xx responses / total requests)
  - **Latency**: p95 request latency (separate for reads/writes)
  - **Error Rate**: % of failed requests (5xx responses / total requests)
- [ ] **SLO Targets**: Service Level Objectives defined
  - **Availability SLO**: 99.9% (43 minutes downtime/month)
  - **Latency SLO**: p95 <200ms (reads), p95 <500ms (writes)
  - **Error Rate SLO**: <0.1%
- [ ] **SLO Windows**: SLO calculated over rolling windows (1 hour, 1 day, 30 days)
- [ ] **Error Budget**: Error budget tracked (1 - SLO = 0.1% error budget)
- [ ] **Burn Rate**: Burn rate alerts configured (alert if burning error budget too fast)

---

## Task Completion Validation

Before marking an observability task as `[X]` complete:

1. ✅ Verify tracing spans - all critical paths instrumented, spans include attributes
2. ✅ Check metrics export - `/metrics` endpoint returns Prometheus metrics, RED metrics present
3. ✅ Verify logs - structured JSON logs with trace_id, no sensitive data
4. ✅ Dashboard deployed - Grafana dashboard created, PromQL queries optimized
5. ✅ Alerts configured - Alertmanager rules created, runbook links included
6. ✅ Health checks working - `/health` and `/ready` endpoints return correct status
7. ✅ SLO tracking - SLI metrics collected, SLO targets defined, error budget calculated
8. ✅ Verify all checklist items above are complete for the specific task

---

**Agent Reference**: `.github/agents/ot.agent.md`  
**Last Updated**: 2025-11-23
