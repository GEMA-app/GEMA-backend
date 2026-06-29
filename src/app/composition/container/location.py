"""Fábricas de dependencias para los casos de uso de ubicaciones."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.location import (
    CreateLocationUseCase,
    DeleteLocationUseCase,
    GetLocationChildrenUseCase,
    GetLocationTreeUseCase,
    GetLocationUseCase,
    UpdateLocationUseCase,
)
from app.composition.container.common import get_uow


async def get_create_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateLocationUseCase:
    """Fábrica de dependencias para el caso de uso de creación de ubicación.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso CreateLocationUseCase.
    """
    return CreateLocationUseCase(uow)


async def get_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de ubicación.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetLocationUseCase.
    """
    return GetLocationUseCase(uow)


async def get_location_tree_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationTreeUseCase:
    """Fábrica de dependencias para el caso de uso de árbol de ubicaciones.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetLocationTreeUseCase.
    """
    return GetLocationTreeUseCase(uow)


async def get_update_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateLocationUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de ubicación.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso UpdateLocationUseCase.
    """
    return UpdateLocationUseCase(uow)


async def get_delete_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteLocationUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de ubicación.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso DeleteLocationUseCase.
    """
    return DeleteLocationUseCase(uow)


async def get_location_children_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationChildrenUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de hijos de ubicación.

    Args:
        uow: Unidad de trabajo inyectada.

    Returns:
        Instancia del caso de uso GetLocationChildrenUseCase.
    """
    return GetLocationChildrenUseCase(uow)
