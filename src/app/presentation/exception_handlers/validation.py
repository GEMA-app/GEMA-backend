"""Manejador de errores de validación de Pydantic (RequestValidationError).
Convierte errores de validación en una respuesta JSON:API con la
lista de errores campo por campo.
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject, ErrorSource
from app.presentation.exception_handlers.base import jsonapi_response


async def request_validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Mapea errores de validación de Pydantic/FastAPI al formato de JSON:API."""
    assert isinstance(exc, RequestValidationError)
    errors = []
    for err in exc.errors():
        loc = err.get("loc", [])
        pointer = "/".join([str(x) for x in loc])
        if not pointer.startswith("/"):
            pointer = f"/{pointer}"
        errors.append(
            ErrorObject(
                status=str(status.HTTP_422_UNPROCESSABLE_ENTITY),
                code="ERR_VALIDATION",
                title="Error de validación en la solicitud",
                detail=err.get("msg"),
                source=ErrorSource(pointer=pointer),
            )
        )
    return jsonapi_response(status.HTTP_422_UNPROCESSABLE_ENTITY, errors)
