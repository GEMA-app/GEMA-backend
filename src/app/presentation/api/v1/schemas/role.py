"""Schemas JSON:API para roles y permisos: atributos, recursos,
documentos individuales y listados, solicitudes de creación,
actualización y asignación.
"""

from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import PermissionModule
from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class PermissionAttributes(BaseModel):
    """Atributos de un permiso individual."""

    module: PermissionModule
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False


class RoleAttributes(BaseModel):
    """Atributos de un rol."""

    nombre: str
    descripcion: str
    permisos: list[PermissionAttributes] = Field(default_factory=list)
    version: int


class RoleResource(BaseModel):
    """Recurso JSON:API de un rol."""

    type: str = Field(default="roles", description="Tipo de recurso")
    id: str = Field(..., description="ID único del rol")
    attributes: RoleAttributes
    links: LinksObject | None = None


class RoleDocument(BaseModel):
    """Documento JSON:API con un rol."""

    data: RoleResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class RoleListDocument(BaseModel):
    """Documento JSON:API con lista de roles."""

    data: list[RoleResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateRoleAttributes(BaseModel):
    """Atributos para crear un rol."""

    nombre: str
    descripcion: str
    permisos: list[PermissionAttributes]


class CreateRoleResource(BaseModel):
    """Recurso JSON:API para crear un rol."""

    type: str = Field(default="roles", description="Tipo de recurso")
    attributes: CreateRoleAttributes


class CreateRoleRequest(BaseModel):
    """Solicitud JSON:API para crear un rol."""

    data: CreateRoleResource


class UpdateRoleAttributes(BaseModel):
    """Atributos para actualizar un rol."""

    nombre: str | None = None
    descripcion: str | None = None
    permisos: list[PermissionAttributes] | None = None
    version: int | None = None


class UpdateRoleResource(BaseModel):
    """Recurso JSON:API para actualizar un rol."""

    type: str = Field(default="roles", description="Tipo de recurso")
    attributes: UpdateRoleAttributes


class UpdateRoleRequest(BaseModel):
    """Solicitud JSON:API para actualizar un rol."""

    data: UpdateRoleResource


class AssignRoleAttributes(BaseModel):
    """Atributos para asignar un rol."""

    usuario_id: str


class AssignRoleResource(BaseModel):
    """Recurso JSON:API para asignar un rol."""

    type: str = Field(default="roles", description="Tipo de recurso")
    attributes: AssignRoleAttributes


class AssignRoleRequest(BaseModel):
    """Solicitud JSON:API para asignar un rol."""

    data: AssignRoleResource
