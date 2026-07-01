"""Caso de uso para list role."""

from app.application.dtos.role_dtos import PermissionDTO, RoleResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.value_objects import CompanyId


class ListRolesUseCase:
    """Caso de uso para listar todos los roles de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str) -> list[RoleResponse]:
        """Obtiene la lista de todos los roles registrados en la empresa."""
        company_id = CompanyId.from_string(company_id_str)
        async with self.uow:
            roles = await self.uow.roles.list_by_company(company_id)
            return [
                RoleResponse(
                    id=str(r.id),
                    empresa_id=str(r.empresa_id),
                    nombre=r.nombre,
                    descripcion=r.descripcion,
                    permisos=[
                        PermissionDTO(
                            module=p.module.value,
                            can_view=p.can_view,
                            can_create=p.can_create,
                            can_edit=p.can_edit,
                            can_delete=p.can_delete,
                        )
                        for p in r.permisos
                    ],
                    version=r.version,
                )
                for r in roles
            ]
