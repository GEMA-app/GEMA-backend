"""Schemas JSON:API para el módulo UsedPart (repuestos utilizados)."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class UsedPartAttributes(BaseModel):
    """Atributos de un repuesto utilizado."""
    empresa_id: UUID = Field(..., description="ID de la empresa")
    intervencion_id: UUID = Field(..., description="ID de la intervención")
    repuesto_id: UUID = Field(..., description="ID del repuesto")
    cantidad_usada: int = Field(..., gt=0, description="Cantidad usada del repuesto")
    precio_unitario: Decimal | None = Field(None, description="Precio unitario histórico")
    moneda: str = Field("USD", description="Moneda del precio")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Fecha de actualización")


class UsedPartResource(BaseModel):
    """Recurso JSON:API para un repuesto utilizado."""
    type: str = Field(default="repuesto-utilizado")
    id: UUID
    attributes: UsedPartAttributes


class UsedPartDocument(BaseModel):
    """Documento JSON:API para un recurso de repuesto utilizado."""
    data: UsedPartResource


class UsedPartsDocument(BaseModel):
    """Documento JSON:API para una lista de repuestos utilizados."""
    data: list[UsedPartResource]


class CreateUsedPartAttributes(BaseModel):
    """Atributos para crear un repuesto utilizado."""
    intervencion_id: UUID
    repuesto_id: UUID
    cantidad_usada: int = Field(..., gt=0)
    precio_unitario: Decimal | None = None
    moneda: str = "USD"


class CreateUsedPartResource(BaseModel):
    """Recurso JSON:API para crear un repuesto utilizado."""
    type: str = Field(default="repuesto-utilizado")
    attributes: CreateUsedPartAttributes


class CreateUsedPartRequest(BaseModel):
    """Request JSON:API para crear un repuesto utilizado."""
    data: CreateUsedPartResource


class UpdateUsedPartAttributes(BaseModel):
    """Atributos para actualizar un repuesto utilizado."""
    cantidad_usada: int | None = Field(None, gt=0)


class UpdateUsedPartResource(BaseModel):
    """Recurso JSON:API para actualizar un repuesto utilizado."""
    type: str = Field(default="repuesto-utilizado")
    id: UUID
    attributes: UpdateUsedPartAttributes


class UpdateUsedPartRequest(BaseModel):
    """Request JSON:API para actualizar un repuesto utilizado."""
    data: UpdateUsedPartResource
