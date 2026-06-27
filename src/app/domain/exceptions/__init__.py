"""Paquete de excepciones de dominio.

Re-exporta todas las excepciones para mantener compatibilidad con los
imports existentes (``from app.domain.exceptions import X``).
"""

from app.domain.exceptions.asset import (
    AssetCodeExistsError,
    AssetException,
    AssetInvalidTransitionError,
    AssetNotFoundError,
    AssetSerialExistsError,
    EmptyAssetCodeError,
    EmptySerialError,
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
from app.domain.exceptions.base import DomainException
from app.domain.exceptions.company import (
    CompanyAlreadyCancelledError,
    CompanyException,
    CompanyNotFoundError,
    CompanyNotSuspendedError,
    CompanySlugExistsError,
    EmptyCompanyNameError,
)
from app.domain.exceptions.event_bus import EventPublishError
from app.domain.exceptions.location import (
    EmptyLocationNameError,
    LocationCircularReferenceError,
    LocationException,
    LocationInvalidTypeHierarchyError,
    LocationNotFoundError,
)
from app.domain.exceptions.permission import (
    InsufficientPermissionsError,
    PermissionException,
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
from app.domain.exceptions.validation import (
    InvalidSlugError,
    InvalidUUIDError,
    ValidationException,
)

__all__ = [
    "DomainException",
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
    "SubscriptionPlanException",
    "SubscriptionPlanNotFoundError",
    "SubscriptionPlanAlreadyExistsError",
    "SubscriptionPlanInvalidDataError",
    "SubscriptionPlanLimitExceededError",
    "SubscriptionPlanPaymentFailedError",
    "SubscriptionPlanHasActiveSubscriptionsError",
]
