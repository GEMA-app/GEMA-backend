"""Paquete de objetos de valor del dominio.

Re-exporta todos los value objects para mantener compatibilidad con los
imports existentes (``from app.domain.value_objects import X``).
"""

from app.domain.value_objects.credential import Email, HashedPassword, PlainPassword
from app.domain.value_objects.identifier import (
    AssetId,
    CompanyId,
    FailureReportId,
    InterventionId,
    LocationId,
    MaintenancePlanId,
    PlanExecutionId,
    RepuestoId,
    RoleId,
    SubscriptionPlanId,
    UserId,
    WorkOrderId,
)
from app.domain.value_objects.slug import Slug

__all__ = [
    "Email",
    "PlainPassword",
    "HashedPassword",
    "UserId",
    "CompanyId",
    "RoleId",
    "AssetId",
    "FailureReportId",
    "InterventionId",
    "LocationId",
    "PlanExecutionId",
    "RepuestoId",
    "MaintenancePlanId",
    "WorkOrderId",
    "Slug",
    "SubscriptionPlanId",
]
