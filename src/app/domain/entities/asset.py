import uuid
from dataclasses import dataclass
from datetime import date

from app.domain.enums import AssetStatus
from app.domain.value_objects import AssetId, CompanyId, LocationId


@dataclass
class Asset:
    """Entidad de dominio que representa un activo físico de la empresa."""
    id: AssetId
    empresa_id: CompanyId
    articulo_id: uuid.UUID
    ubicacion_id: LocationId | None
    serial_interno: str
    codigo_activo: str
    estado: AssetStatus
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str = "USD"
