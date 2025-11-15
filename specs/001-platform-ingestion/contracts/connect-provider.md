# API Contract: Connect Fitness Provider

**Feature**: 001-platform-ingestion  
**User Story**: US-001 (Import Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
POST /api/v1/providers/connect
```

**Purpose**: Initiate OAuth2 authorization flow to connect a fitness data provider.

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
  "provider": "garmin" | "fitbit" | "strava" | "polar" | "apple_health",
  "redirect_uri": "https://muskul.ai/auth/callback",
  "scopes": ["activities", "profile", "sleep"]
}
```

### Validation Rules
- `provider`: Required, must be one of supported providers
- `redirect_uri`: Required, must match registered redirect URIs
- `scopes`: Optional, defaults to provider's default scopes

---

## Response

### Success (200 OK)
```json
{
  "authorization_url": "https://provider.com/oauth/authorize?client_id=...&redirect_uri=...&state=...&code_challenge=...",
  "state": "random_state_string",
  "expires_in": 600
}
```

**Description**: Frontend redirects user to `authorization_url`. After user grants access, provider redirects to `redirect_uri` with authorization code.

### Error Responses

**400 Bad Request** - Invalid provider or redirect URI
```json
{
  "error": "invalid_provider",
  "message": "Provider 'xyz' is not supported. Supported providers: garmin, fitbit, strava, polar, apple_health"
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

## Implementation Notes

- Uses OAuth2 2.0 Authorization Code Flow with PKCE
- `state` parameter prevents CSRF attacks (validated in callback)
- `code_challenge` is SHA-256 hash of `code_verifier` (stored server-side)
- Authorization URL expires in 10 minutes

---

## Testing

### Unit Tests
- Validate provider enum
- Validate redirect URI whitelist
- Generate PKCE code_challenge correctly

### Contract Tests
- POST valid request → 200 OK with authorization_url
- POST invalid provider → 400 Bad Request
- POST without auth header → 401 Unauthorized

### Integration Tests
- Full OAuth2 flow with mock provider
- State parameter validation
- Token exchange success/failure
