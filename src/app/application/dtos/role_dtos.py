from dataclasses import dataclass, field


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
    nombre: str | None = None
    descripcion: str | None = None
    permisos: list[PermissionDTO] | None = None
    version: int | None = None
    _fields_set: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self._fields_set:
            fields_with_values = {
                name for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))


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
    version: int
