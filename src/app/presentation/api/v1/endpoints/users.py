"""Endpoints CRUD de usuarios bajo el alcance de una empresa (Tenant).
"""

from fastapi import APIRouter, Depends, status

from app.application.dtos.user_dtos import (
    CreateUserRequest as CreateUserDTO,
    UpdateUserRequest as EditUserDTO,
)
from app.application.dtos.auth_dtos import UserResponse
from app.application.use_cases.user import (
    CreateUserUseCase,
    DeleteUserUseCase,
    EditUserUseCase,
    GetUserUseCase,
)
from app.composition.container.user import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_edit_user_use_case,
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
    UserResource,
)

router = APIRouter()


@router.post(
    "",
    response_model=UserDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo usuario",
)
async def create_user(
    empresa_id: str,
    request: CreateUserRequest,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "create")
    ),
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserDocument:
    """Registra un nuevo usuario dentro de la empresa especificada en la URL."""
    attrs = request.data.attributes
    dto = CreateUserDTO(
        email=attrs.email,
        password=attrs.password,
        nombre=attrs.nombre,
        telefono=attrs.telefono,
        empresa_id=empresa_id,
    )
    res = await use_case.execute(dto)
    return UserDocument(
        data=UserResource(
            id=res.id,
            attributes=UserAttributes(
                email=res.email,
                nombre=res.nombre,
                telefono=res.telefono,
                activo=res.activo,
                empresa_id=res.empresa_id,
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
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "view")
    ),
    use_case: GetUserUseCase = Depends(get_user_use_case),
) -> UserDocument:
    """Obtiene los detalles de un usuario específico validando su contexto de empresa."""
    res = await use_case.execute(usuario_id)
    return UserDocument(
        data=UserResource(
            id=res.id,
            attributes=UserAttributes(
                email=res.email,
                nombre=res.nombre,
                telefono=res.telefono,
                activo=res.activo,
                empresa_id=res.empresa_id,
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
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "edit")
    ),
    use_case: EditUserUseCase = Depends(get_edit_user_use_case),
) -> UserDocument:
    """Actualiza parcialmente los datos de un usuario perteneciente a la empresa."""
    attrs = request.data.attributes
    sent = attrs.model_dump(exclude_unset=True)
    
    dto = EditUserDTO(
        nombre=sent.get("nombre"),
        email=sent.get("email"),
        telefono=sent.get("telefono"),
        activo=sent.get("activo"),
    )
    res = await use_case.execute(usuario_id, dto)
    return UserDocument(
        data=UserResource(
            id=res.id,
            attributes=UserAttributes(
                email=res.email,
                nombre=res.nombre,
                telefono=res.telefono,
                activo=res.activo,
                empresa_id=res.empresa_id,
                created_at=res.created_at,
                updated_at=res.updated_at,
            ),
        )
    )


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
)
async def delete_user(
    empresa_id: str,
    usuario_id: str,
    current_user: UserResponse = Depends(
        require_permission(PermissionModule.ADMIN, "delete")
    ),
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case),
) -> None:
    """Elimina un usuario asociado al tenant activo."""
    await use_case.execute(usuario_id)