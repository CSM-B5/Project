from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NeuroAI Backend"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_upload_mb: int = 15

    database_url: str = "sqlite:///./storage/medvision.db"
    storage_dir: str = "storage"

    secret_key: str = ""
    access_token_minutes: int = 480
    allow_patient_registration: bool = True

    admin_email: str = ""
    admin_password: str = ""
    seed_demo_users: bool = False

    llm_provider: str = "mock"  # "mock" | "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
