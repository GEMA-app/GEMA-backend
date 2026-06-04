"""Fábricas de dependencias para los casos de uso de autenticación."""

from fastapi import Depends

from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.auth import (
    GetCurrentUserUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
)
from app.composition.container.common import (
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
