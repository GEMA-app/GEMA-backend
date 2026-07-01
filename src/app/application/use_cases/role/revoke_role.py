"""Caso de uso para revocar un rol a un usuario rol."""
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RoleNotFoundError, ValidationException
from app.domain.value_objects import CompanyId, RoleId, UserId


class RevokeRoleFromUserUseCase:
    """Revoca un rol a un usuario de la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(self, company_id_str: str, role_id_str: str, user_id_str: str) -> None:
        """Realiza la revocación del rol del usuario."""
        company_id = CompanyId.from_string(company_id_str)
        role_id = RoleId.from_string(role_id_str)
        user_id = UserId.from_string(user_id_str)

        async with self.uow:
            role = await self.uow.roles.get_by_id(role_id, company_id)
            if not role:
                raise RoleNotFoundError(f"El rol con ID '{role_id_str}' no existe en esta empresa.")

            user = await self.uow.users.get_by_id(user_id)
            if not user or user.empresa_id != company_id:
                raise ValidationException("El usuario no existe o no pertenece a esta empresa.")

            from app.domain.enums import PermissionModule
            from app.domain.exceptions import LastAdminRevocationError

            user_roles = await self.uow.roles.get_user_roles(user_id, company_id)
            has_role = any(r.id == role.id for r in user_roles)

            if has_role:
                # Verificar si el rol es administrador y es el último en la empresa
                if any(p.module == PermissionModule.ADMIN and p.can_delete for p in role.permisos):
                    remaining_admins = await self.uow.roles.count_admin_users(
                        empresa_id=company_id, exclude_user_id=user_id
                    )
                    if remaining_admins == 0:
                        raise LastAdminRevocationError()

                # Registrar evento de revocación en la entidad e invocar guardado
                role.record_revocation(user_id)
                await self.uow.roles.save(role)
                await self.uow.roles.revoke_from_user(role_id, user_id)

            await self.uow.commit()

