# Database Quality Checklist

**Agents**: `@pg` (PostgreSQL), `@mongo` (MongoDB) | **Scope**: `backend/migrations/`, `migrations/`

This checklist ensures all database schema design, migrations, and queries meet production-grade quality standards before marking tasks complete.

---

## PostgreSQL - Schema Design

- [ ] **3NF Normalization**: Schema normalized to 3rd Normal Form (no transitive dependencies)
- [ ] **Proper Data Types**: Use specific types (TIMESTAMPTZ not TIMESTAMP, UUID not TEXT, NUMERIC for money)
- [ ] **Constraints - NOT NULL**: All required fields have NOT NULL constraint
- [ ] **Constraints - UNIQUE**: Unique constraints on natural keys (email, external_id)
- [ ] **Constraints - CHECK**: CHECK constraints for valid ranges/enums (e.g., age > 0, status IN ('active', 'inactive'))
- [ ] **Foreign Keys**: All relationships enforced with FOREIGN KEY constraints (with ON DELETE/ON UPDATE)
- [ ] **Primary Keys**: All tables have primary key (prefer UUID or BIGSERIAL)
- [ ] **Default Values**: Sensible defaults (timestamps DEFAULT NOW(), booleans DEFAULT FALSE)

---

## PostgreSQL - Indexing

- [ ] **Primary Key Index**: Automatic B-tree index on primary key
- [ ] **Foreign Key Indexes**: Indexes on foreign key columns for JOIN performance
- [ ] **Covering Indexes**: Indexes include all columns needed for frequent queries (avoid table lookups)
- [ ] **Partial Indexes**: Use partial indexes for filtered queries (e.g., WHERE deleted_at IS NULL)
- [ ] **Composite Indexes**: Multi-column indexes ordered by selectivity (most selective first)
- [ ] **GIN Indexes**: Use GIN indexes for JSONB, arrays, full-text search
- [ ] **GiST Indexes**: Use GiST indexes for range queries, geospatial data
- [ ] **Index Bloat**: Monitor index bloat, plan for REINDEX if needed

---

## PostgreSQL - Query Optimization

- [ ] **EXPLAIN ANALYZE**: All queries analyzed with EXPLAIN ANALYZE (check for seq scans on large tables)
- [ ] **Index Usage**: Queries use indexes (no seq scan on tables >10K rows)
- [ ] **Query Latency**: Query p95 latency <50ms (measure with EXPLAIN ANALYZE or pgBench)
- [ ] **Prepared Statements**: All queries use parameterized/prepared statements (SQLx in Rust)
- [ ] **Batch Operations**: Use batch inserts/updates (not row-by-row in loops)
- [ ] **CTEs vs Subqueries**: Use CTEs for readability, subqueries for performance (test both)
- [ ] **JOIN Strategy**: Appropriate JOIN types (INNER, LEFT, use EXISTS for semi-joins)
- [ ] **N+1 Prevention**: No N+1 query patterns (use JOINs or batch queries)

---

## PostgreSQL - Performance & Scalability

- [ ] **Connection Pooling**: Application uses connection pool (5-20 connections, configured in SQLx)
- [ ] **Connection Timeouts**: Query timeout configured (10s default)
- [ ] **Transaction Isolation**: Appropriate isolation level (READ COMMITTED default, SERIALIZABLE if needed)
- [ ] **Savepoints**: Use savepoints for partial rollback in complex transactions
- [ ] **Vacuum Strategy**: Tables with high churn have autovacuum configured
- [ ] **Partitioning**: Large tables (>100M rows) partitioned by date or ID range
- [ ] **Materialized Views**: Use materialized views for complex aggregations, refresh strategy defined

---

## PostgreSQL - Migrations

- [ ] **Reversible Migrations**: All migrations have UP and DOWN scripts
- [ ] **Idempotent**: Migrations can be re-run safely (use IF NOT EXISTS, IF EXISTS)
- [ ] **Zero-Downtime**: Migrations allow zero-downtime deployment (no exclusive locks on large tables)
- [ ] **Data Migrations**: Data migrations separated from schema migrations, tested thoroughly
- [ ] **Migration Testing**: Migrations tested on production-like dataset (size, constraints)
- [ ] **Rollback Plan**: Rollback procedure documented for failed migrations
- [ ] **Version Control**: Migrations numbered sequentially, tracked in version control

---

## MongoDB - Document Design

- [ ] **Embedding vs Referencing**: Appropriate strategy chosen (embed for 1:1, reference for 1:many, many:many)
- [ ] **Document Size**: Documents <16MB (MongoDB limit), typically <1MB for performance
- [ ] **Denormalization**: Intentional denormalization for read performance (document trade-offs)
- [ ] **Array Size**: Arrays bounded (avoid unbounded arrays that grow indefinitely)
- [ ] **Schema Validation**: JSON schema validation rules defined for collections
- [ ] **Field Naming**: Consistent field naming (snake_case or camelCase, not mixed)
- [ ] **Time-Series Collections**: Use time-series collections for time-stamped data (MongoDB 5.0+)

---

