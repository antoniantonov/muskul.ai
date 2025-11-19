# API Contract: List Activities

**Feature**: 001-platform-ingestion  
**User Story**: US-002 (Visualize Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
GET /api/v1/activities
```

**Purpose**: Retrieve user's fitness activities with optional filtering.

---

## Request

### Headers
```
Authorization: Bearer <jwt_token>
```

### Query Parameters
```
?start=2024-01-01T00:00:00Z
&end=2024-01-31T23:59:59Z
&activity_type=running,cycling
&user_query=strong,morning
&page=1
&per_page=50
```

**All parameters are optional:**
- `start`: ISO 8601 timestamp (default: 30 days ago)
- `end`: ISO 8601 timestamp (default: now)
- `activity_type`: Comma-separated list (default: all types)
- `user_query`: Search terms to match against notes and exercise metadata (comma-separated)
- `page`: Page number for pagination (default: 1)
- `per_page`: Items per page (default: 50, max: 100)

---

## Response

### Success (200 OK)
```json
{
  "data": [
    {
      "id": "a1b2c3d4-...",
      "userId": "e5f6g7h8-...",
      "providerAccountId": "i9j0k1l2-...",
      "externalId": "12345678",
      "activityType": "running",
      "startTime": "2024-01-15T14:30:00Z",
      "endTime": "2024-01-15T15:15:00Z",
      "durationSeconds": 2700,
      "metrics": {
        "distanceKm": 5.2,
        "heartRateAvg": 145,
        "heartRateMax": 168,
        "calories": 320,
        "elevationGainM": 45
      },
      "gpsTrack": [
        {"lat": 37.7749, "lon": -122.4194, "ts": "2024-01-15T14:30:00Z", "elevationM": 10},
        {"lat": 37.7750, "lon": -122.4195, "ts": "2024-01-15T14:31:00Z", "elevationM": 12}
      ],
      "source": "api",
      "isDuplicate": false,
      "duplicateOf": null,
      "notes": "Felt strong today!",
      "parsedNotes": null,
      "supplementalData": {
        "temperatureCelsius": 18.5,
        "humidityPercent": 65,
        "weatherDescription": "partly cloudy",
        "windSpeedKmh": 12.3,
        "airQualityIndex": 45
      },
      "createdAt": "2024-01-15T15:20:00Z",
      "updatedAt": "2024-01-15T15:25:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "totalItems": 127,
    "totalPages": 3
  },
  "meta": {
    "filters": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z",
      "activityType": ["running", "cycling"],
      "userQuery": ["strong", "morning"]
    }
  }
}
```

### Error Responses

**400 Bad Request** - Invalid date range or parameters
```json
{
  "error": "invalid_date_range",
  "message": "End date must be after start date"
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
  "message": "Too many requests. Please try again in 60 seconds."
}
```

---

## Caching Strategy

- Cache key: `dashboard:{user_id}:{start}:{end}:{activity_type}:{user_query}:{page}`
- TTL: 5 minutes
- Invalidate on: New activity imported, manual entry, data export

---

## Performance Budget

- **p95 latency**: <200ms (including database query + cache check)
- **p99 latency**: <500ms
- **Cache hit rate**: >80% for typical dashboard queries

---

## Implementation Notes

- Queries PostgreSQL `activities` table with LEFT JOIN on `supplemental_data`
- Uses composite index `idx_activities_user_time` for efficient range queries
- Filters out duplicates by default (`is_duplicate = FALSE`)
- If `user_query` provided, match against `notes` field and parsed exercise data using PostgreSQL `ILIKE` or `ts_vector` (full-text search)
- User query applies OR logic: match any term in notes, workout notes, parsed exercise data, or activity type
- GPS track truncated if >1000 points (return sampled points for performance)
- Valkey cache checked first, database query on cache miss
- **API Documentation**: Generate OpenAPI/Swagger specification for this endpoint. Ensure the implementation matches the Swagger schema exactly (request/response types, validation rules, error codes).

---

## Testing

### Unit Tests
- Date range validation
- Pagination logic
- Activity type filtering
- User query parsing (comma-separated terms)

### Contract Tests
- GET with valid params → 200 OK with activity list
- GET with user_query → 200 OK with filtered results
- GET with invalid date range → 400 Bad Request
- GET without auth header → 401 Unauthorized

### Integration Tests
- Query with filters returns correct activities
- User query matching against notes and exercise data
- Cache hit/miss behavior
- GPS track sampling for large tracks

### Performance Tests
- Load test with 10K concurrent users
- Verify p95 < 200ms, p99 < 500ms
- Cache hit rate > 80%
