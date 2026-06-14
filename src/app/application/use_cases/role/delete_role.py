from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RoleNotFoundError
from app.domain.value_objects import CompanyId, RoleId


class DeleteRoleUseCase:
    """Caso de uso para eliminar un rol."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, role_id_str: str) -> None:
        """Elimina un rol por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        role_id = RoleId.from_string(role_id_str)

        async with self.uow:
            role = await self.uow.roles.get_by_id(role_id, company_id)
            if not role:
                raise RoleNotFoundError(f"El rol con ID '{role_id_str}' no existe en esta empresa.")

            from app.domain.enums import PermissionModule
            from app.domain.exceptions import LastAdminRevocationError, ValidationException

            if role.nombre == "Administrador":
                raise ValidationException(
                    "No se puede eliminar el rol de Administrador del sistema."
                )

            if any(p.module == PermissionModule.ADMIN and p.can_delete for p in role.permisos):
                remaining_admins = await self.uow.roles.count_admin_users(empresa_id=company_id)
                if remaining_admins <= 1:
                    raise LastAdminRevocationError()

            await self.uow.roles.delete(role_id, company_id)
            await self.uow.commit()
