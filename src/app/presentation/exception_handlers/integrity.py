"""Manejador para IntegrityError de SQLAlchemy.

Mapea violaciones de restricciones de integridad a respuestas JSON:API
con códigos HTTP apropiados. Soporta asyncpg y otros drivers.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import AssetCodeExistsError, AssetSerialExistsError, CompanySlugExistsError
from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers.base import jsonapi_response
from app.presentation.exception_handlers.domain import domain_exception_handler


def _extract_constraint_name(exc: IntegrityError) -> str | None:
    """Extrae el nombre del constraint violado de forma driver-agnostic.

    Estrategias en orden de precisión:
    1. __cause__.constraint_name — para compatibilidad con mocks de test
    2. constraint_name directamente en exc.orig — asyncpg nativo en producción
    3. String parsing sobre str(exc.orig) — fallback para todos los drivers
    """
    # Estrategia 1: via __cause__ (para compatibilidad con tests)
    cause = getattr(exc.orig, "__cause__", None)
    if cause:
        name = getattr(cause, "constraint_name", None)
        if name and isinstance(name, str):
            return name

    # Estrategia 1b: asyncpg nativo directamente en exc.orig en producción
    constraint_name = getattr(exc.orig, "constraint_name", None)
    if constraint_name and isinstance(constraint_name, str):
        return constraint_name

    # Estrategia 2: Fallback robusto — str() contiene el nombre del constraint
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
    constraint_name = _extract_constraint_name(exc)

    if constraint_name:
        if "codigo_activo" in constraint_name:
            return await domain_exception_handler(
                request,
                AssetCodeExistsError(
                    "Ya existe un activo con ese código en la empresa."
                ),
            )

        if "serial_interno" in constraint_name:
            return await domain_exception_handler(
                request,
                AssetSerialExistsError(
                    "Ya existe un activo con ese número de serie en la empresa."
                ),
            )

        if "slug" in constraint_name or "empresas_slug_key" in constraint_name:
            return await domain_exception_handler(
                request,
                CompanySlugExistsError("El slug identificador de empresa ya existe."),
            )

    # Fallback genérico mapeado por SQLSTATE si está disponible
    status_code = status.HTTP_409_CONFLICT
    detail = "La operación viola una restricción de unicidad en la persistencia."

    if hasattr(exc.orig, "sqlstate"):
        sqlstate = exc.orig.sqlstate
        if sqlstate == "23503":
            detail = "Referencia inválida: el recurso relacionado no existe"
        elif sqlstate == "23502":
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            detail = "Campo obligatorio sin valor"
        elif sqlstate == "23505":
            detail = "El registro ya existe (violación de unicidad)."

    error = ErrorObject(
        status=str(status_code),
        code="ERR_DB_INTEGRITY",
        title="Conflicto de integridad en base de datos",
        detail=detail,
    )
    return jsonapi_response(status_code, [error])
