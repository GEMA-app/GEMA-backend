from typing import Any, Protocol, Self

from app.application.ports.article_category_repository import ArticleCategoryRepositoryPort
from app.application.ports.asset_repository import AssetRepositoryPort
from app.application.ports.asset_state_log_repository import AssetStateLogRepositoryPort
from app.application.ports.catalog_article_repository import CatalogArticleRepositoryPort
from app.application.ports.company_repository import CompanyRepositoryPort
from app.application.ports.event_bus import EventBusPort
from app.application.ports.failure_report_repository import FailureReportRepositoryPort
from app.application.ports.intervention_repository import InterventionRepositoryPort
from app.application.ports.location_repository import LocationRepositoryPort
from app.application.ports.maintenance_plan_repository import MaintenancePlanRepositoryPort
from app.application.ports.plan_execution_repository import (
    PlanExecutionRepositoryPort,
)
from app.application.ports.preference_repository import PreferenceRepositoryPort
from app.application.ports.repository import UserRepositoryPort
from app.application.ports.role_repository import RoleRepositoryPort
from app.application.ports.subscription_plan_repository import SubscriptionPlanRepositoryPort
from app.application.ports.system_audit_repository import SystemAuditRepositoryPort
from app.application.ports.used_part_repository import UsedPartRepositoryPort
from app.application.ports.work_order_repository import WorkOrderRepositoryPort


class UnitOfWorkPort(Protocol):
    """Puerto para el patrón Unit of Work, gestionando transacciones y repositorios."""

    users: UserRepositoryPort
    system_audits: SystemAuditRepositoryPort
    companies: CompanyRepositoryPort
    roles: RoleRepositoryPort
    assets: AssetRepositoryPort
    asset_state_logs: AssetStateLogRepositoryPort
    catalog_articles: CatalogArticleRepositoryPort
    locations: LocationRepositoryPort
    event_bus: EventBusPort
    preferences: PreferenceRepositoryPort
    article_categories: ArticleCategoryRepositoryPort
    failure_reports: FailureReportRepositoryPort
    used_parts: UsedPartRepositoryPort
    work_orders: WorkOrderRepositoryPort
    plan_executions: PlanExecutionRepositoryPort
    subscription_plans: SubscriptionPlanRepositoryPort
    maintenance_plans: MaintenancePlanRepositoryPort
    interventions: InterventionRepositoryPort
    async def __aenter__(self) -> Self:
        """Inicia el contexto transaccional asíncrono."""
        ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, tb: Any) -> None:
        """Cierra el contexto, ejecutando un rollback automático en caso de excepción."""
        ...

    async def commit(self) -> None:
        """Confirma los cambios pendientes en la base de datos."""
        ...

    async def rollback(self) -> None:
        """Deshace los cambios no confirmados en la transacción actual."""
        ...
