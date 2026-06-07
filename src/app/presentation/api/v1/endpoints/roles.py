from typing import Any

from fastapi import APIRouter, Depends, Query, status

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
    get_current_active_user,
    require_permission,
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


@router.post(
    "",
    response_model=RoleDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo rol",
)
async def create_role(
    company_id: str,
    request: CreateRoleRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "create")),
    use_case: CreateRoleUseCase = Depends(get_create_role_use_case),
) -> RoleDocument:
    permisos_dto = [
        PermissionDTO(
            module=p.module,
            can_view=p.can_view,
            can_create=p.can_create,
            can_edit=p.can_edit,
            can_delete=p.can_delete,
        )
        for p in request.data.attributes.permisos
    ]
    dto = CreateRoleDTO(
        nombre=request.data.attributes.nombre,
        descripcion=request.data.attributes.descripcion,
        permisos=permisos_dto,
    )
    res = await use_case.execute(company_id, dto)
    return RoleDocument(
        data=RoleResource(
            id=res.id,
            attributes=RoleAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                permisos=[
                    PermissionAttributes(
                        module=p.module,
                        can_view=p.can_view,
                        can_create=p.can_create,
                        can_edit=p.can_edit,
                        can_delete=p.can_delete,
                    )
                    for p in res.permisos
                ],
            ),
        )
    )


@router.get(
    "",
    response_model=RoleListDocument,
    summary="Listar roles de la empresa",
)
async def list_roles(
    company_id: str,
    current_user: Any = Depends(get_current_active_user),
    use_case: ListRolesUseCase = Depends(get_list_roles_use_case),
) -> RoleListDocument:
    roles = await use_case.execute(company_id)
    return RoleListDocument(
        data=[
            RoleResource(
                id=r.id,
                attributes=RoleAttributes(
                    nombre=r.nombre,
                    descripcion=r.descripcion,
                    permisos=[
                        PermissionAttributes(
                            module=p.module,
                            can_view=p.can_view,
                            can_create=p.can_create,
                            can_edit=p.can_edit,
                            can_delete=p.can_delete,
                        )
                        for p in r.permisos
                    ],
                ),
            )
            for r in roles
        ]
    )


@router.get(
    "/{id}",
    response_model=RoleDocument,
    summary="Obtener rol por ID",
)
async def get_role(
    company_id: str,
    id: str,
    current_user: Any = Depends(get_current_active_user),
    use_case: GetRoleUseCase = Depends(provide_role_use_case),
) -> RoleDocument:
    res = await use_case.execute(company_id, id)
    return RoleDocument(
        data=RoleResource(
            id=res.id,
            attributes=RoleAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                permisos=[
                    PermissionAttributes(
                        module=p.module,
                        can_view=p.can_view,
                        can_create=p.can_create,
                        can_edit=p.can_edit,
                        can_delete=p.can_delete,
                    )
                    for p in res.permisos
                ],
            ),
        )
    )


@router.patch(
    "/{id}",
    response_model=RoleDocument,
    summary="Actualizar rol",
)
async def update_role(
    company_id: str,
    id: str,
    request: UpdateRoleRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: UpdateRoleUseCase = Depends(get_update_role_use_case),
) -> RoleDocument:
    permisos_dto = None
    if request.data.attributes.permisos is not None:
        permisos_dto = [
            PermissionDTO(
                module=p.module,
                can_view=p.can_view,
                can_create=p.can_create,
                can_edit=p.can_edit,
                can_delete=p.can_delete,
            )
            for p in request.data.attributes.permisos
        ]
    dto = UpdateRoleDTO(
        nombre=request.data.attributes.nombre,
        descripcion=request.data.attributes.descripcion,
        permisos=permisos_dto,
    )
    res = await use_case.execute(company_id, id, dto)
    return RoleDocument(
        data=RoleResource(
            id=res.id,
            attributes=RoleAttributes(
                nombre=res.nombre,
                descripcion=res.descripcion,
                permisos=[
                    PermissionAttributes(
                        module=p.module,
                        can_view=p.can_view,
                        can_create=p.can_create,
                        can_edit=p.can_edit,
                        can_delete=p.can_delete,
                    )
                    for p in res.permisos
                ],
            ),
        )
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar rol",
)
async def delete_role(
    company_id: str,
    id: str,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "delete")),
    use_case: DeleteRoleUseCase = Depends(get_delete_role_use_case),
) -> None:
    await use_case.execute(company_id, id)


@router.post(
    "/{id}/assign",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Asignar rol a un usuario",
)
async def assign_role(
    company_id: str,
    id: str,
    request: AssignRoleRequest,
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: AssignRoleToUserUseCase = Depends(get_assign_role_to_user_use_case),
) -> None:
    await use_case.execute(company_id, id, request.data.attributes.usuario_id)


@router.delete(
    "/{id}/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revocar rol a un usuario",
)
async def revoke_role(
    company_id: str,
    id: str,
    usuario_id: str = Query(..., description="ID del usuario al que se le revoca el rol"),
    current_user: Any = Depends(require_permission(PermissionModule.ADMIN, "edit")),
    use_case: RevokeRoleFromUserUseCase = Depends(get_revoke_role_from_user_use_case),
) -> None:
    await use_case.execute(company_id, id, usuario_id)
