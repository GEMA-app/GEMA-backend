"""DTOs del módulo UsedPart (repuestos utilizados)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class UsedPartResponse:
    """DTO de respuesta para un repuesto utilizado."""

    id: UUID
    empresa_id: UUID
    intervencion_id: UUID
    repuesto_id: UUID
    cantidad_usada: int
    precio_unitario: Decimal | None
    moneda: str
    created_at: datetime | None
    updated_at: datetime | None
    precio_total: Decimal | None = None


@dataclass(frozen=True)
class CreateUsedPartRequest:
    """DTO para solicitar la creación de un repuesto utilizado."""

    intervencion_id: UUID
    repuesto_id: UUID
    cantidad_usada: int
    precio_unitario: Decimal | None = None
    moneda: str = "USD"


@dataclass(frozen=True)
class UpdateUsedPartRequest:
    """DTO para solicitar la actualización de un repuesto utilizado."""

    cantidad_usada: int | None = None
