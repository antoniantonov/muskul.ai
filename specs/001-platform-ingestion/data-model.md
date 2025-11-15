# Data Model
**Feature**: 001-platform-ingestion  
**Generated**: 2025-11-15  
**Purpose**: Define database schemas, entity relationships, and data flow for fitness data ingestion platform.

---

## Storage Architecture

### Multi-Tier Storage Strategy

```text
┌─────────────────────┐
│   Provider APIs     │ (Garmin, Fitbit, Strava, etc.)
│   File Uploads      │
│   Manual Entry      │
└──────────┬──────────┘
           │ OAuth2/HTTP
           ▼
┌─────────────────────┐
│  MongoDB (Landing)  │ ← Raw provider data (schema-less)
│  Collection: raw_   │   Preserves original format
│  activities         │   Time-series collections
└──────────┬──────────┘
           │ ETL Pipeline (Python/Go/Scala)
           ▼
┌─────────────────────┐
│ PostgreSQL (Core)   │ ← Normalized structured data
│  Tables: users,     │   ACID transactions
│  provider_accounts, │   JSONB for flexible metrics
│  activities,        │   Foreign key constraints
│  workouts,          │
│  supplemental_data  │
└──────────┬──────────┘
           │ Query Layer
           ▼
┌─────────────────────┐
│  Valkey (Cache)     │ ← Dashboard data, API responses
│  TTL: 5 min         │   Sub-ms latency
│  Keys: dashboard:*  │   Reduces DB load
└─────────────────────┘
```

---

## Entity Definitions

### 1. User

**Purpose**: Represents a platform user account.

**PostgreSQL Schema**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    auth_provider VARCHAR(50) NOT NULL, -- 'google', 'facebook', 'apple', 'microsoft'
    auth_provider_id VARCHAR(255) NOT NULL,
    profile_picture_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    unit_system VARCHAR(10) DEFAULT 'metric', -- 'metric' or 'imperial'
    privacy_settings JSONB DEFAULT '{"data_sharing": false, "public_profile": false}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE, -- Soft delete for GDPR compliance
    
    CONSTRAINT unique_auth_provider UNIQUE (auth_provider, auth_provider_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_auth_provider ON users(auth_provider, auth_provider_id);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;
```

**Rust Model**:
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
struct User {
    id: Uuid,
    email: String,
    name: String,
    auth_provider: AuthProvider,
    auth_provider_id: String,
    profile_picture_url: Option<String>,
    timezone: String,
    unit_system: UnitSystem,
    privacy_settings: PrivacySettings,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
    deleted_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Type)]
#[sqlx(type_name = "varchar")]
enum AuthProvider {
    Google,
    Facebook,
    Apple,
    Microsoft,
}

#[derive(Debug, Clone, Serialize, Deserialize, Type)]
#[sqlx(type_name = "varchar")]
enum UnitSystem {
    Metric,
    Imperial,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PrivacySettings {
    data_sharing: bool,
    public_profile: bool,
}
```

**TypeScript Type**:
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  authProvider: 'google' | 'facebook' | 'apple' | 'microsoft';
  authProviderId: string;
  profilePictureUrl?: string;
  timezone: string;
  unitSystem: 'metric' | 'imperial';
  privacySettings: {
    dataSharing: boolean;
    publicProfile: boolean;
  };
  createdAt: string;
  updatedAt: string;
  deletedAt?: string;
}
```

---

### 2. ProviderAccount

**Purpose**: Represents a linked fitness data provider (OAuth2 connection).

**PostgreSQL Schema**:
```sql
CREATE TABLE provider_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL, -- 'garmin', 'fitbit', 'strava', 'polar', 'apple_health'
    provider_user_id VARCHAR(255) NOT NULL, -- External user ID from provider
    access_token_encrypted BYTEA NOT NULL, -- AES-256-GCM encrypted
    refresh_token_encrypted BYTEA, -- AES-256-GCM encrypted
    token_expires_at TIMESTAMP WITH TIME ZONE,
    scopes TEXT[], -- OAuth2 scopes granted
    sync_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency_hours INT DEFAULT 24, -- Hourly sync = 1, daily = 24
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_sync_status VARCHAR(20) DEFAULT 'pending', -- 'success', 'failed', 'pending'
    last_sync_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_provider_per_user UNIQUE (user_id, provider_name)
);

CREATE INDEX idx_provider_accounts_user_id ON provider_accounts(user_id);
CREATE INDEX idx_provider_accounts_sync_enabled ON provider_accounts(sync_enabled) WHERE sync_enabled = TRUE;
CREATE INDEX idx_provider_accounts_last_sync ON provider_accounts(last_sync_at);
```

**Rust Model**:
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
struct ProviderAccount {
    id: Uuid,
    user_id: Uuid,
    provider_name: ProviderName,
    provider_user_id: String,
    #[serde(skip)] // Never serialize tokens
    access_token_encrypted: Vec<u8>,
    #[serde(skip)]
    refresh_token_encrypted: Option<Vec<u8>>,
    token_expires_at: Option<DateTime<Utc>>,
    scopes: Vec<String>,
    sync_enabled: bool,
    sync_frequency_hours: i32,
    last_sync_at: Option<DateTime<Utc>>,
    last_sync_status: SyncStatus,
    last_sync_error: Option<String>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Type)]
#[sqlx(type_name = "varchar")]
enum ProviderName {
    Garmin,
    Fitbit,
    Strava,
    Polar,
    AppleHealth,
}

#[derive(Debug, Clone, Serialize, Deserialize, Type)]
#[sqlx(type_name = "varchar")]
enum SyncStatus {
    Success,
    Failed,
    Pending,
}
```

**TypeScript Type**:
```typescript
interface ProviderAccount {
  id: string;
  userId: string;
  providerName: 'garmin' | 'fitbit' | 'strava' | 'polar' | 'apple_health';
  providerUserId: string;
  // Tokens never sent to frontend
  tokenExpiresAt?: string;
  scopes: string[];
  syncEnabled: boolean;
  syncFrequencyHours: number;
  lastSyncAt?: string;
  lastSyncStatus: 'success' | 'failed' | 'pending';
  lastSyncError?: string;
  createdAt: string;
  updatedAt: string;
}
```

---

### 3. Activity

**Purpose**: Represents a single fitness activity or workout session.

**MongoDB Schema (Raw Landing Zone)**:
```javascript
// Collection: raw_activities (time-series collection)
db.createCollection("raw_activities", {
   timeseries: {
      timeField: "timestamp",
      metaField: "metadata",
      granularity: "hours"
   }
});

// Document structure (flexible schema)
{
  _id: ObjectId("..."),
  timestamp: ISODate("2024-01-15T14:30:00Z"), // Activity start time
  metadata: {
    user_id: "a1b2c3d4-...",
    provider: "garmin",
    external_id: "12345678", // Provider's activity ID
    ingestion_time: ISODate("2024-01-15T15:00:00Z")
  },
  raw_data: { ... }, // Original provider payload (preserved)
  normalized: false // Flag for ETL processing
}
```

