use axum::{
    response::{IntoResponse, Json},
    routing::get,
    Router,
};
use serde_json::json;
use std::net::SocketAddr;
use tower_http::{cors::CorsLayer, trace::TraceLayer};
use tracing::info;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "muskul_backend=debug,tower_http=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    info!("Starting muskul.ai backend service");

    // Build application router
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/", get(root))
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive());

    // Start server
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    info!("Listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}

async fn health_check() -> impl IntoResponse {
    Json(json!({
        "status": "healthy",
        "service": "muskul-backend",
        "version": env!("CARGO_PKG_VERSION")
    }))
}

async fn root() -> impl IntoResponse {
    Json(json!({
        "message": "Muskul.ai Backend API",
        "version": env!("CARGO_PKG_VERSION"),
        "docs": "/api/docs"
    }))
}
