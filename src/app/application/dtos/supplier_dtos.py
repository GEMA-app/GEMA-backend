"""DTOs de petición/respuesta para proveedores."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateSupplierRequest:
    """DTO de solicitud para crear un proveedor."""

    name: str
    rif: str | None = None
    phone: str | None = None
    email: str | None = None
    contact: str | None = None
    is_active: bool = True
    direccion: str | None = None


@dataclass(frozen=True)
class UpdateSupplierRequest:
    """DTO de solicitud para actualizar parcialmente un proveedor."""

    name: str | None = None
    rif: str | None = None
    phone: str | None = None
    email: str | None = None
    contact: str | None = None
    is_active: bool | None = None
    direccion: str | None = None
    version: int | None = None
    _fields_set: frozenset[str] = field(default_factory=frozenset, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Calcula el conjunto de campos explícitamente establecidos en la inicialización."""
        if not self._fields_set:
            fields_with_values = {
                name
                for name, val in self.__dict__.items()
                if name != "_fields_set" and val is not None
            }
            object.__setattr__(self, "_fields_set", frozenset(fields_with_values))


@dataclass(frozen=True)
class SupplierResponse:
    """DTO de respuesta con los datos serializados de un proveedor."""

    id: UUID
    empresa_id: UUID
    name: str
    rif: str | None
    phone: str | None
    email: str | None
    contact: str | None
    version: int
    is_active: bool = True
    direccion: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
