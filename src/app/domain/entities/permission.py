from dataclasses import dataclass
from app.domain.enums import PermissionModule


@dataclass(frozen=True)
class Permission:
    """Objeto de valor que representa los permisos concedidos para un módulo específico."""
    module: PermissionModule
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False
