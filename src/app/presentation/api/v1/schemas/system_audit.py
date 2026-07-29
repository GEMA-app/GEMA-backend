from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SystemAuditAttributes(BaseModel):
    """Atributos visibles del recurso de auditoría."""

    usuario_id: str | None
    accion: str
    detalles: dict[str, Any]
    ip_address: str | None
    ocurrido_en: datetime
    usuario_nombre: str | None = None
    usuario_email: str | None = None
    modulo: str | None = None
    descripcion: str | None = None


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

    data: list[SystemAuditResource]
    meta: SystemAuditMeta
