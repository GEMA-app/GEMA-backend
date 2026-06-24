from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateCatalogArticleRequest:
    """DTO de entrada para crear un artículo de catálogo."""

    categoria_id: str | None
    nombre: str
    descripcion: str | None = None
    fabricante: str | None = None
    modelo: str | None = None
    unidad_medida: str | None = None


@dataclass(frozen=True)
class UpdateCatalogArticleRequest:
    """DTO de entrada para actualizar un artículo de catálogo."""

    categoria_id: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    fabricante: str | None = None
    modelo: str | None = None
    unidad_medida: str | None = None

    _fields_set: frozenset[str] = field(
        default_factory=frozenset,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not self._fields_set:
            fields_with_values = {
                name
                for name, value in self.__dict__.items()
                if name != "_fields_set" and value is not None
            }
            object.__setattr__(
                self,
                "_fields_set",
                frozenset(fields_with_values),
            )


@dataclass(frozen=True)
class CatalogArticleResponse:
    """DTO de salida para artículos de catálogo."""

    id: str
    empresa_id: str
    categoria_id: str | None
    nombre: str
    descripcion: str | None
    fabricante: str | None
    modelo: str | None
    unidad_medida: str | None