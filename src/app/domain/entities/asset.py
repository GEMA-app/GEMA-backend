from dataclasses import dataclass
from datetime import date
import uuid
from typing import Optional
from app.domain.value_objects import AssetId, CompanyId, LocationId
from app.domain.enums import AssetStatus


@dataclass
class Asset:
    """Entidad de dominio que representa un activo físico de la empresa."""
    id: AssetId
    empresa_id: CompanyId
    articulo_id: uuid.UUID
    ubicacion_id: Optional[LocationId]
    serial_interno: str
    codigo_activo: str
    estado: AssetStatus
    fecha_adquisicion: Optional[date] = None
    valor_monetario: Optional[float] = None
    moneda: str = "USD"
