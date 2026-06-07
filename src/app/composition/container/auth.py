"""Fábricas de dependencias para los casos de uso de autenticación."""

from fastapi import Depends

from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.notifications import NotificationPort
from app.application.ports.unit_of_work import UnitOfWorkPort
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
from app.composition.container.common import (
    get_notification_sender,
    get_password_hasher,
    get_token_service,
    get_uow,
)


async def get_register_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
) -> RegisterUserUseCase:
    """Fábrica de dependencias para el caso de uso de registro de usuario."""
    return RegisterUserUseCase(uow, hasher, token_service)


async def get_login_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
) -> LoginUserUseCase:
    """Fábrica de dependencias para el caso de uso de inicio de sesión."""
    return LoginUserUseCase(uow, hasher, token_service)


async def get_refresh_token_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
) -> RefreshTokenUseCase:
    """Fábrica de dependencias para el caso de uso de rotación de tokens."""
    return RefreshTokenUseCase(uow, token_service)


async def get_logout_user_use_case(
    token_service: TokenServicePort = Depends(get_token_service),
) -> LogoutUserUseCase:
    """Fábrica de dependencias para el caso de uso de cierre de sesión."""
    return LogoutUserUseCase(token_service)


async def provide_current_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
) -> GetCurrentUserUseCase:
    """Fábrica de dependencias para el caso de uso de consulta del usuario actual."""
    return GetCurrentUserUseCase(uow, token_service)


def provide_change_password_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
) -> ChangePasswordUseCase:
    """Fábrica de dependencias para el caso de uso de cambio de contraseña."""
    return ChangePasswordUseCase(uow, hasher)


def provide_request_password_reset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
    notification: NotificationPort = Depends(get_notification_sender),
) -> RequestPasswordResetUseCase:
    """Fábrica de dependencias para el caso de uso de solicitud de reset."""
    from app.infrastructure.config.settings import settings

    return RequestPasswordResetUseCase(
        uow, token_service, notification, frontend_url=settings.FRONTEND_URL
    )


def provide_reset_password_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
    notification: NotificationPort = Depends(get_notification_sender),
) -> ResetPasswordUseCase:
    """Fábrica de dependencias para el caso de uso de reset con token."""
    return ResetPasswordUseCase(uow, hasher, token_service, notification)
