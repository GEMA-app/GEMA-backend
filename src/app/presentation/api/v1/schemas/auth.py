from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject

# --- Atributos y Recursos de Usuario ---


class UserAttributes(BaseModel):
    """Atributos de un usuario en JSON:API."""

    email: str = Field(..., description="Correo electrónico del usuario")
    nombre: str = Field(..., description="Nombre completo del usuario")
    empresa_id: str = Field(..., description="Identificador único de la empresa")
    telefono: str | None = Field(None, description="Teléfono de contacto")
    activo: bool = Field(..., description="Estado de activación del usuario")
    created_at: datetime = Field(..., description="Fecha y hora de creación")
    updated_at: datetime = Field(..., description="Fecha y hora de última actualización")


class UserResource(BaseModel):
    """Recurso de usuario en JSON:API."""

    type: str = Field(default="users", description="Tipo de recurso")
    id: str = Field(..., description="ID único del usuario")
    attributes: UserAttributes
    links: LinksObject | None = None


class UserDocument(BaseModel):
    """Documento JSON:API para una respuesta de usuario."""

    data: UserResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# --- Atributos y Recursos de Tokens ---


class TokenAttributes(BaseModel):
    """Atributos de tokens de autenticación en JSON:API."""

    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresco JWT")
    token_type: str = Field(default="Bearer", description="Tipo de token")


class TokenResource(BaseModel):
    """Recurso de tokens en JSON:API."""

    type: str = Field(default="tokens", description="Tipo de recurso")
    id: str = Field(default="auth", description="Identificador del recurso de tokens")
    attributes: TokenAttributes
    links: LinksObject | None = None


class TokenDocument(BaseModel):
    """Documento JSON:API para una respuesta de tokens."""

    data: TokenResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# --- Solicitudes (Requests) ---


class RegisterAttributes(BaseModel):
    email: str = Field(..., description="Correo electrónico para registro")
    password: str = Field(..., description="Contraseña en texto plano")
    nombre: str = Field(..., description="Nombre completo del usuario")
    company_name: str = Field(..., description="Nombre de la empresa a crear")
    telefono: str | None = Field(None, description="Teléfono de contacto")


class RegisterResource(BaseModel):
    type: str = Field(default="users", description="Tipo de recurso solicitado")
    attributes: RegisterAttributes


class RegisterRequest(BaseModel):
    """Solicitud JSON:API para registro de usuario."""

    data: RegisterResource


class LoginAttributes(BaseModel):
    email: str = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class LoginResource(BaseModel):
    type: str = Field(default="tokens", description="Tipo de recurso solicitado")
    attributes: LoginAttributes


class LoginRequest(BaseModel):
    """Solicitud JSON:API para inicio de sesión."""

    data: LoginResource


class RefreshAttributes(BaseModel):
    refresh_token: str = Field(..., description="Token de refresco actual")


class RefreshResource(BaseModel):
    type: str = Field(default="tokens", description="Tipo de recurso solicitado")
    attributes: RefreshAttributes


class RefreshRequest(BaseModel):
    """Solicitud JSON:API para rotación de tokens."""

    data: RefreshResource


class LogoutAttributes(BaseModel):
    access_token: str | None = Field(None, description="Token de acceso a revocar")


class LogoutResource(BaseModel):
    type: str = Field(default="tokens", description="Tipo de recurso solicitado")
    attributes: LogoutAttributes


class LogoutRequest(BaseModel):
    """Solicitud JSON:API para cierre de sesión."""

    data: LogoutResource


# --- Cambio de Contraseña ---


class ChangePasswordAttributes(BaseModel):
    old_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")


class ChangePasswordResource(BaseModel):
    type: str = Field(default="passwords", description="Tipo de recurso solicitado")
    attributes: ChangePasswordAttributes


class ChangePasswordRequest(BaseModel):
    """Solicitud JSON:API para cambio de contraseña."""

    data: ChangePasswordResource


# --- Recuperación de Contraseña ---


class ForgotPasswordAttributes(BaseModel):
    email: str = Field(..., description="Correo electrónico de la cuenta")


class ForgotPasswordResource(BaseModel):
    type: str = Field(default="passwords", description="Tipo de recurso solicitado")
    attributes: ForgotPasswordAttributes


class ForgotPasswordRequest(BaseModel):
    """Solicitud JSON:API para solicitar reset de contraseña."""

    data: ForgotPasswordResource


# --- Restablecimiento de Contraseña ---


class ResetPasswordAttributes(BaseModel):
    token: str = Field(..., description="Token de recuperación recibido por email")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")


class ResetPasswordResource(BaseModel):
    type: str = Field(default="passwords", description="Tipo de recurso solicitado")
    attributes: ResetPasswordAttributes


class ResetPasswordRequest(BaseModel):
    """Solicitud JSON:API para restablecer contraseña con token."""

    data: ResetPasswordResource
