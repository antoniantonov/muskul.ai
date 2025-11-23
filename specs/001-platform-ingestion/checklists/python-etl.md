# Python ETL Quality Checklist

**Agent**: `@python` | **Scope**: `etl/python/`, `ai-agent-service/`

This checklist ensures all Python ETL and data processing code meets production-grade quality standards before marking tasks complete.

---

## Code Quality

- [ ] **Formatting**: All code passes `black --check .` with no changes needed
- [ ] **Linting**: All code passes `ruff check .` with zero errors/warnings
- [ ] **Type Checking**: All code passes `mypy --strict .` with no type errors
- [ ] **Type Hints**: All functions have type hints for parameters and return values
- [ ] **Docstrings**: All public functions/classes have docstrings (Google style)
- [ ] **Import Order**: Imports organized (standard library → third-party → local)
- [ ] **No Dead Code**: No commented-out code, unused imports, or unused variables
- [ ] **Function Length**: Functions ≤50 lines (prefer smaller, single-purpose functions)

---

## Testing

- [ ] **Unit Tests**: All functions have unit tests in `tests/` directory
- [ ] **Test Framework**: Tests use `pytest` with fixtures and parametrize
- [ ] **Coverage - Overall**: ≥80% code coverage via `pytest --cov`
- [ ] **Coverage - Critical Logic**: ≥90% coverage for data transformations, validation, parsing
- [ ] **Property-Based Tests**: Use `Hypothesis` for testing data transformation edge cases
- [ ] **Test Data**: Test fixtures use realistic sample data (CSV, JSON, API responses)
- [ ] **Test Isolation**: Each test is independent, uses fixtures or mocks for external dependencies
- [ ] **Mock External APIs**: Use `pytest-mock` or `unittest.mock` for external API calls

---

## Data Quality

- [ ] **Pydantic Validation**: All data models use Pydantic with field validation
- [ ] **Schema Validation**: Input data validated against Pydantic schemas before processing
- [ ] **Error Handling**: Invalid records logged with details, not silently dropped
- [ ] **Data Quality Metrics**: Track valid record rate (≥98% target)
- [ ] **Outlier Detection**: Implement outlier detection for numeric fields (z-score, IQR)
- [ ] **Duplicate Detection**: Deduplication logic with clear rules (by activity ID, timestamp, provider)
- [ ] **Missing Value Handling**: Strategy for missing values (skip, default, interpolate) - documented
- [ ] **Data Lineage**: Track data source and transformation steps in metadata

---

## Performance

- [ ] **Throughput**: ≥5,000 records/sec processing speed (benchmarked with realistic data)
- [ ] **Batch Processing**: Large datasets processed in batches (chunk size 1000-10000)
- [ ] **Vectorized Operations**: Use pandas vectorized operations (avoid row-by-row iteration)
- [ ] **Memory Efficiency**: Process data in chunks for large files (avoid loading entire file into memory)
- [ ] **Async I/O**: Use `asyncio` for I/O-bound operations (API calls, file reads)
- [ ] **Database Bulk Inserts**: Use bulk insert operations (not row-by-row inserts)
- [ ] **Performance Benchmarks**: ETL pipelines benchmarked with realistic data volumes
- [ ] **Pipeline Latency**: <10s processing time for 50K records

---

## ETL Architecture

- [ ] **Modular Pipeline**: ETL stages separated (Extract, Transform, Load) into distinct functions
- [ ] **Configurable**: Pipeline parameters configurable via environment variables or config files
- [ ] **Idempotent**: Pipeline can be re-run without duplicate data (use upserts, check for existing records)
- [ ] **Error Recovery**: Failed batches logged and can be retried independently
- [ ] **Progress Tracking**: Pipeline logs progress (records processed, errors, time elapsed)
- [ ] **Checkpointing**: Long-running jobs save checkpoints for restart after failure
- [ ] **Dry Run Mode**: Pipeline supports dry-run mode for testing without writing to database

---

## Data Transformation

- [ ] **Schema Mapping**: Provider schema → normalized schema mapping documented
- [ ] **Unit Conversion**: Units converted to standard (meters, seconds, kg) with validation
- [ ] **Timezone Handling**: All timestamps converted to UTC with timezone info preserved
- [ ] **Enum Mapping**: Provider-specific enums mapped to normalized enums (documented)
- [ ] **Null Handling**: Strategy for null/missing values documented and tested
- [ ] **Data Type Coercion**: Safe type coercion with error handling (str → int, str → datetime)
- [ ] **Calculated Fields**: Derived fields calculated consistently (pace, heart rate zones)

---

## Observability

- [ ] **Structured Logging**: Use `structlog` or `logging` with JSON formatter
- [ ] **Log Levels**: Appropriate log levels (DEBUG for details, INFO for progress, ERROR for failures)
- [ ] **Log Context**: Logs include `job_id`, `pipeline_name`, `record_count`, `error_count`, `duration_ms`
- [ ] **OpenTelemetry Tracing**: Critical ETL stages instrumented with spans
- [ ] **Metrics**: Track metrics (records processed, errors, duration) - export to Prometheus if applicable
- [ ] **Error Tracking**: Failed records logged with full context (input data, error message, stack trace)
- [ ] **No Sensitive Data in Logs**: PII, tokens redacted from logs

---

## AI/ML Integration (if applicable)

- [ ] **Model Versioning**: ML models versioned (track model version in predictions)
- [ ] **Input Validation**: Model inputs validated (shape, data types, ranges)
- [ ] **Prediction Confidence**: Model predictions include confidence scores
- [ ] **Fallback Logic**: Fallback to rule-based logic if model prediction confidence is low
- [ ] **Model Monitoring**: Track model accuracy, drift over time
- [ ] **Batch Predictions**: Use batch predictions for efficiency (not one-by-one)

---

## Deployment

- [ ] **Requirements.txt**: All dependencies pinned with exact versions
- [ ] **Dockerfile**: ETL jobs containerized with multi-stage build
- [ ] **Environment Variables**: All config loaded from environment (no hardcoded values)
- [ ] **Entry Point**: Clear entry point script (e.g., `python -m etl.jobs.normalize_activities`)
- [ ] **Graceful Shutdown**: Jobs handle SIGTERM for graceful shutdown (cleanup, save state)
- [ ] **Resource Limits**: Docker/Kubernetes manifests specify CPU/memory limits
- [ ] **Cron Schedule**: Scheduled jobs have clear cron expressions documented

---

## Task Completion Validation

Before marking a Python ETL task as `[X]` complete:

1. ✅ Run `black . && ruff check .` - all pass
2. ✅ Run `mypy --strict .` - no type errors
3. ✅ Run `pytest --cov` - all tests pass, coverage thresholds met (≥80% overall)
4. ✅ Run ETL pipeline with sample data - verify data quality (≥98% valid records)
5. ✅ Benchmark performance - verify throughput (≥5,000 records/sec)
6. ✅ Check logs - structured, no sensitive data, appropriate levels
7. ✅ Verify all checklist items above are complete for the specific task

---

**Agent Reference**: `.github/agents/python.agent.md`  
**Last Updated**: 2025-11-23
