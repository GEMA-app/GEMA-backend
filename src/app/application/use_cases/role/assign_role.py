"""Caso de uso para asignar un rol a un usuario rol."""

from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RoleNotFoundError, ValidationException
from app.domain.value_objects import CompanyId, RoleId, UserId


class AssignRoleToUserUseCase:
    """Asigna un rol a un usuario de la empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(self, company_id_str: str, role_id_str: str, user_id_str: str) -> None:
        """Realiza la asignación del rol al usuario."""
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

            assigned = await self.uow.roles.assign_to_user(role_id, user_id)
            if assigned:
                role.record_assignment(user_id)
                await self.uow.roles.save(role)

            await self.uow.commit()