## MongoDB - Indexing

- [ ] **Single-Field Indexes**: Indexes on frequently queried fields
- [ ] **Compound Indexes**: Multi-field indexes following ESR rule (Equality, Sort, Range)
- [ ] **Unique Indexes**: Unique constraints on natural keys (external_id, user_id + timestamp)
- [ ] **Partial Indexes**: Use partial indexes for filtered queries (e.g., { status: 'active' })
- [ ] **Text Indexes**: Use text indexes for full-text search on string fields
- [ ] **Geospatial Indexes**: Use 2dsphere indexes for geospatial queries
- [ ] **Index Selectivity**: Indexes on high-cardinality fields (avoid indexing boolean fields alone)
- [ ] **Index Intersection**: MongoDB can use multiple indexes per query (avoid over-indexing)

---

## MongoDB - Query Optimization

- [ ] **EXPLAIN Analysis**: All queries analyzed with `.explain("executionStats")`
- [ ] **Index Usage**: Queries use indexes (no COLLSCAN on large collections)
- [ ] **Query Latency**: Query p95 latency <50ms (measure with explain() or profiler)
- [ ] **Projection**: Use projections to return only needed fields (avoid fetching entire documents)
- [ ] **Aggregation Pipeline**: Pipelines optimized ($match early, $limit after $sort)
- [ ] **Covered Queries**: Use covered queries (all fields in projection are in index)
- [ ] **Batch Size**: Configure batch size for cursors (default 101, adjust for large docs)

---

## MongoDB - Time-Series Optimization

- [ ] **Time-Series Collection**: Use time-series collection for activity metrics, sensor data
- [ ] **Granularity**: Appropriate granularity (seconds, minutes, hours) based on query patterns
- [ ] **Bucketing**: Time-series bucketing configured for efficient storage and queries
- [ ] **Expiration**: TTL index configured for data retention policy (e.g., delete after 2 years)
- [ ] **Metadata Indexing**: Metadata fields indexed for filtering (user_id, activity_type)
- [ ] **Aggregation**: Time-series aggregations use `$dateTrunc`, `$bucket` for grouping

---

## MongoDB - Performance & Scalability

- [ ] **Connection Pooling**: Application uses connection pool (10-100 connections)
- [ ] **Connection Timeouts**: Query timeout configured (10s default)
- [ ] **Read Preference**: Appropriate read preference (primary for consistency, secondary for analytics)
- [ ] **Write Concern**: Appropriate write concern (majority for durability, 1 for performance)
- [ ] **Sharding Strategy**: Large collections (>100GB) have sharding strategy defined (shard key chosen)
- [ ] **Replica Set**: Production uses replica set (1 primary + 2 secondaries minimum)
- [ ] **Oplog Size**: Oplog sized appropriately (hours of operation coverage)

---

## MongoDB - Schema Validation

- [ ] **Validation Rules**: Collections have JSON schema validation rules defined
- [ ] **Validation Action**: Validation action configured (error or warn)
- [ ] **Required Fields**: Required fields enforced in validation schema
- [ ] **Data Types**: Field types enforced (string, number, date, array, object)
- [ ] **Enum Validation**: Enum fields validated (e.g., status: ['active', 'inactive', 'deleted'])
- [ ] **Range Validation**: Numeric fields validated for valid ranges (e.g., age: { min: 0, max: 150 })

---

## Connection Management (Both DBs)

- [ ] **Connection Pool Size**: PostgreSQL (5-20), MongoDB (10-100) - tuned for workload
- [ ] **Connection Timeout**: Timeout configured (10s query timeout, 30s connection timeout)
- [ ] **Retry Logic**: Failed queries retry with exponential backoff (3 attempts max)
- [ ] **Health Checks**: Application health check verifies database connectivity
- [ ] **Connection Leaks**: No connection leaks (connections returned to pool, use `defer` in Go, RAII in Rust)
- [ ] **Graceful Degradation**: Application handles database unavailability gracefully (circuit breaker pattern)

---

## Task Completion Validation

Before marking a database task as `[X]` complete:

### PostgreSQL
1. ✅ Run `sqlx migrate run` - migration applies successfully
2. ✅ Run `EXPLAIN ANALYZE` on queries - indexes used, latency <50ms
3. ✅ Check constraints - FOREIGN KEY, NOT NULL, UNIQUE, CHECK all enforced
4. ✅ Verify indexes - covering indexes, no seq scans on large tables
5. ✅ Test rollback - DOWN migration works correctly

### MongoDB
1. ✅ Run migration script - collection/indexes created successfully
2. ✅ Run `.explain("executionStats")` - indexes used, latency <50ms
3. ✅ Verify schema validation - rules enforced, required fields checked
4. ✅ Check indexes - ESR rule followed, compound indexes optimized
5. ✅ Test time-series collection - bucketing, TTL, metadata indexes configured

### Both
6. ✅ Verify all checklist items above are complete for the specific task

---

**Agent References**: `.github/agents/pg.agent.md`, `.github/agents/mongo.agent.md`  
**Last Updated**: 2025-11-23
