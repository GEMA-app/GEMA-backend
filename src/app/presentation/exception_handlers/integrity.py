"""Manejador para IntegrityError de SQLAlchemy.

Mapea violaciones de restricciones de unicidad a respuestas JSON:API
con código HTTP 409 Conflict. Usa doble mecanismo de parsing:
1. __cause__.constraint_name (asyncpg nativo)
2. str(exc.orig) fallback (todos los drivers)
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import AssetCodeExistsError, AssetSerialExistsError
from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers.base import jsonapi_response
from app.presentation.exception_handlers.domain import domain_exception_handler


def _extract_constraint_name(exc: IntegrityError) -> str | None:
    """Extrae el nombre del constraint violado de forma driver-agnostic.

    Estrategias en orden de precisión:
    1. __cause__.constraint_name — asyncpg expone el nombre directamente
    2. String parsing sobre str(exc.orig) — PostgreSQL siempre incluye
       el nombre del constraint entre comillas en el mensaje de error
    """
    # Estrategia 1: asyncpg nativo via __cause__
    cause = getattr(exc.orig, "__cause__", None)
    if cause:
        name = getattr(cause, "constraint_name", None)
        if name:
            return name  # type: ignore[no-any-return]

    # Estrategia 2: Fallback robusto — str() contiene el nombre del constraint
    error_msg = str(exc.orig)
    for constraint_name in (
        "uq_activos_empresa_codigo_activo",
        "uq_activos_empresa_serial_interno",
        "uq_activos_empresa_codigo_activo_lower",
        "uq_activos_empresa_serial_interno_lower",
    ):
        if constraint_name in error_msg:
            return constraint_name

    return None


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    constraint_name = _extract_constraint_name(exc)

    if constraint_name and "codigo_activo" in constraint_name:
        return await domain_exception_handler(
            request,
            AssetCodeExistsError(
                "Ya existe un activo con ese código en la empresa."
            ),
        )

    if constraint_name and "serial_interno" in constraint_name:
        return await domain_exception_handler(
            request,
            AssetSerialExistsError(
                "Ya existe un activo con ese número de serie en la empresa."
            ),
        )

    # Fallback genérico para otros IntegrityErrors no mapeados
    error = ErrorObject(
        status=str(status.HTTP_409_CONFLICT),
        code="ERR_DB_INTEGRITY",
        title="Conflicto de integridad en base de datos",
        detail="La operación viola una restricción de unicidad en la persistencia.",
    )
    return jsonapi_response(status.HTTP_409_CONFLICT, [error])
