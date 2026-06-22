# src/app/composition/container/repuesto_utilizado.py
from fastapi import Depends

from app.application.use_cases.repuesto_utilizado import (
    CreateRepuestoUtilizadoUseCase,
    DeleteRepuestoUtilizadoUseCase,
    GetRepuestoUtilizadoUseCase,
    ListRepuestosUtilizadosUseCase,
    UpdateRepuestoUtilizadoUseCase,
)
from app.composition.container.common import get_uow
from app.infrastructure.uow import SqlAlchemyUnitOfWork


async def list_repuestos_utilizados_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> ListRepuestosUtilizadosUseCase:
    """Fábrica para el caso de uso ListRepuestosUtilizadosUseCase."""
    return ListRepuestosUtilizadosUseCase(uow)


async def create_repuesto_utilizado_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> CreateRepuestoUtilizadoUseCase:
    """Fábrica para el caso de uso CreateRepuestoUtilizadoUseCase."""
    return CreateRepuestoUtilizadoUseCase(uow)


async def get_repuesto_utilizado_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> GetRepuestoUtilizadoUseCase:
    """Fábrica para el caso de uso GetRepuestoUtilizadoUseCase."""
    return GetRepuestoUtilizadoUseCase(uow)


async def update_repuesto_utilizado_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> UpdateRepuestoUtilizadoUseCase:
    """Fábrica para el caso de uso UpdateRepuestoUtilizadoUseCase."""
    return UpdateRepuestoUtilizadoUseCase(uow)


async def delete_repuesto_utilizado_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> DeleteRepuestoUtilizadoUseCase:
    """Fábrica para el caso de uso DeleteRepuestoUtilizadoUseCase."""
    return DeleteRepuestoUtilizadoUseCase(uow)