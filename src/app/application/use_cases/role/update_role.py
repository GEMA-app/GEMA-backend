from app.application.dtos.role_dtos import PermissionDTO, RoleResponse, UpdateRoleRequest
from app.application.ports.unit_of_work import UnitOfWorkPort
from app.domain.entities import Permission
from app.domain.enums import PermissionModule
from app.domain.exceptions import (
    RoleNameExistsError,
    RoleNotFoundError,
    StaleDataError,
    ValidationException,
)
from app.domain.value_objects import CompanyId, RoleId


class UpdateRoleUseCase:
    """Actualiza los datos de un rol."""

    def __init__(self, uow: UnitOfWorkPort) -> None:
        """Guarda dependencias."""
        self.uow = uow

    async def execute(
        self, company_id_str: str, role_id_str: str, request: UpdateRoleRequest
    ) -> RoleResponse:
        """Actualiza la información del rol."""
        company_id = CompanyId.from_string(company_id_str)
        role_id = RoleId.from_string(role_id_str)

        async with self.uow:
            role = await self.uow.roles.get_by_id(role_id, company_id)
            if not role:
                raise RoleNotFoundError(f"El rol con ID '{role_id_str}' no existe en esta empresa.")

            if request.version is not None and request.version != role.version:
                raise StaleDataError(
                    f"Conflicto de versión para rol: se esperaba {request.version}, "
                    f"la actual es {role.version}."
                )

            if 'nombre' in request._fields_set:
                if request.nombre is None:
                    raise ValidationException("El nombre del rol no puede ser nulo.")
                new_name = request.nombre.strip()
                if not new_name:
                    raise ValidationException("El nombre del rol no puede estar vacío.")
                # Verificar duplicados en la misma empresa
                existing_roles = await self.uow.roles.list_by_company(company_id)
                if any(
                    r.nombre.lower() == new_name.lower() and r.id != role.id for r in existing_roles
                ):
                    raise RoleNameExistsError(
                        f"Ya existe otro rol con el nombre '{new_name}' en esta empresa."
                    )
                role.nombre = new_name

            if 'descripcion' in request._fields_set:
                role.descripcion = request.descripcion or ""

            if 'permisos' in request._fields_set:
                if request.permisos is None:
                    raise ValidationException("Los permisos no pueden ser nulos.")
                permisos_map = {}
                for p in request.permisos:
                    permisos_map[p.module] = Permission(
                        module=PermissionModule(p.module),
                        can_view=p.can_view,
                        can_create=p.can_create,
                        can_edit=p.can_edit,
                        can_delete=p.can_delete,
                    )
                role.permisos = list(permisos_map.values())

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
                version=role.version,
            )
