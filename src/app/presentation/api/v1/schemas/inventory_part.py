"""Schemas JSON:API para repuestos de inventario (InventoryPart): atributos,
recursos, documentos y solicitudes de transporte.
"""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class InventoryPartAttributes(BaseModel):
    """Atributos de serialización de un repuestos de inventario."""

    empresa_id: str
    articulo_id: str
    proveedor_id: str
    stock_actual: int
    stock_minimo: int
    ubicacion_almacen: str
    precio_unitario: Decimal
    moneda: str
    version: int


class InventoryPartResource(BaseModel):
    """Recurso JSON:API que encapsula un repuesto individual."""

    type: str = Field(default="inventory_parts", description="Tipo de recurso")
    id: str = Field(..., description="ID único del repuesto en inventario")
    attributes: InventoryPartAttributes
    links: LinksObject | None = None


class InventoryPartDocument(BaseModel):
    """Documento JSON:API de respuesta para un solo repuesto."""

    data: InventoryPartResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class InventoryPartListDocument(BaseModel):
    """Documento JSON:API de respuesta para listados de repuestos."""

    data: list[InventoryPartResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# --- Solicitudes de Entrada (Requests) ---


class CreateInventoryPartAttributes(BaseModel):
    """Atributos requeridos para registrar un repuesto con stock inicial."""

    articulo_id: str
    proveedor_id: str
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=0, ge=0)
    ubicacion_almacen: str = Field(..., max_length=100)
    precio_unitario: Decimal = Field(default=Decimal("0.00"), ge=0)
    moneda: str = Field(default="USD", max_length=3)


class CreateInventoryPartResource(BaseModel):
    """Recurso JSON:API para procesar la creación de un repuesto."""

    type: str = Field(default="inventory_parts", description="Tipo de recurso")
    attributes: CreateInventoryPartAttributes


class CreateInventoryPartRequest(BaseModel):
    """Solicitud JSON:API de entrada para el endpoint POST."""

    data: CreateInventoryPartResource


class UpdateInventoryPartAttributes(BaseModel):
    """Atributos mutables permitidos para modificaciones parciales."""

    proveedor_id: str | None = None
    stock_minimo: int | None = Field(None, ge=0)
    ubicacion_almacen: str | None = Field(None, max_length=100)
    precio_unitario: Decimal | None = Field(None, ge=0)
    moneda: str | None = Field(None, max_length=3)
    version: int | None = None


class UpdateInventoryPartResource(BaseModel):
    """Recurso JSON:API para procesar la actualización parcial de un repuesto."""

    type: str = Field(default="inventory_parts", description="Tipo de recurso")
    attributes: UpdateInventoryPartAttributes


class UpdateInventoryPartRequest(BaseModel):
    """Solicitud JSON:API de entrada para el endpoint PATCH."""

    data: UpdateInventoryPartResource

    # --- Esquemas para Movimientos de Inventario (InventoryEntry) ---


class InventoryEntryAttributes(BaseModel):
    """Atributos de serialización de un movimiento de inventario."""

    empresa_id: str
    repuesto_id: str
    movement_type: str
    quantity: int
    work_order_id: str | None = None
    usuario_id: str | None = None
    precio_unitario: Decimal | None = None
    moneda: str = "USD"
    fecha_movimiento: str | None = None
    reason: str | None = None


class InventoryEntryResource(BaseModel):
    """Recurso JSON:API que encapsula un movimiento individual."""

    type: str = Field(default="inventory_entries", description="Tipo de recurso")
    id: str = Field(..., description="ID único del movimiento registrado")
    attributes: InventoryEntryAttributes
    links: LinksObject | None = None


class InventoryEntryDocument(BaseModel):
    """Documento JSON:API de respuesta para un solo movimiento."""

    data: InventoryEntryResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class InventoryEntryListDocument(BaseModel):
    """Documento JSON:API de respuesta para listados de movimientos."""

    data: list[InventoryEntryResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# --- Solicitudes de Entrada para Movimientos (Requests) ---


class CreateInventoryEntryAttributes(BaseModel):
    """Atributos requeridos para registrar una entrada o salida de stock."""

    movement_type: str = Field(..., description="Tipo de movimiento: 'entrada' o 'salida'")
    quantity: int = Field(..., ge=1, description="Cantidad de repuestos a mover")
    work_order_id: str | None = Field(default=None, description="ID de la orden de trabajo")
    reason: str | None = Field(default=None, max_length=255, description="Motivo del movimiento")


class CreateInventoryEntryResource(BaseModel):
    """Recurso JSON:API para procesar la creación de un movimiento."""

    type: str = Field(default="inventory_entries", description="Tipo de recurso")
    attributes: CreateInventoryEntryAttributes


class CreateInventoryEntryRequest(BaseModel):
    """Solicitud JSON:API de entrada para el endpoint POST de movimientos."""

    data: CreateInventoryEntryResource
