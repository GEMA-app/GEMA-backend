"""Endpoints CRUD de usuarios bajo el alcance de una empresa (Tenant).

Requiere autenticación JWT y permisos RBAC sobre el módulo administracion.
La validación de tenant (empresa_id del path vs JWT) se realiza dentro de
require_permission() vía validate_tenant_access().
"""

from fastapi import APIRouter, Depends, status

from app.application.dtos.auth_dtos import UserResponse as CurrentUserResponse
from app.application.dtos.user_dtos import (
    CreateUserRequest as CreateUserDTO,
)
from app.application.dtos.user_dtos import (
    UpdateUserRequest as EditUserDTO,
)
from app.application.use_cases.user import (
    CreateUserUseCase,
    DeleteUserUseCase,
    EditUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
)
from app.composition.container.user import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_edit_user_use_case,
    get_list_users_use_case,
    get_user_use_case,
)
from app.domain.enums import PermissionModule
from app.presentation.api.v1.endpoints.dependencies import (
    require_permission,
)
from app.presentation.api.v1.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserAttributes,
    UserDocument,
    UserListDocument,
    UserResource,
)

router = APIRouter()


@router.get(
    "",
    response_model=UserListDocument,
    summary="Listar usuarios de la empresa",
)
async def list_users(
    empresa_id: str,
    current_user: CurrentUserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "view")
    ),
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> UserListDocument:
    """Retorna todos los usuarios pertenecientes a la empresa especificada.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        current_user: Usuario autenticado (validado por require_permission).
        use_case: Caso de uso de listado inyectado.

    Returns:
        Documento JSON:API con la lista de usuarios.
    """
    users = await use_case.execute(empresa_id)
    return UserListDocument(
        data=[
            UserResource(
                id=u.id,
                attributes=UserAttributes(
                    email=u.email,
                    nombre=u.nombre,
                    telefono=u.telefono,
                    activo=u.activo,
                    empresa_id=u.empresa_id,
                    roles=u.roles,
                    created_at=u.created_at,
                    updated_at=u.updated_at,
                ),
            )
            for u in users
        ],
        meta={"total": len(users)},
    )


@router.post(
    "",
    response_model=UserDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
)
async def create_user(
    empresa_id: str,
    request: CreateUserRequest,
    current_user: CurrentUserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "create")
    ),
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserDocument:
    """Registra un nuevo usuario dentro de la empresa especificada en la URL.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        request: Cuerpo de la solicitud JSON:API.
        current_user: Usuario autenticado (validado por require_permission).
        use_case: Caso de uso de creación inyectado.

    Returns:
        Documento JSON:API con los datos del usuario creado.
    """
    attrs = request.data.attributes
    dto = CreateUserDTO(
        email=attrs.email,
        password=attrs.password,
        nombre=attrs.nombre,
        telefono=attrs.telefono,
    )
    res = await use_case.execute(empresa_id, dto)
    return UserDocument(
        data=UserResource(
            id=res.id,
            attributes=UserAttributes(
                email=res.email,
                nombre=res.nombre,
                telefono=res.telefono,
                activo=res.activo,
                empresa_id=res.empresa_id,
                roles=res.roles,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.get(
    "/{usuario_id}",
    response_model=UserDocument,
    summary="Obtener usuario por ID",
)
async def get_user(
    empresa_id: str,
    usuario_id: str,
    current_user: CurrentUserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "view")
    ),
    use_case: GetUserUseCase = Depends(get_user_use_case),
) -> UserDocument:
    """Obtiene los detalles de un usuario específico validando su contexto de empresa.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        usuario_id: Identificador del usuario a consultar.
        current_user: Usuario autenticado (validado por require_permission).
        use_case: Caso de uso de consulta inyectado.

    Returns:
        Documento JSON:API con los datos del usuario encontrado.
    """
    res = await use_case.execute(usuario_id, empresa_id)
    return UserDocument(
        data=UserResource(
            id=res.id,
            attributes=UserAttributes(
                email=res.email,
                nombre=res.nombre,
                telefono=res.telefono,
                activo=res.activo,
                empresa_id=res.empresa_id,
                roles=res.roles,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.patch(
    "/{usuario_id}",
    response_model=UserDocument,
    summary="Actualizar usuario",
)
async def update_user(
    empresa_id: str,
    usuario_id: str,
    request: UpdateUserRequest,
    current_user: CurrentUserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "edit")
    ),
    use_case: EditUserUseCase = Depends(get_edit_user_use_case),
) -> UserDocument:
    """Actualiza parcialmente los datos de un usuario perteneciente a la empresa.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        usuario_id: Identificador del usuario a actualizar.
        request: Cuerpo de la solicitud JSON:API.
        current_user: Usuario autenticado (validado por require_permission).
        use_case: Caso de uso de edición inyectado.

    Returns:
        Documento JSON:API con los datos del usuario actualizado.
    """
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)

    dto = EditUserDTO(
        nombre=sent.get("nombre"),
        email=sent.get("email"),
        telefono=sent.get("telefono"),
        activo=sent.get("activo"),
    )
    res = await use_case.execute(usuario_id, empresa_id, dto)
    return UserDocument(
        data=UserResource(
            id=res.id,
            attributes=UserAttributes(
                email=res.email,
                nombre=res.nombre,
                telefono=res.telefono,
                activo=res.activo,
                empresa_id=res.empresa_id,
                roles=res.roles,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dar de baja (desactivar) usuario",
)
async def delete_user(
    empresa_id: str,
    usuario_id: str,
    current_user: CurrentUserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "delete")
    ),
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case),
) -> None:
    """Desactiva (baja lógica) un usuario cambiando su estado activo a False.

    Args:
        empresa_id: Identificador de la empresa (tenant).
        usuario_id: Identificador del usuario a desactivar.
        current_user: Usuario autenticado (validado por require_permission).
        use_case: Caso de uso de baja lógica inyectado.
    """
    await use_case.execute(usuario_id, empresa_id)
