"""DTOs para el módulo de usuarios."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class CreateUserRequest:
    """DTO de entrada para la solicitud de creación de un nuevo usuario."""

    email: str
    password: str
    nombre: str
    telefono: str | None = None


@dataclass(frozen=True)
class UpdateUserRequest:
    """DTO de entrada para la actualización parcial de un usuario."""

    nombre: str | None = None
    email: str | None = None
    telefono: str | None = None
    activo: bool | None = None


@dataclass(frozen=True)
class UserResponse:
    """DTO de salida con la información pública y detallada de un usuario."""

    id: str
    email: str
    nombre: str
    empresa_id: str
    telefono: str | None
    activo: bool
    created_at: datetime
    updated_at: datetime
    roles: list[str] = field(default_factory=list)
