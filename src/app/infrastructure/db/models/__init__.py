"""Modelos ORM de SQLAlchemy 2.0 para todas las tablas del sistema."""

from app.infrastructure.db.models.asset import AssetModel
from app.infrastructure.db.models.catalog import ArticleCategoryModel, CatalogArticleModel
from app.infrastructure.db.models.company import CompanyModel, SubscriptionPlanModel
from app.infrastructure.db.models.failure_report import FailureReportModel
from app.infrastructure.db.models.location import LocationModel
from app.infrastructure.db.models.mixins import TenantMixin, TimestampMixin, VersionMixin
from app.infrastructure.db.models.preference import UserPreferenceModel
from app.infrastructure.db.models.role import PermissionModel, RoleModel, RoleUserModel
from app.infrastructure.db.models.used_part import UsedPartModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.models.work_order import (
    WorkOrderModel,
    WorkOrderStatusLogModel,
    WorkOrderTechnicianModel,
)

from .asset_state_log import AssetStateLogModel

__all__ = [
    "UserModel",
    "SubscriptionPlanModel",
    "CompanyModel",
    "RoleUserModel",
    "PermissionModel",
    "RoleModel",
    "LocationModel",
    "ArticleCategoryModel",
    "CatalogArticleModel",
    "AssetModel",
    "FailureReportModel",
    "UsedPartModel",
    "UserPreferenceModel",
    "TenantMixin",
    "TimestampMixin",
    "VersionMixin",
    "AssetStateLogModel",
    "WorkOrderModel",
    "WorkOrderTechnicianModel",
    "WorkOrderStatusLogModel",
]
