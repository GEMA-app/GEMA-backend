"""Fábricas de dependencias para los casos de uso de activos."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.asset import (
    CreateAssetUseCase,
    DeleteAssetUseCase,
    GetAssetUseCase,
    ListAssetsUseCase,
    UpdateAssetUseCase,
)
from app.composition.container.common import get_uow


async def get_create_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateAssetUseCase:
    return CreateAssetUseCase(uow)


async def provide_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetAssetUseCase:
    return GetAssetUseCase(uow)


async def get_list_assets_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListAssetsUseCase:
    return ListAssetsUseCase(uow)


async def get_update_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateAssetUseCase:
    return UpdateAssetUseCase(uow)


async def get_delete_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteAssetUseCase:
    return DeleteAssetUseCase(uow)
