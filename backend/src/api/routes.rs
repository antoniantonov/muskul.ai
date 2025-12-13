use axum::Router;

/// Builds the complete API router with all endpoints
pub fn api_router() -> Router {
    Router::new()
    // Routes will be added as implementation progresses:
    // .nest("/activities", activities::routes())
    // .nest("/auth", auth::routes())
    // .nest("/providers", providers::routes())
    // .nest("/sync", sync::routes())
}
