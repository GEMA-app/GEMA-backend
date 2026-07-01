"""Casos de uso para la gestión de repuestos y movimientos de inventario."""

from app.application.use_cases.inventory_part.create_inventory_entry import (
    CreateInventoryEntryUseCase,
)
from app.application.use_cases.inventory_part.create_inventory_part import (
    CreateInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.delete_inventory_part import (
    DeleteInventoryPartUseCase,
)
from app.application.use_cases.inventory_part.get_inventory_entry import GetInventoryEntryUseCase
from app.application.use_cases.inventory_part.get_inventory_part import GetInventoryPartUseCase
from app.application.use_cases.inventory_part.list_inventory_entries import (
    ListInventoryEntriesUseCase,
)
from app.application.use_cases.inventory_part.list_inventory_parts import ListInventoryPartsUseCase
from app.application.use_cases.inventory_part.update_inventory_part import (
    UpdateInventoryPartUseCase,
)

__all__ = [
    "CreateInventoryEntryUseCase",
    "CreateInventoryPartUseCase",
    "DeleteInventoryPartUseCase",
    "GetInventoryEntryUseCase",
    "GetInventoryPartUseCase",
    "ListInventoryEntriesUseCase",
    "ListInventoryPartsUseCase",
    "UpdateInventoryPartUseCase",
]
