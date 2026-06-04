from typing import Any
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.services.authorization_service import AuthorizationService
from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.composition.container import get_authorization_service, get_get_current_user_use_case
from app.domain.enums import PermissionModule
from app.domain.value_objects import CompanyId, UserId

security = HTTPBearer()


def require_permission(module: PermissionModule, action: str) -> Any:
    """Dependencia para requerir un permiso específico usando RBAC."""
    async def dependency(
        token: HTTPAuthorizationCredentials = Depends(security),
        auth_use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
        auth_service: AuthorizationService = Depends(get_authorization_service)
    ) -> Any:
        user_resp = await auth_use_case.execute(token.credentials)
        user_id = UserId.from_string(user_resp.id)
        empresa_id = CompanyId.from_string(user_resp.empresa_id)
        await auth_service.check_permission(user_id, empresa_id, module, action)
        return user_resp
    return dependency


async def get_current_active_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case)
) -> Any:
    """Dependencia para obtener el usuario autenticado activo."""
    return await auth_use_case.execute(token.credentials)
