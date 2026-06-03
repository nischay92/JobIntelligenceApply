from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://applywise:applywise_local_password@postgres:5432/applywise"
    backend_api_url: str = "http://backend:8000"
    ai_service_url: str = "http://ai-service:8001"
    scheduler_timezone: str = "America/Indiana/Indianapolis"
    scheduler_discovery_enabled: bool = False
    scheduler_digests_enabled: bool = False
    discovery_sources: str = "sample"
    discovery_board_tokens: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