**PostgreSQL Schema (Normalized)**:
```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_account_id UUID REFERENCES provider_accounts(id) ON DELETE SET NULL,
    external_id VARCHAR(255), -- Provider's activity ID (for deduplication)
    activity_type VARCHAR(50) NOT NULL, -- 'running', 'cycling', 'swimming', 'strength', 'yoga', etc.
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_seconds INT NOT NULL,
    
    -- Metrics stored as JSONB for flexibility (different activities have different metrics)
    metrics JSONB NOT NULL DEFAULT '{}', -- { "distance_km": 5.2, "heart_rate_avg": 145, "calories": 320, ... }
    
    -- GPS data (array of lat/lon/timestamp points)
    gps_track JSONB, -- [{"lat": 37.7749, "lon": -122.4194, "ts": "2024-01-15T14:30:00Z", "elevation_m": 10}, ...]
    
    -- Source tracking for duplicate analysis
    source VARCHAR(20) NOT NULL, -- 'api', 'file', 'manual'
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of UUID REFERENCES activities(id), -- Points to original if duplicate detected
    
    -- AI-parsed notes
    notes TEXT,
    parsed_notes JSONB, -- AI-extracted structured data from notes
    
    -- MongoDB reference
    raw_data_id VARCHAR(255), -- MongoDB ObjectId for raw_activities document
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT check_end_after_start CHECK (end_time > start_time)
);

CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_start_time ON activities(start_time DESC);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_external_id ON activities(provider_account_id, external_id);
CREATE INDEX idx_activities_duplicate ON activities(is_duplicate) WHERE is_duplicate = FALSE;
CREATE INDEX idx_activities_metrics ON activities USING GIN (metrics); -- GIN index for JSONB queries
```

