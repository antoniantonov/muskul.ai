# Quickstart Guide
**Feature**: 001-platform-ingestion  
**Generated**: 2025-11-15  
**Purpose**: Setup and run the muskul.ai fitness data ingestion platform locally.

---

## Prerequisites

### Required Tools
- **Docker**: 24.0+ with Docker Compose 2.0+
- **Git**: 2.30+
- **Node.js**: 20.x LTS (for frontend development)
- **Rust**: 1.75+ (for backend development)
- **PostgreSQL Client**: psql 16+ (optional, for database inspection)
- **MongoDB Compass**: Latest (optional, for raw data inspection)

### Optional Tools
- **VS Code**: With Rust Analyzer, ESLint, Prettier extensions
- **Postman/Insomnia**: For API testing
- **k9s or kubectl**: For Kubernetes deployment (production)

---

## Quick Start (Docker Compose)

### 1. Clone Repository

```bash
git clone https://github.com/muskul-ai/muskul.ai.git
cd muskul.ai
```

### 2. Environment Setup

Create `.env` file in project root:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=muskul
POSTGRES_USER=muskul_user
POSTGRES_PASSWORD=your_secure_password

MONGODB_URI=mongodb://localhost:27017/muskul_raw
VALKEY_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET=your_256_bit_secret_key_here
JWT_EXPIRATION_HOURS=1

# OAuth2 Provider Credentials (Get from provider developer portals)
GARMIN_CLIENT_ID=your_garmin_client_id
GARMIN_CLIENT_SECRET=your_garmin_client_secret
GARMIN_REDIRECT_URI=http://localhost:8080/api/v1/providers/callback

FITBIT_CLIENT_ID=your_fitbit_client_id
FITBIT_CLIENT_SECRET=your_fitbit_client_secret
FITBIT_REDIRECT_URI=http://localhost:8080/api/v1/providers/callback

STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REDIRECT_URI=http://localhost:8080/api/v1/providers/callback

# AI Agent Service (Optional - for note parsing)
AI_AGENT_URL=http://localhost:8081
AI_AGENT_TIMEOUT_SECONDS=10

# OpenAI API (if using AI agent)
OPENAI_API_KEY=sk-...

# Observability (Optional)
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
GRAFANA_CLOUD_API_KEY=your_grafana_api_key

# Frontend (React)
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

### 3. Start Services

```bash
# Start all services (database, backend, frontend)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

**Services Started:**
- PostgreSQL: `localhost:5432`
- MongoDB: `localhost:27017`
- Valkey (Redis): `localhost:6379`
- Backend API: `http://localhost:8080`
- Frontend: `http://localhost:3000`
- AI Agent (optional): `http://localhost:8081`

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend /bin/bash -c "sqlx migrate run"

# Verify tables created
docker-compose exec postgres psql -U muskul_user -d muskul -c "\dt"
```

Expected output:
```
             List of relations
 Schema |        Name         | Type  |   Owner
--------+---------------------+-------+------------
 public | users               | table | muskul_user
 public | provider_accounts   | table | muskul_user
 public | activities          | table | muskul_user
 public | workouts            | table | muskul_user
 public | supplemental_data   | table | muskul_user
```

### 5. Verify Setup

**Health Check**:
```bash
curl http://localhost:8080/health
# Expected: {"status":"ok","database":"connected","cache":"connected"}
```

**API Documentation**:
Open `http://localhost:8080/docs` (OpenAPI/Swagger UI)

**Frontend**:
Open `http://localhost:3000` (React app)

---

## Development Setup (Native)

### Backend (Rust)

#### Install Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
rustup update
```

#### Install SQLx CLI
```bash
cargo install sqlx-cli --no-default-features --features postgres
```

#### Start Backend
```bash
cd backend

# Install dependencies (first time)
cargo build

# Run migrations
sqlx migrate run --database-url postgres://muskul_user:password@localhost:5432/muskul

# Start development server (hot reload)
cargo watch -x run

# Backend running at http://localhost:8080
```

#### Run Tests
```bash
# Unit tests
cargo test

# Integration tests (requires test database)
DATABASE_URL=postgres://muskul_user:password@localhost:5432/muskul_test cargo test --test '*'

# Coverage report
cargo tarpaulin --out Html
```

---

### Frontend (React + TypeScript)

#### Install Node.js
```bash
# Using nvm (recommended)
nvm install 20
nvm use 20
```

#### Start Frontend
```bash
cd frontend

