# Re-exporta todos los DTOs para mantener compatibilidad
# con imports existentes: `from app.application.dtos import RegisterUserRequest`
from app.application.dtos.auth_dtos import (
    AuthTokensDTO,
    LoginUserRequest,
    RefreshTokenRequest,
    RegisterUserRequest,
    UserResponse,
)

__all__ = [
    "AuthTokensDTO",
    "LoginUserRequest",
    "RefreshTokenRequest",
    "RegisterUserRequest",
    "UserResponse",
]
