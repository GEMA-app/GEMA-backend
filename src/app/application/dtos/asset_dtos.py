from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreateAssetRequest:
    articulo_id: str
    serial_interno: str
    codigo_activo: str
    estado: str
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str = "USD"


@dataclass(frozen=True)
class UpdateAssetRequest:
    serial_interno: str | None = None
    codigo_activo: str | None = None
    estado: str | None = None
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str | None = None


@dataclass(frozen=True)
class AssetResponse:
    id: str
    empresa_id: str
    articulo_id: str
    ubicacion_id: str | None
    serial_interno: str
    codigo_activo: str
    estado: str
    fecha_adquisicion: str | None
    valor_monetario: float | None
    moneda: str
