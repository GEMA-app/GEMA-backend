from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.domain.exceptions import (
    DomainException,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserInactiveError,
    WeakPasswordError,
)
from app.presentation.api.v1.schemas.jsonapi_base import (
    ErrorObject,
    ErrorSource,
    JsonApiErrorDocument,
)


def jsonapi_response(
    status_code: int, errors: list[ErrorObject], headers: Optional[dict[str, str]] = None
) -> JSONResponse:
    """Genera una respuesta JSONResponse formateada estrictamente bajo la especificación JSON:API."""
    doc = JsonApiErrorDocument(errors=errors)
    return JSONResponse(
        status_code=status_code,
        content=doc.model_dump(exclude_none=True),
        headers={"Content-Type": "application/vnd.api+json", **(headers or {})},
    )


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Mapea excepciones del dominio a códigos HTTP y formato JSON:API."""
    assert isinstance(exc, DomainException)
    status_code = status.HTTP_400_BAD_REQUEST
    code = "ERR_DOMAIN"

    if isinstance(exc, WeakPasswordError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        code = "ERR_WEAK_PASSWORD"
    elif isinstance(exc, InvalidEmailError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        code = "ERR_INVALID_EMAIL"
    elif isinstance(exc, UserAlreadyExistsError):
        status_code = status.HTTP_409_CONFLICT
        code = "ERR_USER_ALREADY_EXISTS"
    elif isinstance(exc, InvalidCredentialsError):
        status_code = status.HTTP_401_UNAUTHORIZED
        code = "ERR_INVALID_CREDENTIALS"
    elif isinstance(exc, UserInactiveError):
        status_code = status.HTTP_403_FORBIDDEN
        code = "ERR_USER_INACTIVE"
    elif isinstance(exc, InvalidTokenError):
        status_code = status.HTTP_401_UNAUTHORIZED
        code = "ERR_INVALID_TOKEN"

    error = ErrorObject(
        status=str(status_code),
        code=code,
        title=exc.__class__.__name__,
        detail=str(exc),
    )
    return jsonapi_response(status_code, [error])


async def request_validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Mapea errores de validación de Pydantic/FastAPI al formato de error de JSON:API con JSON Pointers."""
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


async def starlette_http_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Mapea excepciones HTTP genéricas de Starlette al formato JSON:API."""
    assert isinstance(exc, StarletteHTTPException)
    error = ErrorObject(
        status=str(exc.status_code),
        code=f"HTTP_{exc.status_code}",
        title=exc.detail,
        detail=exc.detail,
    )
    return jsonapi_response(exc.status_code, [error], headers=exc.headers)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones en la aplicación FastAPI."""
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
