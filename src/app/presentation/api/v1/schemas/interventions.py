"""Schemas JSON:API para el mÃ³dulo de intervenciones tÃ©cnicas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

# =============================================================================
# Schemas de atributos (JSON:API)
# =============================================================================


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


class UpdateInterventionAttributes(BaseModel):
    """Atributos para actualizar una intervención técnica."""

    tareas_realizadas: str | None = Field(
        None, description="Descripción detallada de las tareas realizadas"
    )
    horas_hombre: float | None = Field(None, description="Horas hombre dedicadas a la intervención")


class InterventionResource(BaseModel):
    """Recurso JSON:API para una intervenciÃ³n."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervenciÃ³n")
    attributes: InterventionAttributes = Field(..., description="Atributos de la intervenciÃ³n")


class UpdateInterventionResource(BaseModel):
    """Recurso JSON:API para actualizar una intervenciÃ³n."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervenciÃ³n")
    attributes: UpdateInterventionAttributes = Field(..., description="Atributos a actualizar")


# =============================================================================
# Schemas de documentos (JSON:API)
# =============================================================================


class InterventionDocument(BaseModel):
    """Documento JSON:API para una intervenciÃ³n."""

    data: InterventionResource = Field(..., description="Recurso de intervenciÃ³n")


class InterventionListDocument(BaseModel):
    """Documento JSON:API para una lista de intervenciones."""

    data: list[InterventionResource] = Field(..., description="Lista de recursos de intervenciÃ³n")
    meta: dict[str, Any] = Field(..., description="Metadatos de la respuesta")


# =============================================================================
# Schemas de solicitud (JSON:API)
# =============================================================================


class CreateInterventionData(BaseModel):
    """Datos de solicitud para crear una intervenciÃ³n."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    attributes: InterventionAttributes = Field(..., description="Atributos de la intervenciÃ³n")


class CreateInterventionRequest(BaseModel):
    """Solicitud JSON:API para crear una intervenciÃ³n."""

    data: CreateInterventionData = Field(..., description="Datos de la solicitud")


class UpdateInterventionData(BaseModel):
    """Datos de solicitud para actualizar una intervenciÃ³n."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervenciÃ³n")
    attributes: UpdateInterventionAttributes = Field(..., description="Atributos a actualizar")


class UpdateInterventionRequest(BaseModel):
    """Solicitud JSON:API para actualizar una intervenciÃ³n."""

    data: UpdateInterventionData = Field(..., description="Datos de la solicitud")
