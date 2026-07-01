"""Fábricas de dependencias para los casos de uso de repuestos de inventario."""

from fastapi import Depends

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.inventory_part.create_inventory_entry import (
    CreateInventoryEntryUseCase,
)
from app.application.use_cases.inventory_part.create_inventory_part import (
    CreateInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.delete_inventory_part import (
    DeleteInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.get_inventory_part import GetInventoryPartUseCase
from app.application.use_cases.inventory_part.list_inventory_parts import ListInventoryPartsUseCase
from app.application.use_cases.inventory_part.update_inventory_part import (
    UpdateInventoryPartUseCase,
)
from app.composition.container.common import get_uow


async def get_create_inventory_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateInventoryPartUseCase:
    """Fábrica de dependencias para el caso de uso de creación de repuestos."""
    return CreateInventoryPartUseCase(uow)


async def get_inventory_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetInventoryPartUseCase:
    """Fábrica de dependencias para el caso de uso de consulta de un repuesto."""
    return GetInventoryPartUseCase(uow)


async def get_update_inventory_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateInventoryPartUseCase:
    """Fábrica de dependencias para el caso de uso de actualización de repuestos."""
    return UpdateInventoryPartUseCase(uow)


async def get_list_inventory_parts_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListInventoryPartsUseCase:
    """Fábrica de dependencias para el caso de uso de listado paginado de repuestos."""
    return ListInventoryPartsUseCase(uow)


async def get_delete_inventory_part_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteInventoryPartUseCase:
    """Fábrica de dependencias para el caso de uso de eliminación de repuestos."""
    return DeleteInventoryPartUseCase(uow)


async def get_create_inventory_entry_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateInventoryEntryUseCase:
    """Fábrica de dependencias para el caso de uso de movimientos de inventario."""
    return CreateInventoryEntryUseCase(uow)
