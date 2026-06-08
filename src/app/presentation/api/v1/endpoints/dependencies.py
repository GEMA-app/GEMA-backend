from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dtos.auth_dtos import UserResponse
from app.application.services.authorization_service import AuthorizationService
from app.application.use_cases.auth import GetCurrentUserUseCase
from app.composition.container import get_authorization_service, provide_current_user_use_case
from app.domain.enums import PermissionModule
from app.domain.exceptions import InsufficientPermissionsError
from app.domain.value_objects import CompanyId, UserId

security = HTTPBearer()


def require_permission(module: PermissionModule, action: str) -> Any:
    """Dependencia unificada: auth + tenant validation + RBAC en una sola llamada."""

    async def dependency(
        company_id: str,
        token: HTTPAuthorizationCredentials = Depends(security),
        auth_use_case: GetCurrentUserUseCase = Depends(provide_current_user_use_case),
        auth_service: AuthorizationService = Depends(get_authorization_service),
    ) -> Any:
        user_resp = await auth_use_case.execute(token.credentials)
        # 1. Tenant validation (cierra IDOR)
        if company_id != user_resp.empresa_id:
            raise InsufficientPermissionsError("No tienes acceso a esta empresa")
        # 2. RBAC check
        user_id = UserId.from_string(user_resp.id)
        empresa_id = CompanyId.from_string(user_resp.empresa_id)
        await auth_service.check_permission(user_id, empresa_id, module, action)
        return user_resp

    return dependency


async def get_current_active_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: GetCurrentUserUseCase = Depends(provide_current_user_use_case),
) -> Any:
    """Dependencia para obtener el usuario autenticado activo."""
    return await auth_use_case.execute(token.credentials)


async def require_tenant_read(
    company_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    """Valida solo tenant access, sin RBAC."""
    if company_id != current_user.empresa_id:
        raise InsufficientPermissionsError("No tienes acceso a esta empresa")
    return current_user
