"""Schemas JSON:API para la API v1.

Re-exporta todos los schemas de los módulos para facilitar las importaciones.
"""

from app.presentation.api.v1.schemas.article_category import (
    ArticleCategoryDocument,
    ArticleCategoryListDocument,
    ArticleCategoryResource,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.presentation.api.v1.schemas.asset import (
    AssetDocument,
    AssetListDocument,
    AssetResource,
    CreateAssetRequest,
    UpdateAssetRequest,
)
from app.presentation.api.v1.schemas.asset_state_log import AssetStateLogListDocument
from app.presentation.api.v1.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RateLimitEmailBody,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenDocument,
)
from app.presentation.api.v1.schemas.catalog_article import (
    CatalogArticleDocument,
    CatalogArticleListDocument,
    CatalogArticleResource,
    CreateCatalogArticleRequest,
    UpdateCatalogArticleRequest,
)
from app.presentation.api.v1.schemas.company import (
    CompanyDocument,
    CompanyListDocument,
    CompanyResource,
    CreateCompanyRequest,
    UpdateCompanyRequest,
)
from app.presentation.api.v1.schemas.failure_report import (
    CreateFailureReportRequest,
    FailureReportDocument,
    FailureReportListDocument,
    FailureReportResource,
    UpdateFailureReportRequest,
)
from app.presentation.api.v1.schemas.intervention import (
    CreateInterventionRequest,
    InterventionDocument,
    InterventionListDocument,
    InterventionResource,
    UpdateInterventionRequest,
)
from app.presentation.api.v1.schemas.location import (
    CreateLocationRequest,
    LocationDocument,
    LocationListDocument,
    LocationResource,
    UpdateLocationRequest,
)
from app.presentation.api.v1.schemas.maintenance_plan import (
    CreateMaintenancePlanRequest,
    MaintenancePlanDocument,
    MaintenancePlanListDocument,
    MaintenancePlanResource,
    UpdateMaintenancePlanRequest,
)
from app.presentation.api.v1.schemas.plan_execution import (
    CreatePlanExecutionRequest,
    PlanExecutionDocument,
    PlanExecutionListDocument,
    PlanExecutionResource,
)
from app.presentation.api.v1.schemas.preference import (
    PreferenceDocument,
    PreferenceResource,
    UpdatePreferenceRequest,
)
from app.presentation.api.v1.schemas.role import (
    AssignRoleRequest,
    CreateRoleRequest,
    RoleDocument,
    RoleListDocument,
    RoleResource,
    UpdateRoleRequest,
)
from app.presentation.api.v1.schemas.subscription_plan import (
    SubscriptionPlanDocument,
    SubscriptionPlanListDocument,
    SubscriptionPlanResource,
)
from app.presentation.api.v1.schemas.system_audit import (
    SystemAuditDocument,
    SystemAuditListDocument,
)
from app.presentation.api.v1.schemas.used_part import (
    CreateUsedPartRequest,
    UpdateUsedPartRequest,
    UsedPartDocument,
    UsedPartResource,
    UsedPartsDocument,
)
from app.presentation.api.v1.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserDocument,
    UserListDocument,
    UserResource,
)
from app.presentation.api.v1.schemas.work_order import (
    AssignTechnicianRequest,
    ChangeStatusRequest,
    CreateWorkOrderRequest,
    UpdateWorkOrderRequest,
    WorkOrderDocument,
    WorkOrderListDocument,
    WorkOrderResource,
)

__all__ = [
    "ArticleCategoryDocument",
    "ArticleCategoryListDocument",
    "ArticleCategoryResource",
    "AssetDocument",
    "AssetListDocument",
    "AssetResource",
    "AssetStateLogListDocument",
    "AssignRoleRequest",
    "AssignTechnicianRequest",
    "CatalogArticleDocument",
    "CatalogArticleListDocument",
    "CatalogArticleResource",
    "ChangePasswordRequest",
    "ChangeStatusRequest",
    "CompanyDocument",
    "CompanyListDocument",
    "CompanyResource",
    "CreateCategoryRequest",
    "CreateAssetRequest",
    "CreateCatalogArticleRequest",
    "CreateCompanyRequest",
    "CreateFailureReportRequest",
    "CreateInterventionRequest",
    "CreateLocationRequest",
    "CreateMaintenancePlanRequest",
    "CreatePlanExecutionRequest",
    "CreateRoleRequest",
    "CreateUsedPartRequest",
    "CreateUserRequest",
    "CreateWorkOrderRequest",
    "FailureReportDocument",
    "FailureReportListDocument",
    "FailureReportResource",
    "ForgotPasswordRequest",
    "InterventionDocument",
    "InterventionListDocument",
    "InterventionResource",
    "LocationDocument",
    "LocationListDocument",
    "LocationResource",
    "LoginRequest",
    "LogoutRequest",
    "MaintenancePlanDocument",
    "MaintenancePlanListDocument",
    "MaintenancePlanResource",
    "PlanExecutionDocument",
    "PlanExecutionListDocument",
    "PlanExecutionResource",
    "PreferenceDocument",
    "PreferenceResource",
    "RateLimitEmailBody",
    "RefreshRequest",
    "RegisterRequest",
    "ResetPasswordRequest",
    "RoleDocument",
    "RoleListDocument",
    "RoleResource",
    "SubscriptionPlanDocument",
    "SubscriptionPlanListDocument",
    "SubscriptionPlanResource",
    "SystemAuditDocument",
    "SystemAuditListDocument",
    "TokenDocument",
    "UpdateCategoryRequest",
    "UpdateAssetRequest",
    "UpdateCatalogArticleRequest",
    "UpdateCompanyRequest",
    "UpdateFailureReportRequest",
    "UpdateInterventionRequest",
    "UpdateLocationRequest",
    "UpdateMaintenancePlanRequest",
    "UpdatePreferenceRequest",
    "UpdateRoleRequest",
    "UpdateUsedPartRequest",
    "UpdateUserRequest",
    "UpdateWorkOrderRequest",
    "UsedPartDocument",
    "UsedPartsDocument",
    "UsedPartResource",
    "UserDocument",
    "UserListDocument",
    "UserResource",
    "WorkOrderDocument",
    "WorkOrderListDocument",
    "WorkOrderResource",
]
