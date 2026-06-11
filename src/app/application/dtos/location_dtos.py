from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateLocationRequest:
    nombre: str
    tipo: str
    parent_id: str | None = None
    descripcion: str | None = None


@dataclass(frozen=True)
class UpdateLocationRequest:
    nombre: str | None = None
    tipo: str | None = None
    parent_id: str | None = None
    descripcion: str | None = None
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
class LocationResponse:
    id: str
    empresa_id: str
    parent_id: str | None
    nombre: str
    tipo: str
    descripcion: str | None
    version: int


@dataclass(frozen=True)
class LocationTreeResponse:
    id: str
    nombre: str
    tipo: str
    descripcion: str | None
    children: list[LocationTreeResponse]
