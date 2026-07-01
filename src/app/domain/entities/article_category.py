"""Entidad de dominio ArticleCategory (Categoría de Artículo del Catálogo)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.exceptions.base import ValidationError

_NAME_MAX_LENGTH = 100
_DESCRIPTION_MAX_LENGTH = 255


@dataclass
class ArticleCategory:
    """Entidad que representa una categoría de artículo en el catálogo de la empresa.

    Protege las invariantes: nombre obligatorio (1-100 caracteres),
    descripción opcional (máximo 255 caracteres), nombre único por tenant.
    """

    id: UUID
    empresa_id: UUID
    name: str
    description: str | None
    version: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    articulos_count: int | None = None

    @classmethod
    def create(
        cls, id: UUID, empresa_id: UUID, name: str, description: str | None
    ) -> "ArticleCategory":
        """Crea una nueva categoría de artículo validando invariantes de negocio.

        Args:
            id: Identificador único UUID de la categoría.
            empresa_id: Identificador UUID del tenant propietario.
            name: Nombre de la categoría (entre 1 y {_NAME_MAX_LENGTH} caracteres).
            description: Descripción opcional de la categoría.

        Returns:
            Una nueva instancia de ArticleCategory con las invariantes validadas.

        Raises:
            ValidationError: Si el nombre está vacío o excede {_NAME_MAX_LENGTH} caracteres.
        """
        if not name or len(name.strip()) == 0:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        if len(name) > _NAME_MAX_LENGTH:
            raise ValidationError(f"El nombre no puede exceder los {_NAME_MAX_LENGTH} caracteres.")
        return cls(
            id=id,
            empresa_id=empresa_id,
            name=name.strip(),
            description=description.strip() if description else None,
            version=1,
        )

    def change_name(self, new_name: str) -> None:
        """Cambia el nombre de la categoría validando la longitud del nuevo valor.

        Args:
            new_name: Nuevo nombre de la categoría.

        Raises:
            ValidationError: Si el nuevo nombre está vacío o excede {_NAME_MAX_LENGTH} caracteres.
        """
        if not new_name or len(new_name.strip()) == 0:
            raise ValidationError("El nombre de la categoría es obligatorio.")
        if len(new_name) > _NAME_MAX_LENGTH:
            raise ValidationError(f"El nombre no puede exceder los {_NAME_MAX_LENGTH} caracteres.")
        self.name = new_name.strip()

    def change_description(self, new_description: str | None) -> None:
        """Cambia la descripción de la categoría validando su longitud.

        Args:
            new_description: Nueva descripción de la categoría (None para limpiar).

        Raises:
            ValidationError: Si la descripción excede {_DESCRIPTION_MAX_LENGTH} caracteres.
        """
        if new_description and len(new_description) > _DESCRIPTION_MAX_LENGTH:
            raise ValidationError(
                f"La descripción no puede exceder los {_DESCRIPTION_MAX_LENGTH} caracteres."
            )
        self.description = new_description.strip() if new_description else None
