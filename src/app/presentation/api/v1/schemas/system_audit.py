from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SystemAuditAttributes(BaseModel):
    """Atributos visibles del recurso de auditoría."""
    usuario_id: Optional[int]
    accion: str
    detalles: Dict[str, Any]
    ip_address: Optional[str]
    ocurrido_en: datetime


class SystemAuditResource(BaseModel):
    """Estructura de un recurso individual bajo el estándar JSON:API."""
    type: str = Field(default="system-audits")
    id: str
    attributes: SystemAuditAttributes


class SystemAuditDocument(BaseModel):
    """Documento JSON:API para devolver una sola auditoría (GET por ID)."""
    data: SystemAuditResource


class SystemAuditMeta(BaseModel):
    """Metadatos de paginación obligatorios en GEMA."""
    total: int
    offset: int
    limit: int


class SystemAuditListDocument(BaseModel):
    """Documento JSON:API para devolver la lista paginada de auditorías."""
    data: List[SystemAuditResource]
    meta: SystemAuditMeta