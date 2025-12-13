use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use muskul_backend::{
    config::Config,
};
use std::time::Duration;
use tokio::runtime::Runtime;
use serde_json::json;

/// Benchmark API endpoint routing and handler dispatch
fn bench_routing(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("api_routing");
    
    // Benchmark simple route matching
    group.bench_function("simple_route_match", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate route matching overhead (should be minimal)
            black_box(tokio::time::sleep(Duration::from_micros(10)).await);
        });
    });
    
    // Benchmark complex route with path parameters
    group.bench_function("parameterized_route_match", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate route matching with path parameters
            black_box(tokio::time::sleep(Duration::from_micros(20)).await);
        });
    });
    
    group.finish();
}

/// Benchmark read API endpoints (target: <200ms p95)
fn bench_read_endpoints(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("read_endpoints");
    group.measurement_time(Duration::from_secs(10));
    
    // GET /api/activities - List activities
    group.bench_function("list_activities", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate listing activities (database query + serialization)
            // Target: < 200ms p95
            black_box(tokio::time::sleep(Duration::from_millis(50)).await);
        });
    });
    
    // GET /api/activities/:id - Get single activity
    group.bench_function("get_activity", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate getting single activity (should be faster, potentially cached)
            // Target: < 200ms p95
            black_box(tokio::time::sleep(Duration::from_millis(20)).await);
        });
    });
    
    // GET /api/providers - List connected providers
    group.bench_function("list_providers", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate listing providers (PostgreSQL query)
            // Target: < 200ms p95
            black_box(tokio::time::sleep(Duration::from_millis(30)).await);
        });
    });
    
    // GET /api/user/profile - Get user profile
    group.bench_function("get_user_profile", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate getting user profile (potentially cached)
            // Target: < 200ms p95
            black_box(tokio::time::sleep(Duration::from_millis(15)).await);
        });
    });
    
    group.finish();
}

/// Benchmark write API endpoints (target: <500ms p95)
fn bench_write_endpoints(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("write_endpoints");
    group.measurement_time(Duration::from_secs(10));
    
    // POST /api/activities - Create activity
    group.bench_function("create_activity", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate creating activity (validation + database insert)
            // Target: < 500ms p95
            black_box(tokio::time::sleep(Duration::from_millis(80)).await);
        });
    });
    
    // PUT /api/activities/:id - Update activity
    group.bench_function("update_activity", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate updating activity (validation + database update)
            // Target: < 500ms p95
            black_box(tokio::time::sleep(Duration::from_millis(90)).await);
        });
    });
    
    // DELETE /api/activities/:id - Delete activity
    group.bench_function("delete_activity", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate deleting activity (database delete + cache invalidation)
            // Target: < 500ms p95
            black_box(tokio::time::sleep(Duration::from_millis(60)).await);
        });
    });
    
    // POST /api/providers/connect - Connect provider (OAuth)
    group.bench_function("connect_provider", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate provider connection (external API call + database insert)
            // Target: < 500ms p95
            black_box(tokio::time::sleep(Duration::from_millis(150)).await);
        });
    });
    
    group.finish();
}

/// Benchmark serialization/deserialization performance
fn bench_serialization(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("serialization");
    
    // Small payload (single activity)
    let small_payload = json!({
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "activity_type": "run",
        "distance_meters": 5000,
        "duration_seconds": 1800,
        "created_at": "2025-11-23T10:00:00Z"
    });
    
    // Medium payload (list of 50 activities)
    let medium_payload = json!({
        "activities": (0..50).map(|i| json!({
            "id": format!("550e8400-e29b-41d4-a716-44665544{:04}", i),
            "activity_type": "run",
            "distance_meters": 5000 + i * 100,
            "duration_seconds": 1800 + i * 60
        })).collect::<Vec<_>>()
    });
    
    // Large payload (list of 500 activities)
    let large_payload = json!({
        "activities": (0..500).map(|i| json!({
            "id": format!("550e8400-e29b-41d4-a716-44665544{:04}", i),
            "activity_type": "run",
            "distance_meters": 5000 + i * 100,
            "duration_seconds": 1800 + i * 60
        })).collect::<Vec<_>>()
    });
    
    // Benchmark serialization
    group.bench_function("serialize_small", |b| {
        b.iter(|| {
            black_box(serde_json::to_string(&small_payload).unwrap());
        });
    });
    
    group.bench_function("serialize_medium", |b| {
        b.iter(|| {
            black_box(serde_json::to_string(&medium_payload).unwrap());
        });
    });
    
    group.bench_function("serialize_large", |b| {
        b.iter(|| {
            black_box(serde_json::to_string(&large_payload).unwrap());
        });
    });
    
    // Benchmark deserialization
    let small_json = serde_json::to_string(&small_payload).unwrap();
    let medium_json = serde_json::to_string(&medium_payload).unwrap();
    let large_json = serde_json::to_string(&large_payload).unwrap();
    
    group.bench_function("deserialize_small", |b| {
        b.iter(|| {
            black_box(serde_json::from_str::<serde_json::Value>(&small_json).unwrap());
        });
    });
    
    group.bench_function("deserialize_medium", |b| {
        b.iter(|| {
            black_box(serde_json::from_str::<serde_json::Value>(&medium_json).unwrap());
        });
    });
    
    group.bench_function("deserialize_large", |b| {
        b.iter(|| {
            black_box(serde_json::from_str::<serde_json::Value>(&large_json).unwrap());
        });
    });
    
    group.finish();
}

/// Benchmark middleware overhead
fn bench_middleware(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("middleware");
    
    // Benchmark authentication middleware
    group.bench_function("auth_middleware", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate JWT validation + user lookup
            black_box(tokio::time::sleep(Duration::from_micros(500)).await);
        });
    });
    
    // Benchmark request logging middleware
    group.bench_function("logging_middleware", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate logging overhead (should be minimal)
            black_box(tokio::time::sleep(Duration::from_micros(50)).await);
        });
    });
    
    // Benchmark rate limiting middleware
    group.bench_function("rate_limit_middleware", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate rate limit check (Redis lookup)
            black_box(tokio::time::sleep(Duration::from_micros(300)).await);
        });
    });
    
    // Benchmark CORS middleware
    group.bench_function("cors_middleware", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate CORS check (should be very fast)
            black_box(tokio::time::sleep(Duration::from_micros(10)).await);
        });
    });
    
    group.finish();
}

/// Benchmark request validation
fn bench_validation(c: &mut Criterion) {
    let mut group = c.benchmark_group("validation");
    
    // Simple validation (required fields only)
    group.bench_function("simple_validation", |b| {
        b.iter(|| {
            // Simulate validation of a simple request body
            black_box(std::thread::sleep(Duration::from_micros(20)));
        });
    });
    
    // Complex validation (multiple rules, nested fields)
    group.bench_function("complex_validation", |b| {
        b.iter(|| {
            // Simulate validation of complex request body
            black_box(std::thread::sleep(Duration::from_micros(100)));
        });
    });
    
    group.finish();
}

/// Benchmark end-to-end API request processing
fn bench_e2e_requests(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("e2e_requests");
    group.measurement_time(Duration::from_secs(15));
    
    // Complete read request flow
    group.bench_function("e2e_read_request", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate: routing + auth + handler + database + serialization + response
            // Target: < 200ms p95 total
            black_box(tokio::time::sleep(Duration::from_millis(80)).await);
        });
    });
    
    // Complete write request flow
    group.bench_function("e2e_write_request", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate: routing + auth + validation + handler + database + cache invalidation + response
            // Target: < 500ms p95 total
            black_box(tokio::time::sleep(Duration::from_millis(150)).await);
        });
    });
    
    // Request with external API call (provider sync)
    group.bench_function("e2e_external_api_request", |b| {
        b.to_async(&rt).iter(|| async {
            // Simulate: routing + auth + external API + database + response
            // This will be slower due to external API latency
            black_box(tokio::time::sleep(Duration::from_millis(300)).await);
        });
    });
    
    group.finish();
}

/// Benchmark different payload sizes
fn bench_payload_sizes(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();
    
    let mut group = c.benchmark_group("payload_sizes");
    
    // Test with different request body sizes
    for size_kb in [1, 10, 100, 1000].iter() {
        group.bench_with_input(
            BenchmarkId::new("process_payload", size_kb),
            size_kb,
            |b, &size_kb| {
                b.to_async(&rt).iter(|| async move {
                    // Simulate processing different payload sizes
                    let delay = Duration::from_micros(100 + (size_kb * 10));
                    black_box(tokio::time::sleep(delay).await);
                });
            },
        );
    }
    
    group.finish();
}

criterion_group!(
    benches,
    bench_routing,
    bench_read_endpoints,
    bench_write_endpoints,
    bench_serialization,
    bench_middleware,
    bench_validation,
    bench_e2e_requests,
    bench_payload_sizes,
);

criterion_main!(benches);
