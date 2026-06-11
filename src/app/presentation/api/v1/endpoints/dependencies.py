from typing import Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dtos.auth_dtos import UserResponse
from app.application.services.authorization_service import AuthorizationService
from app.application.use_cases.auth import GetCurrentUserUseCase
from app.composition.container import get_authorization_service, provide_current_user_use_case
from app.domain.enums import PermissionModule
from app.domain.exceptions import InsufficientPermissionsError, InvalidUUIDError
from app.domain.value_objects import CompanyId, UserId
from app.infrastructure.cache.redis import redis_client

security = HTTPBearer()


def validate_tenant_access(empresa_id: str, user_empresa_id: str) -> None:
    """Valida que empresa_id pertenezca al tenant del usuario.
    Normaliza UUID para evitar bypass por formato (con/sin guiones, mayúsculas/minúsculas).
    """
    try:
        if UUID(empresa_id) != UUID(user_empresa_id):
            raise InsufficientPermissionsError("No tienes acceso a esta empresa")
    except ValueError as e:
        raise InvalidUUIDError(
            f"El identificador '{empresa_id}' no es un UUID válido."
        ) from e


def require_platform_permission(module: PermissionModule, action: str) -> Any:
    """Auth + RBAC para endpoints SIN empresa_id en el path (ej: POST /v1/empresas)."""
    async def dependency(
        token: HTTPAuthorizationCredentials = Depends(security),
        auth_use_case: GetCurrentUserUseCase = Depends(provide_current_user_use_case),
        auth_service: AuthorizationService = Depends(get_authorization_service),
    ) -> UserResponse:
        user_resp = await auth_use_case.execute(token.credentials)
        user_id = UserId.from_string(user_resp.id)
        empresa_id = CompanyId.from_string(user_resp.empresa_id)
        await auth_service.check_permission(user_id, empresa_id, module, action)
        return user_resp
    return dependency


def require_permission(module: PermissionModule, action: str) -> Any:
    """Dependencia unificada: auth + tenant validation + RBAC en una sola llamada."""

    async def dependency(
        empresa_id: str,
        token: HTTPAuthorizationCredentials = Depends(security),
        auth_use_case: GetCurrentUserUseCase = Depends(provide_current_user_use_case),
        auth_service: AuthorizationService = Depends(get_authorization_service),
    ) -> UserResponse:
        user_resp = await auth_use_case.execute(token.credentials)
        # 1. Tenant validation (UUID normalization)
        validate_tenant_access(empresa_id, user_resp.empresa_id)
        # 2. RBAC check
        user_id = UserId.from_string(user_resp.id)
        empresa_id_obj = CompanyId.from_string(user_resp.empresa_id)
        await auth_service.check_permission(user_id, empresa_id_obj, module, action)
        return user_resp

    return dependency


async def get_current_active_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: GetCurrentUserUseCase = Depends(provide_current_user_use_case),
) -> UserResponse:
    """Dependencia para obtener el usuario autenticado activo."""
    return await auth_use_case.execute(token.credentials)


async def require_tenant_read(
    empresa_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    """Valida solo tenant access, sin RBAC (UUID normalization)."""
    validate_tenant_access(empresa_id, current_user.empresa_id)
    return current_user


EMAIL_LUA_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""

email_rate_limit_script = redis_client.register_script(EMAIL_LUA_SCRIPT)


async def rate_limit_by_email(request: Request) -> None:
    """Limita intentos por email en endpoints de autenticación."""
    from fastapi import HTTPException, status
    from redis.exceptions import RedisError


    try:
        body = await request.json()
    except Exception:
        return  # Fail-open

    email = body.get("data", {}).get("attributes", {}).get("email", "")
    if not email:
        return

    email_clean = str(email).lower().strip()
    path = request.url.path.rstrip("/")

    limit = 5
    if path.endswith("/registrar"):
        limit = 3

    key = f"rate_limit:email:{email_clean}"
    try:
        current = await email_rate_limit_script(keys=[key], args=["60"])
        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Has excedido el límite de {limit} solicitudes por minuto para este correo.",
            )
    except RedisError:
        pass  # Fail-open

