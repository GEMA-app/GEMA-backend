"""Puerto (Protocol) del servicio de autorización RBAC."""
from typing import Protocol

from app.domain.enums import PermissionModule
from app.domain.value_objects import CompanyId, UserId


class AuthorizationService(Protocol):
    """Servicio que verifica permisos RBAC antes de ejecutar operaciones."""

    async def check_permission(
        self,
        user_id: UserId,
        empresa_id: CompanyId,
        module: PermissionModule,
        action: str,  # 'view' | 'create' | 'edit' | 'delete'
    ) -> None:
        """Lanza InsufficientPermissionsError si el usuario no tiene el permiso requerido."""
        ...
