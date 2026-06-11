from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import AssetStatus
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class AssetAttributes(BaseModel):
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
    type: str = Field(default="assets", description="Tipo de recurso")
    id: str = Field(..., description="ID único del activo")
    attributes: AssetAttributes
    links: LinksObject | None = None


class AssetDocument(BaseModel):
    data: AssetResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class AssetListDocument(BaseModel):
    data: list[AssetResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateAssetAttributes(BaseModel):
    articulo_id: str
    serial_interno: str
    codigo_activo: str
    estado: AssetStatus
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str = "USD"


class CreateAssetResource(BaseModel):
    type: str = Field(default="assets", description="Tipo de recurso")
    attributes: CreateAssetAttributes


class CreateAssetRequest(BaseModel):
    data: CreateAssetResource


class UpdateAssetAttributes(BaseModel):
    serial_interno: str | None = None
    codigo_activo: str | None = None
    estado: AssetStatus | None = None
    ubicacion_id: str | None = None
    fecha_adquisicion: date | None = None
    valor_monetario: float | None = None
    moneda: str | None = None
    version: int | None = None


class UpdateAssetResource(BaseModel):
    type: str = Field(default="assets", description="Tipo de recurso")
    attributes: UpdateAssetAttributes


class UpdateAssetRequest(BaseModel):
    data: UpdateAssetResource
