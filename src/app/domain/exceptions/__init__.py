"""Paquete de excepciones de dominio.

Re-exporta todas las excepciones para mantener compatibilidad con los
imports existentes (``from app.domain.exceptions import X``).
"""
from app.domain.exceptions.article_category import (
    ArticleCategoryException,
    ArticleCategoryNameExistsError,
    ArticleCategoryNotFoundError,
)
from app.domain.exceptions.asset import (
    AssetCodeExistsError,
    AssetException,
    AssetInvalidTransitionError,
    AssetNotFoundError,
    AssetSerialExistsError,
    EmptyAssetCodeError,
    EmptySerialError,
)
from app.domain.exceptions.asset_state_log import (
    AssetStateLogException,
    AssetStateLogNotFoundError,
)
from app.domain.exceptions.auth import (
    AuthException,
    EmptyHashedPasswordError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserInactiveError,
    WeakPasswordError,
)
from app.domain.exceptions.base import DomainException, ValidationError
from app.domain.exceptions.catalog import (
    CatalogArticleException,
    CatalogArticleHasAssetsError,
    CatalogArticleNotFoundError,
    EmptyCatalogArticleCodeError,
    EmptyCatalogArticleNameError,
)
from app.domain.exceptions.company import (
    CompanyAlreadyCancelledError,
    CompanyException,
    CompanyNotFoundError,
    CompanyNotSuspendedError,
    CompanySlugExistsError,
    EmptyCompanyNameError,
)
from app.domain.exceptions.event_bus import EventPublishError
from app.domain.exceptions.failure_report import (
    EmptyDescriptionError,
    EmptyLocationError,
    EmptyReportedByError,
    EmptyTitleError,
    FailureReportException,
    FailureReportNotFoundError,
)
from app.domain.exceptions.intervention import (
    InterventionException,
    InterventionInvalidDataError,
    InterventionInvalidTransitionError,
    InterventionNotFoundError,
)
from app.domain.exceptions.location import (
    EmptyLocationNameError,
    LocationCircularReferenceError,
    LocationException,
    LocationInvalidTypeHierarchyError,
    LocationNotFoundError,
)
from app.domain.exceptions.maintenance_plan import (
    MaintenancePlanDueDateError,
    MaintenancePlanException,
    MaintenancePlanIntervalError,
    MaintenancePlanNameEmptyError,
    MaintenancePlanNotFoundError,
)
from app.domain.exceptions.notifications import (
    NotificationError,
    TemplateNotFoundError,
)
from app.domain.exceptions.permission import (
    InsufficientPermissionsError,
    PermissionException,
)
from app.domain.exceptions.plan_execution import (
    PlanExecutionException,
    PlanExecutionNotFoundError,
    PlanExecutionObservationsEmptyError,
)
from app.domain.exceptions.preference import (
    PreferenceException,
    PreferenceNotFoundError,
    PreferenceThemeInvalidError,
)
from app.domain.exceptions.role import (
    EmptyRoleNameError,
    LastAdminRevocationError,
    RoleException,
    RoleNameExistsError,
    RoleNotFoundError,
)
from app.domain.exceptions.stale_data import StaleDataError
from app.domain.exceptions.subscription_plan import (
    SubscriptionPlanAlreadyExistsError,
    SubscriptionPlanException,
    SubscriptionPlanHasActiveSubscriptionsError,
    SubscriptionPlanInvalidDataError,
    SubscriptionPlanLimitExceededError,
    SubscriptionPlanNotFoundError,
    SubscriptionPlanPaymentFailedError,
)
from app.domain.exceptions.system_audit import (
    EmptyActionError,
    NullCompanyError,
    SystemAuditException,
    SystemAuditNotFoundError,
)
from app.domain.exceptions.used_part import (
    InsufficientStockError,
    UsedPartException,
    UsedPartInvalidPriceError,
    UsedPartInvalidQuantityError,
    UsedPartNotFoundError,
)
from app.domain.exceptions.user import UserException, UserNotFoundError
from app.domain.exceptions.validation import (
    InvalidSlugError,
    InvalidUUIDError,
    ValidationException,
)
from app.domain.exceptions.work_order import (
    WorkOrderCodeExistsError,
    WorkOrderException,
    WorkOrderInvalidDataError,
    WorkOrderInvalidStateError,
    WorkOrderNotFoundError,
)

