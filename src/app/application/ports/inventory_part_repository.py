"""Puerto (Protocol) para el repositorio de partes de inventario."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.inventory_part import InventoryPart
from app.domain.value_objects import CompanyId, SparePartId


class InventoryPartRepositoryPort(Protocol):
    """Interfaz para el repositorio de repuestos del inventario con CRUD completo."""

    async def save(self, entity: InventoryPart) -> None:
        """Persiste o actualiza un repuesto en el inventario."""
        ...

    async def get_by_id(self, part_id: SparePartId, empresa_id: CompanyId) -> InventoryPart | None:
        """Obtiene un repuesto por ID filtrado por empresa.

        Returns:
            La entidad InventoryPart o None si no existe.
        """
        ...

    async def get_all_by_company(
        self,
        empresa_id: CompanyId,
        limit: int = 20,
        offset: int = 0,
        bajo_minimo: bool = False,
        proveedor_id: UUID | None = None,
    ) -> tuple[list[InventoryPart], int]:
        """Lista los repuestos de una empresa con paginación y conteo total.

        Args:
            empresa_id: Identificador de la empresa.
            limit: Máximo de resultados.
            offset: Desplazamiento para paginación.
            bajo_minimo: Filtra las piezas que están por debajo del nivel mínimo.
            proveedor_id: Identificador opcional del proveedor.

        Returns:
            Una tupla con la lista de entidades InventoryPart y el conteo total.
        """
        ...

    async def delete(self, part_id: SparePartId, empresa_id: CompanyId) -> None:
        """Elimina un repuesto del inventario filtrado por empresa."""
        ...

    async def validate_and_decrement_stock(
        self, repuesto_id: UUID, cantidad: int, empresa_id: CompanyId
    ) -> None:
        """Valida que exista stock suficiente para el consumo de repuestos y lo decrementa."""
        ...

    async def restore_stock(self, repuesto_id: UUID, cantidad: int, empresa_id: CompanyId) -> None:
        """Incrementa el stock del repuesto en inventario tras eliminar o reducir consumo."""
        ...
