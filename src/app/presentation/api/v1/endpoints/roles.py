"""Endpoints CRUD de roles: creación, listado, obtención, actualización,
eliminación, asignación y revocación de roles a usuarios.
"""

from fastapi import APIRouter, Depends, Query, status

from app.application.dtos.auth_dtos import UserResponse
from app.application.dtos.role_dtos import (
    CreateRoleRequest as CreateRoleDTO,
)
from app.application.dtos.role_dtos import (
    PermissionDTO,
)
from app.application.dtos.role_dtos import (
    UpdateRoleRequest as UpdateRoleDTO,
)
from app.application.use_cases.role import (
    AssignRoleToUserUseCase,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetRoleUseCase,
    ListRolesUseCase,
    RevokeRoleFromUserUseCase,
    UpdateRoleUseCase,
)
from app.composition.container import (
    get_assign_role_to_user_use_case,
    get_create_role_use_case,
    get_delete_role_use_case,
    get_list_roles_use_case,
    get_revoke_role_from_user_use_case,
    get_update_role_use_case,
    provide_role_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
    require_tenant_read,
)
from app.presentation.api.v1.schemas.role import (
    AssignRoleRequest,
    CreateRoleRequest,
    PermissionAttributes,
    RoleAttributes,
    RoleDocument,
    RoleListDocument,
    RoleResource,
    UpdateRoleRequest,
)

router = APIRouter()


def _to_permission_dto(p: PermissionAttributes) -> PermissionDTO:
    """Convierte PermissionAttributes (schema) a PermissionDTO (application)."""
    return PermissionDTO(
        module=p.module,
        can_view=p.can_view,
        can_create=p.can_create,
        can_edit=p.can_edit,
        can_delete=p.can_delete,
    )


def _to_permission_attributes(p: PermissionDTO) -> PermissionAttributes:
    """Convierte PermissionDTO (application) a PermissionAttributes (schema)."""
    return PermissionAttributes(
        module=p.module,
        can_view=p.can_view,
        can_create=p.can_create,
        can_edit=p.can_edit,
        can_delete=p.can_delete,
    )


@router.post(
    "",
    response_model=RoleDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo rol",
)
async def create_role(
    empresa_id: str,
    request: CreateRoleRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "create")),
    use_case: CreateRoleUseCase = Depends(get_create_role_use_case),
) -> RoleDocument:
    """Crea un nuevo rol con permisos en una empresa.

    Args:
        empresa_id: Identificador de la empresa.
        request: Datos del rol en formato JSON:API.
        current_user: Usuario autenticado con permiso de administración.
        use_case: Caso de uso de creación de rol.

    Returns:
        Documento JSON:API con los datos del rol creado.
    """
    permisos_dto = [_to_permission_dto(p) for p in request.data.attributes.permisos]
    dto = CreateRoleDTO(
        nombre=request.data.attributes.nombre,
        descripcion=request.data.attributes.descripcion,
        permisos=permisos_dto,
    )
    res = await use_case.execute(empresa_id, dto)
    return RoleDocument(
        data=RoleResource(
            id=res.id,
            attributes=RoleAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                permisos=[_to_permission_attributes(p) for p in res.permisos],
                version=res.version,
            ),
        )
    )


@router.get(
    "",
    response_model=RoleListDocument,
    summary="Listar roles de la empresa",
)
async def list_roles(
    empresa_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: ListRolesUseCase = Depends(get_list_roles_use_case),
) -> RoleListDocument:
    """Lista todos los roles de una empresa.

    Args:
        empresa_id: Identificador de la empresa.
        current_user: Usuario autenticado con acceso al tenant.
        use_case: Caso de uso de listado de roles.

    Returns:
        Documento JSON:API con la lista de roles.
    """
    roles = await use_case.execute(empresa_id)
    return RoleListDocument(
        data=[
            RoleResource(
                id=r.id,
                attributes=RoleAttributes(
                    nombre=r.nombre,
                    descripcion=r.descripcion,
                permisos=[_to_permission_attributes(p) for p in r.permisos],
                    version=r.version,
                ),
            )
            for r in roles
        ]
    )


