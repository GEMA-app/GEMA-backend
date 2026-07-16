"""DTOs de entrada y salida para el módulo de System Audit."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SystemAuditResponse:
    """DTO de salida plano con los datos de una auditoría para la API."""

    id: str
    empresa_id: str
    usuario_id: str | None
    accion: str
    detalles: dict[str, Any]
    ip_address: str | None
    ocurrido_en: datetime
    usuario_nombre: str | None = None
    usuario_email: str | None = None



@dataclass(frozen=True)
class ListSystemAuditsRequest:
    """DTO de entrada para agrupar los filtros de búsqueda de auditorías."""

    usuario_id: str | None = None
    accion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
