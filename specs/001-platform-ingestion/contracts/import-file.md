# API Contract: Import Activity (File Upload)

**Feature**: 001-platform-ingestion  
**User Story**: US-001 (Import Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
POST /api/v1/activities/import/file
```

**Purpose**: Import fitness activity from uploaded file (CSV, JSON, XML, GPX, TCX, FIT).

---

## Request

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

### Body (multipart/form-data)
```
file: <binary file data>
provider: "garmin" | "polar" | "generic"
```

### Validation Rules
- `file`: Required, max size 10MB, allowed extensions: .csv, .json, .xml, .gpx, .tcx, .fit
- `provider`: Optional (default: "generic"), helps with format detection

---

## Response

### Success (202 Accepted)
```json
{
  "importId": "z9y8x7w6-...",
  "status": "processing",
  "message": "File upload successful. Processing activities...",
  "estimatedTimeSeconds": 30
}
```

**Description**: File accepted for processing. Use `/activities/import/{importId}/status` to check progress.

### Success (201 Created) - Immediate Processing
```json
{
  "importId": "z9y8x7w6-...",
  "status": "completed",
  "activitiesImported": 12,
  "activitiesFailed": 1,
  "errors": [
    {
      "row": 5,
      "reason": "Invalid date format for start_time"
    }
  ],
  "activities": [
    {ß
      "id": "a1b2c3d4-...",
      "activityType": "running",
      "startTime": "2024-01-15T14:30:00Z",
      "durationSeconds": 2700
    }
  ]
}
```

### Error Responses

**400 Bad Request** - Invalid file format or missing file
```json
{
  "error": "invalid_file_format",
  "message": "File format not supported. Supported formats: CSV, JSON, XML, GPX, TCX, FIT"
}
```

**413 Payload Too Large** - File size exceeds limit
```json
{
  "error": "file_too_large",
  "message": "File size exceeds 10MB limit"
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
  "message": "Too many file uploads. Please try again in 60 seconds."
}
```

---

## Implementation Notes

- File uploaded to temporary storage (local disk or S3 or Storage Account if deployed to Azure)
- Async processing: Parse file → Validate → Normalize → Store in MongoDB (raw) → ETL to PostgreSQL
- For async processing, return 202 Accepted with `importId`. Use `importId` to keep track of the processing status in separate table in PG.
- Supports batch import (multiple activities per file)
- Duplicate detection: Check hash of (provider + external_id + start_time)
- Failed activities logged with reason (validation errors, parsing errors). This also needs to be updated in the import status tracking table in PG.
- Import job timeout: 5 minutes
- Monitoring and logging - log metrics, traces and logs to OpenTelemetry format. Scrape the logs, metrics, traces with Prometheus and visualize in Grafana.
- **API Documentation**: Generate OpenAPI/Swagger specification for this endpoint. Ensure the implementation matches the Swagger schema exactly (request/response types, validation rules, error codes).

---

## File Format Examples

### CSV Format (Metadata)
```csv
date,activity_type,duration_minutes,distance_km,calories,heart_rate_avg,notes
2024-01-15 14:30:00,running,45,5.2,320,145,"Felt strong"
2024-01-16 08:00:00,cycling,60,15.0,450,130,"Easy ride"
```

### CSV Format (Heart Rate Time-Series)
```csv
timestamp,hr,respiration
2024-01-15 14:30:00,145,18
2024-01-15 14:30:01,146,18
2024-01-15 14:30:02,147,18
2024-01-15 14:30:03,148,19
2024-01-15 14:30:04,149,19
```

**Note**: Heart rate CSV imports time-series data at 1-second intervals. Each row represents a measurement timestamp with heart rate (bpm) and respiration rate (breaths per minute).

### JSON Format
```json
{
  "activities": [
    {
      "start_time": "2024-01-15T14:30:00Z",
      "end_time": "2024-01-15T15:15:00Z",
      "activity_type": "running",
      "metrics": {
        "distance_km": 5.2,
        "heart_rate_avg": 145,
        "calories": 320
      }
    }
  ]
}
```

### GPX Format (GPS Track)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1">
  <trk>
    <name>Morning Run</name>
    <trkseg>
      <trkpt lat="37.7749" lon="-122.4194">
        <ele>10</ele>
        <time>2024-01-15T14:30:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
```

---

## Endpoint: Check Import Status

```
GET /api/v1/activities/import/{importId}/status
```

**Purpose**: Check the processing status of an uploaded file import.

---

## Request

### Headers
```
Authorization: Bearer <jwt_token>
```

### Path Parameters
```
importId: UUID of the import job
```

---

## Response

### Success (200 OK) - Processing
```json
{
  "importId": "z9y8x7w6-...",
  "status": "processing",
  "startedAt": "2024-01-15T16:00:00Z",
  "progress": {
    "totalRows": 150,
    "processedRows": 75,
    "percentage": 50
  },
  "estimatedTimeRemainingSeconds": 15
}
```

### Success (200 OK) - Completed
```json
{
  "importId": "z9y8x7w6-...",
  "status": "completed",
  "startedAt": "2024-01-15T16:00:00Z",
  "completedAt": "2024-01-15T16:02:15Z",
  "activitiesImported": 12,
  "activitiesFailed": 1,
  "errors": [
    {
      "row": 5,
      "reason": "Invalid date format for start_time"
    }
  ],
  "activities": [
    {
      "id": "a1b2c3d4-...",
      "activityType": "running",
      "startTime": "2024-01-15T14:30:00Z",
      "durationSeconds": 2700
    }
  ]
}
```

### Success (200 OK) - Failed
```json
{
  "importId": "z9y8x7w6-...",
  "status": "failed",
  "startedAt": "2024-01-15T16:00:00Z",
  "failedAt": "2024-01-15T16:01:00Z",
  "error": "File parsing failed",
  "details": "Unsupported CSV format or corrupted file"
}
```

### Error Responses

**404 Not Found** - Import ID not found
```json
{
  "error": "import_not_found",
  "message": "Import job with ID 'xyz' not found"
}
```

**401 Unauthorized** - Missing or invalid JWT
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired JWT token"
}
```

**403 Forbidden** - Import doesn't belong to user
```json
{
  "error": "forbidden",
  "message": "You do not have permission to view this import job"
}
```

---

## Implementation Notes

### Import Status Tracking Table (PostgreSQL)

```sql
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL, -- 'processing', 'completed', 'failed'
    file_name VARCHAR(255),
    file_size_bytes BIGINT,
    provider VARCHAR(50),
    total_rows INT,
    processed_rows INT,
    activities_imported INT DEFAULT 0,
    activities_failed INT DEFAULT 0,
    errors JSONB, -- Array of {row, reason}
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_import_jobs_user_id ON import_jobs(user_id);
CREATE INDEX idx_import_jobs_status ON import_jobs(status);
```

### Status Polling
- Frontend polls this endpoint every 2-5 seconds while `status = 'processing'`
- Backend updates `import_jobs` table as processing progresses
- Use WebSocket or Server-Sent Events (SSE) for real-time updates (future enhancement)

---

## Testing

### Contract Tests
- GET valid importId → 200 OK with status
- GET non-existent importId → 404 Not Found
- GET without auth header → 401 Unauthorized
- GET different user's importId → 403 Forbidden

### Integration Tests
- Status transitions: processing → completed
- Status transitions: processing → failed
- Progress percentage calculation
- Error accumulation in import_jobs table

---

## Testing

### Unit Tests
- File format detection (CSV, JSON, GPX, etc.)
- Row validation (date parsing, numeric ranges)
- Duplicate detection logic

### Contract Tests
- POST valid CSV → 202 Accepted with importId
- POST invalid file format → 400 Bad Request
- POST oversized file → 413 Payload Too Large
- POST without auth header → 401 Unauthorized

### Integration Tests
- Full file processing pipeline (upload → parse → store)
- Error handling for malformed files
- Duplicate activity detection
- Import status endpoint returns correct progress
