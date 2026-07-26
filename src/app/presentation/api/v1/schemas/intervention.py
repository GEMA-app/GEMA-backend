"""Schemas JSON:API para el módulo de intervenciones técnicas."""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Schemas de atributos (JSON:API)
# =============================================================================


class UsedPartAttributes(BaseModel):
    """Atributos de un repuesto utilizado en una intervención."""

    empresa_id: UUID = Field(..., description="ID de la empresa")
    intervencion_id: UUID = Field(..., description="ID de la intervención")
    repuesto_id: UUID = Field(..., description="ID del repuesto en inventario")
    cantidad_usada: int = Field(..., description="Cantidad consumida")
    precio_unitario: Decimal | None = Field(None, description="Precio unitario histórico")
    moneda: str = Field("USD", description="Código ISO de la moneda")
    created_at: str | None = Field(None, description="Fecha de creación")
    updated_at: str | None = Field(None, description="Fecha de actualización")
    precio_total: Decimal | None = Field(None, description="Precio total calculado")


class InterventionAttributes(BaseModel):
    """Atributos de una intervención técnica."""

    work_order_id: UUID = Field(..., description="ID de la orden de trabajo asociada")
    technician_id: UUID = Field(..., description="ID del técnico que realizó la intervención")
    tareas_realizadas: str = Field(
        ..., description="Descripción detallada de las tareas realizadas"
    )
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fecha_fin: datetime | None = Field(None, description="Fecha y hora de finalización")
    horas_hombre: float = Field(..., description="Horas hombre dedicadas a la intervención")
    used_parts: list[UsedPartAttributes] = Field(
        default_factory=list, description="Repuestos consumidos en la intervención"
    )


class UpdateInterventionAttributes(BaseModel):
    """Atributos para actualizar una intervención técnica."""

    tareas_realizadas: str | None = Field(
        None, description="Descripción detallada de las tareas realizadas"
    )
    horas_hombre: float | None = Field(None, description="Horas hombre dedicadas a la intervención")
    fecha_fin: datetime | None = Field(None, description="Fecha y hora de finalización")


class InterventionResource(BaseModel):
    """Recurso JSON:API para una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervención")
    attributes: InterventionAttributes = Field(..., description="Atributos de la intervención")


class UpdateInterventionResource(BaseModel):
    """Recurso JSON:API para actualizar una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervención")
    attributes: UpdateInterventionAttributes = Field(..., description="Atributos a actualizar")


# =============================================================================
# Schemas de documentos (JSON:API)
# =============================================================================


class InterventionDocument(BaseModel):
    """Documento JSON:API para una intervención."""

    data: InterventionResource = Field(..., description="Recurso de intervención")


class InterventionListDocument(BaseModel):
    """Documento JSON:API para una lista de intervenciones."""

    data: list[InterventionResource] = Field(..., description="Lista de recursos de intervención")
    meta: dict[str, Any] = Field(..., description="Metadatos de la respuesta")


# =============================================================================
# Schemas de solicitud (JSON:API)
# =============================================================================


class CreateInterventionData(BaseModel):
    """Datos de solicitud para crear una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    attributes: InterventionAttributes = Field(..., description="Atributos de la intervención")


class CreateInterventionRequest(BaseModel):
    """Solicitud JSON:API para crear una intervención."""

    data: CreateInterventionData = Field(..., description="Datos de la solicitud")


class UpdateInterventionData(BaseModel):
    """Datos de solicitud para actualizar una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervención")
    attributes: UpdateInterventionAttributes = Field(..., description="Atributos a actualizar")


class UpdateInterventionRequest(BaseModel):
    """Solicitud JSON:API para actualizar una intervención."""

    data: UpdateInterventionData = Field(..., description="Datos de la solicitud")
