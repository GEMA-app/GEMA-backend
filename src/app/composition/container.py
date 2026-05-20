from fastapi import Depends
from redis.asyncio import Redis
from app.application.ports.auth import PasswordHasherPort, TokenServicePort
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.logout_user import LogoutUserUseCase
from app.application.use_cases.refresh_token import RefreshTokenUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.infrastructure.cache.redis import get_redis
from app.infrastructure.security.hashing import BcryptPasswordHasher
from app.infrastructure.security.jwt import PyJwtTokenService
from app.infrastructure.uow import SqlAlchemyUnitOfWork


def get_uow() -> UnitOfWorkPort:
    """Fábrica de dependencias para el Unit of Work de SQLAlchemy."""
    return SqlAlchemyUnitOfWork()


def get_password_hasher() -> PasswordHasherPort:
    """Fábrica de dependencias para el servicio de hashing con Bcrypt."""
    return BcryptPasswordHasher()


async def get_token_service(redis: Redis = Depends(get_redis)) -> TokenServicePort:
    """Fábrica de dependencias para el servicio de tokens JWT con Redis."""
    return PyJwtTokenService(redis)


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


async def get_get_current_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
    token_service: TokenServicePort = Depends(get_token_service),
) -> GetCurrentUserUseCase:
    """Fábrica de dependencias para el caso de uso de consulta del usuario actual."""
    return GetCurrentUserUseCase(uow, token_service)
