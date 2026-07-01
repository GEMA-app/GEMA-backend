"""Configuración centralizada de la aplicación usando Pydantic Settings."""

from pathlib import Path

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación basada en Pydantic Settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_TITLE: str = "GEMA Backend"
    APP_VERSION: str = "0.1.0"
    STRICT_JSONAPI: bool = True

    # --- Email / Notificaciones ---
    EMAIL_PROVIDER: str = "log"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USE_TLS: bool = False
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM_ADDRESS: str = "noreply@gema.unegia.com"
    EMAIL_FROM_NAME: str = "GEMA"
    EMAIL_TEMPLATES_DIR: Path = Path("src/app/infrastructure/notifications/templates")
    FRONTEND_URL: str = "http://localhost:3000"

    SUPER_ADMIN_IDS: list[str] = []

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Valida que la clave secreta JWT sea lo suficientemente segura en producción.

        Args:
            v: El valor de JWT_SECRET_KEY a validar.
            info: Información de contexto de la validación.

        Returns:
            La clave secreta validada.

        Raises:
            ValueError: Si el entorno es de producción y la clave no es segura.
        """
        app_env = info.data.get("APP_ENV", "development")
        if app_env == "production" and (v == "dev-secret-change-in-production" or len(v) < 32):
            raise ValueError("JWT_SECRET_KEY debe ser segura y no por defecto en producción")
        return v


settings = Settings()