@router.get(
    "/{rol_id}",
    response_model=RoleDocument,
    summary="Obtener rol por ID",
)
async def get_role(
    empresa_id: str,
    rol_id: str,
    current_user: UserResponse = Depends(require_tenant_read),
    use_case: GetRoleUseCase = Depends(provide_role_use_case),
) -> RoleDocument:
    """Obtiene los detalles de un rol por su ID.

    Args:
        empresa_id: Identificador de la empresa.
        rol_id: Identificador único del rol.
        current_user: Usuario autenticado con acceso al tenant.
        use_case: Caso de uso de obtención de rol.

    Returns:
        Documento JSON:API con los datos del rol.
    """
    res = await use_case.execute(empresa_id, rol_id)
    return RoleDocument(
        data=RoleResource(
            id=res.id,
            attributes=RoleAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                permisos=[_to_permission_attributes(p) for p in res.permisos],
                version=res.version,
            ),
        )
    )


@router.patch(
    "/{rol_id}",
    response_model=RoleDocument,
    summary="Actualizar rol",
)
async def update_role(
    empresa_id: str,
    rol_id: str,
    request: UpdateRoleRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateRoleUseCase = Depends(get_update_role_use_case),
) -> RoleDocument:
    """Actualiza los datos y permisos de un rol existente.

    Args:
        empresa_id: Identificador de la empresa.
        rol_id: Identificador único del rol.
        request: Datos actualizados en formato JSON:API.
        current_user: Usuario autenticado con permiso de edición.
        use_case: Caso de uso de actualización de rol.

    Returns:
        Documento JSON:API con los datos actualizados del rol.
    """
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    permisos_dto = None
    if "permisos" in sent and attrs.permisos is not None:
        permisos_dto = [_to_permission_dto(p) for p in attrs.permisos]
    dto = UpdateRoleDTO(
        nombre=sent.get("nombre") if "nombre" in sent else None,
        descripcion=sent.get("descripcion") if "descripcion" in sent else None,
        permisos=permisos_dto,
        version=sent.get("version") if "version" in sent else None,
        _fields_set=frozenset(sent.keys()),
    )
    res = await use_case.execute(empresa_id, rol_id, dto)
    return RoleDocument(
        data=RoleResource(
            id=res.id,
            attributes=RoleAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                permisos=[_to_permission_attributes(p) for p in res.permisos],
                version=res.version,
            ),
        )
    )


@router.delete(
    "/{rol_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar rol",
)
async def delete_role(
    empresa_id: str,
    rol_id: str,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteRoleUseCase = Depends(get_delete_role_use_case),
) -> None:
    """Elimina un rol de la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        rol_id: Identificador único del rol a eliminar.
        current_user: Usuario autenticado con permiso de eliminación.
        use_case: Caso de uso de eliminación de rol.
    """
    await use_case.execute(empresa_id, rol_id)


@router.post(
    "/{rol_id}/asignar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Asignar rol a un usuario",
)
async def assign_role(
    empresa_id: str,
    rol_id: str,
    request: AssignRoleRequest,
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: AssignRoleToUserUseCase = Depends(get_assign_role_to_user_use_case),
) -> None:
    """Asigna un rol a un usuario de la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        rol_id: Identificador único del rol.
        request: Datos con el ID del usuario destino.
        current_user: Usuario autenticado con permiso de edición.
        use_case: Caso de uso de asignación de rol.
    """
    await use_case.execute(empresa_id, rol_id, request.data.attributes.usuario_id)


@router.delete(
    "/{rol_id}/revocar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revocar rol a un usuario",
)
async def revoke_role(
    empresa_id: str,
    rol_id: str,
    usuario_id: str = Query(..., description="ID del usuario al que se le revoca el rol"),
    current_user: UserResponse = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: RevokeRoleFromUserUseCase = Depends(get_revoke_role_from_user_use_case),
) -> None:
    """Revoca un rol asignado a un usuario de la empresa.

    Args:
        empresa_id: Identificador de la empresa.
        rol_id: Identificador único del rol.
        usuario_id: Identificador del usuario destino.
        current_user: Usuario autenticado con permiso de edición.
        use_case: Caso de uso de revocación de rol.
    """
    await use_case.execute(empresa_id, rol_id, usuario_id)
