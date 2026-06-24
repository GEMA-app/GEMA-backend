"""Schemas JSON:API para el módulo de intervenciones técnicas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import EstadoIntervencion


# =============================================================================
# Schemas de atributos (JSON:API)
# =============================================================================


class IntervencionAttributes(BaseModel):
    """Atributos de una intervención técnica."""

    orden_trabajo_id: UUID = Field(..., description="ID de la orden de trabajo asociada")
    tecnico_id: UUID = Field(..., description="ID del técnico que realizó la intervención")
    descripcion: str = Field(..., description="Descripción de la intervención")
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fecha_fin: datetime | None = Field(None, description="Fecha y hora de finalización")
    horas_trabajadas: float = Field(..., description="Horas trabajadas en la intervención")
    costo: float = Field(..., description="Costo total de la intervención")
    estado: EstadoIntervencion = Field(..., description="Estado actual de la intervención")
    observaciones: str | None = Field(None, description="Observaciones adicionales")


class UpdateIntervencionAttributes(BaseModel):
    """Atributos para actualizar una intervención técnica."""

    descripcion: str | None = Field(None, description="Descripción de la intervención")
    horas_trabajadas: float | None = Field(None, description="Horas trabajadas en la intervención")
    costo: float | None = Field(None, description="Costo total de la intervención")
    observaciones: str | None = Field(None, description="Observaciones adicionales")


# =============================================================================
# Schemas de recursos (JSON:API)
# =============================================================================


class IntervencionResource(BaseModel):
    """Recurso JSON:API para una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervención")
    attributes: IntervencionAttributes = Field(..., description="Atributos de la intervención")


class UpdateIntervencionResource(BaseModel):
    """Recurso JSON:API para actualizar una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervención")
    attributes: UpdateIntervencionAttributes = Field(..., description="Atributos a actualizar")


# =============================================================================
# Schemas de documentos (JSON:API)
# =============================================================================


class IntervencionDocument(BaseModel):
    """Documento JSON:API para una intervención."""

    data: IntervencionResource = Field(..., description="Recurso de intervención")


class IntervencionListDocument(BaseModel):
    """Documento JSON:API para una lista de intervenciones."""

    data: list[IntervencionResource] = Field(..., description="Lista de recursos de intervención")
    meta: dict[str, Any] = Field(..., description="Metadatos de la respuesta")


# =============================================================================
# Schemas de solicitud (JSON:API)
# =============================================================================


class CreateIntervencionData(BaseModel):
    """Datos de solicitud para crear una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    attributes: IntervencionAttributes = Field(..., description="Atributos de la intervención")


class CreateIntervencionRequest(BaseModel):
    """Solicitud JSON:API para crear una intervención."""

    data: CreateIntervencionData = Field(..., description="Datos de la solicitud")


class UpdateIntervencionData(BaseModel):
    """Datos de solicitud para actualizar una intervención."""

    type: str = Field("intervenciones", description="Tipo de recurso")
    id: str = Field(..., description="ID de la intervención")
    attributes: UpdateIntervencionAttributes = Field(..., description="Atributos a actualizar")


class UpdateIntervencionRequest(BaseModel):
    """Solicitud JSON:API para actualizar una intervención."""

    data: UpdateIntervencionData = Field(..., description="Datos de la solicitud")