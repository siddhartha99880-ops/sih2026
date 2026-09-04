from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = False
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/land_intelligence"
    secret_key: str = "replace_me"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()