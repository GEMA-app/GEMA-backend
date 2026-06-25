"""Esquemas de validación Pydantic para la entidad de Usuarios,
siguiendo estrictamente las convenciones de JSON:API de la plataforma.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, EmailStr

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject

# --- Atributos y Recursos de Respuesta (Output) ---

class UserAttributes(BaseModel):
    """Atributos públicos de un usuario devueltos en las respuestas HTTP."""

    email: str = Field(..., description="Correo electrónico del usuario")
    nombre: str = Field(..., description="Nombre completo del usuario")
    empresa_id: str = Field(..., description="Identificador único de la empresa")
    telefono: str | None = Field(None, description="Teléfono de contacto")
    activo: bool = Field(..., description="Estado de activación del usuario")
    created_at: datetime = Field(..., description="Fecha y hora de creación")
    updated_at: datetime = Field(..., description="Fecha y hora de última actualización")

    class Config:
        from_attributes = True


class UserResource(BaseModel):
    """Representación del recurso de usuario dentro del estándar JSON:API."""

    type: str = Field(default="users", description="Tipo de recurso")
    id: str = Field(..., description="ID único del usuario")
    attributes: UserAttributes
    links: LinksObject | None = None


class UserDocument(BaseModel):
    """Documento de respuesta para un único usuario."""

    data: UserResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class UserListDocument(BaseModel):
    """Documento de respuesta para listados de usuarios, incluyendo paginación."""

    data: list[UserResource]
    links: LinksObject | None = None
    meta: dict[str, Any] = Field(..., description="Metadatos de paginación")


# --- Solicitudes de Creación (POST) ---

class CreateUserAttributes(BaseModel):
    """Atributos requeridos en el cuerpo de la petición para registrar un usuario."""

    email: EmailStr = Field(..., description="Correo electrónico para el nuevo usuario")
    password: str = Field(..., min_length=6, description="Contraseña en texto plano")
    nombre: str = Field(..., description="Nombre completo del usuario")
    telefono: str | None = Field(None, description="Teléfono de contacto")


class CreateUserResource(BaseModel):
    """Contenedor del recurso de creación."""

    type: str = Field(default="users", description="Tipo de recurso solicitado")
    attributes: CreateUserAttributes


class CreateUserRequest(BaseModel):
    """Esquema de entrada para la creación de un usuario."""

    data: CreateUserResource


# --- Solicitudes de Actualización (PATCH) ---

class UpdateUserAttributes(BaseModel):
    """Atributos opcionales permitidos para la modificación de un usuario."""

    email: Optional[EmailStr] = Field(None, description="Nuevo correo electrónico")
    nombre: Optional[str] = Field(None, description="Nuevo nombre completo")
    telefono: Optional[str] = Field(None, description="Nuevo teléfono de contacto")
    activo: Optional[bool] = Field(None, description="Nuevo estado de activación")


class UpdateUserResource(BaseModel):
    """Contenedor del recurso de actualización."""

    type: str = Field(default="users", description="Tipo de recurso solicitado")
    attributes: UpdateUserAttributes


class UpdateUserRequest(BaseModel):
    """Esquema de entrada para la actualización parcial (PATCH) de un usuario."""

    data: UpdateUserResource