from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RoleNotFoundError, ValidationException
from app.domain.value_objects import CompanyId, RoleId, UserId


class RevokeRoleFromUserUseCase:
    """Caso de uso para revocar un rol a un usuario."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Inicializa el caso de uso con la unidad de trabajo (UoW)."""
        self.uow = uow

    async def execute(self, company_id_str: str, role_id_str: str, user_id_str: str) -> None:
        """Ejecuta la revocación de un rol de un usuario."""
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

            await self.uow.roles.revoke_from_user(role_id, user_id)
            await self.uow.commit()
