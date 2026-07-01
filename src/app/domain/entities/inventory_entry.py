"""Entidad de dominio InventoryEntry (movimiento de inventario de repuestos)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.exceptions.inventory_part import InvalidStockError
from app.domain.value_objects import CompanyId


@dataclass(frozen=True)
class InventoryEntry:
    """Entidad que representa una transacción de movimiento en el inventario."""

    id: UUID
    empresa_id: CompanyId
    repuesto_id: UUID
    ordenes_trabajo_id: UUID | None
    usuario_id: UUID | None
    cantidad: int
    tipo_movimiento: str  # entrada | salida
    precio_unitario: Decimal | None
    moneda: str = "USD"
    fecha_movimiento: datetime | None = None
    observaciones: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida invariantes después de inicializar.

        Raises:
            InvalidStockError: Si la cantidad es menor o igual a cero.
            ValueError: Si el tipo de movimiento no es 'entrada' o 'salida'.
        """
        if self.cantidad <= 0:
            raise InvalidStockError("La cantidad del movimiento debe ser mayor que cero.")
        if self.tipo_movimiento not in ("entrada", "salida"):
            raise ValueError(f"Tipo de movimiento inválido: {self.tipo_movimiento}")

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        repuesto_id: UUID,
        cantidad: int,
        tipo_movimiento: str,
        ordenes_trabajo_id: UUID | None = None,
        usuario_id: UUID | None = None,
        precio_unitario: Decimal | None = None,
        moneda: str = "USD",
        observaciones: str | None = None,
    ) -> "InventoryEntry":
        """Crea una nueva transacción de movimiento.

        Args:
            empresa_id: Identificador del tenant.
            repuesto_id: UUID del repuesto asociado.
            cantidad: Cantidad de repuestos.
            tipo_movimiento: 'entrada' o 'salida'.
            ordenes_trabajo_id: OT asociada opcional.
            usuario_id: Técnico que ejecuta el movimiento.
            precio_unitario: Costo unitario.
            moneda: Moneda.
            observaciones: Nota o descripción.

        Returns:
            Instancia de InventoryEntry.
        """
        return cls(
            id=uuid4(),
            empresa_id=empresa_id,
            repuesto_id=repuesto_id,
            ordenes_trabajo_id=ordenes_trabajo_id,
            usuario_id=usuario_id,
            cantidad=cantidad,
            tipo_movimiento=tipo_movimiento,
            precio_unitario=precio_unitario,
            moneda=moneda,
            fecha_movimiento=datetime.now(),
            observaciones=observaciones,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
