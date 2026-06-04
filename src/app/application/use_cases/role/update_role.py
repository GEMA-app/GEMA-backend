from app.application.dtos.role_dtos import PermissionDTO, RoleResponse, UpdateRoleRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Permission
from app.domain.enums import PermissionModule
from app.domain.exceptions import RoleNameExistsError, RoleNotFoundError
from app.domain.value_objects import CompanyId, RoleId


class UpdateRoleUseCase:
    """Caso de uso para actualizar un rol."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        self.uow = uow

    async def execute(
        self, company_id_str: str, role_id_str: str, request: UpdateRoleRequest
    ) -> RoleResponse:
        company_id = CompanyId.from_string(company_id_str)
        role_id = RoleId.from_string(role_id_str)

        async with self.uow:
            role = await self.uow.roles.get_by_id(role_id, company_id)
            if not role:
                raise RoleNotFoundError(f"El rol con ID '{role_id_str}' no existe en esta empresa.")

            if request.nombre is not None:
                new_name = request.nombre.strip()
                if not new_name:
                    raise ValueError("El nombre del rol no puede estar vacío.")
                # Verificar duplicados en la misma empresa
                existing_roles = await self.uow.roles.list_by_company(company_id)
                if any(
                    r.nombre.lower() == new_name.lower() and r.id != role.id for r in existing_roles
                ):
                    raise RoleNameExistsError(
                        f"Ya existe otro rol con el nombre '{new_name}' en esta empresa."
                    )
                role.nombre = new_name

            if request.descripcion is not None:
                role.descripcion = request.descripcion

            if request.permisos is not None:
                role.permisos = [
                    Permission(
                        module=PermissionModule(p.module),
                        can_view=p.can_view,
                        can_create=p.can_create,
                        can_edit=p.can_edit,
                        can_delete=p.can_delete,
                    )
                    for p in request.permisos
                ]

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
