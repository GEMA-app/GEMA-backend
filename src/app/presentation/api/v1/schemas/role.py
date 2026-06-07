from typing import Any

from pydantic import BaseModel, Field

from app.presentation.api.v1.schemas.jsonapi_base import LinksObject


class PermissionAttributes(BaseModel):
    module: str
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False


class RoleAttributes(BaseModel):
    nombre: str
    descripcion: str
    permisos: list[PermissionAttributes] = []


class RoleResource(BaseModel):
    type: str = Field(default="roles", description="Tipo de recurso")
    id: str = Field(..., description="ID único del rol")
    attributes: RoleAttributes
    links: LinksObject | None = None


class RoleDocument(BaseModel):
    data: RoleResource
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


class RoleListDocument(BaseModel):
    data: list[RoleResource]
    links: LinksObject | None = None
    meta: dict[str, Any] | None = None


# Solicitudes (Requests)
class CreateRoleAttributes(BaseModel):
    nombre: str
    descripcion: str
    permisos: list[PermissionAttributes]


class CreateRoleResource(BaseModel):
    type: str = Field(default="roles", description="Tipo de recurso")
    attributes: CreateRoleAttributes


class CreateRoleRequest(BaseModel):
    data: CreateRoleResource


class UpdateRoleAttributes(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    permisos: list[PermissionAttributes] | None = None


class UpdateRoleResource(BaseModel):
    type: str = Field(default="roles", description="Tipo de recurso")
    attributes: UpdateRoleAttributes


class UpdateRoleRequest(BaseModel):
    data: UpdateRoleResource


class AssignRoleAttributes(BaseModel):
    usuario_id: str


class AssignRoleResource(BaseModel):
    type: str = Field(default="roles", description="Tipo de recurso")
    attributes: AssignRoleAttributes


class AssignRoleRequest(BaseModel):
    data: AssignRoleResource
