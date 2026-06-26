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
from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers.base import jsonapi_response
from app.presentation.exception_handlers.domain import domain_exception_handler


def _map_integrity_error(exc: IntegrityError) -> tuple[int, str] | None:
    """Mapea IntegrityError a HTTP status + mensaje. Soporta asyncpg y otros drivers.

    Estrategia 1: Extracción por nombre de constraint (driver-agnostic, específico).
    Estrategia 2: Fallback por SQLSTATE (genérico, para casos no mapeados).
    """
    # Estrategia 1: Nombre de constraint (específico por dominio)
    constraint_name = _extract_constraint_name(exc)
    if constraint_name:
        if "codigo_activo" in constraint_name:
            return (409, "Ya existe un activo con ese código en la empresa.")
        if "serial_interno" in constraint_name:
            return (409, "Ya existe un activo con ese número de serie en la empresa.")
        if "slug" in constraint_name or "empresas_slug_key" in constraint_name:
            return (409, "El slug identificador de empresa ya existe.")

    # Estrategia 2: SQLSTATE directo (fallback genérico)
    if exc.orig is not None and hasattr(exc.orig, 'sqlstate'):
        sqlstate = getattr(exc.orig, 'sqlstate', None)
        mapping = {
            "23505": (409, "El registro ya existe"),
            "23503": (409, "Referencia inválida: el recurso relacionado no existe"),
            "23502": (422, "Campo obligatorio sin valor"),
        }
        if sqlstate in mapping:
            return mapping[sqlstate]

    return None


def _extract_constraint_name(exc: IntegrityError) -> str | None:
    """Extrae el nombre del constraint violado de forma driver-agnostic."""
    if exc.orig is None:
        return None
    # intentar directamente en exc.orig (asyncpg)
    constraint_name = getattr(exc.orig, "constraint_name", None)
    if constraint_name and isinstance(constraint_name, str):
        return str(constraint_name)

    # via __cause__ (para compatibilidad con mocks de test)
    cause = getattr(exc.orig, "__cause__", None)
    if cause:
        name = getattr(cause, "constraint_name", None)
        if name and isinstance(name, str):
            return str(name)

    # Fallback: string parsing
    error_msg = str(exc.orig)
    for name in (
        "uq_activos_empresa_codigo_activo",
        "uq_activos_empresa_serial_interno",
        "uq_activos_empresa_codigo_activo_lower",
        "uq_activos_empresa_serial_interno_lower",
        "empresas_slug_key",
    ):
        if name in error_msg:
            return name

    return None


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Manejador de excepciones de tipo IntegrityError para retornar JSON:API."""
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

    error = ErrorObject(
        status=str(status.HTTP_409_CONFLICT),
        code="ERR_DB_INTEGRITY",
        title="Conflicto de integridad en base de datos",
        detail="La operación viola una restricción de unicidad en la persistencia.",
    )
    return jsonapi_response(status.HTTP_409_CONFLICT, [error])
