use config::{Config, ConfigError, Environment, File};
use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
pub struct Settings {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub mongodb: MongoDbConfig,
    pub redis: RedisConfig,
    pub auth: AuthConfig,
    pub providers: ProvidersConfig,
    pub observability: ObservabilityConfig,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Deserialize, Clone)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub min_connections: u32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct MongoDbConfig {
    pub url: String,
    pub database: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct RedisConfig {
    pub url: String,
    pub max_connections: usize,
}

#[derive(Debug, Deserialize, Clone)]
pub struct AuthConfig {
    pub jwt_secret: String,
    pub jwt_expiration_hours: i64,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ProvidersConfig {
    pub strava: ProviderCredentials,
    pub garmin: ProviderCredentials,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ProviderCredentials {
    pub client_id: String,
    pub client_secret: String,
    pub redirect_uri: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ObservabilityConfig {
    pub otlp_endpoint: String,
    pub service_name: String,
}

impl Settings {
    pub fn new() -> Result<Self, ConfigError> {
        let run_mode = std::env::var("RUN_MODE").unwrap_or_else(|_| "development".into());

        let s = Config::builder()
            // Start with default configuration
            .add_source(File::with_name("config/default").required(false))
            // Add environment-specific configuration
            .add_source(File::with_name(&format!("config/{}", run_mode)).required(false))
            // Add local configuration (gitignored)
            .add_source(File::with_name("config/local").required(false))
            // Add environment variables (with MUSKUL_ prefix)
            .add_source(Environment::with_prefix("MUSKUL").separator("__"))
            .build()?;

        s.try_deserialize()
    }
}
