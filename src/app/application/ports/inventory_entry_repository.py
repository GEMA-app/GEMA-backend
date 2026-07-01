"""Puerto del repositorio para la entidad de dominio InventoryEntry."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.inventory_entry import InventoryEntry
from app.domain.value_objects import CompanyId


class InventoryEntryRepositoryPort(Protocol):
    """Puerto para el repositorio de movimientos de inventario (InventoryEntry)."""

    async def save(self, entry: InventoryEntry) -> None:
        """Persiste o actualiza un movimiento de inventario."""
        ...

    async def get_by_id(self, entry_id: UUID, empresa_id: CompanyId) -> InventoryEntry | None:
        """Busca un movimiento por su ID filtrado por empresa."""
        ...

    async def get_all_by_repuesto(
        self, repuesto_id: UUID, empresa_id: CompanyId, limit: int = 20, offset: int = 0
    ) -> list[InventoryEntry]:
        """Obtiene la lista paginada de movimientos asociados a un repuesto."""
        ...
