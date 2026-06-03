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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()

