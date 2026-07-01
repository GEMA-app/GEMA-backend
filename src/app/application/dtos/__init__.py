from app.application.dtos.article_category_dtos import (
    ArticleCategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from app.application.dtos.asset_dtos import AssetResponse, CreateAssetRequest, UpdateAssetRequest
from app.application.dtos.asset_state_log_dtos import AssetStateLogResponse
from app.application.dtos.auth_dtos import (
    AuthTokensDTO,
    ChangePasswordRequest,
    GetCurrentUserRequest,
    LoginUserRequest,
    LogoutUserRequest,
    RefreshTokenRequest,
    RegisterUserRequest,
    RequestPasswordResetRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.application.dtos.catalog_article_dtos import (
    CatalogArticleResponse,
    CreateCatalogArticleRequest,
    UpdateCatalogArticleRequest,
)
from app.application.dtos.company_dtos import (
    CompanyResponse,
    CreateCompanyRequest,
    UpdateCompanyRequest,
)
from app.application.dtos.failure_report_dtos import (
    CreateFailureReportRequest,
    FailureReportResponse,
)
from app.application.dtos.intervention_dtos import (
    CreateInterventionRequest,
    InterventionResponse,
    UpdateInterventionRequest,
)
from app.application.dtos.inventory_part_dtos import (
    CreateInventoryEntryRequest,
    CreateInventoryPartRequest,
    InventoryEntryResponse,
    InventoryPartQueryFilter,
    InventoryPartResponse,
    UpdateInventoryPartRequest,
)
from app.application.dtos.location_dtos import (
    CreateLocationRequest,
    LocationResponse,
    LocationTreeResponse,
    UpdateLocationRequest,
)
from app.application.dtos.maintenance_plan_dtos import (
    CreateMaintenancePlanRequest,
    MaintenancePlanResponse,
    UpdateMaintenancePlanRequest,
)
from app.application.dtos.plan_execution_dtos import (
    PlanExecutionCreateRequest,
    PlanExecutionListResponse,
    PlanExecutionResponse,
)
from app.application.dtos.preference_dtos import PreferenceResponse, UpdatePreferenceRequest
from app.application.dtos.role_dtos import (
    AssignRoleRequest,
    CreateRoleRequest,
    PermissionDTO,
    RoleResponse,
    UpdateRoleRequest,
)
from app.application.dtos.subscription_plan_dtos import (
    CreateSubscriptionPlanRequest,
    SubscriptionPlanResponse,
    UpdateSubscriptionPlanRequest,
)
from app.application.dtos.supplier_dtos import (
    CreateSupplierRequest,
    SupplierResponse,
    UpdateSupplierRequest,
)
from app.application.dtos.system_audit_dtos import (
    ListSystemAuditsRequest,
    SystemAuditResponse,
)
from app.application.dtos.used_part_dtos import (
    CreateUsedPartRequest,
    UpdateUsedPartRequest,
    UsedPartResponse,
)
from app.application.dtos.user_dtos import (
    CreateUserRequest,
    UpdateUserRequest,
)
from app.application.dtos.user_dtos import (
    UserResponse as UserDetailResponse,
)
from app.application.dtos.work_order_dtos import (
    ChangeWorkOrderStatusRequest,
    CreateWorkOrderRequest,
    UpdateWorkOrderRequest,
    WorkOrderResponse,
)

__all__ = [
    "AuthTokensDTO",
    "ChangePasswordRequest",
    "GetCurrentUserRequest",
    "LoginUserRequest",
    "LogoutUserRequest",
    "RefreshTokenRequest",
    "RegisterUserRequest",
    "RequestPasswordResetRequest",
    "ResetPasswordRequest",
    "UserResponse",
    "CreateCompanyRequest",
    "UpdateCompanyRequest",
    "CompanyResponse",
    "PermissionDTO",
    "CreateRoleRequest",
    "UpdateRoleRequest",
    "AssignRoleRequest",
    "RoleResponse",
    "CreateAssetRequest",
    "UpdateAssetRequest",
    "AssetResponse",
    "AssetStateLogResponse",
    "CreateLocationRequest",
    "UpdateLocationRequest",
    "LocationResponse",
    "LocationTreeResponse",
    "PreferenceResponse",
    "UpdatePreferenceRequest",
    "CatalogArticleResponse",
    "CreateCatalogArticleRequest",
    "UpdateCatalogArticleRequest",
    "CreateFailureReportRequest",
    "FailureReportResponse",
    "CreateUsedPartRequest",
    "UpdateUsedPartRequest",
    "UsedPartResponse",
    # Inventory Part
    "CreateInventoryEntryRequest",
    "CreateInventoryPartRequest",
    "InventoryEntryResponse",
    "InventoryPartQueryFilter",
    "InventoryPartResponse",
    "UpdateInventoryPartRequest",
    "CreateWorkOrderRequest",
    "UpdateWorkOrderRequest",
    "WorkOrderResponse",
    "ChangeWorkOrderStatusRequest",
    "CreateSubscriptionPlanRequest",
    "SubscriptionPlanResponse",
    "UpdateSubscriptionPlanRequest",
    "CreateSupplierRequest",
    "SupplierResponse",
    "UpdateSupplierRequest",
    "CreateInterventionRequest",
    "InterventionResponse",
    "UpdateInterventionRequest",
    "ArticleCategoryResponse",
    "CreateCategoryRequest",
    "UpdateCategoryRequest",
    "CreateMaintenancePlanRequest",
    "MaintenancePlanResponse",
    "UpdateMaintenancePlanRequest",
    "PlanExecutionCreateRequest",
    "PlanExecutionResponse",
    "PlanExecutionListResponse",
    "ListSystemAuditsRequest",
    "SystemAuditResponse",
    "CreateUserRequest",
    "UpdateUserRequest",
    "UserDetailResponse",
]
