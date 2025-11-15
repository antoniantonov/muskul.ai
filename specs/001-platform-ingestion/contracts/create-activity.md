# API Contract: Create Activity (Manual Entry)

**Feature**: 001-platform-ingestion  
**User Story**: US-001 (Import Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
POST /api/v1/activities
```

**Purpose**: Manually create a fitness activity with user-entered data.

---

## Request

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Body
```json
{
  "activityType": "running",
  "startTime": "2024-01-15T14:30:00Z",
  "endTime": "2024-01-15T15:15:00Z",
  "metrics": {
    "distanceKm": 5.2,
    "heartRateAvg": 145,
    "calories": 320
  },
  "notes": "5 sets of 10 squats at 135 lbs, felt strong",
  "gpsTrack": [
    {"lat": 37.7749, "lon": -122.4194, "ts": "2024-01-15T14:30:00Z", "elevationM": 10}
  ]
}
```

### Validation Rules
- `activityType`: Required, string (e.g., "running", "cycling", "strength")
- `startTime`: Required, ISO 8601 timestamp
- `endTime`: Required, ISO 8601 timestamp, must be after startTime
- `metrics`: Optional, object with numeric values (heart_rate_avg: 30-220, calories: >0, etc.)
- `notes`: Optional, string (max 5000 characters)
- `gpsTrack`: Optional, array of GPS points (max 10,000 points)

---

## Response

### Success (201 Created)
```json
{
  "id": "a1b2c3d4-...",
  "userId": "e5f6g7h8-...",
  "providerAccountId": null,
  "externalId": null,
  "activityType": "running",
  "startTime": "2024-01-15T14:30:00Z",
  "endTime": "2024-01-15T15:15:00Z",
  "durationSeconds": 2700,
  "metrics": {
    "distanceKm": 5.2,
    "heartRateAvg": 145,
    "calories": 320
  },
  "gpsTrack": [
    {"lat": 37.7749, "lon": -122.4194, "ts": "2024-01-15T14:30:00Z", "elevationM": 10}
  ],
  "source": "manual",
  "isDuplicate": false,
  "notes": "5 sets of 10 squats at 135 lbs, felt strong",
  "parsedNotes": {
    "exercises": [
      {"name": "squat", "sets": 5, "reps": 10, "weightKg": 61.2}
    ],
    "intensity": "moderate"
  },
  "createdAt": "2024-01-15T15:20:00Z",
  "updatedAt": "2024-01-15T15:20:00Z"
}
```

**Description**: Activity created successfully. If `notes` are provided, AI service parses them asynchronously and updates `parsedNotes` field.

### Error Responses

**400 Bad Request** - Validation errors
```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": [
    {
      "field": "endTime",
      "reason": "End time must be after start time"
    },
    {
      "field": "metrics.heartRateAvg",
      "reason": "Heart rate must be between 30 and 220 bpm"
    }
  ]
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
  "message": "Too many manual entries. Please try again in 60 seconds."
}
```

---

## Implementation Notes

- Activity stored directly in PostgreSQL (no MongoDB landing zone for manual entries)
- `source` field set to `"manual"`
- `providerAccountId` and `externalId` are NULL (no provider connection)
- If `notes` are provided:
  - Store notes immediately
  - Call AI service asynchronously (`POST /api/v1/parse-note`)
  - Update `parsedNotes` when AI response received (within 10 seconds)
- If GPS track provided, queue for enrichment (weather/altitude)
- Duplicate detection: Check hash of (user_id + start_time + activity_type)
- Cache invalidation: Invalidate dashboard cache for this user

---

## AI Note Parsing (FR-003b)

**Async Flow**:
1. Activity created with notes
2. Backend calls AI service: `POST /ai-agent/api/v1/parse-note`
3. AI service responds with structured data (exercises, intensity)
4. Backend updates `parsedNotes` field
5. Frontend can poll `/activities/{id}` to check if `parsedNotes` is populated

**Timeout Handling**:
- AI service timeout: 10 seconds
- Retry with exponential backoff (3 attempts over 15 minutes per FR-007a)
- If all retries fail, log error and leave `parsedNotes` as NULL

---

## Testing

### Unit Tests
- Date range validation (endTime > startTime)
- Metrics validation (heart_rate 30-220, calories >0)
- Notes length validation (max 5000 chars)

### Contract Tests
- POST valid activity → 201 Created with activity data
- POST invalid endTime → 400 Bad Request with validation errors
- POST without auth header → 401 Unauthorized

### Integration Tests
- Full manual entry flow (create → store → AI parse → update)
- AI service timeout handling
- GPS track enrichment triggered
- Cache invalidation verified
