from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dtos import LoginUserRequest, RefreshTokenRequest, RegisterUserRequest
from app.application.use_cases.auth import (
    ChangePasswordUseCase,
    GetCurrentUserUseCase,
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from app.composition.container import (
    get_login_user_use_case,
    get_logout_user_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
    provide_change_password_use_case,
    provide_current_user_use_case,
    provide_request_password_reset_use_case,
    provide_reset_password_use_case,
)
from app.presentation.api.v1.endpoints.dependencies import get_current_active_user
from app.presentation.api.v1.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenAttributes,
    TokenDocument,
    TokenResource,
    UserAttributes,
    UserDocument,
    UserResource,
)

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/register",
    response_model=TokenDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> TokenDocument:
    dto_req = RegisterUserRequest(
        email=request.data.attributes.email,
        password=request.data.attributes.password,
        nombre=request.data.attributes.nombre,
        company_name=request.data.attributes.company_name,
        telefono=request.data.attributes.telefono,
    )
    tokens_dto = await use_case.execute(dto_req)
    return TokenDocument(
        data=TokenResource(
            id="auth",
            attributes=TokenAttributes(
                access_token=tokens_dto.access_token,
                refresh_token=tokens_dto.refresh_token,
            ),
        )
    )


@router.post(
    "/login",
    response_model=TokenDocument,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
)
async def login(
    request: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> TokenDocument:
    """Autentica a un usuario y devuelve los tokens de acceso y refresco en formato JSON:API."""
    dto_req = LoginUserRequest(
        email=request.data.attributes.email,
        password=request.data.attributes.password,
    )
    tokens_dto = await use_case.execute(dto_req)
    return TokenDocument(
        data=TokenResource(
            id="auth",
            attributes=TokenAttributes(
                access_token=tokens_dto.access_token,
                refresh_token=tokens_dto.refresh_token,
            ),
        )
    )


@router.post(
    "/refresh",
    response_model=TokenDocument,
    status_code=status.HTTP_200_OK,
    summary="Rotar tokens de autenticación",
)
async def refresh(
    request: RefreshRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> TokenDocument:
    """Revoca el token de refresco actual y emite un nuevo par de tokens en formato JSON:API."""
    dto_req = RefreshTokenRequest(
        refresh_token=request.data.attributes.refresh_token,
    )
    tokens_dto = await use_case.execute(dto_req)
    return TokenDocument(
        data=TokenResource(
            id="auth",
            attributes=TokenAttributes(
                access_token=tokens_dto.access_token,
                refresh_token=tokens_dto.refresh_token,
            ),
        )
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión",
)
async def logout(
    token: HTTPAuthorizationCredentials = Depends(security),
    use_case: LogoutUserUseCase = Depends(get_logout_user_use_case),
) -> None:
    """Revoca el token de acceso actual añadiendo su JTI a la lista de bloqueo en Redis."""
    await use_case.execute(token.credentials)


@router.get(
    "/me",
    response_model=UserDocument,
    status_code=status.HTTP_200_OK,
    summary="Consultar perfil del usuario actual",
)
async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    use_case: GetCurrentUserUseCase = Depends(provide_current_user_use_case),
) -> UserDocument:
    """Obtiene la información del perfil del usuario autenticado actual en formato JSON:API."""
    user_resp = await use_case.execute(token.credentials)
    return UserDocument(
        data=UserResource(
            id=user_resp.id,
            attributes=UserAttributes(
                email=user_resp.email,
                nombre=user_resp.nombre,
                empresa_id=user_resp.empresa_id,
                telefono=user_resp.telefono,
                activo=user_resp.activo,
                created_at=user_resp.created_at,
                updated_at=user_resp.updated_at,
            ),
        )
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña del usuario actual",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: Any = Depends(get_current_active_user),
    use_case: ChangePasswordUseCase = Depends(provide_change_password_use_case),
) -> JSONResponse:
    """Cambia la contraseña del usuario autenticado y emite la alerta de seguridad."""
    await use_case.execute(
        user_id=current_user.id,
        old_password=request.data.attributes.old_password,
        new_password=request.data.attributes.new_password,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"meta": {"message": "Contraseña cambiada exitosamente"}},
        headers={"Content-Type": "application/vnd.api+json"},
    )


@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar reset de contraseña",
)
async def forgot_password(
    request: ForgotPasswordRequest,
    use_case: RequestPasswordResetUseCase = Depends(provide_request_password_reset_use_case),
) -> Response:
    """Envía un email con un enlace de reset. Siempre responde 202 para evitar enumeración."""
    await use_case.execute(request.data.attributes.email)
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña con token",
)
async def reset_password(
    request: ResetPasswordRequest,
    use_case: ResetPasswordUseCase = Depends(provide_reset_password_use_case),
) -> JSONResponse:
    """Consume el token de un solo uso, actualiza la contraseña y envía la confirmación."""
    await use_case.execute(
        raw_token=request.data.attributes.token,
        new_password=request.data.attributes.new_password,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"meta": {"message": "Contraseña restablecida exitosamente"}},
        headers={"Content-Type": "application/vnd.api+json"},
    )
