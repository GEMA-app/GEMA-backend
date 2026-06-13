from app.application.dtos.role_dtos import PermissionDTO, RoleResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.exceptions import RoleNotFoundError
from app.domain.value_objects import CompanyId, RoleId


class GetRoleUseCase:
    """Caso de uso para obtener un rol por su ID."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, role_id_str: str) -> RoleResponse:
        """Obtiene un rol por su ID."""
        company_id = CompanyId.from_string(company_id_str)
        role_id = RoleId.from_string(role_id_str)

        async with self.uow:
            role = await self.uow.roles.get_by_id(role_id, company_id)
            if not role:
                raise RoleNotFoundError(f"El rol con ID '{role_id_str}' no existe en esta empresa.")

            return RoleResponse(
                id=str(role.id),
                empresa_id=str(role.empresa_id),
                nombre=role.nombre,
                descripcion=role.descripcion,
                permisos=[
                    PermissionDTO(
                        module=p.module.value,
                        can_view=p.can_view,
                        can_create=p.can_create,
                        can_edit=p.can_edit,
                        can_delete=p.can_delete,
                    )
                    for p in role.permisos
                ],
                version=role.version,
            )
