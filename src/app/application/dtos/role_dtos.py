"""DTOs de entrada y salida para el módulo de Role."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PermissionDTO:
    """DTO que representa un permiso granular por módulo."""

    module: str
    can_view: bool = False
    can_create: bool = False
    can_edit: bool = False
    can_delete: bool = False


@dataclass(frozen=True)
class CreateRoleRequest:
    """DTO de entrada para la creación de un rol."""

    nombre: str
    descripcion: str
    permisos: list[PermissionDTO]


@dataclass(frozen=True)
class UpdateRoleRequest:
    """DTO de entrada para la actualización parcial de un rol."""

    nombre: str | None = None
    descripcion: str | None = None
    permisos: list[PermissionDTO] | None = None
    version: int | None = None
    _fields_set: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Calcula el conjunto de campos explícitamente establecidos en la inicialización."""
        if not self._fields_set:
            fields_with_values = {
                name for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))


@dataclass(frozen=True)
class AssignRoleRequest:
    """DTO de entrada para asignar un rol a un usuario."""

    usuario_id: str


@dataclass(frozen=True)
class RoleResponse:
    """DTO de salida con los datos completos de un rol."""

    id: str
    empresa_id: str
    nombre: str
    descripcion: str
    permisos: list[PermissionDTO]
    version: int
