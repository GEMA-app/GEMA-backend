"""DTOs de entrada y salida para el módulo de Auth."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class RegisterUserRequest:
    """DTO de entrada para la solicitud de registro de usuario."""

    email: str
    password: str
    nombre: str
    company_name: str
    telefono: str | None = None


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
    nombre: str
    empresa_id: str
    telefono: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime
    roles: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RefreshTokenRequest:
    """DTO de entrada para la solicitud de rotación de tokens."""

    refresh_token: str


@dataclass(frozen=True)
class ChangePasswordRequest:
    """DTO de entrada para el cambio de contraseña."""

    user_id: str
    old_password: str
    new_password: str


@dataclass(frozen=True)
class LogoutUserRequest:
    """DTO de entrada para el cierre de sesión."""

    access_token: str
    refresh_token: str | None = None


@dataclass(frozen=True)
class GetCurrentUserRequest:
    """DTO de entrada para la consulta del usuario autenticado."""

    access_token: str


@dataclass(frozen=True)
class RequestPasswordResetRequest:
    """DTO de entrada para solicitar restablecimiento de contraseña."""

    email: str


@dataclass(frozen=True)
class ResetPasswordRequest:
    """DTO de entrada para completar el restablecimiento de contraseña."""

    raw_token: str
    new_password: str
