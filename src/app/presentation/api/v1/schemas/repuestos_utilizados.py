# src/app/presentation/api/v1/schemas/repuestos_utilizados.py
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class RepuestoUtilizadoAttributes(BaseModel):
    """Atributos de un repuesto utilizado."""
    empresa_id: UUID = Field(..., description="ID de la empresa")
    intervencion_id: UUID = Field(..., description="ID de la intervención")
    repuesto_id: UUID = Field(..., description="ID del repuesto")
    cantidad_usada: int = Field(..., gt=0, description="Cantidad usada del repuesto")
    precio_unitario: Decimal | None = Field(None, description="Precio unitario histórico")
    moneda: str = Field("USD", description="Moneda del precio")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Fecha de actualización")


class RepuestoUtilizadoResource(BaseModel):
    """Recurso JSON:API para un repuesto utilizado."""
    type: str = Field("repuesto-utilizado", const=True)
    id: UUID
    attributes: RepuestoUtilizadoAttributes


class RepuestoUtilizadoDocument(BaseModel):
    """Documento JSON:API para un recurso de repuesto utilizado."""
    data: RepuestoUtilizadoResource


class RepuestosUtilizadosDocument(BaseModel):
    """Documento JSON:API para una lista de repuestos utilizados."""
    data: list[RepuestoUtilizadoResource]


class CreateRepuestoUtilizadoAttributes(BaseModel):
    """Atributos para crear un repuesto utilizado."""
    intervencion_id: UUID
    repuesto_id: UUID
    cantidad_usada: int = Field(..., gt=0)
    precio_unitario: Decimal | None = None
    moneda: str = "USD"


class CreateRepuestoUtilizadoResource(BaseModel):
    """Recurso JSON:API para crear un repuesto utilizado."""
    type: str = Field("repuesto-utilizado", const=True)
    attributes: CreateRepuestoUtilizadoAttributes


class CreateRepuestoUtilizadoRequest(BaseModel):
    """Request JSON:API para crear un repuesto utilizado."""
    data: CreateRepuestoUtilizadoResource


class UpdateRepuestoUtilizadoAttributes(BaseModel):
    """Atributos para actualizar un repuesto utilizado."""
    cantidad_usada: int | None = Field(None, gt=0)


class UpdateRepuestoUtilizadoResource(BaseModel):
    """Recurso JSON:API para actualizar un repuesto utilizado."""
    type: str = Field("repuesto-utilizado", const=True)
    id: UUID
    attributes: UpdateRepuestoUtilizadoAttributes


class UpdateRepuestoUtilizadoRequest(BaseModel):
    """Request JSON:API para actualizar un repuesto utilizado."""
    data: UpdateRepuestoUtilizadoResource