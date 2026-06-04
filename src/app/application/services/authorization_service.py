from typing import Protocol
from app.domain.value_objects import UserId, CompanyId
from app.domain.enums import PermissionModule


class AuthorizationService(Protocol):
    """Servicio que verifica permisos RBAC antes de ejecutar operaciones."""

    async def check_permission(
        self,
        user_id: UserId,
        empresa_id: CompanyId,
        module: PermissionModule,
        action: str  # 'view' | 'create' | 'edit' | 'delete'
    ) -> None:
        """Lanza InsufficientPermissionsError si el usuario no tiene el permiso requerido."""
        ...
