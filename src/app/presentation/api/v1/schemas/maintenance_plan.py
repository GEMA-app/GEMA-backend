"""Schemas JSON:API para el módulo MaintenancePlan (Plan de Mantenimiento)."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class PlanExecutionAttributes(BaseModel):
    """Atributos de una ejecución de plan en formato JSON:API."""

    id: str = Field(..., description="ID único de la ejecución")
    work_order_id: str = Field(..., description="ID de la orden de trabajo generada")
    execution_date: datetime = Field(..., description="Fecha de ejecución")
    observations: str | None = Field(None, description="Observaciones de la ejecución")


class MaintenancePlanAttributes(BaseModel):
    """Atributos del plan de mantenimiento en formato JSON:API."""

    empresa_id: str
    activo_id: str
    nombre: str
    tipo: str
    intervalo_dias: int
    proxima_ejecucion: date
    tecnico_responsable_id: str | None = None
    descripcion_tareas: str | None = None
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    es_urgente: bool = False
    ejecuciones: list[PlanExecutionAttributes] = Field(
        default_factory=list, description="Historial de ejecuciones del plan"
    )


class MaintenancePlanResource(BaseModel):
    """Recurso JSON:API de un plan de mantenimiento."""

    type: str = Field(default="maintenance-plans")
    id: str = Field(..., description="ID único del plan")
    attributes: MaintenancePlanAttributes


class MaintenancePlanDocument(BaseModel):
    """Documento JSON:API con un plan de mantenimiento."""

    data: MaintenancePlanResource


class MaintenancePlanListDocument(BaseModel):
    """Documento JSON:API con una lista de planes de mantenimiento."""

    data: list[MaintenancePlanResource]
    meta: dict[str, Any] = Field(default_factory=lambda: {"total": 0})


class CreateMaintenancePlanRequest(BaseModel):
    """Payload JSON:API para crear un plan de mantenimiento."""

    class Data(BaseModel):
        """Contenedor JSON:API del payload."""

        class Attributes(BaseModel):
            """Atributos del plan a crear."""

            activo_id: str
            nombre: str
            tipo: str
            intervalo_dias: int
            proxima_ejecucion: date
            tecnico_responsable_id: str | None = None
            descripcion_tareas: str | None = None

        type: str = Field(default="maintenance-plans")
        attributes: Attributes

    data: Data


class UpdateMaintenancePlanRequest(BaseModel):
    """Payload JSON:API para actualizar un plan de mantenimiento."""

    class Data(BaseModel):
        """Contenedor JSON:API del payload."""

        class Attributes(BaseModel):
            """Atributos del plan a actualizar."""

            nombre: str | None = None
            tipo: str | None = None
            intervalo_dias: int | None = None
            proxima_ejecucion: date | None = None
            tecnico_responsable_id: str | None = None
            descripcion_tareas: str | None = None
            activo: bool | None = None

        type: str = Field(default="maintenance-plans")
        attributes: Attributes

    data: Data
