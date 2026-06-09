"""Manejadores globales de excepciones para la aplicación FastAPI.

Re-exporta los símbolos públicos para mantener compatibilidad.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import DomainException
from app.presentation.exception_handlers.base import jsonapi_response
from app.presentation.exception_handlers.domain import domain_exception_handler
from app.presentation.exception_handlers.http import starlette_http_exception_handler
from app.presentation.exception_handlers.integrity import integrity_error_handler
from app.presentation.exception_handlers.validation import (
    request_validation_exception_handler,
)

__all__ = [
    "jsonapi_response",
    "domain_exception_handler",
    "request_validation_exception_handler",
    "starlette_http_exception_handler",
    "integrity_error_handler",
    "register_exception_handlers",
]


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones en la aplicación FastAPI."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # type: ignore[arg-type]
