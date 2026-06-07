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
    return CreateLocationUseCase(uow)


async def provide_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationUseCase:
    return GetLocationUseCase(uow)


async def provide_location_tree_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationTreeUseCase:
    return GetLocationTreeUseCase(uow)


async def provide_location_children_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationChildrenUseCase:
    return GetLocationChildrenUseCase(uow)


async def get_update_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateLocationUseCase:
    return UpdateLocationUseCase(uow)


async def get_delete_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteLocationUseCase:
    return DeleteLocationUseCase(uow)
