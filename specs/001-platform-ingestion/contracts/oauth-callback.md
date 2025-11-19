# API Contract: OAuth2 Callback

**Feature**: 001-platform-ingestion  
**User Story**: US-001 (Import Data)  
**Generated**: 2025-11-15

---

## Endpoint

```
GET /api/v1/providers/callback
```

**Purpose**: Complete OAuth2 authorization flow after user grants access.

---

## Request

### Query Parameters
```
?code=authorization_code
&state=random_state_string
&provider=garmin
```

### Validation Rules
- `code`: Required, authorization code from provider
- `state`: Required, must match state from `/providers/connect`
- `provider`: Required, must match provider from initial request

---

## Response

### Success (302 Redirect)
```
Location: https://muskul.ai/dashboard?provider=garmin&status=success
Set-Cookie: session_token=<jwt>; HttpOnly; Secure; SameSite=Strict
```

**Description**: Exchanges authorization code for access/refresh tokens, stores encrypted tokens in database, redirects user to dashboard.

### Error Responses

**302 Redirect** - OAuth2 error (user denied, invalid code, etc.)
```
Location: https://muskul.ai/dashboard?provider=garmin&status=error&error=access_denied
```

**400 Bad Request** - Invalid state or missing parameters
```json
{
  "error": "invalid_state",
  "message": "State parameter does not match. Possible CSRF attack."
}
```

**500 Internal Server Error** - Token exchange failed
```json
{
  "error": "token_exchange_failed",
  "message": "Failed to exchange authorization code for access token"
}
```

---

## Implementation Notes

- Validates `state` parameter against session-stored value (CSRF protection)
- Exchanges `code` for `access_token` + `refresh_token` using PKCE `code_verifier`
- Encrypts tokens with AES-256-GCM before storing in database
- Creates `ProviderAccount` record with `sync_enabled = TRUE`
- Schedules initial sync job (background task)
- **API Documentation**: Generate OpenAPI/Swagger specification for this endpoint. Ensure the implementation matches the Swagger schema exactly (request/response types, validation rules, error codes).

---

## Testing

### Unit Tests
- Validate state parameter matching
- Token encryption/decryption

### Contract Tests
- GET with valid code/state → 302 Redirect to dashboard with success
- GET with invalid state → 400 Bad Request
- GET with invalid code → 302 Redirect with error

### Integration Tests
- Full OAuth2 flow with real provider (sandbox environment)
- Token storage verification
- Initial sync job triggered
