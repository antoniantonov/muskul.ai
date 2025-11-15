# API Contract: AI Note Parsing Service

**Feature**: 001-platform-ingestion  
**User Story**: US-001 (Import Data - FR-003b)  
**Generated**: 2025-11-15

---

## Endpoint

```
POST /ai-agent/api/v1/parse-note
```

**Purpose**: Parse unstructured user notes and extract structured exercise data using AI/LLM.

**Service Type**: External microservice (separate from main backend)

---

## Request

### Headers
```
Content-Type: application/json
Authorization: Bearer <service_token>
X-Request-ID: <trace_id>
```

### Body
```json
{
  "note": "Did 5 sets of 10 squats at 135 lbs, then 3 sets of 8 deadlifts at 225 lbs. Felt strong today!",
  "activity_type": "strength",
  "userId": "e5f6g7h8-..."
}
```

### Validation Rules
- `note`: Required, string (min 1 char, max 5000 chars)
- `activity_type`: Optional, helps AI with context
- `userId`: Optional, for logging/analytics only (never stored)

---

## Response

### Success (200 OK)
```json
{
  "exercises": [
    {
      "name": "squat",
      "sets": 5,
      "reps": 10,
      "weightLbs": 135,
      "weightKg": 61.2
    },
    {
      "name": "deadlift",
      "sets": 3,
      "reps": 8,
      "weightLbs": 225,
      "weightKg": 102.1
    }
  ],
  "intensity": "moderate",
  "duration_minutes": null,
  "notes": "Felt strong today!",
  "confidence": 0.92
}
```

**Fields:**
- `exercises`: Array of extracted exercise data
  - `name`: Exercise name (normalized, e.g., "squat", "bench_press")
  - `sets`: Number of sets (integer, nullable)
  - `reps`: Number of repetitions per set (integer, nullable)
  - `weightLbs`: Weight in pounds (float, nullable)
  - `weightKg`: Weight in kilograms (float, nullable, auto-converted from lbs)
- `intensity`: Perceived intensity ("low", "moderate", "high", "vigorous", null)
- `duration_minutes`: Total workout duration if mentioned (integer, nullable)
- `notes`: Remaining text not parsed as structured data
- `confidence`: AI confidence score (0.0 - 1.0, where >0.8 is high confidence)

### Success (200 OK) - No Structured Data Found
```json
{
  "exercises": [],
  "intensity": null,
  "duration_minutes": null,
  "notes": "Just a casual walk in the park",
  "confidence": 0.5
}
```

### Error Responses

**400 Bad Request** - Invalid input
```json
{
  "error": "invalid_input",
  "message": "Note text is required and must not be empty"
}
```

**408 Request Timeout** - LLM API timeout
```json
{
  "error": "timeout",
  "message": "AI parsing timed out after 10 seconds"
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again in 10 seconds."
}
```

**500 Internal Server Error** - LLM API error
```json
{
  "error": "llm_error",
  "message": "Failed to parse note using AI service"
}
```

---

## Implementation Notes

### AI Service Architecture
- **Separate Microservice**: Deployed independently from main backend (Python/Flask or FastAPI)
- **LLM Provider**: OpenAI GPT-4, Anthropic Claude, or Azure OpenAI Service
- **Prompt Engineering**: Structured prompt with few-shot examples to extract exercise data
- **Fallback**: If LLM fails, return empty exercises array (graceful degradation)

### Example Prompt (OpenAI GPT-4)
```text
You are an exercise data parser. Extract structured exercise data from user notes.

Input: "Did 5 sets of 10 squats at 135 lbs, then 3 sets of 8 deadlifts at 225 lbs. Felt strong today!"

Output (JSON):
{
  "exercises": [
    {"name": "squat", "sets": 5, "reps": 10, "weight_lbs": 135},
    {"name": "deadlift", "sets": 3, "reps": 8, "weight_lbs": 225}
  ],
  "intensity": "moderate",
  "notes": "Felt strong today!"
}

Now parse the following note:
{note}
```

### Performance & Timeout
- **Timeout**: 10 seconds (backend retries on timeout per FR-007a)
- **Retry Logic**: Backend retries 3 times with exponential backoff (15 minutes total)
- **Caching**: Cache parsed results in Valkey (key: `parsed_note:sha256(note)`, TTL: 24 hours)

### Security
- **Authentication**: Service-to-service auth using JWT or API key
- **Input Sanitization**: Escape user input to prevent prompt injection
- **Rate Limiting**: 100 requests/minute per user to prevent abuse
- **PII Handling**: User notes may contain PII; ensure GDPR compliance (data retention, deletion)

---

## Testing

### Unit Tests
- Note validation (empty, max length)
- Weight unit conversion (lbs ↔ kg)
- Exercise name normalization

### Contract Tests
- POST valid note → 200 OK with parsed exercises
- POST empty note → 400 Bad Request
- POST with LLM timeout → 408 Request Timeout

### Integration Tests
- Full flow: Backend → AI service → Response → Store in database
- Retry logic on timeout
- Cache hit/miss behavior

### Performance Tests
- Load test with 100 concurrent requests
- Verify p95 < 5s, p99 < 10s
- Cache hit rate > 50% (for repeated notes)

---

## Example Test Cases

### Test Case 1: Strength Training
**Input**:
```json
{"note": "Bench press: 3x10 at 185 lbs, Rows: 4x12 at 135 lbs"}
```

**Expected Output**:
```json
{
  "exercises": [
    {"name": "bench_press", "sets": 3, "reps": 10, "weightLbs": 185, "weightKg": 83.9},
    {"name": "row", "sets": 4, "reps": 12, "weightLbs": 135, "weightKg": 61.2}
  ],
  "intensity": null,
  "notes": "",
  "confidence": 0.95
}
```

### Test Case 2: Cardio (No Structured Data)
**Input**:
```json
{"note": "Easy 30-minute jog around the neighborhood"}
```

**Expected Output**:
```json
{
  "exercises": [],
  "intensity": "low",
  "duration_minutes": 30,
  "notes": "Easy jog around the neighborhood",
  "confidence": 0.85
}
```

### Test Case 3: Mixed Data
**Input**:
```json
{"note": "Warm up with 10 min run, then 5x5 squats at 225 lbs, felt tired"}
```

**Expected Output**:
```json
{
  "exercises": [
    {"name": "squat", "sets": 5, "reps": 5, "weightLbs": 225, "weightKg": 102.1}
  ],
  "intensity": "low",
  "duration_minutes": 10,
  "notes": "Warm up with run, felt tired",
  "confidence": 0.88
}
```

---

## Deployment

- **Container**: Docker image deployed to Azure Container Apps or Kubernetes
- **Scaling**: Horizontal autoscaling based on request queue length (min 2, max 10 instances)
- **Monitoring**: OpenTelemetry traces exported to Grafana, metrics to Prometheus
- **Logging**: Structured JSON logs with `trace_id`, `user_id`, `latency_ms`, `confidence`

---

## Future Enhancements

- **Multi-Language Support**: Parse notes in Spanish, French, German, etc.
- **Fine-Tuned Model**: Train custom LLM on fitness data for higher accuracy
- **Exercise Database**: Map parsed exercise names to canonical database (e.g., "bench" → "bench press")
- **Voice Input**: Integrate with speech-to-text API for voice notes
