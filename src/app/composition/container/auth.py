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
from app.infrastructure.config.settings import settings


async def get_register_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
) -> RegisterUserUseCase:
    """Fábrica de dependencias para el caso de uso de registro de usuario.

    Args:
        uow: Unidad de trabajo para persistir el nuevo usuario.
        hasher: Servicio de hashing para la contraseña.
        token_service: Servicio de tokens JWT para emitir tokens iniciales.

    Returns:
        El caso de uso de registro de usuario con sus dependencias inyectadas.
    """
    return RegisterUserUseCase(uow, hasher, token_service)


async def get_login_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
) -> LoginUserUseCase:
    """Fábrica de dependencias para el caso de uso de inicio de sesión.

    Args:
        uow: Unidad de trabajo para consultar credenciales.
        hasher: Servicio de hashing para verificar la contraseña.
        token_service: Servicio de tokens JWT para emitir tokens.

    Returns:
        El caso de uso de inicio de sesión con sus dependencias inyectadas.
    """
    return LoginUserUseCase(uow, hasher, token_service)


async def get_refresh_token_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
) -> RefreshTokenUseCase:
    """Fábrica de dependencias para el caso de uso de rotación de tokens.

    Args:
        uow: Unidad de trabajo para validar el usuario.
        token_service: Servicio de tokens JWT para rotar el token.

    Returns:
        El caso de uso de rotación de tokens con sus dependencias inyectadas.
    """
    return RefreshTokenUseCase(uow, token_service)


async def get_logout_user_use_case(
    token_service: TokenServicePort = Depends(get_token_service),
) -> LogoutUserUseCase:
    """Fábrica de dependencias para el caso de uso de cierre de sesión.

    Args:
        token_service: Servicio de tokens JWT para invalidar el token.

    Returns:
        El caso de uso de cierre de sesión con sus dependencias inyectadas.
    """
    return LogoutUserUseCase(token_service)


async def get_current_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
) -> GetCurrentUserUseCase:
    """Fábrica de dependencias para el caso de uso de consulta del usuario actual.

    Args:
        uow: Unidad de trabajo para obtener los datos del usuario.
        token_service: Servicio de tokens JWT para validar el token.

    Returns:
        El caso de uso de consulta del usuario actual con sus dependencias inyectadas.
    """
    return GetCurrentUserUseCase(uow, token_service)


async def get_change_password_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
) -> ChangePasswordUseCase:
    """Fábrica de dependencias para el caso de uso de cambio de contraseña.

    Args:
        uow: Unidad de trabajo para persistir la nueva contraseña.
        hasher: Servicio de hashing para la nueva contraseña.

    Returns:
        El caso de uso de cambio de contraseña con sus dependencias inyectadas.
    """
    return ChangePasswordUseCase(uow, hasher)


async def get_request_password_reset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
    notification: NotificationPort = Depends(get_notification_sender),
) -> RequestPasswordResetUseCase:
    """Fábrica de dependencias para el caso de uso de solicitud de reset.

    Args:
        uow: Unidad de trabajo para validar el usuario.
        token_service: Servicio de tokens JWT para generar el token de reset.
        notification: Servicio de notificaciones para enviar el correo.

    Returns:
        El caso de uso de solicitud de reset con sus dependencias inyectadas.
    """
    return RequestPasswordResetUseCase(
        uow, token_service, notification, frontend_url=settings.FRONTEND_URL
    )


async def get_reset_password_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_service: TokenServicePort = Depends(get_token_service),
    notification: NotificationPort = Depends(get_notification_sender),
) -> ResetPasswordUseCase:
    """Fábrica de dependencias para el caso de uso de reset con token.

    Args:
        uow: Unidad de trabajo para persistir la nueva contraseña.
        hasher: Servicio de hashing para la nueva contraseña.
        token_service: Servicio de tokens JWT para validar el token de reset.
        notification: Servicio de notificaciones para confirmar el cambio.

    Returns:
        El caso de uso de reset de contraseña con sus dependencias inyectadas.
    """
    return ResetPasswordUseCase(uow, hasher, token_service, notification)
