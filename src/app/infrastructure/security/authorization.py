from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.services.authorization_service import AuthorizationService
from app.domain.enums import PermissionModule
from app.domain.exceptions import InsufficientPermissionsError
from app.domain.value_objects import CompanyId, UserId


class RbacAuthorizationService(AuthorizationService):
    """Verifica permisos consultando roles_usuarios y permisos vía el Unit of Work."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def check_permission(
        self,
        user_id: UserId,
        empresa_id: CompanyId,
        module: PermissionModule,
        action: str  # 'view' | 'create' | 'edit' | 'delete'
    ) -> None:
        async with self.uow:
            # Obtener los roles del usuario asignados en esa empresa
            roles = await self.uow.roles.get_user_roles(user_id, empresa_id)

            for role in roles:
                if role.has_permission(module, action):
                    return

            raise InsufficientPermissionsError(
                f"El usuario no tiene permisos para realizar la acción '{action}' "
                f"en el módulo '{module.value}'."
            )
