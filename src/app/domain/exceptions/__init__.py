"""Paquete de excepciones de dominio.

Re-exporta todas las excepciones para mantener compatibilidad con los
imports existentes (``from app.domain.exceptions import X``).
"""

from app.domain.exceptions.asset import (
    AssetCodeExistsError,
    AssetException,
    AssetNotFoundError,
    AssetSerialExistsError,
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
    CompanyException,
    CompanyNotFoundError,
    CompanySlugExistsError,
    EmptyCompanyNameError,
)
from app.domain.exceptions.location import (
    LocationCircularReferenceError,
    LocationException,
    LocationInvalidTypeHierarchyError,
    LocationNotFoundError,
)
from app.domain.exceptions.permission import (
    InsufficientPermissionsError,
    PermissionException,
)
from app.domain.exceptions.role import (
    EmptyRoleNameError,
    RoleException,
    RoleNameExistsError,
    RoleNotFoundError,
)
from app.domain.exceptions.validation import (
    InvalidSlugError,
    InvalidUUIDError,
    ValidationException,
)

from app.domain.exceptions.preferences import (
    PreferenceException,
    PreferenceNotFoundError,
    PreferenceThemeInvalidError,
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
    "LocationException",
    "LocationNotFoundError",
    "LocationCircularReferenceError",
    "LocationInvalidTypeHierarchyError",
    "ValidationException",
    "PreferenceException",
    "PreferenceNotFoundError",
    "PreferenceThemeInvalidError",
]
