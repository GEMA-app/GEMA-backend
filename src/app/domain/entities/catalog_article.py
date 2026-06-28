"""Entidades de dominio para el catálogo: ArticleCategory y CatalogArticle."""

import uuid
from dataclasses import dataclass
from datetime import datetime

# ---------------------------------------------------------------------------
# Constantes de validación
# ---------------------------------------------------------------------------
MAX_CATEGORY_NAME_LENGTH: int = 100
MAX_ARTICLE_NAME_LENGTH: int = 255
MAX_DESCRIPTION_LENGTH: int = 2000
MAX_MANUFACTURER_LENGTH: int = 100
MAX_MODEL_LENGTH: int = 100
MAX_UNIT_OF_MEASURE_LENGTH: int = 50


@dataclass
class ArticleCategory:
    """Entidad de dominio para una categoría de artículos del catálogo.

    Attributes:
        id: Identificador único de la categoría.
        empresa_id: Identificador de la empresa (tenant) a la que pertenece.
        nombre: Nombre de la categoría.
        description: Descripción opcional de la categoría.
        created_at: Fecha y hora de creación.
        updated_at: Fecha y hora de la última actualización.
    """

    id: uuid.UUID
    empresa_id: uuid.UUID
    nombre: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CatalogArticle:
    """Entidad de dominio para un artículo del catálogo.

    Representa un artículo genérico del catálogo de la empresa, que puede ser
    instanciado como activo físico. Contiene información descriptiva como
    fabricante, modelo y unidad de medida.

    Attributes:
        id: Identificador único del artículo.
        empresa_id: Identificador de la empresa (tenant) a la que pertenece.
        category_id: Identificador de la categoría a la que pertenece (opcional).
        name: Nombre del artículo.
        description: Descripción opcional del artículo.
        manufacturer: Fabricante del artículo (opcional).
        model: Modelo del artículo (opcional).
        unit_of_measure: Unidad de medida del artículo (opcional).
        created_at: Fecha y hora de creación.
        updated_at: Fecha y hora de la última actualización.
    """

    id: uuid.UUID
    empresa_id: uuid.UUID
    category_id: uuid.UUID | None
    name: str
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    unit_of_measure: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def create(
        cls,
        empresa_id: uuid.UUID,
        name: str,
        category_id: uuid.UUID | None = None,
        description: str | None = None,
        manufacturer: str | None = None,
        model: str | None = None,
        unit_of_measure: str | None = None,
    ) -> "CatalogArticle":
        """Crea un nuevo artículo de catálogo validando las reglas de negocio.

        Args:
            empresa_id: Identificador de la empresa propietaria.
            name: Nombre del artículo (no puede estar vacío).
            category_id: Identificador de la categoría (opcional).
            description: Descripción del artículo (opcional).
            manufacturer: Fabricante del artículo (opcional).
            model: Modelo del artículo (opcional).
            unit_of_measure: Unidad de medida (opcional).

        Returns:
            Una nueva instancia de CatalogArticle con los datos proporcionados.

        Raises:
            EmptyCatalogArticleNameError: Si el nombre está vacío o solo contiene espacios.
        """
        from app.domain.exceptions import EmptyCatalogArticleNameError

        stripped = name.strip()
        if not stripped:
            raise EmptyCatalogArticleNameError()

        return cls(
            id=uuid.uuid4(),
            empresa_id=empresa_id,
            category_id=category_id,
            name=stripped,
            description=description.strip() if description else None,
            manufacturer=manufacturer.strip() if manufacturer else None,
            model=model.strip() if model else None,
            unit_of_measure=unit_of_measure.strip() if unit_of_measure else None,
        )

    def change_name(self, new_name: str) -> None:
        """Cambia el nombre del artículo.

        Args:
            new_name: Nuevo nombre del artículo (no puede estar vacío).

        Raises:
            EmptyCatalogArticleNameError: Si el nuevo nombre está vacío.
        """
        from app.domain.exceptions import EmptyCatalogArticleNameError

        stripped = new_name.strip()
        if not stripped:
            raise EmptyCatalogArticleNameError()
        self.name = stripped

    def change_description(self, new_description: str | None) -> None:
        """Cambia la descripción del artículo.

        Args:
            new_description: Nueva descripción, o None para limpiar.
        """
        self.description = new_description.strip() if new_description else None

    def change_manufacturer(self, new_manufacturer: str | None) -> None:
        """Cambia el fabricante del artículo.

        Args:
            new_manufacturer: Nuevo fabricante, o None para limpiar.
        """
        self.manufacturer = new_manufacturer.strip() if new_manufacturer else None

    def change_model(self, new_model: str | None) -> None:
        """Cambia el modelo del artículo.

        Args:
            new_model: Nuevo modelo, o None para limpiar.
        """
        self.model = new_model.strip() if new_model else None

    def change_unit_of_measure(self, new_unit: str | None) -> None:
        """Cambia la unidad de medida del artículo.

        Args:
            new_unit: Nueva unidad de medida, o None para limpiar.
        """
        self.unit_of_measure = new_unit.strip() if new_unit else None

    def assign_category(self, category_id: uuid.UUID | None) -> None:
        """Asigna o desasigna una categoría al artículo.

        Args:
            category_id: Identificador de la categoría, o None para desasignar.
        """
        self.category_id = category_id
