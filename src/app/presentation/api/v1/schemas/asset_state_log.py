"""Schemas JSON:API para el historial de cambios de estado de activos (AssetStateLog)."""

from typing import Any

from pydantic import BaseModel, Field


class AssetStateLogAttributes(BaseModel):
    """Atributos de un registro de cambio de estado."""

    empresa_id: str
    activo_id: str
    estado_anterior: str | None = None
    estado_nuevo: str
    motivo: str | None = None
    fecha_cambio: str
    usuario_id: str | None = None
    version: int


class AssetStateLogResource(BaseModel):
    """Recurso JSON:API de un registro de cambio de estado."""

    type: str = Field(default="asset_state_logs", description="Tipo de recurso")
    id: str = Field(..., description="ID único del registro")
    attributes: AssetStateLogAttributes


class AssetStateLogListDocument(BaseModel):
    """Documento JSON:API con lista de registros de cambio de estado."""

    data: list[AssetStateLogResource]
    meta: dict[str, Any] | None = None
