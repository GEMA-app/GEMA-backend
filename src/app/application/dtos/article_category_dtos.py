"""DTOs de petición/respuesta para categorías de artículos del catálogo."""

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class CreateCategoryRequest:
    """DTO de solicitud para crear una categoría de artículo."""

    name: str
    description: str | None = None


@dataclass(frozen=True)
class UpdateCategoryRequest:
    """DTO de solicitud para actualizar parcialmente una categoría de artículo."""

    name: str | None = None
    description: str | None = None
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
class ArticleCategoryResponse:
    """DTO de respuesta con los datos serializados de una categoría de artículo."""

    id: UUID
    empresa_id: UUID
    name: str
    description: str | None
    version: int