# Install dependencies (first time)
npm install

# Start development server (hot reload)
npm run dev

# Frontend running at http://localhost:3000
```

#### Run Tests
```bash
# Unit tests (Vitest)
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Coverage report
npm run test:coverage
```

#### Build Production
```bash
npm run build
# Output in dist/
```

---

### AI Agent Service (Python - Optional)

#### Install Python
```bash
# Using pyenv (recommended)
pyenv install 3.11.5
pyenv local 3.11.5
```

#### Start AI Agent
```bash
cd ai-agent-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Flask server
python app.py

# AI Agent running at http://localhost:8081
```

#### Run Tests
```bash
pytest tests/
```

---

## Database Management

### PostgreSQL

#### Create Tables
```bash
cd backend
sqlx migrate run
```

#### Rollback Last Migration
```bash
sqlx migrate revert
```

#### Connect to Database
```bash
psql -h localhost -U muskul_user -d muskul
```

#### Useful Queries
```sql
-- Count activities by type
SELECT activity_type, COUNT(*) FROM activities GROUP BY activity_type;

-- Recent activities
SELECT id, activity_type, start_time, metrics->>'heart_rate_avg' AS hr 
FROM activities 
ORDER BY start_time DESC 
LIMIT 10;

-- Connected providers per user
SELECT u.email, COUNT(pa.id) AS provider_count
FROM users u
LEFT JOIN provider_accounts pa ON u.id = pa.user_id
GROUP BY u.email;
```

### MongoDB

#### Connect to MongoDB
```bash
mongosh mongodb://localhost:27017/muskul_raw
```

#### Useful Commands
```javascript
// Count raw activities
db.raw_activities.countDocuments()

// Find recent activities
db.raw_activities.find().sort({timestamp: -1}).limit(10)

// Aggregate by provider
db.raw_activities.aggregate([
  {$group: {_id: "$metadata.provider", count: {$sum: 1}}}
])
```

### Valkey (Redis)

#### Connect to Valkey
```bash
redis-cli -h localhost -p 6379
```

#### Useful Commands
```bash
# View all keys
KEYS *

# Get dashboard cache
GET dashboard:user_id:2024-01-01:2024-01-31

# Flush all cache (development only)
FLUSHALL
```

---

## OAuth2 Provider Setup

### Garmin Connect

1. Register app at [Garmin Developer Portal](https://developer.garmin.com/)
2. Create OAuth2 application
3. Set redirect URI: `http://localhost:8080/api/v1/providers/callback`
4. Copy Client ID and Client Secret to `.env`

### Fitbit

1. Register app at [Fitbit Developer Portal](https://dev.fitbit.com/)
2. Create OAuth2 application
3. Set redirect URI: `http://localhost:8080/api/v1/providers/callback`
4. Copy Client ID and Client Secret to `.env`

### Strava

1. Register app at [Strava API Settings](https://www.strava.com/settings/api)
2. Set redirect URI: `http://localhost:8080/api/v1/providers/callback`
3. Copy Client ID and Client Secret to `.env`

### Polar

1. Register app at [Polar AccessLink](https://www.polar.com/accesslink-api)
2. Follow OAuth2 setup
3. Copy credentials to `.env`

---

## Testing

### Run All Tests
```bash
# Backend
cd backend && cargo test --all

# Frontend
cd frontend && npm run test

# E2E
cd frontend && npm run test:e2e
```

### Manual API Testing

#### Create User (via OAuth2 mock)
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "email": "test@example.com",
    "name": "Test User"
  }'
```

Response:
```json
{
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "e5f6g7h8-...",
    "email": "test@example.com",
    "name": "Test User"
  }
}
```

#### Create Manual Activity
```bash
export TOKEN="<jwt_token_from_above>"

curl -X POST http://localhost:8080/api/v1/activities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activityType": "running",
    "startTime": "2024-01-15T14:30:00Z",
    "endTime": "2024-01-15T15:15:00Z",
    "metrics": {
      "distanceKm": 5.2,
      "heartRateAvg": 145,
      "calories": 320
    },
    "notes": "5 sets of 10 squats at 135 lbs"
  }'
```

#### List Activities
```bash
curl http://localhost:8080/api/v1/activities \
  -H "Authorization: Bearer $TOKEN" \
  -G \
  --data-urlencode "start=2024-01-01T00:00:00Z" \
  --data-urlencode "end=2024-01-31T23:59:59Z"
