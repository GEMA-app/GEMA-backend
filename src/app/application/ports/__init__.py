"""Puertos (interfaces) de la capa de aplicación.

Define los contratos que la infraestructura debe implementar para cada repositorio y servicio.
"""

from app.application.ports.article_category_repository import ArticleCategoryRepositoryPort
from app.application.ports.asset_repository import AssetRepositoryPort
from app.application.ports.asset_state_log_repository import AssetStateLogRepositoryPort
from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.catalog_article_repository import CatalogArticleRepositoryPort
from app.application.ports.company_repository import CompanyRepositoryPort
from app.application.ports.event_bus import EventBusPort
from app.application.ports.failure_report_repository import FailureReportRepositoryPort
from app.application.ports.intervention_repository import InterventionRepositoryPort
from app.application.ports.inventory_part_repository import InventoryPartRepositoryPort
from app.application.ports.location_repository import LocationRepositoryPort
from app.application.ports.maintenance_plan_repository import MaintenancePlanRepositoryPort
from app.application.ports.notifications import NotificationPort
from app.application.ports.plan_execution_repository import PlanExecutionRepositoryPort
from app.application.ports.preference_repository import PreferenceRepositoryPort
from app.application.ports.repository import UserRepositoryPort
from app.application.ports.role_repository import RoleRepositoryPort
from app.application.ports.subscription_plan_repository import SubscriptionPlanRepositoryPort
from app.application.ports.system_audit_repository import SystemAuditRepositoryPort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.ports.used_part_repository import UsedPartRepositoryPort
from app.application.ports.work_order_repository import WorkOrderRepositoryPort

__all__ = [
    "UserRepositoryPort",
    "CompanyRepositoryPort",
    "RoleRepositoryPort",
    "AssetRepositoryPort",
    "CatalogArticleRepositoryPort",
    "FailureReportRepositoryPort",
    "LocationRepositoryPort",
    "UnitOfWorkPort",
    "EventBusPort",
    "PreferenceRepositoryPort",
    "PasswordHasherPort",
    "TokenServicePort",
    "NotificationPort",
    "UsedPartRepositoryPort",
    "WorkOrderRepositoryPort",
    "SubscriptionPlanRepositoryPort",
    "InterventionRepositoryPort",
    "ArticleCategoryRepositoryPort",
    "AssetStateLogRepositoryPort",
    "MaintenancePlanRepositoryPort",
    "PlanExecutionRepositoryPort",
    "SystemAuditRepositoryPort",
    "InventoryPartRepositoryPort",
]
