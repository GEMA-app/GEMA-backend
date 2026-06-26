"""Manejadores globales de excepciones para la aplicación FastAPI.

Re-exporta los símbolos públicos para mantener compatibilidad.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import DomainException
from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
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
    "generic_exception_handler",
    "register_exception_handlers",
]


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador genérico para excepciones no capturadas (500 Internal Server Error).

    Args:
        request: Objeto de solicitud FastAPI.
        exc: Excepción no capturada.

    Returns:
        Respuesta JSON:API con código de error 500.
    """
    error = ErrorObject(
        status=str(status.HTTP_500_INTERNAL_SERVER_ERROR),
        code="ERR_INTERNAL_SERVER_ERROR",
        title="Error interno del servidor",
        detail="Ha ocurrido un error inesperado. Intenta nuevamente más tarde.",
    )
    return jsonapi_response(status.HTTP_500_INTERNAL_SERVER_ERROR, [error])


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones en la aplicación FastAPI."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)