```

---

## Troubleshooting

### Backend Won't Start

**Error**: "Failed to connect to PostgreSQL"
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql -h localhost -U muskul_user -d muskul

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**Error**: "SQLx migration failed"
```bash
# Reset database (WARNING: deletes all data)
sqlx database drop
sqlx database create
sqlx migrate run
```

### Frontend Build Fails

**Error**: "Cannot find module '@/components/...'"
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error**: "Vite build timeout"
```bash
# Increase Node.js memory
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### OAuth2 Connection Fails

**Error**: "redirect_uri_mismatch"
- Verify redirect URI in `.env` matches provider settings exactly (including protocol, port)
- Garmin/Fitbit/Strava must whitelist `http://localhost:8080/api/v1/providers/callback`

**Error**: "invalid_client"
- Verify Client ID and Client Secret in `.env` are correct
- Check if provider credentials expired (regenerate if needed)

### Database Performance Issues

**Slow Queries**:
```sql
-- Check missing indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public';

-- Analyze query plan
EXPLAIN ANALYZE 
SELECT * FROM activities 
WHERE user_id = 'xxx' AND start_time > '2024-01-01';
```

**High Memory Usage**:
```sql
-- Check table sizes
SELECT 
  tablename, 
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Production Deployment

### Docker Build

#### Backend
```bash
cd backend
docker build -t muskul-backend:latest .
docker push your-registry.io/muskul-backend:latest
```

#### Frontend
```bash
cd frontend
docker build -t muskul-frontend:latest .
docker push your-registry.io/muskul-frontend:latest
```

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f infra/k8s/backend/
kubectl apply -f infra/k8s/frontend/

# Check status
kubectl get pods -n muskul

# View logs
kubectl logs -f deployment/muskul-backend -n muskul
```

### Azure Container Apps

```bash
# Deploy backend
az containerapp create \
  --name muskul-backend \
  --resource-group muskul-rg \
  --image your-registry.io/muskul-backend:latest \
  --target-port 8080 \
  --ingress external \
  --env-vars \
    POSTGRES_HOST=... \
    MONGODB_URI=... \
    JWT_SECRET=...

# Deploy frontend
az containerapp create \
  --name muskul-frontend \
  --resource-group muskul-rg \
  --image your-registry.io/muskul-frontend:latest \
  --target-port 80 \
  --ingress external
```

---

## Monitoring & Observability

### Grafana Dashboards

1. Open Grafana: `http://localhost:3001`
2. Import dashboard: `infra/grafana/dashboards/muskul-overview.json`
3. Configure data sources:
   - Prometheus: `http://localhost:9090`
   - Tempo: `http://localhost:9411`

### Prometheus Metrics

Backend exposes metrics at `http://localhost:8080/metrics`:
```
# HTTP request duration
http_request_duration_seconds_bucket{method="GET",path="/api/v1/activities"}

# Active users
muskul_active_users{window="5m"}

# Sync jobs
muskul_sync_jobs_total{provider="garmin",status="success"}
```

### OpenTelemetry Traces

View traces in Grafana Tempo:
1. Open Grafana: `http://localhost:3001`
2. Go to Explore → Tempo
3. Search for trace ID from logs

---

## Next Steps

1. **Configure OAuth2 Providers**: Follow [OAuth2 Provider Setup](#oauth2-provider-setup)
2. **Explore API**: Open `http://localhost:8080/docs` for interactive API documentation
3. **Run Tests**: Verify setup with `cargo test` and `npm run test`
4. **Connect Provider**: Use frontend to connect Garmin/Fitbit/Strava account
5. **View Dashboard**: Navigate to `http://localhost:3000/dashboard` to see imported activities

---

## Resources

- **API Documentation**: `http://localhost:8080/docs` (OpenAPI/Swagger UI)
- **Spec Files**: `/specs/001-platform-ingestion/`
- **Contracts**: `/specs/001-platform-ingestion/contracts/`
- **Constitution**: `/.specify/memory/constitution.md`
- **Rust Documentation**: `cargo doc --open`
- **React Components**: Storybook at `http://localhost:6006` (if configured)

---

## Support

For questions or issues:
- **GitHub Issues**: [muskul-ai/muskul.ai/issues](https://github.com/muskul-ai/muskul.ai/issues)
- **Slack**: `#muskul-ai-dev` (internal)
- **Email**: dev@muskul.ai
