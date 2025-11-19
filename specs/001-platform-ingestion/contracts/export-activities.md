# API Contract: Export Activities

**Feature**: 001-platform-ingestion  
**User Story**: US-002 (Visualize Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
GET /api/v1/activities/export
```

**Purpose**: Export user's fitness activities in CSV format or charts in PNG/PDF format.

---

## Request

### Headers
```
Authorization: Bearer <jwt_token>
```

### Query Parameters
```
?format=csv|png|pdf
&start=2024-01-01T00:00:00Z
&end=2024-01-31T23:59:59Z
&activity_type=running,cycling
&user_query=strong,morning
&csv_type=metadata|heartrate (required for csv)
&chart_type=line|bar (required for png/pdf)
&metric=heart_rate_avg|calories|distance_km (required for png/pdf)
```

**Required parameters:**
- `format`: Export format ("csv", "png", "pdf")
- `csv_type`: CSV format type ("metadata", "heartrate") - required for csv format

**Optional parameters:**
- `start`: ISO 8601 timestamp (default: 30 days ago)
- `end`: ISO 8601 timestamp (default: now)
- `activity_type`: Comma-separated list (default: all types)
- `user_query`: Search terms to match against notes and exercise metadata (comma-separated)
- `chart_type`: Chart type for visualizations ("line", "bar") - required for png/pdf
- `metric`: Metric to visualize - required for png/pdf

---

## Response

### Success (200 OK) - CSV Format (metadata type)

**Headers**:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="activities_metadata_2024-01-01_to_2024-01-31.csv"
```

**Body** (CSV stream):
```csv
date,activity_type,duration_minutes,distance_km,calories,heart_rate_avg,heart_rate_max,notes
2024-01-15 14:30:00,running,45,5.2,320,145,168,"Felt strong today!"
2024-01-16 08:00:00,cycling,60,15.0,450,130,155,"Easy ride"
```

### Success (200 OK) - CSV Format (heartrate type)

**Headers**:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="activities_heartrate_2024-01-01_to_2024-01-31.csv"
```

**Body** (CSV stream):
```csv
timestamp,hr,respiration
2024-01-15 14:30:00,145,18
2024-01-15 14:30:01,146,18
2024-01-15 14:30:02,147,18
2024-01-15 14:30:03,148,19
2024-01-15 14:30:04,149,19
```

**Note**: Heart rate CSV exports time-series data points from activities with heart rate monitoring. Each row represents a single measurement timestamp at 1-second intervals.

### Success (200 OK) - PNG Format

**Headers**:
```
Content-Type: image/png
Content-Disposition: attachment; filename="heart_rate_chart_2024-01-01_to_2024-01-31.png"
```

**Body**: Binary PNG image data (generated client-side via Plotly.js)

### Success (200 OK) - PDF Format

**Headers**:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="activities_report_2024-01-01_to_2024-01-31.pdf"
```

**Body**: Binary PDF document with embedded charts (generated client-side via jsPDF + Plotly.js)

### Error Responses

**400 Bad Request** - Invalid parameters
```json
{
  "error": "invalid_parameters",
  "message": "csv_type is required for csv exports. Valid values: metadata, heartrate"
}
```

**401 Unauthorized** - Missing or invalid JWT
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired JWT token"
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many export requests. Please try again in 60 seconds."
}
```

---

## Implementation Notes

### CSV Export (Server-Side)

#### Metadata CSV Type
- Query PostgreSQL `activities` table with filters
- If `user_query` provided, match against `notes` field and parsed exercise data (ILIKE search)
- Stream rows as CSV (avoid loading all data in memory)
- Columns: date, activity_type, duration_minutes, distance_km, calories, heart_rate_avg, heart_rate_max, notes
- Date format: YYYY-MM-DD HH:MM:SS (ISO 8601)
- Handle NULL values: empty string

#### Heart Rate CSV Type
- Query PostgreSQL `activities` table with filters, join with time-series heart rate data
- If `user_query` provided, match against parent activity notes and metadata
- Extract heart rate measurements from `metrics` JSONB field or separate heart rate data table
- Stream time-series data points as CSV at 1-second intervals
- Columns: timestamp, hr (heart rate in bpm), respiration (breaths per minute)
- One row per second of activity data
- Date format: YYYY-MM-DD HH:MM:SS (ISO 8601, per-second precision)
- Handle missing respiration data: empty string

#### User Query Matching
- Parse `user_query` parameter (comma-separated terms)
- Apply full-text search against:
  - `activities.notes` field
  - `workouts.notes` field
  - `parsed_notes` JSONB data (exercise names, intensity)
  - `activity_type` field
- Use PostgreSQL `ILIKE` or `ts_vector` for text search
- Combine multiple terms with OR logic (match any term)

### PNG Export (Client-Side)
- Frontend fetches activity data via `GET /api/v1/activities`
- Renders chart using Plotly.js
- Calls `Plotly.downloadImage('chart-div', {format: 'png', width: 1200, height: 800})`
- Downloads PNG file directly to user's device

### PDF Export (Client-Side)
- Frontend fetches activity data via `GET /api/v1/activities`
- Renders chart using Plotly.js
- Converts chart to SVG via `Plotly.toImage('chart-div', {format: 'svg'})`
- Embeds SVG in jsPDF document with title/metadata
- Downloads PDF file directly to user's device

### API Documentation
- **API Documentation**: Generate OpenAPI/Swagger specification for this endpoint. Ensure the implementation matches the Swagger schema exactly (request/response types, validation rules, error codes).

---

## Performance Budget

- **CSV Export (metadata)**: p95 < 2s for 1000 activities, p99 < 5s for 10,000 activities
- **CSV Export (heartrate)**: p95 < 3s for 1000 data points, p99 < 8s for 100,000 data points (time-series data)
- **PNG Export**: Client-side, no backend latency
- **PDF Export**: Client-side, no backend latency

---

## Testing

### Unit Tests
- CSV formatting (date, NULL handling, delimiter escaping)
- Date range validation
- User query parsing (comma-separated terms)
- CSV type validation (metadata vs heartrate)

### Contract Tests
- GET format=csv&csv_type=metadata → 200 OK with metadata CSV
- GET format=csv&csv_type=heartrate → 200 OK with heartrate CSV
- GET format=csv without csv_type → 400 Bad Request
- GET format=png without chart_type → 400 Bad Request
- GET without auth header → 401 Unauthorized
- GET with user_query → 200 OK with filtered results

### Integration Tests
- CSV metadata export with 10,000 activities (streaming performance)
- CSV heartrate export with 100,000 data points (verify time-series extraction)
- User query matching against notes and exercise data (verify text search)
- PNG export with complex chart (verify rendering)
- PDF export with multiple charts (verify layout)

### Performance Tests
- Load test with 100 concurrent CSV exports
- Verify p95 < 2s for 1000 activities (metadata)
- Verify p95 < 3s for 1000 data points (heartrate)
- User query performance with large dataset (verify index usage)
