"""Implementación del servicio de autorización RBAC."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.application.services.authorization_service import AuthorizationService
from app.domain.enums import PermissionModule
from app.domain.exceptions import InsufficientPermissionsError
from app.domain.value_objects import CompanyId, UserId


class RbacAuthorizationService(AuthorizationService):
    """Verifica permisos consultando roles_usuarios y permisos vía el Unit of Work."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Inicializa el servicio de autorización con el Unit of Work.

        Args:
            uow: Unidad de trabajo para acceder a los roles y permisos.
        """
        self.uow = uow

    async def check_permission(
        self,
        user_id: UserId,
        empresa_id: CompanyId,
        module: PermissionModule,
        action: str,  # 'view' | 'create' | 'edit' | 'delete'
    ) -> None:
        """Verifica si un usuario tiene permisos para realizar una acción específica en un módulo.

        Args:
            user_id: Identificador del usuario a verificar.
            empresa_id: Identificador de la empresa asociada.
            module: Módulo del sistema sobre el que se realiza la acción.
            action: Acción a realizar ('view', 'create', 'edit' o 'delete').

        Raises:
            InsufficientPermissionsError: Si el usuario no cuenta con los permisos necesarios.
        """
        async with self.uow:
            roles = await self.uow.roles.get_user_roles(user_id, empresa_id)

            for role in roles:
                if role.has_permission(module, action):
                    return

            raise InsufficientPermissionsError(
                f"El usuario no tiene permisos para realizar la acción '{action}' "
                f"en el módulo '{module.value}'."
            )
