"""Schemas JSON:API para activos físicos: atributos, recursos,
documentos individuales y listados con filtros.
"""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import AssetStatus
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class AssetAttributes(BaseModel):
    """Atributos de un activo físico."""

    empresa_id: str
    articulo_id: str
    serial_interno: str
    codigo_activo: str
    estado: AssetStatus
    ubicacion_id: str | None = None
    fecha_adquisicion: str | None = None
    valor_monetario: float | None = None
    moneda: str = "USD"
    version: int


class AssetResource(BaseModel):
    """Recurso JSON:API de un activo físico."""

    type: str = Field(default="assets", description="Tipo de recurso")
    id: str = Field(..., description="ID único del activo")
    attributes: AssetAttributes
    links: LinksObject | None = None


class AssetDocument(BaseModel):
    """Documento JSON:API con un activo."""

    data: AssetResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class AssetListDocument(BaseModel):
    """Documento JSON:API con lista de activos."""

    data: list[AssetResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateAssetAttributes(BaseModel):
    """Atributos para crear un activo."""

    articulo_id: str
    serial_interno: str
    codigo_activo: str
    estado: AssetStatus
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str = "USD"


class CreateAssetResource(BaseModel):
    """Recurso JSON:API para crear un activo."""

    type: str = Field(default="assets", description="Tipo de recurso")
    attributes: CreateAssetAttributes


class CreateAssetRequest(BaseModel):
    """Solicitud JSON:API para crear un activo."""

    data: CreateAssetResource


class UpdateAssetAttributes(BaseModel):
    """Atributos para actualizar un activo."""

    serial_interno: str | None = None
    codigo_activo: str | None = None
    estado: AssetStatus | None = None
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str | None = None
    version: int | None = None


class UpdateAssetResource(BaseModel):
    """Recurso JSON:API para actualizar un activo."""

    type: str = Field(default="assets", description="Tipo de recurso")
    attributes: UpdateAssetAttributes


class UpdateAssetRequest(BaseModel):
    """Solicitud JSON:API para actualizar un activo."""

    data: UpdateAssetResource
