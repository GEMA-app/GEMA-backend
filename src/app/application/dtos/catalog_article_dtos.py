"""DTOs de entrada y salida para los casos de uso de artículos de catálogo."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CreateCatalogArticleRequest:
    """DTO de entrada para crear un artículo de catálogo.

    Attributes:
        category_id: Identificador de la categoría (opcional).
        name: Nombre del artículo.
        description: Descripción del artículo (opcional).
        manufacturer: Fabricante del artículo (opcional).
        model: Modelo del artículo (opcional).
        unit_of_measure: Unidad de medida del artículo (opcional).
    """

    category_id: str | None
    name: str
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_of_measure: str | None = None


@dataclass(frozen=True)
class UpdateCatalogArticleRequest:
    """DTO de entrada para actualizar un artículo de catálogo.

    Atributos opcionales. Solo los campos provistos (no None) se actualizan.
    _fields_set se usa internamente para detectar qué campos envió el cliente.

    Attributes:
        category_id: Identificador de la categoría (opcional).
        name: Nombre del artículo (opcional).
        description: Descripción del artículo (opcional).
        manufacturer: Fabricante del artículo (opcional).
        model: Modelo del artículo (opcional).
        unit_of_measure: Unidad de medida del artículo (opcional).
    """

    category_id: str | None = None
    name: str | None = None
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_of_measure: str | None = None

    _fields_set: frozenset[str] = field(
        default_factory=frozenset,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        """Inicializa _fields_set con los campos que tienen valor distinto de None."""
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
    """DTO de salida para artículos de catálogo.

    Attributes:
        id: Identificador único del artículo.
        empresa_id: Identificador de la empresa propietaria.
        category_id: Identificador de la categoría asignada (opcional).
        name: Nombre del artículo.
        description: Descripción del artículo (opcional).
        manufacturer: Fabricante del artículo (opcional).
        model: Modelo del artículo (opcional).
        unit_of_measure: Unidad de medida del artículo (opcional).
    """

    id: str
    empresa_id: str
    category_id: str | None
    name: str
    description: str | None
    manufacturer: str | None
    model: str | None
    unit_of_measure: str | None