**Rust Model**:
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
struct Activity {
    id: Uuid,
    user_id: Uuid,
    provider_account_id: Option<Uuid>,
    external_id: Option<String>,
    activity_type: String,
    start_time: DateTime<Utc>,
    end_time: DateTime<Utc>,
    duration_seconds: i32,
    metrics: ActivityMetrics, // JSONB
    gps_track: Option<Vec<GpsPoint>>, // JSONB
    source: ActivitySource,
    is_duplicate: bool,
    duplicate_of: Option<Uuid>,
    notes: Option<String>,
    parsed_notes: Option<ParsedNotes>, // JSONB
    raw_data_id: Option<String>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ActivityMetrics {
    distance_km: Option<f64>,
    heart_rate_avg: Option<f64>,
    heart_rate_max: Option<f64>,
    heart_rate_min: Option<f64>,
    calories: Option<i32>,
    steps: Option<i32>,
    elevation_gain_m: Option<f64>,
    pace_avg_min_per_km: Option<f64>,
    power_avg_watts: Option<f64>,
    cadence_avg_rpm: Option<f64>,
    // Extensible: add new metrics without schema migration
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct GpsPoint {
    lat: f64,
    lon: f64,
    ts: DateTime<Utc>,
    elevation_m: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Type)]
#[sqlx(type_name = "varchar")]
enum ActivitySource {
    Api,
    File,
    Manual,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ParsedNotes {
    exercises: Vec<Exercise>,
    intensity: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Exercise {
    name: String,
    sets: Option<i32>,
    reps: Option<i32>,
    weight_kg: Option<f64>,
}
```

**TypeScript Type**:
```typescript
interface Activity {
  id: string;
  userId: string;
  providerAccountId?: string;
  externalId?: string;
  activityType: string;
  startTime: string;
  endTime: string;
  durationSeconds: number;
  metrics: ActivityMetrics;
  gpsTrack?: GpsPoint[];
  source: 'api' | 'file' | 'manual';
  isDuplicate: boolean;
  duplicateOf?: string;
  notes?: string;
  parsedNotes?: ParsedNotes;
  rawDataId?: string;
  createdAt: string;
  updatedAt: string;
}

interface ActivityMetrics {
  distanceKm?: number;
  heartRateAvg?: number;
  heartRateMax?: number;
  heartRateMin?: number;
  calories?: number;
  steps?: number;
  elevationGainM?: number;
  paceAvgMinPerKm?: number;
  powerAvgWatts?: number;
  cadenceAvgRpm?: number;
  [key: string]: number | undefined; // Extensible
}

interface GpsPoint {
  lat: number;
  lon: number;
  ts: string;
  elevationM?: number;
}

interface ParsedNotes {
  exercises: Exercise[];
  intensity?: string;
}

interface Exercise {
  name: string;
  sets?: number;
  reps?: number;
  weightKg?: number;
}
```

---

### 4. Workout

**Purpose**: Represents structured exercise data (strength training, HIIT, etc.).

**PostgreSQL Schema**:
```sql
CREATE TABLE workouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    workout_type VARCHAR(50) NOT NULL, -- 'strength', 'hiit', 'cardio', 'yoga', 'stretching'
    duration_seconds INT NOT NULL,
    intensity VARCHAR(20), -- 'low', 'moderate', 'high', 'vigorous'
    exercises JSONB NOT NULL, -- Array of Exercise objects
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_workouts_activity_id ON workouts(activity_id);
CREATE INDEX idx_workouts_type ON workouts(workout_type);
CREATE INDEX idx_workouts_exercises ON workouts USING GIN (exercises);
```

**Rust Model**:
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
struct Workout {
    id: Uuid,
    activity_id: Uuid,
    workout_type: String,
    duration_seconds: i32,
    intensity: Option<String>,
    exercises: Vec<Exercise>, // JSONB
    notes: Option<String>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}
```

**TypeScript Type**:
```typescript
interface Workout {
  id: string;
  activityId: string;
  workoutType: 'strength' | 'hiit' | 'cardio' | 'yoga' | 'stretching';
  durationSeconds: number;
  intensity?: 'low' | 'moderate' | 'high' | 'vigorous';
  exercises: Exercise[];
  notes?: string;
  createdAt: string;
  updatedAt: string;
}
```

---

### 5. SupplementalData

**Purpose**: Represents weather, altitude, and air quality data enriching activities.

**PostgreSQL Schema**:
```sql
CREATE TABLE supplemental_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    activity_id UUID NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    
    -- Weather data
    temperature_celsius FLOAT,
    humidity_percent FLOAT,
    weather_description VARCHAR(100), -- 'clear', 'cloudy', 'rainy', 'snowy'
    wind_speed_kmh FLOAT,
    air_quality_index INT, -- 0-500 scale
    
    -- Location data
    altitude_m FLOAT,
    location_lat FLOAT,
    location_lon FLOAT,
    
    -- Source tracking
    source_api VARCHAR(50), -- 'openweathermap', 'open-meteo'
    source_timestamp TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_activity_supplement UNIQUE (activity_id)
);

CREATE INDEX idx_supplemental_data_activity_id ON supplemental_data(activity_id);
```

**Rust Model**:
```rust
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
struct SupplementalData {
    id: Uuid,
    activity_id: Uuid,
    temperature_celsius: Option<f64>,
    humidity_percent: Option<f64>,
    weather_description: Option<String>,
    wind_speed_kmh: Option<f64>,
    air_quality_index: Option<i32>,
    altitude_m: Option<f64>,
    location_lat: Option<f64>,
    location_lon: Option<f64>,
    source_api: String,
    source_timestamp: DateTime<Utc>,
    created_at: DateTime<Utc>,
}
```

**TypeScript Type**:
```typescript
interface SupplementalData {
  id: string;
  activityId: string;
  temperatureCelsius?: number;
  humidityPercent?: number;
  weatherDescription?: string;
  windSpeedKmh?: number;
  airQualityIndex?: number;
  altitudeM?: number;
  locationLat?: number;
  locationLon?: number;
  sourceApi: string;
  sourceTimestamp: string;
  createdAt: string;
}
```

---

## Entity Relationships

```text
┌──────────────┐
│    User      │
└──────┬───────┘
       │ 1
       │
       │ N
┌──────▼──────────────┐          ┌──────────────────┐
│ ProviderAccount     │          │   Activity       │
│                     │          │                  │
│ - provider_name     │          │ - activity_type  │
│ - access_token      │          │ - metrics (JSONB)│
│ - sync_enabled      │          │ - gps_track      │
└─────────────────────┘          │ - is_duplicate   │
       │ 1                       │ - notes          │
       │                         └────────┬─────────┘
       │ N                                │ 1
       └────────────────────────┐         │
                                │         │ 1
                         ┌──────▼─────────▼───────┐
                         │   Activity (continued) │
                         └────────┬───────┬────────┘
                                  │       │
                          ┌───────┘       └────────┐
                          │ 1                      │ 1
                          │                        │
                   ┌──────▼────────┐      ┌────────▼────────────┐
                   │    Workout    │      │ SupplementalData    │
                   │               │      │                     │
                   │ - exercises   │      │ - weather           │
                   │   (JSONB)     │      │ - altitude          │
                   └───────────────┘      └─────────────────────┘
```

**Cardinality**:
- **User** → **ProviderAccount**: 1:N (one user, many connected providers)
- **User** → **Activity**: 1:N (one user, many activities)
- **ProviderAccount** → **Activity**: 1:N (one provider, many imported activities)
- **Activity** → **Workout**: 1:1 (optional, only for structured workouts)
- **Activity** → **SupplementalData**: 1:1 (optional, only for activities with GPS/time)
- **Activity** → **Activity** (duplicate_of): 1:1 (self-referential for duplicate tracking)

---

## Data Flow

### 1. OAuth2 Provider Connection

```text
User → Frontend → Backend → Provider OAuth2 Endpoint
                    ↓
              Exchange code for tokens
                    ↓
              Encrypt tokens (AES-256-GCM)
                    ↓
         Store in provider_accounts table
                    ↓
              Return success to frontend
```

### 2. Activity Ingestion (API)

```text
Background Sync Job → Provider API (GET /activities)
         ↓
   Store raw JSON in MongoDB raw_activities (time-series)
         ↓
   Trigger ETL pipeline (Python/Go job)
         ↓
   Normalize data (map fields, validate schema)
         ↓
   Check for duplicates (hash provider + external_id + start_time)
         ↓
   Store normalized activity in PostgreSQL activities table
         ↓
   If notes exist → Call AI service → Store parsed_notes
         ↓
   Queue for enrichment (mark enrichment_status = 'pending')
```

### 3. Data Enrichment (Weather/Altitude)

```text
Background Enrichment Job → Query pending activities (PostgreSQL)
         ↓
   Batch by location/time (reduce API calls)
         ↓
   Call weather API (OpenWeatherMap, Open-Meteo)
         ↓
   Store in supplemental_data table
         ↓
   Update enrichment_status = 'completed' or 'failed'
```

### 4. Dashboard Query

```text
Frontend → GET /api/v1/activities?start=X&end=Y
         ↓
   Check Valkey cache (key: dashboard:user_id:start:end)
         ↓
   Cache HIT → Return cached data (p99 < 50ms)
         ↓
   Cache MISS → Query PostgreSQL with indexes
         ↓
   Join activities + supplemental_data (LEFT JOIN)
         ↓
   Cache result in Valkey (TTL 5 minutes)
         ↓
   Return to frontend (p99 < 200ms)
```

---

## Migration Strategy

### Initial Schema Setup

**Order**: Create tables in dependency order to satisfy foreign keys.

```sql
-- Step 1: Create users table (no dependencies)
CREATE TABLE users (...);

-- Step 2: Create provider_accounts table (depends on users)
CREATE TABLE provider_accounts (...);

-- Step 3: Create activities table (depends on users, provider_accounts)
CREATE TABLE activities (...);

-- Step 4: Create workouts table (depends on activities)
CREATE TABLE workouts (...);

-- Step 5: Create supplemental_data table (depends on activities)
CREATE TABLE supplemental_data (...);
```

### Adding New Metrics (Non-Breaking)

**Example**: Add "blood_oxygen_percent" to activities.metrics.

```sql
-- No schema migration needed! JSONB is flexible.
-- Just update application code to handle new field.
```

### Adding New Provider (Non-Breaking)

**Example**: Add "Whoop" provider.

```sql
-- No schema migration needed! provider_name is VARCHAR.
-- Just update application code to add 'whoop' enum variant.
```

### Breaking Changes (Rare)

**Example**: Split `activities.metrics` JSONB into separate columns (heart_rate, calories, etc.).

```sql
-- Step 1: Add new columns with default values
ALTER TABLE activities ADD COLUMN heart_rate_avg INT;
ALTER TABLE activities ADD COLUMN calories INT;

-- Step 2: Backfill data from JSONB
UPDATE activities 
SET heart_rate_avg = (metrics->>'heart_rate_avg')::int,
    calories = (metrics->>'calories')::int;

-- Step 3: Deploy new application version (reads from new columns)
-- Step 4: Drop old JSONB column (after data validation)
ALTER TABLE activities DROP COLUMN metrics;
```

---

## Data Retention & GDPR Compliance

### Retention Policy

- **User Data**: Retained indefinitely until user deletes account or requests deletion (per FR-009).
- **Activity Data**: Same as user data (tied to user lifecycle).
- **Raw Data (MongoDB)**: Retained for 90 days, then purged (configurable per provider).

### Deletion Workflow (GDPR Right to Erasure)

```text
User Requests Deletion → Backend receives DELETE /api/v1/users/:id
         ↓
   Soft delete user (set deleted_at = NOW())
         ↓
   Cascade delete activities, workouts, supplemental_data (ON DELETE CASCADE)
         ↓
   Delete provider_accounts (revoke OAuth2 tokens)
         ↓
   Delete raw data from MongoDB (raw_activities where metadata.user_id = ...)
         ↓
   Purge Valkey cache (keys: dashboard:user_id:*)
         ↓
   Return 204 No Content to frontend
```

---

## Performance Optimizations

### 1. Composite Indexes

```sql
-- Optimize dashboard query (user_id + start_time range)
CREATE INDEX idx_activities_user_time ON activities(user_id, start_time DESC);

-- Optimize duplicate detection (provider + external_id)
CREATE INDEX idx_activities_dedup ON activities(provider_account_id, external_id);
```

### 2. Partial Indexes

```sql
-- Index only non-duplicate activities (faster queries)
CREATE INDEX idx_activities_non_duplicate ON activities(user_id, start_time DESC) 
WHERE is_duplicate = FALSE;

-- Index only active users (exclude soft-deleted)
CREATE INDEX idx_users_active ON users(id) 
WHERE deleted_at IS NULL;
```

### 3. JSONB Indexing

```sql
-- GIN index for JSONB metrics (enables fast queries like "find activities with heart_rate > 150")
CREATE INDEX idx_activities_metrics_gin ON activities USING GIN (metrics);

-- Example query:
SELECT * FROM activities 
WHERE metrics->>'heart_rate_avg' > '150';
```

### 4. Materialized Views (Future Optimization)

```sql
-- Pre-aggregate dashboard stats (daily summaries)
CREATE MATERIALIZED VIEW daily_activity_summary AS
SELECT 
    user_id,
    DATE(start_time) AS activity_date,
    COUNT(*) AS activity_count,
    SUM((metrics->>'calories')::int) AS total_calories,
    SUM((metrics->>'distance_km')::float) AS total_distance_km
FROM activities
WHERE is_duplicate = FALSE
GROUP BY user_id, DATE(start_time);

-- Refresh daily (cron job)
REFRESH MATERIALIZED VIEW daily_activity_summary;
```

---

## Conclusion

This data model supports the muskul.ai platform's requirements for **flexibility** (JSONB for varying metrics), **performance** (indexes, caching, time-series collections), **scalability** (multi-tier storage, horizontal sharding), and **compliance** (soft deletes, GDPR erasure). The PostgreSQL schema enforces referential integrity while allowing schema evolution without migrations (via JSONB). MongoDB preserves raw provider data for auditing and reprocessing. Valkey caches hot data for sub-second dashboard loads.

**Next Steps**: Generate API contracts (`contracts/`) and quickstart guide (`quickstart.md`).
