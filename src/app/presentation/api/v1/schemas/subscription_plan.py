"""Schemas JSON:API para planes de suscripción: atributos, recursos, 
documentos individuales y listados con filtros.
"""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject

class SubscriptionPlanAttributes(BaseModel):
    """Atributos de un plan de suscripción."""

    nombre: str
    descripcion: str | None = None
    precio_mensual_usd: Decimal
    max_usuarios: int | None = None
    max_activos: int | None = None
    version: int

class SubscriptionPlanResource(BaseModel):
    """Recurso JSON:API de un plan de suscripción."""

    type: str = Field(default="subscription_plans", description="Tipo de recurso")
    id: str = Field(..., description="ID único del plan de suscripción")
    attributes: SubscriptionPlanAttributes

class SubscriptionPlanDocument(BaseModel):
    """Documento JSON:API con un plan de suscripción."""

    data: SubscriptionPlanResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None

class SubscriptionPlanListDocument(BaseModel):
    """Documento JSON:API con lista de planes de suscripción."""

    data: list[SubscriptionPlanResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None

#Solicitudes (Requests)
class CreateSubscriptionPlanAttributes(BaseModel):
    """Atributos para crear un plan de suscripción."""

    nombre: str
    descripcion: str | None = None
    precio_mensual_usd: Decimal
    max_usuarios: int | None = None
    max_activos: int | None = None

class CreateSubscriptionPlanResource(BaseModel):
    """Recurso JSON:API para crear un plan de suscripción."""

    type: str = Field(default="subscription_plans", description="Tipo de recurso")
    attributes: CreateSubscriptionPlanAttributes

class CreateSubscriptionPlanRequest(BaseModel):
    """Solicitud JSON:API para crear un plan de suscripción."""

    data: CreateSubscriptionPlanResource

class UpdateSubscriptionPlanAttributes(BaseModel):
    """Atributos para actualizar un plan de suscripción."""

    nombre: str | None = None
    descripcion: str | None = None
    precio_mensual_usd: Decimal | None = None
    max_usuarios: int | None = None
    max_activos: int | None = None
    version: int | None = None

class UpdateSubscriptionPlanResource(BaseModel):
    """Recurso JSON:API para actualizar un plan de suscripción."""

    type: str = Field(default="subscription_plans", description="Tipo de recurso")
    attributes: UpdateSubscriptionPlanAttributes

class UpdateSubscriptionPlanRequest(BaseModel):
    """Solicitud JSON:API para actualizar un plan de suscripción."""

    data: UpdateSubscriptionPlanResource