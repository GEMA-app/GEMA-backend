"""Re-exporta todas las entidades del dominio para imports planos."""

from app.domain.entities.article_category import ArticleCategory
from app.domain.entities.asset import Asset
from app.domain.entities.asset_state_log import AssetStateLog
from app.domain.entities.catalog_article import CatalogArticle
from app.domain.entities.company import Company
from app.domain.entities.failure_report import FailureReport
from app.domain.entities.location import Location
from app.domain.entities.maintenance_plan import MaintenancePlan
from app.domain.entities.permission import Permission
from app.domain.entities.plan_execution import PlanExecution
from app.domain.entities.preference import UserPreference
from app.domain.entities.role import Role
from app.domain.entities.subscription_plan import SubscriptionPlan
from app.domain.entities.system_audit import SystemAudit
from app.domain.entities.used_part import UsedPart
from app.domain.entities.user import User
from app.domain.entities.work_order import WorkOrder

__all__ = [
    "UsedPart",
    "User",
    "Company",
    "Role",
    "Permission",
    "Location",
    "PlanExecution",
    "MaintenancePlan",
    "Asset",
    "AssetStateLog",
    "ArticleCategory",
    "CatalogArticle",
    "SystemAudit",
    "UserPreference",
    "FailureReport",
    "WorkOrder",
    "SubscriptionPlan",
]
