from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.application.dtos import LoginUserRequest, RefreshTokenRequest, RegisterUserRequest
from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.logout_user import LogoutUserUseCase
from app.application.use_cases.refresh_token import RefreshTokenUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.composition.container import (
    get_get_current_user_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
)
from app.presentation.api.v1.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
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
    """Registra un nuevo usuario en el sistema y devuelve los tokens de acceso y refresco en formato JSON:API."""
    dto_req = RegisterUserRequest(
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
    use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
) -> UserDocument:
    """Obtiene la información del perfil del usuario autenticado actual en formato JSON:API."""
    user_resp = await use_case.execute(token.credentials)
    return UserDocument(
        data=UserResource(
            id=user_resp.id,
            attributes=UserAttributes(
                email=user_resp.email,
                is_active=user_resp.is_active,
                created_at=user_resp.created_at,
                updated_at=user_resp.updated_at,
            ),
        )
    )
