from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    log_level: str = "INFO"
    ai_service_host: str = "0.0.0.0"
    ai_service_port: int = 8001
    llm_provider: str = "mock"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    chroma_url: str = "http://chromadb:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

