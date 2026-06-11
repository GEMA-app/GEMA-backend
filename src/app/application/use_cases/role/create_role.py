from app.application.dtos.role_dtos import CreateRoleRequest, PermissionDTO, RoleResponse
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Permission, Role
from app.domain.enums import PermissionModule
from app.domain.exceptions import RoleNameExistsError
from app.domain.value_objects import CompanyId


class CreateRoleUseCase:
    """Caso de uso para crear un rol dentro de una empresa."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(self, company_id_str: str, request: CreateRoleRequest) -> RoleResponse:
        company_id = CompanyId.from_string(company_id_str)

        async with self.uow:
            existing_roles = await self.uow.roles.list_by_company(company_id)
            if any(r.nombre.lower() == request.nombre.strip().lower() for r in existing_roles):
                raise RoleNameExistsError(
                    f"Ya existe un rol con el nombre '{request.nombre}' en esta empresa."
                )

            permisos_map = {}
            for p in request.permisos:
                permisos_map[p.module] = Permission(
                    module=PermissionModule(p.module),
                    can_view=p.can_view,
                    can_create=p.can_create,
                    can_edit=p.can_edit,
                    can_delete=p.can_delete,
                )
            permisos = list(permisos_map.values())

            role = Role.create(
                empresa_id=company_id,
                nombre=request.nombre,
                descripcion=request.descripcion,
                permisos=permisos,
            )

            await self.uow.roles.save(role)
            await self.uow.commit()

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
            )
