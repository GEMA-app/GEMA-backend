"""Configuración de la aplicación: settings y logging."""

from app.infrastructure.config.logger import setup_logging
from app.infrastructure.config.settings import Settings, settings

__all__ = [
    "Settings",
    "settings",
    "setup_logging",
]
