"""Puerto (Protocol) para el repositorio de partes de inventario."""

from typing import Protocol
from uuid import UUID

from app.domain.value_objects import CompanyId


class InventoryPartRepositoryPort(Protocol):
    """Interfaz para la consulta y decremento del stock de repuestos en el inventario."""

    async def validate_and_decrement_stock(
        self, repuesto_id: UUID, cantidad: int, empresa_id: CompanyId
    ) -> None:
        """Valida que exista stock suficiente para el consumo de repuestos y lo decrementa.

        Args:
            repuesto_id: Identificador único del repuesto.
            cantidad: Cantidad que se desea consumir.
            empresa_id: Identificador de la empresa (tenant).

        Raises:
            InsufficientStockError: Si el stock actual es menor que la cantidad requerida.
        """
        ...
