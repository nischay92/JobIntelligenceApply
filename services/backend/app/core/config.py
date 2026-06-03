from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://applywise:applywise_local_password@postgres:5432/applywise"
    ai_service_url: str = "http://ai-service:8001"
    chroma_url: str = "http://chromadb:8000"
    session_secret: str = "replace-with-local-dev-secret"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    frontend_url: str = "http://localhost:5173"
    session_cookie_name: str = "applywise_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 7
    upload_storage_dir: str = "uploads"
    max_upload_size_bytes: int = 5 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
