# API Contract: Trigger Manual Sync

**Feature**: 001-platform-ingestion  
**User Story**: US-001 (Import Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
POST /api/v1/providers/{providerAccountId}/sync
```

**Purpose**: Manually trigger data sync from a connected fitness provider (on-demand sync per FR-002a).

---

## Request

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Path Parameters
```
providerAccountId: UUID of the provider account to sync
```

### Body (Optional)
```json
{
  "fullSync": false
}
```

**Parameters:**
- `fullSync`: Boolean, if true syncs all historical data, if false syncs only new data since last sync (default: false)

---

## Response

### Success (202 Accepted)
```json
{
  "syncId": "s1t2u3v4-...",
  "providerAccountId": "i9j0k1l2-...",
  "status": "pending",
  "message": "Sync job queued. Processing...",
  "estimatedTimeSeconds": 60
}
```

**Description**: Sync job accepted and queued for background processing. Use `GET /providers/{providerAccountId}/sync/{syncId}` to check progress.

### Error Responses

**400 Bad Request** - Sync already in progress
```json
{
  "error": "sync_in_progress",
  "message": "A sync job is already running for this provider. Please wait for it to complete."
}
```

**401 Unauthorized** - Missing or invalid JWT
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired JWT token"
}
```

**403 Forbidden** - Provider account doesn't belong to user
```json
{
  "error": "forbidden",
  "message": "You do not have permission to sync this provider account"
}
```

**404 Not Found** - Provider account not found
```json
{
  "error": "provider_account_not_found",
  "message": "Provider account with ID 'xyz' not found"
}
```

**429 Too Many Requests** - Rate limit exceeded
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many sync requests. Please try again in 60 seconds."
}
```

**503 Service Unavailable** - Provider API unavailable
```json
{
  "error": "provider_unavailable",
  "message": "Garmin API is currently unavailable. Please try again later."
}
```

---

## Implementation Notes

- Queues async sync job (message queue: Azure Service Bus, RabbitMQ)
- Sync job workflow:
  1. Check token expiration → Refresh if needed
  2. Call provider API (`GET /activities?since=last_sync_at`)
  3. Store raw data in MongoDB `raw_activities`
  4. Trigger ETL pipeline for normalization
  5. Update `last_sync_at` and `last_sync_status` in `provider_accounts` table
- Retry logic: Exponential backoff (3 attempts over 15 minutes per FR-007a)
- Conflict detection: Only one sync job per provider account at a time (use distributed lock with Valkey)
- Full sync: Retrieves all historical data (may take 5-10 minutes for providers with 1000+ activities)
- Incremental sync: Retrieves only activities since `last_sync_at` (typically <1 minute)

---

## Sync Status Endpoint

### GET /api/v1/providers/{providerAccountId}/sync/{syncId}

**Response (200 OK)**:
```json
{
  "syncId": "s1t2u3v4-...",
  "providerAccountId": "i9j0k1l2-...",
  "status": "completed",
  "startedAt": "2024-01-15T16:00:00Z",
  "completedAt": "2024-01-15T16:02:15Z",
  "activitiesImported": 23,
  "activitiesFailed": 1,
  "errors": [
    {
      "externalId": "12345678",
      "reason": "Invalid GPS data format"
    }
  ]
}
```

**Status values:**
- `pending`: Sync job queued but not started
- `in_progress`: Sync job running
- `completed`: Sync job finished successfully
- `failed`: Sync job failed (check `errors` array)

---

## Testing

### Unit Tests
- Validate providerAccountId UUID format
- Token refresh logic
- Conflict detection (prevent duplicate syncs)

### Contract Tests
- POST with valid providerAccountId → 202 Accepted with syncId
- POST with non-existent providerAccountId → 404 Not Found
- POST without auth header → 401 Unauthorized
- POST for different user's provider → 403 Forbidden

### Integration Tests
- Full sync workflow (queue → process → store → update status)
- Incremental sync (only new activities)
- Retry logic on provider API failure
- Sync status endpoint returns correct progress

### Performance Tests
- Full sync with 1000+ activities (verify < 10 minutes)
- Incremental sync with 10 activities (verify < 1 minute)
