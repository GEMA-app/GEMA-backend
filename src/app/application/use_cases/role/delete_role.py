from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import RoleId, CompanyId
from app.domain.exceptions import RoleNotFoundError


class DeleteRoleUseCase:
    """Caso de uso para eliminar un rol."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, role_id_str: str) -> None:
        company_id = CompanyId.from_string(company_id_str)
        role_id = RoleId.from_string(role_id_str)

        async with self.uow:
            role = await self.uow.roles.get_by_id(role_id, company_id)
            if not role:
                raise RoleNotFoundError(f"El rol con ID '{role_id_str}' no existe en esta empresa.")

            await self.uow.roles.delete(role_id, company_id)
            await self.uow.commit()
