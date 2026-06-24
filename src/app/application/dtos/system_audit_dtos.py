from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class SystemAuditResponse:
    """DTO de salida plano con los datos de una auditoría para la API."""
    id: int
    empresa_id: str
    usuario_id: Optional[int]
    accion: str
    detalles: Dict[str, Any]
    ip_address: Optional[str]
    ocurrido_en: datetime


@dataclass(frozen=True)
class ListSystemAuditsRequest:
    """DTO de entrada para agrupar los filtros de búsqueda de auditorías."""
    usuario_id: Optional[int] = None
    accion: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None