__all__ = [
    "DomainException",
    "CatalogArticleException",
    "CatalogArticleNotFoundError",
    "CatalogArticleHasAssetsError",
    "EmptyCatalogArticleNameError",
    "EmptyCatalogArticleCodeError",
    "EmptyCompanyNameError",
    "EmptyHashedPasswordError",
    "EmptyRoleNameError",
    "InvalidSlugError",
    "InvalidUUIDError",
    "AuthException",
    "WeakPasswordError",
    "InvalidEmailError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "UserInactiveError",
    "InvalidTokenError",
    "CompanyException",
    "CompanyNotFoundError",
    "CompanySlugExistsError",
    "RoleException",
    "RoleNotFoundError",
    "RoleNameExistsError",
    "PermissionException",
    "InsufficientPermissionsError",
    "AssetException",
    "AssetNotFoundError",
    "AssetCodeExistsError",
    "AssetSerialExistsError",
    "AssetInvalidTransitionError",
    "EmptySerialError",
    "EmptyAssetCodeError",
    "AssetStateLogException",
    "AssetStateLogNotFoundError",
    "MaintenancePlanDueDateError",
    "MaintenancePlanException",
    "MaintenancePlanNotFoundError",
    "MaintenancePlanNameEmptyError",
    "MaintenancePlanIntervalError",
    "EmptyLocationNameError",
    "CompanyAlreadyCancelledError",
    "CompanyNotSuspendedError",
    "LocationException",
    "LocationNotFoundError",
    "LocationCircularReferenceError",
    "LocationInvalidTypeHierarchyError",
    "ValidationException",
    "PreferenceException",
    "PreferenceNotFoundError",
    "PreferenceThemeInvalidError",
    "LastAdminRevocationError",
    "StaleDataError",
    "EventPublishError",
    "ValidationError",
    "ArticleCategoryException",
    "ArticleCategoryNameExistsError",
    "ArticleCategoryNotFoundError",
    "FailureReportException",
    "FailureReportNotFoundError",
    "EmptyTitleError",
    "EmptyDescriptionError",
    "EmptyLocationError",
    "EmptyReportedByError",
    "UsedPartException",
    "UsedPartNotFoundError",
    "UsedPartInvalidQuantityError",
    "UsedPartInvalidPriceError",
    "InsufficientStockError",
    "WorkOrderException",
    "WorkOrderNotFoundError",
    "WorkOrderCodeExistsError",
    "WorkOrderInvalidStateError",
    "WorkOrderInvalidDataError",
    "PlanExecutionException",
    "PlanExecutionNotFoundError",
    "PlanExecutionObservationsEmptyError",
    "SubscriptionPlanException",
    "SubscriptionPlanNotFoundError",
    "SubscriptionPlanAlreadyExistsError",
    "SubscriptionPlanInvalidDataError",
    "SubscriptionPlanLimitExceededError",
    "SubscriptionPlanPaymentFailedError",
    "SubscriptionPlanHasActiveSubscriptionsError",
    "SystemAuditException",
    "SystemAuditNotFoundError",
    "EmptyActionError",
    "NullCompanyError",
    "UserException",
    "UserNotFoundError",
    # Excepciones de intervención
    "InterventionException",
    "InterventionInvalidDataError",
    "InterventionInvalidTransitionError",
    "InterventionNotFoundError",
    # Excepciones de notificaciones
    "NotificationError",
    "TemplateNotFoundError",
]
