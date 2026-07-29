"""Manejador para IntegrityError de SQLAlchemy.

Mapea violaciones de restricciones de integridad a respuestas JSON:API
con códigos HTTP apropiados. Soporta asyncpg y otros drivers.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import (
    AssetCodeExistsError,
    AssetSerialExistsError,
    CompanySlugExistsError,
)
from app.infrastructure.config.logger import logger
from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers.base import jsonapi_response
from app.presentation.exception_handlers.domain import domain_exception_handler

CONSTRAINT_MAP: dict[str, tuple[int, str]] = {
    "uq_activos_empresa_codigo_activo_lower": (
        409,
        "Ya existe un activo con ese código en la empresa.",
    ),
    "uq_activos_empresa_serial_interno_lower": (
        409,
        "Ya existe un activo con ese número de serie en la empresa.",
    ),
    "empresas_slug_key": (409, "El slug identificador de empresa ya existe."),
}

SQLSTATE_MAP: dict[str, tuple[int, str]] = {
    "23505": (409, "El registro ya existe."),
    "23503": (
        409,
        "No se puede eliminar este registro porque está en uso en otros "
        "módulos. Debes desvincular o eliminar los elementos asociados primero.",
    ),
    "23502": (422, "Campo obligatorio sin valor."),
}


def _map_integrity_error(exc: IntegrityError) -> tuple[int, str] | None:
    """Mapea IntegrityError a HTTP status + mensaje. Soporta asyncpg y otros drivers."""
    constraint_name = _extract_constraint_name(exc)
    if constraint_name and constraint_name in CONSTRAINT_MAP:
        return CONSTRAINT_MAP[constraint_name]

    if exc.orig is not None and hasattr(exc.orig, "sqlstate"):
        sqlstate = getattr(exc.orig, "sqlstate", None)
        if sqlstate in SQLSTATE_MAP:
            return SQLSTATE_MAP[sqlstate]

    return None


def _extract_constraint_name(exc: IntegrityError) -> str | None:
    """Extrae el nombre del constraint violado de forma driver-agnostic."""
    if exc.orig is None:
        return None
    constraint_name: str | None = getattr(exc.orig, "constraint_name", None)
    if isinstance(constraint_name, str):
        return constraint_name

    cause: object | None = getattr(exc.orig, "__cause__", None)
    if cause:
        name: str | None = getattr(cause, "constraint_name", None)
        if isinstance(name, str):
            return name

    error_msg = str(exc.orig)
    for name in CONSTRAINT_MAP:
        if name in error_msg:
            return name

    return None


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Manejador de excepciones de tipo IntegrityError para retornar JSON:API."""
    logger.error(
        "integrity_error",
        method=request.method,
        path=str(request.url.path),
        constraint=_extract_constraint_name(exc),
        orig=str(exc.orig)[:500],
    )

    result = _map_integrity_error(exc)

    if result:
        status_code, detail = result
        if "código" in detail:
            return await domain_exception_handler(
                request,
                AssetCodeExistsError(detail),
            )
        if "serial" in detail:
            return await domain_exception_handler(
                request,
                AssetSerialExistsError(detail),
            )
        if "slug" in detail:
            return await domain_exception_handler(
                request,
                CompanySlugExistsError(detail),
            )
        error = ErrorObject(
            status=str(status_code),
            code="ERR_DB_INTEGRITY",
            title="Conflicto de integridad en base de datos",
            detail=detail,
        )
        return jsonapi_response(status_code, [error])

    if request.method == "GET":
        error = ErrorObject(
            status=str(status.HTTP_500_INTERNAL_SERVER_ERROR),
            code="ERR_DATA_CORRUPTION",
            title="Error de integridad en lectura de datos",
            detail="Se detectó una inconsistencia en los datos. Contacte al administrador.",
        )
        return jsonapi_response(status.HTTP_500_INTERNAL_SERVER_ERROR, [error])

    error = ErrorObject(
        status=str(status.HTTP_409_CONFLICT),
        code="ERR_DB_INTEGRITY",
        title="Conflicto de integridad en base de datos",
        detail="La operación viola una restricción de unicidad en la persistencia.",
    )
    return jsonapi_response(status.HTTP_409_CONFLICT, [error])
