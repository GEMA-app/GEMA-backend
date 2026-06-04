from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PermissionDTO:
    module: str
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False


@dataclass(frozen=True)
class CreateRoleRequest:
    nombre: str
    descripcion: str
    permisos: list[PermissionDTO]


@dataclass(frozen=True)
class UpdateRoleRequest:
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    permisos: Optional[list[PermissionDTO]] = None


@dataclass(frozen=True)
class AssignRoleRequest:
    usuario_id: str


@dataclass(frozen=True)
class RoleResponse:
    id: str
    empresa_id: str
    nombre: str
    descripcion: str
    permisos: list[PermissionDTO]
