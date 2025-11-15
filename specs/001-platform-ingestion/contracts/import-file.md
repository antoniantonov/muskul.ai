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
provider: "garmin" | "fitbit" | "strava" | "polar" | "apple_health" | "generic"
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
    {
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

- File uploaded to temporary storage (local disk or S3)
- Async processing: Parse file → Validate → Normalize → Store in MongoDB (raw) → ETL to PostgreSQL
- Supports batch import (multiple activities per file)
- Duplicate detection: Check hash of (provider + external_id + start_time)
- Failed activities logged with reason (validation errors, parsing errors)
- Import job timeout: 5 minutes

---

## File Format Examples

### CSV Format
```csv
date,activity_type,duration_minutes,distance_km,calories,heart_rate_avg,notes
2024-01-15 14:30:00,running,45,5.2,320,145,"Felt strong"
2024-01-16 08:00:00,cycling,60,15.0,450,130,"Easy ride"
```

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
