"""Puerto (Protocol) para el repositorio de partes de inventario."""

from typing import Protocol
from uuid import UUID

from app.domain.entities.inventory_part import InventoryPart
from app.domain.value_objects import CompanyId, RepuestoId


class InventoryPartRepositoryPort(Protocol):
    """Interfaz para el repositorio de repuestos del inventario con CRUD completo."""

    async def save(self, entity: InventoryPart) -> None:
        """Persiste o actualiza un repuesto en el inventario."""
        ...

    async def get_by_id(self, part_id: RepuestoId, empresa_id: CompanyId) -> InventoryPart | None:
        """Obtiene un repuesto por ID filtrado por empresa.

        Returns:
            La entidad InventoryPart o None si no existe.
        """
        ...

    async def get_all_by_empresa(
        self, empresa_id: CompanyId, limit: int = 20, offset: int = 0
    ) -> list[InventoryPart]:
        """Lista los repuestos de una empresa con paginación.

        Args:
            empresa_id: Identificador de la empresa.
            limit: Máximo de resultados.
            offset: Desplazamiento para paginación.

        Returns:
            Lista de entidades InventoryPart.
        """
        ...

    async def delete(self, part_id: RepuestoId, empresa_id: CompanyId) -> None:
        """Elimina un repuesto del inventario filtrado por empresa."""
        ...

    async def validate_and_decrement_stock(
        self, repuesto_id: UUID, cantidad: int, empresa_id: CompanyId
    ) -> None:
        """Valida que exista stock suficiente para el consumo de repuestos y lo decrementa."""
        ...
