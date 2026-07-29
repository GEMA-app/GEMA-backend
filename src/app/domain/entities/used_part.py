"""Entidad de dominio UsedPart (repuesto utilizado en una intervención)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.exceptions.used_part import (
    UsedPartInvalidPriceError,
    UsedPartInvalidQuantityError,
)
from app.domain.value_objects import CompanyId


@dataclass(frozen=True)
class UsedPart:
    """Entidad que representa un repuesto utilizado en una intervención técnica."""

    id: UUID
    empresa_id: CompanyId
    intervencion_id: UUID
    repuesto_id: UUID
    cantidad_usada: int
    precio_unitario: Decimal | None
    moneda: str = "USD"
    version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida las invariantes de la entidad después de la inicialización.

        Raises:
            UsedPartInvalidQuantityError: Si cantidad_usada <= 0.
            UsedPartInvalidPriceError: Si precio_unitario no es None y <= 0.
        """
        if self.cantidad_usada <= 0:
            raise UsedPartInvalidQuantityError(self.cantidad_usada)
        if self.precio_unitario is not None and self.precio_unitario <= Decimal("0"):
            raise UsedPartInvalidPriceError(self.precio_unitario)

    @property
    def precio_total(self) -> Decimal | None:
        """Calcula el costo total del repuesto utilizado."""
        return (
            self.cantidad_usada * self.precio_unitario if self.precio_unitario is not None else None
        )

    @classmethod
    def create(
        cls,
        empresa_id: CompanyId,
        intervencion_id: UUID,
        repuesto_id: UUID,
        cantidad_usada: int,
        precio_unitario: Decimal | None = None,
        moneda: str = "USD",
    ) -> "UsedPart":
        """Crea una nueva instancia de UsedPart.

        Args:
            empresa_id: Identificador de la empresa (tenant).
            intervencion_id: Identificador de la intervención técnica.
            repuesto_id: Identificador del repuesto en el catálogo.
            cantidad_usada: Cantidad consumida del repuesto.
            precio_unitario: Precio unitario histórico (opcional).
            moneda: Código ISO de la moneda (por defecto USD).

        Returns:
            Una nueva instancia de UsedPart con UUID y marcas de tiempo.
        """
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

    def change_quantity(self, new_quantity: int) -> "UsedPart":
        """Crea una nueva instancia con la cantidad actualizada.

        Args:
            new_quantity: Nueva cantidad consumida del repuesto.

        Returns:
            Una nueva instancia de UsedPart con la cantidad y marca de tiempo actualizadas.

        Raises:
            UsedPartInvalidQuantityError: Si new_quantity <= 0.
        """
        if new_quantity <= 0:
            raise UsedPartInvalidQuantityError(new_quantity)
        return UsedPart(
            id=self.id,
            empresa_id=self.empresa_id,
            intervencion_id=self.intervencion_id,
            repuesto_id=self.repuesto_id,
            cantidad_usada=new_quantity,
            precio_unitario=self.precio_unitario,
            moneda=self.moneda,
            version=self.version,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )
