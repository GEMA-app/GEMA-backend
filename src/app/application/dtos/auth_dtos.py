from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegisterUserRequest:
    """DTO de entrada para la solicitud de registro de usuario."""
    email: str
    password: str


@dataclass(frozen=True)
class LoginUserRequest:
    """DTO de entrada para la solicitud de inicio de sesión."""
    email: str
    password: str


@dataclass(frozen=True)
class AuthTokensDTO:
    """DTO de salida que contiene los tokens de acceso y refresco."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


@dataclass(frozen=True)
class UserResponse:
    """DTO de salida con la información pública de un usuario."""
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class RefreshTokenRequest:
    """DTO de entrada para la solicitud de rotación de tokens."""
    refresh_token: str
