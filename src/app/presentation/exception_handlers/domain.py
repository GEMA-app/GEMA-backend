"""Manejador de excepciones de dominio. Mapea cada excepción de
dominio (DomainException) a su código HTTP correspondiente según
la tabla definida en AGENTS.md.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AssetCodeExistsError,
    AssetInvalidTransitionError,
    AssetNotFoundError,
    AssetSerialExistsError,
    CompanyAlreadyCancelledError,
    CompanyNotFoundError,
    CompanyNotSuspendedError,
    CompanySlugExistsError,
    DomainException,
    EmptyAssetCodeError,
    EmptyCompanyNameError,
    EmptyHashedPasswordError,
    EmptyLocationNameError,
    EmptyRoleNameError,
    EmptySerialError,
    InsufficientPermissionsError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidSlugError,
    InvalidTokenError,
    InvalidUUIDError,
    LastAdminRevocationError,
    LocationCircularReferenceError,
    LocationInvalidTypeHierarchyError,
    LocationNotFoundError,
    PreferenceNotFoundError,
    PreferenceThemeInvalidError,
    RoleNameExistsError,
    RoleNotFoundError,
    StaleDataError,
    UserAlreadyExistsError,
    UserInactiveError,
    ValidationException,
    WeakPasswordError,
)
from app.presentation.api.v1.schemas.jsonapi_base import ErrorObject
from app.presentation.exception_handlers.base import jsonapi_response

# ---------------------------------------------------------------------------
# Registro declarativo: tipo de excepción → (código HTTP, código de error).
# Para agregar una excepción nueva, basta con añadir una línea al dict.
# ---------------------------------------------------------------------------
_EXCEPTION_MAP: dict[type[DomainException], tuple[int, str]] = {
    WeakPasswordError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_WEAK_PASSWORD"
    ),
    InvalidEmailError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_INVALID_EMAIL"
    ),
    UserAlreadyExistsError: (
        status.HTTP_409_CONFLICT,
        "ERR_USER_ALREADY_EXISTS"
    ),
    InvalidCredentialsError: (
        status.HTTP_401_UNAUTHORIZED,
        "ERR_INVALID_CREDENTIALS"
    ),
    UserInactiveError: (
        status.HTTP_403_FORBIDDEN,
        "ERR_USER_INACTIVE"
    ),
    InvalidTokenError: (
        status.HTTP_401_UNAUTHORIZED,
        "ERR_INVALID_TOKEN"
    ),
    CompanyNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "ERR_COMPANY_NOT_FOUND"
    ),
    CompanySlugExistsError: (
        status.HTTP_409_CONFLICT,
        "ERR_COMPANY_SLUG_EXISTS"
    ),
    RoleNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "ERR_ROLE_NOT_FOUND"
    ),
    RoleNameExistsError: (
        status.HTTP_409_CONFLICT,
        "ERR_ROLE_NAME_EXISTS"
    ),
    InsufficientPermissionsError: (
        status.HTTP_403_FORBIDDEN,
        "ERR_INSUFFICIENT_PERMISSIONS"
    ),
    AssetNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "ERR_ASSET_NOT_FOUND"
    ),
    AssetCodeExistsError: (
        status.HTTP_409_CONFLICT,
        "ERR_ASSET_CODE_EXISTS"
    ),
    AssetSerialExistsError: (
        status.HTTP_409_CONFLICT,
        "ERR_ASSET_SERIAL_EXISTS"
    ),
    LocationNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "ERR_LOCATION_NOT_FOUND"
    ),
    LocationCircularReferenceError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_LOCATION_CIRCULAR_REFERENCE",
    ),
    LocationInvalidTypeHierarchyError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_LOCATION_INVALID_TYPE_HIERARCHY",
    ),
    InvalidUUIDError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_INVALID_UUID"
    ),
    InvalidSlugError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_INVALID_SLUG"
    ),
    CompanyAlreadyCancelledError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_COMPANY_ALREADY_CANCELLED",
    ),
    CompanyNotSuspendedError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_COMPANY_NOT_SUSPENDED",
    ),
    EmptyCompanyNameError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_EMPTY_COMPANY_NAME"
    ),
    EmptyRoleNameError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_EMPTY_ROLE_NAME"
    ),
    EmptyHashedPasswordError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_EMPTY_HASHED_PASSWORD"
    ),
    ValidationException: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_VALIDATION",
    ),
    PreferenceNotFoundError: (
        status.HTTP_404_NOT_FOUND,
        "ERR_PREFERENCE_NOT_FOUND"
    ),
    PreferenceThemeInvalidError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_PREFERENCE_THEME_INVALID"
    ),
    AssetInvalidTransitionError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_ASSET_INVALID_TRANSITION",
    ),
    EmptySerialError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_EMPTY_SERIAL",
    ),
    EmptyAssetCodeError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_EMPTY_ASSET_CODE",
    ),
    EmptyLocationNameError: (
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERR_EMPTY_LOCATION_NAME",
    ),
    LastAdminRevocationError: (
        status.HTTP_403_FORBIDDEN,
        "ERR_LAST_ADMIN_REVOCATION",
    ),
    StaleDataError: (
        status.HTTP_409_CONFLICT,
        "ERR_STALE_DATA",
    ),
}


async def domain_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Mapea excepciones del dominio a códigos HTTP y formato JSON:API."""
    assert isinstance(exc, DomainException)
    status_code, code = _EXCEPTION_MAP.get(type(exc), (status.HTTP_400_BAD_REQUEST, "ERR_DOMAIN"))
    error = ErrorObject(
        status=str(status_code),
        code=code,
        title=exc.__class__.__name__,
        detail=str(exc),
    )
    return jsonapi_response(status_code, [error])
