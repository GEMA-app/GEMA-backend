from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class CreateAssetRequest:
    articulo_id: str
    serial_interno: str
    codigo_activo: str
    estado: str
    ubicacion_id: Optional[str] = None
    fecha_adquisicion: Optional[date] = None
    valor_monetario: Optional[float] = None
    moneda: str = "USD"


@dataclass(frozen=True)
class UpdateAssetRequest:
    serial_interno: Optional[str] = None
    codigo_activo: Optional[str] = None
    estado: Optional[str] = None
    ubicacion_id: Optional[str] = None
    fecha_adquisicion: Optional[date] = None
    valor_monetario: Optional[float] = None
    moneda: Optional[str] = None


@dataclass(frozen=True)
class AssetResponse:
    id: str
    empresa_id: str
    articulo_id: str
    ubicacion_id: Optional[str]
    serial_interno: str
    codigo_activo: str
    estado: str
    fecha_adquisicion: Optional[str]
    valor_monetario: Optional[float]
    moneda: str
