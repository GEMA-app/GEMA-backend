from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateUserRequest:
    """DTO de entrada para la solicitud de creación de un nuevo usuario."""

    email: str
    password: str
    nombre: str
    telefono: str | None = None


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