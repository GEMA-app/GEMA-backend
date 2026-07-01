"""Adaptadores concretos de repositorios SQLAlchemy.

Implementaciones de los puertos de repositorio definidos en la capa de aplicación.
"""

from app.infrastructure.repositories.article_category_repository import (
    SqlAlchemyArticleCategoryRepository,
)
from app.infrastructure.repositories.asset_repository import SqlAlchemyAssetRepository
from app.infrastructure.repositories.asset_state_log_repository import (
    SqlAlchemyAssetStateLogRepository,
)
from app.infrastructure.repositories.base import SqlAlchemyRepository
from app.infrastructure.repositories.catalog_article_repository import (
    SqlAlchemyCatalogArticleRepository,
)
from app.infrastructure.repositories.company_repository import SqlAlchemyCompanyRepository
from app.infrastructure.repositories.failure_report_repository import (
    SqlAlchemyFailureReportRepository,
)
from app.infrastructure.repositories.intervention_repository import SqlAlchemyInterventionRepository
from app.infrastructure.repositories.inventory_part_repository import (
    SqlAlchemyInventoryPartRepository,
)
from app.infrastructure.repositories.location_repository import SqlAlchemyLocationRepository
from app.infrastructure.repositories.maintenance_plan_repository import (
    SqlAlchemyMaintenancePlanRepository,
)
from app.infrastructure.repositories.plan_execution_repository import (
    SqlAlchemyPlanExecutionRepository,
)
from app.infrastructure.repositories.preference_repository import SqlAlchemyPreferenceRepository
from app.infrastructure.repositories.role_repository import SqlAlchemyRoleRepository
from app.infrastructure.repositories.subscription_plan_repository import (
    SqlAlchemySubscriptionPlanRepository,
)
from app.infrastructure.repositories.system_audit_repository import (
    SqlAlchemySystemAuditRepository,
)
from app.infrastructure.repositories.tenant_repository import SqlAlchemyTenantRepository
from app.infrastructure.repositories.used_part_repository import SqlAlchemyUsedPartRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.repositories.work_order_repository import SqlAlchemyWorkOrderRepository

__all__ = [
    "SqlAlchemyRepository",
    "SqlAlchemyTenantRepository",
    "SqlAlchemyUserRepository",
    "SqlAlchemySubscriptionPlanRepository",
    "SqlAlchemyCompanyRepository",
    "SqlAlchemyRoleRepository",
    "SqlAlchemyAssetRepository",
    "SqlAlchemyArticleCategoryRepository",
    "SqlAlchemyAssetStateLogRepository",
    "SqlAlchemyCatalogArticleRepository",
    "SqlAlchemyFailureReportRepository",
    "SqlAlchemyLocationRepository",
    "SqlAlchemyPlanExecutionRepository",
    "SqlAlchemyMaintenancePlanRepository",
    "SqlAlchemyPreferenceRepository",
    "SqlAlchemyUsedPartRepository",
    "SqlAlchemyWorkOrderRepository",
    "SqlAlchemyInterventionRepository",
    "SqlAlchemySystemAuditRepository",
    "SqlAlchemyInventoryPartRepository",
]
