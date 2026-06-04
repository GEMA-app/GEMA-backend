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


from app.application.services.authorization_service import AuthorizationService

# Asset use cases
from app.application.use_cases.asset import (
    CreateAssetUseCase,
    DeleteAssetUseCase,
    GetAssetUseCase,
    ListAssetsUseCase,
    UpdateAssetUseCase,
)

# Company use cases
from app.application.use_cases.company import (
    CreateCompanyUseCase,
    DeleteCompanyUseCase,
    GetCompanyUseCase,
    ListCompaniesUseCase,
    UpdateCompanyUseCase,
)

# Location use cases
from app.application.use_cases.location import (
    CreateLocationUseCase,
    DeleteLocationUseCase,
    GetLocationChildrenUseCase,
    GetLocationTreeUseCase,
    GetLocationUseCase,
    UpdateLocationUseCase,
)

# Role use cases
from app.application.use_cases.role import (
    AssignRoleToUserUseCase,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    RevokeRoleFromUserUseCase,
    UpdateRoleUseCase,
)
from app.infrastructure.security.authorization import RbacAuthorizationService


async def get_authorization_service(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AuthorizationService:
    """Fábrica de dependencias para el servicio de autorización RBAC."""
    return RbacAuthorizationService(uow)


# Company Factories
async def get_create_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateCompanyUseCase:
    return CreateCompanyUseCase(uow)


async def get_get_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetCompanyUseCase:
    return GetCompanyUseCase(uow)


async def get_list_companies_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListCompaniesUseCase:
    return ListCompaniesUseCase(uow)


async def get_update_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateCompanyUseCase:
    return UpdateCompanyUseCase(uow)


async def get_delete_company_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteCompanyUseCase:
    return DeleteCompanyUseCase(uow)


# Role Factories
async def get_create_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateRoleUseCase:
    return CreateRoleUseCase(uow)


async def get_get_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetRoleUseCase:
    return GetRoleUseCase(uow)


async def get_list_roles_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListRolesUseCase:
    return ListRolesUseCase(uow)


async def get_update_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateRoleUseCase:
    return UpdateRoleUseCase(uow)


async def get_delete_role_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteRoleUseCase:
    return DeleteRoleUseCase(uow)


async def get_assign_role_to_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> AssignRoleToUserUseCase:
    return AssignRoleToUserUseCase(uow)


async def get_revoke_role_from_user_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> RevokeRoleFromUserUseCase:
    return RevokeRoleFromUserUseCase(uow)


# Asset Factories
async def get_create_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateAssetUseCase:
    return CreateAssetUseCase(uow)


async def get_get_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetAssetUseCase:
    return GetAssetUseCase(uow)


async def get_list_assets_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> ListAssetsUseCase:
    return ListAssetsUseCase(uow)


async def get_update_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateAssetUseCase:
    return UpdateAssetUseCase(uow)


async def get_delete_asset_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteAssetUseCase:
    return DeleteAssetUseCase(uow)


# Location Factories
async def get_create_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> CreateLocationUseCase:
    return CreateLocationUseCase(uow)


async def get_get_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationUseCase:
    return GetLocationUseCase(uow)


async def get_get_location_tree_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationTreeUseCase:
    return GetLocationTreeUseCase(uow)


async def get_get_location_children_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> GetLocationChildrenUseCase:
    return GetLocationChildrenUseCase(uow)


async def get_update_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> UpdateLocationUseCase:
    return UpdateLocationUseCase(uow)


async def get_delete_location_use_case(
    uow: UnitOfWorkPort = Depends(get_uow),
) -> DeleteLocationUseCase:
    return DeleteLocationUseCase(uow)

