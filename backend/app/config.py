"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Values are loaded from environment variables and/or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- Application -----
    app_name: str = "AI Interviewer"
    environment: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # ----- Database -----
    database_url: str = (
        "postgresql+asyncpg://ai_interviewer:localdev@localhost:5432/ai_interviewer"
    )
    database_echo: bool = False

    # ----- Firebase -----
    firebase_project_id: str = ""
    google_application_credentials: str = ""

    # ----- CORS -----
    cors_origins: str = "http://localhost:3000"

    # ----- Storage -----
    storage_backend: str = "local"  # "local" or "s3"
    local_storage_path: str = "./uploads"
    s3_bucket: str = ""
    s3_endpoint: str = ""
    s3_region: str = "us-east-1"

    # ----- LLM -----
    llm_provider: str = "gemini"
    llm_api_key: str = ""
    llm_model: str = "gemini-2.5-flash"

    # ----- Monitoring -----
    sentry_dsn: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


# Singleton instance
settings = Settings()
