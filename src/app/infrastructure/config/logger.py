"""Configuración del sistema de logging estructurado con structlog."""

import logging

import structlog


def setup_logging(app_env: str) -> None:
    """Configura structlog y el logging estándar según el entorno de la aplicación.

    Args:
        app_env: Entorno de la aplicación ('development', 'production', etc.).
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
            if app_env == "development"
            else structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()
