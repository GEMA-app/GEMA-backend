"""Schemas JSON:API para ejecuciones de planes de mantenimiento."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class PlanExecutionAttributes(BaseModel):
    """Atributos de una ejecución de plan."""

    empresa_id: str
    plan_id: str
    work_order_id: str | None = None
    execution_date: datetime
    observations: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PlanExecutionResource(BaseModel):
    """Recurso JSON:API de una ejecución de plan."""

    type: str = Field(default="planExecution", description="Tipo de recurso")
    id: str = Field(..., description="ID único de la ejecución")
    attributes: PlanExecutionAttributes
    links: LinksObject | None = None


class PlanExecutionDocument(BaseModel):
    """Documento JSON:API con una ejecución de plan."""

    data: PlanExecutionResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class PlanExecutionListDocument(BaseModel):
    """Documento JSON:API con lista de ejecuciones de plan."""

    data: list[PlanExecutionResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreatePlanExecutionAttributes(BaseModel):
    """Atributos para crear una ejecución de plan."""

    plan_id: str
    work_order_id: str | None = None
    execution_date: datetime | None = None
    observations: str | None = None


class CreatePlanExecutionResource(BaseModel):
    """Recurso JSON:API para crear una ejecución de plan."""

    type: str = Field(default="planExecution", description="Tipo de recurso")
    attributes: CreatePlanExecutionAttributes


class CreatePlanExecutionRequest(BaseModel):
    """Solicitud JSON:API para crear una ejecución de plan."""

    data: CreatePlanExecutionResource
