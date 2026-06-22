from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from app.domain.exceptions import (
    RepuestoUtilizadoCantidadInvalidaError,
    RepuestoUtilizadoPrecioInvalidoError,
)
from app.domain.value_objects import UserId


@dataclass(frozen=True)
class RepuestoUtilizado:
    """Entidad que representa un repuesto utilizado en una intervención."""
    id: UUID
    empresa_id: UserId
    intervencion_id: UUID
    repuesto_id: UUID
    cantidad_usada: int
    precio_unitario: float | None
    moneda: str = "USD"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Valida las invariantes de la entidad después de la inicialización."""
        if self.cantidad_usada <= 0:
            raise RepuestoUtilizadoCantidadInvalidaError(self.cantidad_usada)
        if self.precio_unitario is not None and self.precio_unitario <= 0:
            raise RepuestoUtilizadoPrecioInvalidoError(self.precio_unitario)

    @classmethod
    def create(
        cls,
        empresa_id: UserId,
        intervencion_id: UUID,
        repuesto_id: UUID,
        cantidad_usada: int,
        precio_unitario: float | None,
        moneda: str = "USD",
    ) -> "RepuestoUtilizado":
        """Método fábrica para crear una nueva instancia."""
        return cls(
            id=uuid4(),
            empresa_id=empresa_id,
            intervencion_id=intervencion_id,
            repuesto_id=repuesto_id,
            cantidad_usada=cantidad_usada,
            precio_unitario=precio_unitario,
            moneda=moneda,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def cambiar_cantidad(self, nueva_cantidad: int) -> "RepuestoUtilizado":
        """Crea una nueva instancia con la cantidad actualizada."""
        if nueva_cantidad <= 0:
            raise RepuestoUtilizadoCantidadInvalidaError(nueva_cantidad)
        return RepuestoUtilizado(
            id=self.id,
            empresa_id=self.empresa_id,
            intervencion_id=self.intervencion_id,
            repuesto_id=self.repuesto_id,
            cantidad_usada=nueva_cantidad,
            precio_unitario=self.precio_unitario,
            moneda=self.moneda,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )