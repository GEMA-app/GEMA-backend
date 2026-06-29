from typing import Protocol
from app.domain.entities.inventory_part import InventoryPart
from app.domain.value_objects import CompanyId, InventoryPartId


class InventoryPartRepositoryPort(Protocol):
    """Puerto de repositorio para las operaciones de persistencia de Repuestos."""
    
    async def save(self, inventory_part: InventoryPart) -> None:
        """Guarda o actualiza un repuesto en el inventario."""
        ...

    async def get_by_id(self, empresa_id: CompanyId, part_id: InventoryPartId) -> InventoryPart | None:
        """Busca un repuesto específico por su ID garantizando el aislamiento por empresa (Multi-tenant)."""
        ...

    async def get_all_by_empresa(self, empresa_id: CompanyId, limit: int = 20, offset: int = 0) -> list[InventoryPart]:
        """Obtiene el listado paginado de repuestos pertenecientes a una empresa."""
        ...