"""Value Object Slug — identificador URL-friendly validado para empresas."""

import re
import unicodedata
from dataclasses import dataclass

from app.domain.exceptions import InvalidSlugError


@dataclass(frozen=True)
class Slug:
    """Objeto de valor que representa un identificador URL-friendly para una empresa.

    Formato válido: solo letras minúsculas, dígitos y guiones (a-z, 0-9, -).
    No puede comenzar ni terminar con guión. Longitud entre 2 y 63 caracteres.

    Raises:
        InvalidSlugError: Si el slug está vacío o tiene formato inválido.
    """

    value: str

    _PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")

    def __post_init__(self) -> None:
        """Valida que el slug no esté vacío y tenga formato correcto."""
        if not self.value or not isinstance(self.value, str):
            raise InvalidSlugError("El slug no puede estar vacío.")
        if not self._PATTERN.match(self.value):
            raise InvalidSlugError(
                f"El slug '{self.value}' tiene un formato inválido. "
                "Solo se permiten letras minúsculas, dígitos y guiones, "
                "sin comenzar ni terminar con guión."
            )

    @classmethod
    def from_name(cls, name: str) -> "Slug":
        """Genera un slug a partir de un nombre de empresa.

        Args:
            name: El nombre de empresa a convertir en slug.

        Returns:
            Un nuevo Slug normalizado (minúsculas, sin acentos, con guiones).
        """
        # Normalizar unicode y eliminar acentos
        normalized = unicodedata.normalize("NFD", name.lower())
        ascii_name = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
        return cls(value=slug[:63] if slug else "empresa")
