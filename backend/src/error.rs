use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use thiserror::Error;

pub type Result<T> = std::result::Result<T, Error>;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("MongoDB error: {0}")]
    MongoDB(#[from] mongodb::error::Error),

    #[error("HTTP client error: {0}")]
    HttpClient(#[from] reqwest::Error),

    #[error("Authentication error: {0}")]
    Auth(String),

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Conflict: {0}")]
    Conflict(String),

    #[error("External provider error: {0}")]
    Provider(String),

    #[error("Configuration error: {0}")]
    Config(String),

    #[error("Internal error: {0}")]
    Internal(String),
}

impl IntoResponse for Error {
    fn into_response(self) -> Response {
        let (status, error_message) = match self {
            Error::Database(ref e) => {
                tracing::error!("Database error: {:?}", e);
                (StatusCode::INTERNAL_SERVER_ERROR, "Database error")
            }
            Error::MongoDB(ref e) => {
                tracing::error!("MongoDB error: {:?}", e);
                (StatusCode::INTERNAL_SERVER_ERROR, "Database error")
            }
            Error::HttpClient(ref e) => {
                tracing::error!("HTTP client error: {:?}", e);
                (StatusCode::BAD_GATEWAY, "External service error")
            }
            Error::Auth(_) => (StatusCode::UNAUTHORIZED, "Authentication failed"),
            Error::Validation(_) => (StatusCode::BAD_REQUEST, "Validation error"),
            Error::NotFound(_) => (StatusCode::NOT_FOUND, "Resource not found"),
            Error::Conflict(_) => (StatusCode::CONFLICT, "Resource conflict"),
            Error::Provider(_) => (StatusCode::BAD_GATEWAY, "Provider error"),
            Error::Config(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Configuration error"),
            Error::Internal(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Internal error"),
        };

        let body = Json(json!({
            "error": error_message,
            "message": self.to_string(),
        }));

        (status, body).into_response()
    }
}
