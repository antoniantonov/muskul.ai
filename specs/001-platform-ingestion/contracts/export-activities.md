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
&include_duplicates=false
&chart_type=line|bar (required for png/pdf)
&metric=heart_rate_avg|calories|distance_km (required for png/pdf)
```

**Required parameters:**
- `format`: Export format ("csv", "png", "pdf")

**Optional parameters:**
- `start`: ISO 8601 timestamp (default: 30 days ago)
- `end`: ISO 8601 timestamp (default: now)
- `activity_type`: Comma-separated list (default: all types)
- `include_duplicates`: Include duplicate activities (default: false)
- `chart_type`: Chart type for visualizations ("line", "bar") - required for png/pdf
- `metric`: Metric to visualize - required for png/pdf

---

## Response

### Success (200 OK) - CSV Format

**Headers**:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="activities_2024-01-01_to_2024-01-31.csv"
```

**Body** (CSV stream):
```csv
date,activity_type,duration_minutes,distance_km,calories,heart_rate_avg,heart_rate_max,notes
2024-01-15 14:30:00,running,45,5.2,320,145,168,"Felt strong today!"
2024-01-16 08:00:00,cycling,60,15.0,450,130,155,"Easy ride"
```

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
  "message": "chart_type and metric are required for png/pdf exports"
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
- Query PostgreSQL `activities` table with filters
- Stream rows as CSV (avoid loading all data in memory)
- Columns: date, activity_type, duration_minutes, distance_km, calories, heart_rate_avg, heart_rate_max, notes
- Date format: YYYY-MM-DD HH:MM:SS (ISO 8601)
- Handle NULL values: empty string

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

---

## Performance Budget

- **CSV Export**: p95 < 2s for 1000 activities, p99 < 5s for 10,000 activities
- **PNG Export**: Client-side, no backend latency
- **PDF Export**: Client-side, no backend latency

---

## Testing

### Unit Tests
- CSV formatting (date, NULL handling)
- Date range validation

### Contract Tests
- GET format=csv → 200 OK with CSV data
- GET format=png without chart_type → 400 Bad Request
- GET without auth header → 401 Unauthorized

### Integration Tests
- CSV export with 10,000 activities (streaming performance)
- PNG export with complex chart (verify rendering)
- PDF export with multiple charts (verify layout)

### Performance Tests
- Load test with 100 concurrent CSV exports
- Verify p95 < 2s for 1000 activities
