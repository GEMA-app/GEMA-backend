"""Paquete de casos de uso — orquestación de la lógica de negocio por módulo."""

from app.application.use_cases.article_category import (
    CreateArticleCategoryUseCase,
    DeleteArticleCategoryUseCase,
    GetArticleCategoryByIdUseCase,
    ListArticleCategoriesUseCase,
    UpdateArticleCategoryUseCase,
)
from app.application.use_cases.asset import (
    CreateAssetUseCase,
    DeleteAssetUseCase,
    GetAssetUseCase,
    ListAssetsUseCase,
    UpdateAssetUseCase,
)
from app.application.use_cases.asset_state_log import ListAssetStateLogUseCase
from app.application.use_cases.auth import (
    ChangePasswordUseCase,
    GetCurrentUserUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from app.application.use_cases.catalog_article import (
    CreateCatalogArticleUseCase,
    DeleteCatalogArticleUseCase,
    GetCatalogArticleUseCase,
    ListCatalogArticlesUseCase,
    UpdateCatalogArticleUseCase,
)
from app.application.use_cases.company import (
    CreateCompanyUseCase,
    DeleteCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    UpdateCompanyUseCase,
)
from app.application.use_cases.failure_report import (
    CreateFailureReportUseCase,
    DeleteFailureReportUseCase,
    GetFailureReportUseCase,
    ListFailureReportsUseCase,
    UpdateFailureReportUseCase,
)
from app.application.use_cases.intervention import (
    CreateInterventionUseCase,
    DeleteInterventionUseCase,
    GetInterventionUseCase,
    ListInterventionsUseCase,
    UpdateInterventionUseCase,
)
from app.application.use_cases.location import (
    CreateLocationUseCase,
    DeleteLocationUseCase,
    GetLocationChildrenUseCase,
    GetLocationTreeUseCase,
    GetLocationUseCase,
    UpdateLocationUseCase,
)
from app.application.use_cases.maintenance_plan import (
    CreateMaintenancePlanUseCase,
    DeleteMaintenancePlanUseCase,
    GetMaintenancePlanUseCase,
    ListMaintenancePlansUseCase,
    UpdateMaintenancePlanUseCase,
)
from app.application.use_cases.plan_execution import (
    CreatePlanExecutionUseCase,
    GetPlanExecutionUseCase,
    ListPlanExecutionUseCase,
)
from app.application.use_cases.preference import (
    GetUserPreferencesUseCase,
    UpdateUserPreferencesUseCase,
)
from app.application.use_cases.role import (
    AssignRoleToUserUseCase,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    RevokeRoleFromUserUseCase,
    UpdateRoleUseCase,
)
from app.application.use_cases.subscription_plan import (
    CreateSubscriptionPlanUseCase,
    DeleteSubscriptionPlanUseCase,
    GetSubscriptionPlanUseCase,
    ListSubscriptionPlansUseCase,
    UpdateSubscriptionPlanUseCase,
)
from app.application.use_cases.system_audit import (
    GetSystemAuditUseCase,
    ListSystemAuditsUseCase,
)
from app.application.use_cases.used_part import (
    CreateUsedPartUseCase,
    DeleteUsedPartUseCase,
    GetUsedPartUseCase,
    ListUsedPartsUseCase,
    UpdateUsedPartUseCase,
)
from app.application.use_cases.user import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from app.application.use_cases.work_order import (
    AssignTechnicianUseCase,
    ChangeWorkOrderStatusUseCase,
    CreateWorkOrderUseCase,
    DeleteWorkOrderUseCase,
    GetWorkOrderStatusHistoryUseCase,
    GetWorkOrderUseCase,
    ListWorkOrdersUseCase,
    RemoveTechnicianUseCase,
    UpdateWorkOrderUseCase,
    ValidateWorkOrderUseCase,
)

__all__ = [
    # Article Category
    "CreateArticleCategoryUseCase",
    "GetArticleCategoryByIdUseCase",
    "ListArticleCategoriesUseCase",
    "UpdateArticleCategoryUseCase",
    "DeleteArticleCategoryUseCase",
    # Asset
    "CreateAssetUseCase",
    "GetAssetUseCase",
    "UpdateAssetUseCase",
    "DeleteAssetUseCase",
    "ListAssetsUseCase",
    # Asset State Log
    "ListAssetStateLogUseCase",
    # Auth
    "LoginUserUseCase",
    "LogoutUserUseCase",
    "RefreshTokenUseCase",
    "RegisterUserUseCase",
    "GetCurrentUserUseCase",
    "ChangePasswordUseCase",
    "RequestPasswordResetUseCase",
    "ResetPasswordUseCase",
    # Catalog Article
    "CreateCatalogArticleUseCase",
    "GetCatalogArticleUseCase",
    "UpdateCatalogArticleUseCase",
    "DeleteCatalogArticleUseCase",
    "ListCatalogArticlesUseCase",
    # Company
    "CreateCompanyUseCase",
    "GetCompanyUseCase",
    "UpdateCompanyUseCase",
    "DeleteCompanyUseCase",
    "ListCompaniesUseCase",
    # Failure Report
    "CreateFailureReportUseCase",
    "GetFailureReportUseCase",
    "UpdateFailureReportUseCase",
    "DeleteFailureReportUseCase",
    "ListFailureReportsUseCase",
    # Intervention
    "CreateInterventionUseCase",
    "GetInterventionUseCase",
    "ListInterventionsUseCase",
    "UpdateInterventionUseCase",
    "DeleteInterventionUseCase",
    # Location
    "CreateLocationUseCase",
    "GetLocationUseCase",
    "UpdateLocationUseCase",
    "DeleteLocationUseCase",
    "GetLocationTreeUseCase",
    "GetLocationChildrenUseCase",
    # Maintenance Plan
    "CreateMaintenancePlanUseCase",
    "GetMaintenancePlanUseCase",
    "UpdateMaintenancePlanUseCase",
    "DeleteMaintenancePlanUseCase",
    "ListMaintenancePlansUseCase",
    # Plan Execution
    "CreatePlanExecutionUseCase",
    "GetPlanExecutionUseCase",
    "ListPlanExecutionUseCase",
    # Preference
    "GetUserPreferencesUseCase",
    "UpdateUserPreferencesUseCase",
    # Role
    "CreateRoleUseCase",
    "GetRoleUseCase",
    "UpdateRoleUseCase",
    "DeleteRoleUseCase",
    "ListRolesUseCase",
    "AssignRoleToUserUseCase",
    "RevokeRoleFromUserUseCase",
    # Subscription Plan
    "CreateSubscriptionPlanUseCase",
    "GetSubscriptionPlanUseCase",
    "UpdateSubscriptionPlanUseCase",
    "DeleteSubscriptionPlanUseCase",
    "ListSubscriptionPlansUseCase",
    # System Audit
    "GetSystemAuditUseCase",
    "ListSystemAuditsUseCase",
    # Used Part
    "CreateUsedPartUseCase",
    "GetUsedPartUseCase",
    "UpdateUsedPartUseCase",
    "DeleteUsedPartUseCase",
    "ListUsedPartsUseCase",
    # User
    "CreateUserUseCase",
    "GetUserUseCase",
    "ListUsersUseCase",
    "UpdateUserUseCase",
    "DeleteUserUseCase",
    # Work Order
    "CreateWorkOrderUseCase",
    "GetWorkOrderUseCase",
    "UpdateWorkOrderUseCase",
    "DeleteWorkOrderUseCase",
    "ListWorkOrdersUseCase",
    "AssignTechnicianUseCase",
    "RemoveTechnicianUseCase",
    "ChangeWorkOrderStatusUseCase",
    "GetWorkOrderStatusHistoryUseCase",
    "ValidateWorkOrderUseCase",
]
