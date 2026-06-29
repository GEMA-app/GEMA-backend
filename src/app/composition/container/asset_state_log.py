"""Fábricas de dependencias para los casos de uso de AssetStateLog."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.asset_state_log import ListAssetStateLogUseCase
from app.composition.container.common import get_uow


async def get_list_asset_state_log_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListAssetStateLogUseCase:
    """Fábrica de dependencias para el caso de uso de listado de historial de estados.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso ListAssetStateLogUseCase.
    """
    return ListAssetStateLogUseCase(uow)
