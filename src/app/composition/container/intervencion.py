"""Fábricas para el módulo de intervenciones técnicas."""

from fastapi import Depends

from app.application.use_cases.intervencion import (
    ActualizarIntervencionUseCase,
    CrearIntervencionUseCase,
    ListarIntervencionesUseCase,
    ObtenerIntervencionUseCase,
)
from app.infrastructure.uow import SqlAlchemyUnitOfWork


async def get_crear_intervencion_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(SqlAlchemyUnitOfWork),
) -> CrearIntervencionUseCase:
    """Fábrica para el caso de uso CrearIntervencion."""
    return CrearIntervencionUseCase(
        uow=uow,
        intervencion_repository=uow.intervenciones,
    )


async def get_listar_intervenciones_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(SqlAlchemyUnitOfWork),
) -> ListarIntervencionesUseCase:
    """Fábrica para el caso de uso ListarIntervenciones."""
    return ListarIntervencionesUseCase(
        uow=uow,
        intervencion_repository=uow.intervenciones,
    )


async def get_obtener_intervencion_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(SqlAlchemyUnitOfWork),
) -> ObtenerIntervencionUseCase:
    """Fábrica para el caso de uso ObtenerIntervencion."""
    return ObtenerIntervencionUseCase(
        uow=uow,
        intervencion_repository=uow.intervenciones,
    )


async def get_actualizar_intervencion_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(SqlAlchemyUnitOfWork),
) -> ActualizarIntervencionUseCase:
    """Fábrica para el caso de uso ActualizarIntervencion."""
    return ActualizarIntervencionUseCase(
        uow=uow,
        intervencion_repository=uow.intervenciones,
    )