from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación basada en Pydantic Settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="forbid", case_sensitive=False)

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_TITLE: str = "SIGMA Backend"
    APP_VERSION: str = "0.1.0"
    STRICT_JSONAPI: bool = True

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        app_env = info.data.get("APP_ENV", "development")
        if app_env == "production" and (v == "dev-secret-change-in-production" or len(v) < 32):
            raise ValueError("JWT_SECRET_KEY debe ser segura y no por defecto en producción")
        return v


settings = Settings()
